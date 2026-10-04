import datetime as dt

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gift_points import GiftPoints
from app.models.order import Order, OrderStatus
from app.models.user import User


async def cancel_order(db: AsyncSession, order: Order, user: User) -> Order:
    now = dt.datetime.now(dt.timezone.utc)
    cancel_by = order.cancel_by
    if cancel_by.tzinfo is None:
        cancel_by = cancel_by.replace(tzinfo=dt.timezone.utc)

    if order.status in (OrderStatus.CANCELLED, OrderStatus.DELIVERED):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Order is already {order.status.value.lower()} and cannot be cancelled",
        )

    if now > cancel_by:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cancellation window has expired",
        )

    order.status = OrderStatus.CANCELLED

    if order.gift_points_redeemed:
        user.gift_points_balance += order.gift_points_redeemed
        db.add(
            GiftPoints(
                user_id=user.id,
                order_id=order.id,
                points=order.gift_points_redeemed,
                reason=f"Refunded on cancellation of order #{order.id}",
            )
        )

    await db.commit()
    await db.refresh(order)
    return order
