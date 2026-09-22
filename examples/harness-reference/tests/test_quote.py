"""Execute the same port contract against a fake and the memory adapter."""
import importlib
import unittest

from orders.ports import Catalog


class FakeCatalog:
    def __init__(self):
        self.requested = []

    def price_cents(self, product_id: str) -> int:
        self.requested.append(product_id)
        if product_id != "tea":
            raise KeyError(product_id)
        return 1000


class QuoteTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.usecases = importlib.import_module("orders.usecases")
            self.adapters = importlib.import_module("orders.adapters.memory")
        except ModuleNotFoundError:
            self.fail("quote implementation is missing")

    def test_fake_is_used_by_business_behavior(self) -> None:
        catalog: Catalog = FakeCatalog()
        self.assertEqual(2700, self.usecases.quote("tea", 3, catalog))
        self.assertEqual(["tea"], catalog.requested)

    def test_memory_adapter_and_fake_satisfy_same_contract(self) -> None:
        for catalog in (FakeCatalog(), self.adapters.MemoryCatalog({"tea": 1000})):
            with self.subTest(catalog=type(catalog).__name__):
                self.assertEqual(1000, catalog.price_cents("tea"))
                with self.assertRaises(KeyError):
                    catalog.price_cents("missing")

    def test_single_item_has_no_discount(self) -> None:
        self.assertEqual(1000, self.usecases.quote("tea", 1, FakeCatalog()))

    def test_zero_quantity_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.usecases.quote("tea", 0, FakeCatalog())


if __name__ == "__main__":
    unittest.main()
