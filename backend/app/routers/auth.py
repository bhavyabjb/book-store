from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserProfile
from app.schemas.common import Error

router = APIRouter(tags=["auth"])


@router.post(
    "/auth/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": Error}},
)
async def register_user(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token, token_type="bearer", user=UserProfile.model_validate(user))


@router.post("/auth/login", response_model=TokenResponse, responses={401: {"model": Error}})
async def login_user(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token, token_type="bearer", user=UserProfile.model_validate(user))


@router.get("/auth/me", response_model=UserProfile, responses={401: {"model": Error}})
async def get_me(current_user: User = Depends(get_current_user)):
    return UserProfile.model_validate(current_user)
