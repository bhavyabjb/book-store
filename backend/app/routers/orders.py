from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.book import Book
from app.models.cart import Cart, CartItem
from app.models.order import Order
from app.models.order import OrderItem as OrderItemModel
from app.models.user import User
from app.routers.cart import CART_TOKEN_COOKIE
from app.schemas.common import Error
from app.schemas.order import Order as OrderSchema
from app.schemas.order import OrderCreateRequest
from app.schemas.order import OrderSummary as OrderSummarySchema
from app.services.cancel_service import cancel_order as do_cancel_order
from app.services.checkout_service import create_order_from_cart
from app.services.serializers import order_to_schema

router = APIRouter(tags=["orders"])

_ORDER_LOAD_OPTS = (
    selectinload(Order.items).selectinload(OrderItemModel.book).selectinload(Book.author),
    selectinload(Order.items).selectinload(OrderItemModel.book).selectinload(Book.tags),
    selectinload(Order.address),
)

_CART_LOAD_OPTS = (
    selectinload(Cart.items).selectinload(CartItem.book).selectinload(Book.author),
    selectinload(Cart.items).selectinload(CartItem.book).selectinload(Book.tags),
)


async def _resolve_checkout_cart(db: AsyncSession, user: User, cart_token: Optional[str]) -> Cart:
    """Prefer the user's own cart; fall back to / merge a guest cart_token cart.

    This lets a shopper add items while browsing as a guest and then log in
    (or register) right before checkout without losing their cart.
    """
    result = await db.execute(select(Cart).options(*_CART_LOAD_OPTS).where(Cart.user_id == user.id))
    user_cart = result.scalar_one_or_none()

    guest_cart = None
    if cart_token:
        result = await db.execute(select(Cart).options(*_CART_LOAD_OPTS).where(Cart.cart_token == cart_token))
        guest_cart = result.scalar_one_or_none()

    if (user_cart is None or not user_cart.items) and guest_cart is not None and guest_cart.items:
        if user_cart is not None:
            await db.delete(user_cart)
            await db.flush()
        guest_cart.user_id = user.id
        guest_cart.cart_token = None
        await db.commit()
        await db.refresh(guest_cart)
        return guest_cart

    if user_cart is None:
        user_cart = Cart(user_id=user.id)
        db.add(user_cart)
        await db.commit()
        result = await db.execute(select(Cart).options(*_CART_LOAD_OPTS).where(Cart.id == user_cart.id))
        user_cart = result.scalar_one()

    return user_cart


@router.get("/orders", response_model=list[OrderSummarySchema])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Order)
        .options(*_ORDER_LOAD_OPTS)
        .where(Order.user_id == current_user.id)
        .order_by(Order.placed_at.desc())
    )
    result = await db.execute(stmt)
    orders = result.scalars().unique().all()
    return [order_to_schema(o) for o in orders]


@router.post("/orders", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    cart_token: Optional[str] = Cookie(default=None, alias=CART_TOKEN_COOKIE),
):
    cart = await _resolve_checkout_cart(db, current_user, cart_token)
    order = await create_order_from_cart(
        db,
        current_user,
        cart,
        payload.address_id,
        payload.coupon_code,
        payload.gift_points_to_redeem,
    )
    return order_to_schema(order)


@router.get("/orders/{orderId}", response_model=OrderSchema)
async def get_order(
    orderId: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Order).options(*_ORDER_LOAD_OPTS).where(Order.id == orderId, Order.user_id == current_user.id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order_to_schema(order)


@router.post("/orders/{orderId}/cancel", response_model=OrderSchema, responses={422: {"model": Error}})
async def cancel_order_endpoint(
    orderId: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Order).options(*_ORDER_LOAD_OPTS).where(Order.id == orderId, Order.user_id == current_user.id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order = await do_cancel_order(db, order, current_user)
    return order_to_schema(order)
