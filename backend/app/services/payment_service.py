import uuid
from dataclasses import dataclass
from typing import Optional

from app.models.payment import PaymentStatus

DECLINE_SUFFIX = "0000"
CANNED_FAILURE_REASON = "Payment declined by issuing bank. Please try a different card, UPI ID, or payment method."


@dataclass
class PaymentOutcome:
    status: PaymentStatus
    transaction_ref: Optional[str]
    failure_reason: Optional[str]


class PaymentGatewaySimulator:
    """A synchronous, offline stand-in for a real payment gateway.

    Rule: any card or UPI identifier ending in the literal digits "0000" is
    declined; everything else succeeds. No network calls are made.
    """

    def charge(
        self,
        method: str,
        card_number: Optional[str] = None,
        upi_id: Optional[str] = None,
        **_: object,
    ) -> PaymentOutcome:
        identifier = (card_number or upi_id or "").strip()

        if identifier.endswith(DECLINE_SUFFIX):
            return PaymentOutcome(
                status=PaymentStatus.FAILED,
                transaction_ref=None,
                failure_reason=CANNED_FAILURE_REASON,
            )

        transaction_ref = str(uuid.uuid4())
        return PaymentOutcome(
            status=PaymentStatus.SUCCESS,
            transaction_ref=transaction_ref,
            failure_reason=None,
        )
