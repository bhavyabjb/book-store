from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class GiftPoints(Base):
    """Ledger of gift-point earn/redeem events, backing users.gift_points_balance."""

    __tablename__ = "gift_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    points: Mapped[int] = mapped_column(Integer, nullable=False)  # positive=earned, negative=redeemed
    reason: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship()
    order: Mapped["Order"] = relationship()
