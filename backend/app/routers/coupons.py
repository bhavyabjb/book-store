from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import get_current_user_optional
from app.models.user import User
from app.routers.cart import CART_TOKEN_COOKIE, _resolve_cart
from app.schemas.common import Error
from app.schemas.coupon import CouponApplyRequest, CouponApplyResponse
from app.services.checkout_service import preview_coupon

router = APIRouter(tags=["coupons"])


@router.post(
    "/coupons/apply", response_model=CouponApplyResponse, responses={404: {"model": Error}}
)
async def apply_coupon(
    payload: CouponApplyRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    cart_token: Optional[str] = Cookie(default=None, alias=CART_TOKEN_COOKIE),
):
    cart = await _resolve_cart(db, response, current_user, cart_token)
    coupon, discount, new_total = await preview_coupon(db, cart, payload.code)
    return CouponApplyResponse(code=coupon.code, discount=float(discount), new_total=float(new_total))
