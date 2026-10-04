from decimal import Decimal

from app.services.cart_service import compute_totals


def test_compute_totals_empty_cart():
    totals = compute_totals([])
    assert totals == {"subtotal": 0.0, "tax": 0.0, "delivery_charge": 0.0, "total": 0.0}


def test_compute_totals_under_free_delivery_threshold():
    totals = compute_totals([Decimal("199.00"), Decimal("100.00")])
    assert totals["subtotal"] == 299.0
    assert totals["tax"] == 29.9
    assert totals["delivery_charge"] == 49.0
    assert totals["total"] == 377.9


def test_compute_totals_exactly_at_threshold_still_charges_delivery():
    # Spec: free delivery over 499, so exactly 499 should still incur the fee.
    totals = compute_totals([Decimal("499.00")])
    assert totals["delivery_charge"] == 49.0


def test_compute_totals_over_threshold_is_free_delivery():
    totals = compute_totals([Decimal("500.00")])
    assert totals["subtotal"] == 500.0
    assert totals["tax"] == 50.0
    assert totals["delivery_charge"] == 0.0
    assert totals["total"] == 550.0
