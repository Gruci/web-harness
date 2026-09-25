"""Python import boundaries; unsupported and dynamic analysis remains unverified."""
import ast
from pathlib import Path
from kernel import component_graph, port_contracts


def _module(relative):
    parts = list(Path(relative).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _imports(tree, module, is_package):
    imports = []
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, None, node.lineno))
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name if alias.asname else alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            prefix = module.split(".") if is_package else module.split(".")[:-1]
            if node.level:
                prefix = prefix[:len(prefix) - node.level + 1]
                target = ".".join(prefix + ([node.module] if node.module else []))
            else:
                target = node.module or ""
            for alias in node.names:
                imports.append((target, alias.name, node.lineno))
                aliases[alias.asname or alias.name] = target + "." + alias.name
    return imports, aliases


def _attribute(node, aliases):
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        return _attribute(node.value, aliases) + "." + node.attr
    return ""


def check(graph: dict, root: Path, sources: list[Path]) -> tuple[list[str], list[str], list[dict]]:
    """Return violations, unresolved analysis, and observed (never allowed) edges.

    `graph` is already validated by `component_graph.load`; this gate does not re-validate it.
    """
    if graph["technology"]["syntax"] != "python":
        return [], [f"{graph['technology']['syntax']}: component syntax analyzer unavailable"], []
    violations, unverified, observed = [], [], []
    components = {item["id"]: item for item in graph["components"]}
    modules, parsed = {}, {}
    for path in sources:
        try:
            relative = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            violations.append(f"{path}: source escapes repository")
            continue
        if component_graph.excluded(graph, relative):
            continue
        found = component_graph.owners(graph, relative)
        if len(found) != 1:
            unverified.append(f"{relative}: dependency owner unresolved")
            continue
        if path.suffix != ".py":
            unverified.append(f"{relative}: Python analyzer cannot inspect this source")
            continue
        module = _module(relative)
        modules[module] = (found[0], relative)
        try:
            parsed[module] = ast.parse(path.read_text(encoding="utf-8-sig"), filename=relative)
        except (OSError, UnicodeError, SyntaxError) as error:
            unverified.append(f"{relative}: cannot parse source: {error}")
    contracts = {item["module"]: (component["id"], item) for component in components.values() for item in component["public"]}
    for module, (owner, contract) in contracts.items():
        if components[owner]["state"] != "implemented":
            continue
        if module not in parsed:
            unverified.append(f"{owner}: public module {module} has no parsed source evidence")
            continue
        if modules[module][0][0] != owner:
            violations.append(f"{owner}: public module {module} belongs to another component")
        symbols = set()
        for node in parsed[module].body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.add(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                symbols.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                symbols.update(target.id for target in targets if isinstance(target, ast.Name))
        for symbol in contract["symbols"]:
            if symbol not in symbols:
                violations.append(f"{owner}: public symbol {module}.{symbol} has no declaration")
    for module, tree in parsed.items():
        (owner, role), relative = modules[module]
        imports, aliases = _imports(tree, module, relative.endswith("/__init__.py"))
        for target, symbol, line in imports:
            imported = target + "." + symbol if symbol and target + "." + symbol in modules else target
            name = None if imported != target else symbol
            _boundary(graph, components, modules, contracts, owner, role, imported, name,
                      f"{relative}:{line}", violations, unverified, observed)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                qualified = _attribute(node, aliases)
                matches = [key for key in modules if qualified.startswith(key + ".")]
                if matches:
                    imported = max(matches, key=len)
                    symbol = qualified[len(imported) + 1:].split(".")[0]
                    _boundary(graph, components, modules, contracts, owner, role, imported, symbol,
                              f"{relative}:{node.lineno}", violations, unverified, observed)
            if isinstance(node, ast.Call):
                call = _attribute(node.func, aliases)
                if call in {"__import__", "importlib.import_module", "exec", "eval", "getattr"}:
                    unverified.append(f"{relative}:{node.lineno}: dynamic access {call} needs contract evidence")
                if role == "domain" and call in {"open", "input", "print", "datetime.datetime.now", "datetime.datetime.utcnow", "time.time", "time.sleep"}:
                    violations.append(f"{relative}:{node.lineno}: domain side effect {call}")
    port_failures, port_unknown = port_contracts.check(root, graph, parsed)
    violations.extend(port_failures)
    unverified.extend(port_unknown)
    return sorted(set(violations)), sorted(set(unverified)), sorted(observed, key=lambda item: tuple(item.values()))


def _boundary(graph, components, modules, contracts, owner, role, target, symbol, location,
              violations, unverified, observed):
    match = modules.get(target)
    if not match:
        local_roots = {module.split(".")[0] for module in modules}
        if target.split(".")[0] in local_roots:
            unverified.append(f"{location}: unresolved local import {target}")
        elif target.split(".")[0] not in components[owner]["external"]:
            violations.append(f"{location}: external dependency {target} is not allowed for {owner}")
        return
    (target_owner, target_role), _ = match
    if target_role not in graph["role_dependencies"].get(role, []):
        violations.append(f"{location}: forbidden role dependency {role} -> {target_role}")
    if owner == target_owner:
        return
    declaration = contracts.get(target)
    if not declaration or declaration[0] != target_owner:
        violations.append(f"{location}: private module bypass {target}")
        return
    contract = declaration[1]
    if symbol == "*" or (symbol and symbol not in contract["symbols"]):
        violations.append(f"{location}: private symbol bypass {target}.{symbol}")
    edge = {"source": owner, "target": target_owner, "contract": contract["id"], "kind": "import"}
    if edge not in observed:
        observed.append(edge)
    if edge not in graph["edges"]:
        violations.append(f"{location}: undeclared dependency {owner} -> {target_owner} ({contract['id']}); needs_decision")
