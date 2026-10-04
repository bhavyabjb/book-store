import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class OrderStatus(str, enum.Enum):
    PLACED = "PLACED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    DELIVERED = "DELIVERED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status"), nullable=False, default=OrderStatus.PLACED
    )
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tax: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    delivery_charge: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    coupon_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gift_points_redeemed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    cancel_by: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(back_populates="orders")
    address: Mapped["Address"] = relationship()
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    book: Mapped["Book"] = relationship()
