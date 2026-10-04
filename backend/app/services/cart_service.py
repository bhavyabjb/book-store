import uuid
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.book import Book
from app.models.cart import Cart, CartItem
from app.models.user import User
from app.schemas.cart import Cart as CartSchema
from app.schemas.cart import CartItem as CartItemSchema
from app.services.serializers import book_to_summary

TAX_RATE = Decimal("0.10")
FREE_DELIVERY_THRESHOLD = Decimal("499")
DELIVERY_FLAT_FEE = Decimal("49")


def _round2(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def compute_totals(line_totals: list[Decimal]) -> dict:
    subtotal = sum(line_totals, Decimal("0"))
    tax = subtotal * TAX_RATE
    if subtotal == 0:
        delivery = Decimal("0")
    elif subtotal > FREE_DELIVERY_THRESHOLD:
        delivery = Decimal("0")
    else:
        delivery = DELIVERY_FLAT_FEE
    total = subtotal + tax + delivery
    return {
        "subtotal": _round2(subtotal),
        "tax": _round2(tax),
        "delivery_charge": _round2(delivery),
        "total": _round2(total),
    }


async def get_or_create_cart(
    db: AsyncSession, user: Optional[User], cart_token: Optional[str]
) -> tuple[Cart, Optional[str]]:
    """Resolve the cart for this request, creating one if needed.

    Returns (cart, new_cart_token). new_cart_token is non-None only when a
    fresh guest token was minted and the caller should set it as a cookie.
    """
    stmt = select(Cart).options(
        selectinload(Cart.items).selectinload(CartItem.book).selectinload(Book.author),
        selectinload(Cart.items).selectinload(CartItem.book).selectinload(Book.tags),
    )

    if user is not None:
        result = await db.execute(stmt.where(Cart.user_id == user.id))
        cart = result.scalar_one_or_none()
        if cart is None:
            cart = Cart(user_id=user.id)
            db.add(cart)
            await db.commit()
            cart = await reload_cart(db, cart.id)
        return cart, None

    if cart_token:
        result = await db.execute(stmt.where(Cart.cart_token == cart_token))
        cart = result.scalar_one_or_none()
        if cart is not None:
            return cart, None

    new_token = uuid.uuid4().hex
    cart = Cart(cart_token=new_token)
    db.add(cart)
    await db.commit()
    cart = await reload_cart(db, cart.id)
    return cart, new_token


async def add_item(db: AsyncSession, cart: Cart, book_id: int, quantity: int) -> Cart:
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if book is None:
        raise ValueError("Book not found")

    result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.book_id == book_id)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        existing.quantity += quantity
    else:
        db.add(CartItem(cart_id=cart.id, book_id=book_id, quantity=quantity))
    await db.commit()
    return await reload_cart(db, cart.id)


async def update_item(db: AsyncSession, cart: Cart, book_id: int, quantity: int) -> Cart:
    result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.book_id == book_id)
    )
    existing = result.scalar_one_or_none()
    if existing is None:
        if quantity > 0:
            db.add(CartItem(cart_id=cart.id, book_id=book_id, quantity=quantity))
    elif quantity <= 0:
        await db.delete(existing)
    else:
        existing.quantity = quantity
    await db.commit()
    return await reload_cart(db, cart.id)


async def remove_item(db: AsyncSession, cart: Cart, book_id: int) -> Cart:
    result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.book_id == book_id)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        await db.delete(existing)
        await db.commit()
    return await reload_cart(db, cart.id)


async def reload_cart(db: AsyncSession, cart_id: int) -> Cart:
    """Re-fetch a cart with its items freshly loaded.

    Uses populate_existing() because the Cart for this id may already be in
    the session's identity map (e.g. from get_or_create_cart) with its
    `items` relationship already loaded (possibly empty) — without this,
    SQLAlchemy would return the stale cached collection instead of
    re-querying after we just inserted/updated/deleted cart items.
    """
    stmt = (
        select(Cart)
        .options(
            selectinload(Cart.items).selectinload(CartItem.book).selectinload(Book.author),
            selectinload(Cart.items).selectinload(CartItem.book).selectinload(Book.tags),
        )
        .where(Cart.id == cart_id)
        .execution_options(populate_existing=True)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


def cart_to_schema(cart: Cart) -> CartSchema:
    line_totals: list[Decimal] = []
    item_schemas: list[CartItemSchema] = []
    for item in cart.items:
        line_total = Decimal(str(item.book.price)) * item.quantity
        line_totals.append(line_total)
        item_schemas.append(
            CartItemSchema(
                book=book_to_summary(item.book),
                quantity=item.quantity,
                line_total=_round2(line_total),
            )
        )
    totals = compute_totals(line_totals)
    return CartSchema(items=item_schemas, **totals)
