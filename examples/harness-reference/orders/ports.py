"""The business-owned lookup contract, independent of persistence."""
from typing import Protocol


class Catalog(Protocol):
    def price_cents(self, product_id: str) -> int:
        """Return nonnegative integer cents or raise KeyError for an unknown product."""
        ...
