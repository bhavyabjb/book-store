from app.models.payment import PaymentStatus
from app.services.payment_service import PaymentGatewaySimulator


def test_card_ending_in_0000_is_declined():
    gateway = PaymentGatewaySimulator()
    outcome = gateway.charge(method="CARD", card_number="4111111110000")
    assert outcome.status == PaymentStatus.FAILED
    assert outcome.transaction_ref is None
    assert outcome.failure_reason


def test_upi_ending_in_0000_is_declined():
    gateway = PaymentGatewaySimulator()
    outcome = gateway.charge(method="UPI", upi_id="alice@upi0000")
    assert outcome.status == PaymentStatus.FAILED


def test_normal_card_succeeds():
    gateway = PaymentGatewaySimulator()
    outcome = gateway.charge(method="CARD", card_number="4111111111111111")
    assert outcome.status == PaymentStatus.SUCCESS
    assert outcome.transaction_ref is not None
    assert outcome.failure_reason is None


def test_wallet_with_no_identifier_succeeds():
    gateway = PaymentGatewaySimulator()
    outcome = gateway.charge(method="WALLET")
    assert outcome.status == PaymentStatus.SUCCESS
