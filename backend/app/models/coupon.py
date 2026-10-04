from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Coupon(Base):
    __tablename__ = "coupons"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    discount_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    discount_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
