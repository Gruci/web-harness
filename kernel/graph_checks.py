"""Read-only runner integration for component ownership, decisions and maps."""

from pathlib import Path

from kernel import component_graph, feature_map, graph_workflow, port_contracts
from kernel.gates import components, context_api


def sections(root: Path, verify: bool = False) -> list[tuple]:
    """Graph rules cannot be exempted by the legacy file baseline."""
    try:
        graph = component_graph.load(root)
        sources = feature_map.source_paths(root, graph)
    except FileNotFoundError:
        return [("graph_schema", "컴포넌트 그래프", ["first code requires classification; needs_decision"], None)]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [("graph_schema", "컴포넌트 그래프", [str(exc)], None)]
    failures, unresolved, _observed = context_api.check(graph, root, sources)
    classification = components.check(graph, root, sources)
    approval = graph_workflow.check_approval(root, graph)
    result = [
        ("graph_schema", "컴포넌트 그래프 서식", [], None),
        ("component_classification", "컴포넌트 분류", classification, None),
        ("graph_approval", "그래프 사용자 결정", approval, None),
        ("component_dependencies", "공개 계약과 의존 방향", failures, None),
        ("component_syntax", "컴포넌트 구문 분석", [], ("TOOL", "; ".join(unresolved)) if unresolved else None),
        ("graph_projection", "기능 지도 대조", feature_map.check(root) if not (classification or approval or failures) else [],
         ("SKIP", "resolve graph decisions first") if classification or approval or failures else None),
    ]
    if verify:
        failures, unresolved = port_contracts.run(root, graph)
        result += [("port_contracts", "선언 포트의 실행 계약", failures, None),
                   ("port_tools", "포트 계약 실행 환경", [], ("TOOL", "; ".join(unresolved)) if unresolved else None)]
    return result
