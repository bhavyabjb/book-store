import datetime as dt
import enum

from app.schemas.address import Address
from app.schemas.catalog import BookSummary
from app.schemas.common import CamelModel


class OrderStatus(str, enum.Enum):
    PLACED = "PLACED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    DELIVERED = "DELIVERED"


class OrderCreateRequest(CamelModel):
    address_id: int
    coupon_code: str | None = None
    gift_points_to_redeem: int = 0


class OrderItem(CamelModel):
    book: BookSummary
    quantity: int
    unit_price: float


class OrderSummary(CamelModel):
    id: int
    status: OrderStatus
    total: float
    placed_at: dt.datetime
    cancel_by: dt.datetime
    items: list[OrderItem] = []


class Order(OrderSummary):
    address: Address
    subtotal: float
    tax: float
    delivery_charge: float
    discount: float
    coupon_code: str | None = None
    gift_points_redeemed: int = 0
