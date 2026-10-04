from fastapi import APIRouter, Depends, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.address import Address
from app.models.user import User
from app.schemas.address import Address as AddressSchema
from app.schemas.address import AddressCreate
from app.services.serializers import address_to_schema

router = APIRouter(tags=["addresses"])


@router.get("/addresses", response_model=list[AddressSchema])
async def list_addresses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Address).where(Address.user_id == current_user.id))
    addresses = result.scalars().all()
    return [address_to_schema(a) for a in addresses]


@router.post("/addresses", response_model=AddressSchema, status_code=status.HTTP_201_CREATED)
async def create_address(
    payload: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.is_default:
        await db.execute(
            update(Address).where(Address.user_id == current_user.id).values(is_default=False)
        )

    address = Address(
        user_id=current_user.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        line1=payload.line1,
        city=payload.city,
        state=payload.state,
        pin=payload.pin,
        country=payload.country,
        phone=payload.phone,
        email=payload.email,
        is_default=payload.is_default,
    )
    db.add(address)
    await db.commit()
    await db.refresh(address)
    return address_to_schema(address)
