import datetime as dt

from pydantic import Field

from app.schemas.common import CamelModel


class Review(CamelModel):
    id: int
    book_id: int
    reviewer_name: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    created_at: dt.datetime


class ReviewCreate(CamelModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)
