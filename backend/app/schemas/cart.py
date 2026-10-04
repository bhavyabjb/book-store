from pydantic import Field

from app.schemas.catalog import BookSummary
from app.schemas.common import CamelModel


class CartItem(CamelModel):
    book: BookSummary
    quantity: int = Field(ge=1)
    line_total: float


class Cart(CamelModel):
    items: list[CartItem] = []
    subtotal: float
    tax: float
    delivery_charge: float
    total: float


class CartItemCreate(CamelModel):
    book_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(CamelModel):
    quantity: int = Field(ge=0)
