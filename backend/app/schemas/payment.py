import enum

from app.schemas.common import CamelModel


class PaymentMethod(str, enum.Enum):
    CARD = "CARD"
    DEBIT_CARD = "DEBIT_CARD"
    UPI = "UPI"
    WALLET = "WALLET"


class PaymentStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PaymentRequest(CamelModel):
    method: PaymentMethod
    card_number: str | None = None
    name_on_card: str | None = None
    cvv: str | None = None
    expiry: str | None = None
    upi_id: str | None = None
    wallet_provider: str | None = None


class PaymentResult(CamelModel):
    status: PaymentStatus
    order_id: int
    amount: float
    transaction_ref: str | None = None
    failure_reason: str | None = None
