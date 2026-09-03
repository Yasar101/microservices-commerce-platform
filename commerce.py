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
        if not payment(total):
            self.inventory.release(sku, quantity)
            return Order(order_id, sku, quantity, total, OrderStatus.REJECTED, "payment failed")
        return Order(order_id, sku, quantity, total, OrderStatus.CONFIRMED)
