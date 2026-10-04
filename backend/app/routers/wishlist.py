from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.book import Book
from app.models.user import User
from app.models.wishlist import WishlistItem
from app.schemas.catalog import BookSummary
from app.services.serializers import book_to_summary

router = APIRouter(tags=["wishlist"])

_BOOK_LOAD_OPTS = (selectinload(Book.author), selectinload(Book.tags))


@router.get("/wishlist", response_model=list[BookSummary])
async def get_wishlist(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Book)
        .join(WishlistItem, WishlistItem.book_id == Book.id)
        .options(*_BOOK_LOAD_OPTS)
        .where(WishlistItem.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    books = result.scalars().unique().all()
    return [book_to_summary(b) for b in books]


@router.post("/wishlist/{bookId}", status_code=status.HTTP_204_NO_CONTENT)
async def add_to_wishlist(
    bookId: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Book).where(Book.id == bookId))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    result = await db.execute(
        select(WishlistItem).where(WishlistItem.user_id == current_user.id, WishlistItem.book_id == bookId)
    )
    if result.scalar_one_or_none() is None:
        db.add(WishlistItem(user_id=current_user.id, book_id=bookId))
        await db.commit()
    return None


@router.delete("/wishlist/{bookId}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    bookId: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WishlistItem).where(WishlistItem.user_id == current_user.id, WishlistItem.book_id == bookId)
    )
    item = result.scalar_one_or_none()
    if item is not None:
        await db.delete(item)
        await db.commit()
    return None
