import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class BookFormat(str, enum.Enum):
    PAPERBACK = "Paperback"
    HARDCOVER = "Hardcover"
    EBOOK = "eBook"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    format: Mapped[BookFormat] = mapped_column(SAEnum(BookFormat, name="book_format"), nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="English")
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    cover_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    back_cover_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(32), nullable=True)
    rating_avg: Mapped[float | None] = mapped_column(Float, nullable=True)
    units_sold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delivery_days: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_bestseller: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_new_launch: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    author: Mapped["Author"] = relationship(back_populates="books")
    category: Mapped["Category"] = relationship(back_populates="books")
    tags: Mapped[list["BookTag"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="book", cascade="all, delete-orphan")


class BookTag(Base):
    __tablename__ = "book_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    tag: Mapped[str] = mapped_column(String(100), nullable=False)

    book: Mapped["Book"] = relationship(back_populates="tags")
