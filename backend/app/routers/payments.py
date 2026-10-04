from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.order import Order, OrderStatus
from app.models.payment import Payment
from app.models.payment import PaymentMethod as PaymentMethodModel
from app.models.user import User
from app.schemas.payment import PaymentRequest, PaymentResult
from app.services.payment_service import PaymentGatewaySimulator

router = APIRouter(tags=["payments"])

_gateway = PaymentGatewaySimulator()


@router.post("/orders/{orderId}/payment", response_model=PaymentResult)
async def pay_for_order(
    orderId: int,
    payload: PaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Order).where(Order.id == orderId, Order.user_id == current_user.id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.status not in (OrderStatus.PLACED,):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Order is {order.status.value.lower()} and cannot be paid for",
        )

    outcome = _gateway.charge(
        method=payload.method.value,
        card_number=payload.card_number,
        upi_id=payload.upi_id,
    )

    payment = Payment(
        order_id=order.id,
        method=PaymentMethodModel(payload.method.value),
        status=outcome.status,
        amount=order.total,
        transaction_ref=outcome.transaction_ref,
    )
    db.add(payment)

    if outcome.status.value == "SUCCESS":
        order.status = OrderStatus.PAID

    await db.commit()

    return PaymentResult(
        status=outcome.status.value,
        order_id=order.id,
        amount=float(order.total),
        transaction_ref=outcome.transaction_ref,
        failure_reason=outcome.failure_reason,
    )
