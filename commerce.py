"""Transactional commerce workflow with compensating inventory actions."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable
from uuid import uuid4


class OrderStatus(str, Enum):
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Order:
    id: str
    sku: str
    quantity: int
    total: Decimal
    status: OrderStatus
    reason: str = ""


class Inventory:
    def __init__(self, stock: dict[str, int]) -> None:
        self.stock = dict(stock)

    def reserve(self, sku: str, quantity: int) -> bool:
        if quantity < 1 or self.stock.get(sku, 0) < quantity:
            return False
        self.stock[sku] -= quantity
        return True

    def release(self, sku: str, quantity: int) -> None:
        self.stock[sku] = self.stock.get(sku, 0) + quantity


class CommerceService:
    def __init__(self, inventory: Inventory, prices: dict[str, Decimal]) -> None:
        self.inventory, self.prices = inventory, prices

    def place_order(self, sku: str, quantity: int, payment: Callable[[Decimal], bool]) -> Order:
        order_id = str(uuid4())
        if sku not in self.prices or not self.inventory.reserve(sku, quantity):
            return Order(order_id, sku, quantity, Decimal("0"), OrderStatus.REJECTED, "unavailable")
        total = self.prices[sku] * quantity
        try:
            paid = payment(total)
        except Exception:
            # Restore local stock; the caller must reconcile an uncertain payment.
            self.inventory.release(sku, quantity)
            raise
        if not paid:
            self.inventory.release(sku, quantity)
            return Order(order_id, sku, quantity, total, OrderStatus.REJECTED, "payment failed")
        return Order(order_id, sku, quantity, total, OrderStatus.CONFIRMED)


def main() -> None:
    """Run an explicit fictional transaction through the orchestration model."""
    import argparse

    parser = argparse.ArgumentParser(description="Run a local commerce reservation and payment demonstration.")
    parser.add_argument("--quantity", type=int, default=1)
    parser.add_argument("--decline-payment", action="store_true", help="exercise payment compensation")
    args = parser.parse_args()
    inventory = Inventory({"demo-book": 2})
    service = CommerceService(inventory, {"demo-book": Decimal("12.50")})
    order = service.place_order("demo-book", args.quantity, lambda _: not args.decline_payment)
    print("Fictional local transaction; inventory and payment services are in-process.")
    print(f"Order {order.id}: {order.status.value}; total £{order.total}; reason: {order.reason or '—'}")
    print(f"Inventory after workflow: {inventory.stock['demo-book']} demo-book")
    if args.decline_payment:
        print("Payment declined: reserved stock was compensated (released).")


if __name__ == "__main__":
    main()
