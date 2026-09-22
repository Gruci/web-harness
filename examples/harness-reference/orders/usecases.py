"""Quote an order through the declared catalog contract and pricing policy."""
from orders.ports import Catalog
from pricing.domain import total_cents


def quote(product_id: str, quantity: int, catalog: Catalog) -> int:
    return total_cents(catalog.price_cents(product_id), quantity)
