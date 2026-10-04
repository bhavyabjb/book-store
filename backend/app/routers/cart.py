from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import get_current_user_optional
from app.models.user import User
from app.schemas.cart import Cart as CartSchema
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.services import cart_service

router = APIRouter(tags=["cart"])

CART_TOKEN_COOKIE = "cart_token"
COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 30  # 30 days


def _set_cookie_if_needed(response: Response, new_token: Optional[str]) -> None:
    if new_token:
        response.set_cookie(
            key=CART_TOKEN_COOKIE,
            value=new_token,
            max_age=COOKIE_MAX_AGE_SECONDS,
            httponly=True,
            samesite="lax",
        )


async def _resolve_cart(
    db: AsyncSession,
    response: Response,
    current_user: Optional[User],
    cart_token: Optional[str],
):
    cart, new_token = await cart_service.get_or_create_cart(db, current_user, cart_token)
    _set_cookie_if_needed(response, new_token)
    return cart


@router.get("/cart", response_model=CartSchema)
async def get_cart(
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    cart_token: Optional[str] = Cookie(default=None, alias=CART_TOKEN_COOKIE),
):
    cart = await _resolve_cart(db, response, current_user, cart_token)
    return cart_service.cart_to_schema(cart)


@router.post("/cart/items", response_model=CartSchema)
async def add_cart_item(
    payload: CartItemCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    cart_token: Optional[str] = Cookie(default=None, alias=CART_TOKEN_COOKIE),
):
    cart = await _resolve_cart(db, response, current_user, cart_token)
    try:
        cart = await cart_service.add_item(db, cart, payload.book_id, payload.quantity)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return cart_service.cart_to_schema(cart)


@router.patch("/cart/items/{bookId}", response_model=CartSchema)
async def update_cart_item(
    bookId: int,
    payload: CartItemUpdate,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    cart_token: Optional[str] = Cookie(default=None, alias=CART_TOKEN_COOKIE),
):
    cart = await _resolve_cart(db, response, current_user, cart_token)
    cart = await cart_service.update_item(db, cart, bookId, payload.quantity)
    return cart_service.cart_to_schema(cart)


@router.delete("/cart/items/{bookId}", response_model=CartSchema)
async def remove_cart_item(
    bookId: int,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    cart_token: Optional[str] = Cookie(default=None, alias=CART_TOKEN_COOKIE),
):
    cart = await _resolve_cart(db, response, current_user, cart_token)
    cart = await cart_service.remove_item(db, cart, bookId)
    return cart_service.cart_to_schema(cart)
