from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.book import Book
from app.models.review import Review
from app.models.user import User
from app.schemas.review import Review as ReviewSchema
from app.schemas.review import ReviewCreate
from app.services.serializers import review_to_schema

router = APIRouter(tags=["reviews"])


@router.get("/books/{bookId}/reviews", response_model=list[ReviewSchema])
async def list_reviews(bookId: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review).where(Review.book_id == bookId).order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    return [review_to_schema(r) for r in reviews]


@router.post("/books/{bookId}/reviews", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    bookId: int,
    payload: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Book).where(Book.id == bookId))
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    review = Review(
        book_id=bookId,
        user_id=current_user.id,
        reviewer_name=f"{current_user.first_name} {current_user.last_name}".strip(),
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    agg_result = await db.execute(select(Review.rating).where(Review.book_id == bookId))
    ratings = agg_result.scalars().all()
    if ratings:
        book.rating_avg = sum(ratings) / len(ratings)
        await db.commit()

    return review_to_schema(review)
