"""Canonical architecture graph validation and ownership contracts."""
import copy
import importlib
import unittest


def example_graph():
    return {
        "schema": 1, "revision": 1,
        "categories": [{"id": "business", "name": "Business", "description": "Rules",
                        "roles": ["domain", "usecases"]}],
        "components": [{"id": "orders", "name": "Orders", "category": "business",
                        "responsibility": "Place orders", "excludes": ["Payments"],
                        "root": "orders", "roles": {"domain": ["*.py", "**/*.py"]},
                        "public": [{"id": "orders-api", "module": "orders.api", "symbols": ["place"]}],
                        "state": "implemented", "external": []}],
        "edges": [], "technology": {"sources": ["**/*.py"], "syntax": "python", "exclude": []},
        "role_dependencies": {"domain": ["domain"], "usecases": ["domain", "usecases"]},
    }


class GraphTests(unittest.TestCase):
    def setUp(self):
        try:
            self.graph_module = importlib.import_module("kernel.component_graph")
        except ModuleNotFoundError:
            self.fail("canonical component graph module is not implemented")
        self.graph = example_graph()

    def test_valid_graph(self):
        self.assertEqual([], self.graph_module.validate(self.graph))

    def test_unknown_reference_and_escape_fail(self):
        self.graph["components"][0]["category"] = "missing"
        self.graph["components"][0]["root"] = "../outside"
        errors = self.graph_module.validate(self.graph)
        self.assertTrue(any("category" in error for error in errors))
        self.assertTrue(any("root" in error for error in errors))

    def test_set_order_does_not_change_digest(self):
        other = copy.deepcopy(self.graph)
        other["categories"][0]["roles"].reverse()
        other["components"][0]["roles"]["domain"].reverse()
        self.assertEqual(self.graph_module.digest(self.graph), self.graph_module.digest(other))

    def test_globs_do_not_duplicate_same_owner(self):
        self.assertEqual([("orders", "domain")], self.graph_module.owners(self.graph, "orders/api.py"))
        self.assertEqual([], self.graph_module.owners(self.graph, "outside/api.py"))

    def test_single_star_does_not_claim_nested_role(self):
        self.graph["components"][0]["roles"] = {"domain": ["*.py"], "usecases": ["nested/*.py"]}
        self.assertEqual([("orders", "usecases")], self.graph_module.owners(self.graph, "orders/nested/api.py"))

    def test_cycles_require_explicit_exception(self):
        self.graph["edges"] = [{"source": "orders", "target": "orders", "contract": "orders-api", "kind": "import"}]
        self.assertTrue(any("cycle" in error for error in self.graph_module.validate(self.graph)))

    def test_malformed_inputs_return_errors(self):
        for value in [None, [], {"schema": 1}, {**self.graph, "components": [None]}]:
            with self.subTest(value=value):
                self.assertTrue(self.graph_module.validate(value))

    def test_duplicate_contract_and_unknown_fields_rejected(self):
        self.graph["components"][0]["public"] *= 2
        self.graph["approved"] = True
        self.assertTrue(self.graph_module.validate(self.graph))


if __name__ == "__main__":
    unittest.main()
