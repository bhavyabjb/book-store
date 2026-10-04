"""Small helpers for creating DB rows directly in tests (there's no admin API)."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.author import Author
from app.models.book import Book, BookFormat, BookTag
from app.models.category import Category


async def register_user(client: AsyncClient, email: str = "user@example.com", password: str = "password123") -> dict:
    resp = await client.post(
        "/auth/register",
        json={"email": email, "password": password, "firstName": "Test", "lastName": "User"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def auth_headers(client: AsyncClient, email: str = "user@example.com") -> dict:
    data = await register_user(client, email=email)
    return {"Authorization": f"Bearer {data['accessToken']}"}


async def make_category(db: AsyncSession, name: str = "Fiction", slug: str = "fiction") -> Category:
    category = Category(name=name, slug=slug)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def make_author(db: AsyncSession, name: str = "Test Author") -> Author:
    author = Author(name=name, bio="A test author bio")
    db.add(author)
    await db.commit()
    await db.refresh(author)
    return author


async def make_book(
    db: AsyncSession,
    category: Category,
    author: Author,
    title: str = "Test Book",
    slug: str = "test-book",
    price: float = 199,
    format: BookFormat = BookFormat.PAPERBACK,
    tags: list[str] | None = None,
    **kwargs,
) -> Book:
    book = Book(
        slug=slug,
        title=title,
        description=kwargs.pop("description", "A great test book."),
        author_id=author.id,
        category_id=category.id,
        format=format,
        language=kwargs.pop("language", "English"),
        price=price,
        cover_image_url=kwargs.pop("cover_image_url", "https://example.com/cover.jpg"),
        delivery_days=kwargs.pop("delivery_days", 5),
        units_sold=kwargs.pop("units_sold", 10),
        rating_avg=kwargs.pop("rating_avg", 4.5),
        **kwargs,
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)

    for tag in tags or ["Fiction"]:
        db.add(BookTag(book_id=book.id, tag=tag))
    await db.commit()
    await db.refresh(book)
    return book
