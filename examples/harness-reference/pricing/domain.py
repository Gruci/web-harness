"""Pure pricing policy; amounts are integer cents."""


def total_cents(unit_cents: int, quantity: int) -> int:
    if unit_cents < 0 or quantity < 1:
        raise ValueError("price must be nonnegative and quantity positive")
    subtotal = unit_cents * quantity
    return subtotal * 90 // 100 if quantity >= 3 else subtotal
