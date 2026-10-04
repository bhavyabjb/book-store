import datetime as dt
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.address import Address
from app.models.book import Book
from app.models.cart import Cart
from app.models.coupon import Coupon
from app.models.gift_points import GiftPoints
from app.models.order import Order, OrderItem, OrderStatus
from app.models.user import User
from app.services.cart_service import compute_totals

CANCEL_WINDOW_HOURS = 48
GIFT_POINT_VALUE = Decimal("1")  # 1 point = ₹1 of discount
GIFT_POINTS_EARN_RATE = Decimal("100")  # 1 point earned per ₹100 spent


def _round2(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


async def _get_active_coupon(db: AsyncSession, code: str) -> Coupon:
    result = await db.execute(select(Coupon).where(Coupon.code == code, Coupon.active.is_(True)))
    coupon = result.scalar_one_or_none()
    if coupon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or inactive coupon")
    return coupon


def _coupon_discount(coupon: Coupon, subtotal: Decimal) -> Decimal:
    if coupon.discount_amount is not None:
        return min(Decimal(str(coupon.discount_amount)), subtotal)
    if coupon.discount_pct is not None:
        return (subtotal * Decimal(str(coupon.discount_pct)) / Decimal("100")).quantize(Decimal("0.01"))
    return Decimal("0")


async def preview_coupon(db: AsyncSession, cart: Cart, code: str) -> tuple[Coupon, Decimal, Decimal]:
    coupon = await _get_active_coupon(db, code)
    line_totals = [Decimal(str(i.book.price)) * i.quantity for i in cart.items]
    totals = compute_totals(line_totals)
    subtotal = Decimal(str(totals["subtotal"]))
    discount = _coupon_discount(coupon, subtotal)
    new_total = max(Decimal(str(totals["total"])) - discount, Decimal("0"))
    return coupon, discount, new_total


async def create_order_from_cart(
    db: AsyncSession,
    user: User,
    cart: Cart,
    address_id: int,
    coupon_code: Optional[str],
    gift_points_to_redeem: int,
) -> Order:
    if not cart.items:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cart is empty")

    result = await db.execute(select(Address).where(Address.id == address_id, Address.user_id == user.id))
    address = result.scalar_one_or_none()
    if address is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    line_totals = [Decimal(str(i.book.price)) * i.quantity for i in cart.items]
    totals = compute_totals(line_totals)
    subtotal = Decimal(str(totals["subtotal"]))
    tax = Decimal(str(totals["tax"]))
    delivery = Decimal(str(totals["delivery_charge"]))

    discount = Decimal("0")
    coupon: Optional[Coupon] = None
    if coupon_code:
        coupon = await _get_active_coupon(db, coupon_code)
        discount = _coupon_discount(coupon, subtotal)

    running_total = subtotal + tax + delivery - discount

    gift_points_to_redeem = max(0, gift_points_to_redeem or 0)
    redeemable = min(gift_points_to_redeem, user.gift_points_balance)
    gift_points_value = min(Decimal(redeemable) * GIFT_POINT_VALUE, running_total)
    gift_points_redeemed = int(gift_points_value / GIFT_POINT_VALUE) if GIFT_POINT_VALUE else 0

    total = max(running_total - gift_points_value, Decimal("0"))

    now = dt.datetime.now(dt.timezone.utc)
    order = Order(
        user_id=user.id,
        address_id=address.id,
        status=OrderStatus.PLACED,
        subtotal=_round2(subtotal),
        tax=_round2(tax),
        delivery_charge=_round2(delivery),
        discount=_round2(discount),
        total=_round2(total),
        coupon_code=coupon.code if coupon else None,
        gift_points_redeemed=gift_points_redeemed,
        placed_at=now,
        cancel_by=now + dt.timedelta(hours=CANCEL_WINDOW_HOURS),
    )
    db.add(order)
    await db.flush()

    for item in cart.items:
        db.add(
            OrderItem(
                order_id=order.id,
                book_id=item.book_id,
                quantity=item.quantity,
                unit_price=item.book.price,
            )
        )
        item.book.units_sold = (item.book.units_sold or 0) + item.quantity

    if gift_points_redeemed:
        user.gift_points_balance -= gift_points_redeemed
        db.add(
            GiftPoints(
                user_id=user.id,
                order_id=order.id,
                points=-gift_points_redeemed,
                reason=f"Redeemed on order #{order.id}",
            )
        )

    points_earned = int(total // GIFT_POINTS_EARN_RATE)
    if points_earned:
        user.gift_points_balance += points_earned
        db.add(
            GiftPoints(
                user_id=user.id,
                order_id=order.id,
                points=points_earned,
                reason=f"Earned on order #{order.id}",
            )
        )

    for item in list(cart.items):
        await db.delete(item)

    await db.commit()

    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.book).selectinload(Book.author),
            selectinload(Order.items).selectinload(OrderItem.book).selectinload(Book.tags),
            selectinload(Order.address),
        )
        .where(Order.id == order.id)
    )
    return result.scalar_one()
