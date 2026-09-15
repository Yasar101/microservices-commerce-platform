# Commerce Workflow Core

**TESTED CORE** · [Live demo](https://yasar101.github.io/software-engineering-portfolio/demos/commerce.html) · [Portfolio](https://github.com/Yasar101/software-engineering-portfolio)

An in-process order workflow with pricing, stock reservation and an injected payment callback.

## Purpose and engineering skills

Explore service boundaries and compensation when a downstream operation fails.

## Structure

commerce.py separates Inventory, immutable Order and CommerceService. [Source](commerce.py).

## Run

From this directory with Python 3.11+, run this offline example using `python3` (no dependencies or credentials):

```python
from decimal import Decimal
from commerce import CommerceService, Inventory
inventory = Inventory({"book": 2})
service = CommerceService(inventory, {"book": Decimal("12.50")})
print(service.place_order("book", 1, lambda total: True))
service.place_order("book", 1, lambda total: False)
assert inventory.stock["book"] == 1
```

## Test

```sh
python3 -m compileall -q .
python3 - <<'PY'
from decimal import Decimal
from commerce import CommerceService, Inventory
inventory = Inventory({"book": 2})
service = CommerceService(inventory, {"book": Decimal("2")})
order = service.place_order("book", 1, lambda total: True)
assert order.status.value == "confirmed"
failed = service.place_order("book", 1, lambda total: False)
assert failed.status.value == "rejected"
assert inventory.stock["book"] == 1  # rejected order released its reservation
print("compensation example passed")
PY
```

The full regression suite (failure paths, README examples and demo checks) runs in the [portfolio repository](https://github.com/Yasar101/software-engineering-portfolio).

## Complete and remaining

**Complete:** Success, payment rejection, unavailable stock and local reservation compensation. Payment exceptions restore local stock and propagate.

**Remaining / limitations:** No deployed microservices, database transaction, locking, idempotency or durable saga. A payment timeout may have charged the customer: reconciliation is required before retrying.

## Learning takeaway

Compensation restores local state; it cannot prove or reverse an external payment outcome.

## Command-line demonstration
Exercise a fictional local transaction and its compensation path:

```bash
python3 -m commerce --decline-payment
```

This is an in-process workflow demonstration, not deployed microservices.