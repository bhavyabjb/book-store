import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class PaymentMethod(str, enum.Enum):
    CARD = "CARD"
    DEBIT_CARD = "DEBIT_CARD"
    UPI = "UPI"
    WALLET = "WALLET"


class PaymentStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(SAEnum(PaymentMethod, name="payment_method"), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus, name="payment_status"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_ref: Mapped[str | None] = mapped_column(String(64), nullable=True)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    order: Mapped["Order"] = relationship(back_populates="payments")
