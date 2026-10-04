import datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.models.author import Author
from app.models.book import Book, BookFormat
from app.models.category import Category
from app.schemas.catalog import BookDetail, BookPage
from app.schemas.catalog import BookFormat as BookFormatSchema
from app.schemas.catalog import BookSummary
from app.schemas.catalog import Category as CategorySchema
from app.schemas.common import Error
from app.services.serializers import book_to_detail, book_to_summary, category_to_schema

router = APIRouter(tags=["catalog"])

_BOOK_LOAD_OPTS = (selectinload(Book.author), selectinload(Book.tags), selectinload(Book.category))

_SECTION_FIELD = {
    "recommended": Book.is_recommended,
    "bestsellers": Book.is_bestseller,
    "new_launches": Book.is_new_launch,
}


@router.get("/categories", response_model=list[CategorySchema])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.name))
    categories = result.scalars().all()
    return [category_to_schema(c) for c in categories]


@router.get("/books", response_model=BookPage)
async def list_books(
    q: Optional[str] = None,
    category: Optional[str] = None,
    author: Optional[str] = None,
    language: Optional[str] = None,
    format: Optional[BookFormatSchema] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    maxDeliveryDate: Optional[dt.date] = None,
    sort: str = Query(default="relevance", pattern="^(relevance|price_asc|price_desc|rating|newest)$"),
    section: Optional[str] = Query(default=None, pattern="^(recommended|bestsellers|new_launches)$"),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=12, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Book).join(Author, Book.author_id == Author.id).options(*_BOOK_LOAD_OPTS)
    count_stmt = select(func.count(Book.id)).select_from(Book).join(Author, Book.author_id == Author.id)

    if q:
        pattern = f"%{q}%"
        clause = or_(Book.title.ilike(pattern), Author.name.ilike(pattern))
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)
    if category:
        stmt = stmt.join(Category, Book.category_id == Category.id).where(Category.slug == category)
        count_stmt = count_stmt.join(Category, Book.category_id == Category.id).where(Category.slug == category)
    if author:
        stmt = stmt.where(Author.name.ilike(f"%{author}%"))
        count_stmt = count_stmt.where(Author.name.ilike(f"%{author}%"))
    if language:
        stmt = stmt.where(Book.language.ilike(language))
        count_stmt = count_stmt.where(Book.language.ilike(language))
    if format:
        stmt = stmt.where(Book.format == BookFormat(format.value))
        count_stmt = count_stmt.where(Book.format == BookFormat(format.value))
    if minPrice is not None:
        stmt = stmt.where(Book.price >= minPrice)
        count_stmt = count_stmt.where(Book.price >= minPrice)
    if maxPrice is not None:
        stmt = stmt.where(Book.price <= maxPrice)
        count_stmt = count_stmt.where(Book.price <= maxPrice)
    if maxDeliveryDate is not None:
        # delivery_date is computed as today + delivery_days (not stored), so
        # translate the requested cutoff date into a max delivery_days value.
        max_days = (maxDeliveryDate - dt.date.today()).days
        stmt = stmt.where(Book.delivery_days <= max_days)
        count_stmt = count_stmt.where(Book.delivery_days <= max_days)
    if section:
        field = _SECTION_FIELD[section]
        stmt = stmt.where(field.is_(True))
        count_stmt = count_stmt.where(field.is_(True))

    if sort == "price_asc":
        stmt = stmt.order_by(Book.price.asc())
    elif sort == "price_desc":
        stmt = stmt.order_by(Book.price.desc())
    elif sort == "rating":
        stmt = stmt.order_by(Book.rating_avg.desc().nulls_last())
    elif sort == "newest":
        stmt = stmt.order_by(Book.created_at.desc())
    else:
        stmt = stmt.order_by(Book.id.asc())

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    stmt = stmt.offset((page - 1) * pageSize).limit(pageSize)
    result = await db.execute(stmt)
    books = result.scalars().unique().all()

    return BookPage(
        items=[book_to_summary(b) for b in books],
        total=total,
        page=page,
        page_size=pageSize,
    )


@router.get("/books/{bookId}", response_model=BookDetail, responses={404: {"model": Error}})
async def get_book(bookId: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Book).options(*_BOOK_LOAD_OPTS).where(Book.id == bookId)
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book_to_detail(book)


@router.get("/books/{bookId}/related", response_model=list[BookSummary])
async def get_related_books(bookId: int, limit: int = 4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == bookId))
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    stmt = (
        select(Book)
        .options(*_BOOK_LOAD_OPTS)
        .where(
            Book.id != bookId,
            or_(Book.category_id == book.category_id, Book.author_id == book.author_id),
        )
        .limit(limit)
    )
    result = await db.execute(stmt)
    related = result.scalars().unique().all()
    return [book_to_summary(b) for b in related]
