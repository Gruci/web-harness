"""Replaceable memory storage for the catalog port."""
from orders.ports import Catalog


class MemoryCatalog(Catalog):
    def __init__(self, prices: dict[str, int]):
        self.prices = dict(prices)

    def price_cents(self, product_id: str) -> int:
        return self.prices[product_id]
