import datetime as dt
import enum

from app.schemas.common import CamelModel


class BookFormat(str, enum.Enum):
    PAPERBACK = "Paperback"
    HARDCOVER = "Hardcover"
    EBOOK = "eBook"


class Category(CamelModel):
    id: int
    name: str
    slug: str
    parent_id: int | None = None


class Author(CamelModel):
    id: int
    name: str
    bio: str | None = None
    photo_url: str | None = None


class BookSummary(CamelModel):
    id: int
    slug: str
    title: str
    author: Author
    description: str | None = None
    price: float
    format: BookFormat
    cover_image_url: str | None = None
    tags: list[str] = []
    rating_avg: float | None = None
    delivery_date: dt.date


class BookDetail(BookSummary):
    publisher: str | None = None
    language: str
    isbn: str | None = None
    back_cover_image_url: str | None = None
    units_sold: int
    category: Category


class BookPage(CamelModel):
    items: list[BookSummary]
    total: int
    page: int
    page_size: int
