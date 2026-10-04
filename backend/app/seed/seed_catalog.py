"""One-off catalog seeding script. NOT run automatically on app startup
because it makes live calls to the Open Library API.

Usage:
    cd backend
    DATABASE_URL=postgresql+asyncpg://... python -m app.seed.seed_catalog

Idempotent: re-running will not create duplicate books. Books are matched
by (title, author name); existing rows are left alone (for Open-Library
sourced books) or refreshed in place (for the hand-authored "override"
books that must exactly match the wireframes).
"""

import asyncio
import logging
import random
import re
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.author import Author
from app.models.book import Book, BookFormat, BookTag
from app.models.category import Category
from app.models.review import Review
from app.seed.cover_art import write_cover
from app.seed.openlibrary_client import cover_image_url, fetch_subject_books

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("seed_catalog")

# Deterministic RNG — never touch the global `random` module so results are
# reproducible across runs (per the single run's insertion order).
rng = random.Random(42)

BOOKS_PER_SUBJECT = 10

# Display name -> Open Library subject slug
CATEGORY_SUBJECTS: dict[str, str] = {
    "Romance": "romance",
    "Mystery": "mystery",
    "Science Fiction": "science_fiction",
    "Fantasy": "fantasy",
    "Historical": "history",
    "Biography": "biography",
    "Self-help": "self_help",
    "Memoir": "memoir",
    "Travel": "travel",
    "Cooking": "cooking",
    "Children's": "children",
    "Young Adult": "young_adult",
    "Comics & Graphic Novels": "comics",
    "Poetry": "poetry",
    "Drama": "drama",
    "Science": "science",
    "Philosophy": "philosophy",
    "Religion": "religion",
    "Language Learning": "foreign_language_study",
}

GENRE_WORDS: dict[str, list[str]] = {
    "Romance": ["Love Story", "Contemporary"],
    "Mystery": ["Suspense", "Crime"],
    "Science Fiction": ["Sci-Fi", "Dystopian"],
    "Fantasy": ["Adventure", "Epic"],
    "Historical": ["Historical Fiction", "Period Drama"],
    "Biography": ["Life Story", "Non-fiction"],
    "Self-help": ["Self Help", "Personal Growth"],
    "Memoir": ["Memoir", "Life Story"],
    "Travel": ["Travel", "Adventure"],
    "Cooking": ["Recipes", "Food & Drink"],
    "Children's": ["Picture Book", "Kids"],
    "Young Adult": ["Coming of Age", "YA Fiction"],
    "Comics & Graphic Novels": ["Graphic Novel", "Illustrated"],
    "Poetry": ["Verse", "Anthology"],
    "Drama": ["Playwriting", "Theatre"],
    "Science": ["Non-fiction", "Popular Science"],
    "Philosophy": ["Non-fiction", "Ideas"],
    "Religion": ["Spirituality", "Faith"],
    "Language Learning": ["Education", "Reference"],
}

# Exact, hand-authored books required to match the wireframes.
# category assignment is a judgment call made from each book's tags/blurb,
# since the spec gives tags but not an explicit category for these.
OVERRIDE_BOOKS = [
    dict(
        title="The Art of Focus",
        author_name="Arjun Patel",
        category_name="Self-help",
        price=399,
        format=BookFormat.PAPERBACK,
        tags=["Non-fiction", "Self Help"],
        description="Practical guide to mastering focus & boosting productivity every day.",
        section="recommended",
        cover_bg="#EDE4D3",
        cover_fg="#2B2420",
    ),
    dict(
        title="The Art of Learning",
        author_name="Raj Patel",
        category_name="Self-help",
        price=259,
        format=BookFormat.PAPERBACK,
        tags=["Non-fiction", "Self Help"],
        description="Master the mindset and methods for effective lifelong learning.",
        section="recommended",
        cover_bg="#E8432F",
        cover_fg="#FFFFFF",
    ),
    dict(
        title="The Path to Success",
        author_name="James Wright",
        category_name="Self-help",
        price=359,
        format=BookFormat.PAPERBACK,
        tags=["Non-fiction", "Self Help"],
        description="A practical guide to achieving goals with clarity and confidence.",
        section="recommended",
        cover_bg="#1C6E78",
        cover_fg="#F4D35E",
    ),
    dict(
        title="The Midnight Hour",
        author_name="James Adams",
        category_name="Mystery",
        price=299,
        format=BookFormat.PAPERBACK,
        tags=["Fiction", "Thriller", "Horror"],
        description="Haunting tale of a man's journey & the shadows of a forgotten past.",
        section="bestseller",
        cover_bg="#1B2A3A",
        cover_fg="#D8DEE9",
    ),
    dict(
        title="Beneath the Stars",
        author_name="Jessica Martin",
        category_name="Romance",
        price=499,
        format=BookFormat.HARDCOVER,
        tags=["Fiction", "Love", "Drama"],
        description="A heartwarming tale, where two souls discover who you need.",
        section="bestseller",
        cover_bg="#6B3B5C",
        cover_fg="#F7D9A0",
    ),
    dict(
        title="The Final Frontier",
        author_name="Laura Mitchell",
        category_name="Science Fiction",
        price=359,
        format=BookFormat.PAPERBACK,
        tags=["Fiction", "Thriller"],
        description="A mission to space secrets to change humanity forever.",
        section="bestseller",
        cover_bg="#16233F",
        cover_fg="#9FD8CB",
    ),
    dict(
        title="Joy of Minimalism",
        author_name="Daniel Reed",
        category_name="Self-help",
        price=149,
        format=BookFormat.PAPERBACK,
        tags=["Non-fiction", "Self Help"],
        description=(
            "Declutter your life to uncover peace, clarity, and joy.\n\n"
            "Joy of Minimalism is a warm, practical guide to letting go of the excess that "
            "crowds out what truly matters. Daniel Reed draws on years of coaching clients "
            "through decluttering, both physical and mental, to lay out a simple framework "
            "for identifying what adds value to your life and releasing what doesn't.\n\n"
            "Across short, actionable chapters, you'll learn how to simplify your home, your "
            "schedule, and your mind, building habits that compound into lasting calm. Whether "
            "you're drowning in belongings or just craving more breathing room, this book offers "
            "a gentle, realistic path to a lighter, more intentional life."
        ),
        section="new_launch",
        publisher="ABC Publishers",
        author_bio=(
            "Daniel Reed is a writer, minimalist, and productivity coach based in San Francisco. "
            "After a decade in fast-paced tech startups left him burnt out and buried in clutter, "
            "he rebuilt his life around simplicity and intention. He now writes and speaks about "
            "minimalism, focus, and sustainable productivity for a global audience."
        ),
        reviews=[dict(reviewer_name="John Smith", rating=5, comment=None)],
        cover_bg="#F2C230",
        cover_fg="#241C04",
    ),
    dict(
        title="The Vanishing House",
        author_name="Clara Nelson",
        category_name="Mystery",
        price=99,
        format=BookFormat.EBOOK,
        tags=["Fiction", "Horror"],
        description="A chilling mystery unfolds within a house that disappears.",
        section="new_launch",
        cover_bg="#1E3B38",
        cover_fg="#E8DCC8",
    ),
    dict(
        title="The Lost Kitten",
        author_name="Emily Parker",
        category_name="Children's",
        price=339,
        format=BookFormat.HARDCOVER,
        tags=["Fiction", "Children"],
        description="A heartwarming tale of courage, friendship, and feline adventure.",
        section="new_launch",
        cover_bg="#E2792A",
        cover_fg="#2B1706",
    ),
]


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def category_slug(name: str) -> str:
    return slugify(name)


async def get_or_create_category(db: AsyncSession, name: str) -> Category:
    slug = category_slug(name)
    result = await db.execute(select(Category).where(Category.slug == slug))
    category = result.scalar_one_or_none()
    if category is None:
        category = Category(name=name, slug=slug)
        db.add(category)
        await db.flush()
    return category


async def get_or_create_author(
    db: AsyncSession, name: str, bio: str | None = None, photo_url: str | None = None
) -> Author:
    result = await db.execute(select(Author).where(Author.name == name))
    author = result.scalar_one_or_none()
    if author is None:
        author = Author(name=name, bio=bio, photo_url=photo_url)
        db.add(author)
        await db.flush()
    else:
        if bio and not author.bio:
            author.bio = bio
        if photo_url and not author.photo_url:
            author.photo_url = photo_url
    return author


async def find_book(db: AsyncSession, title: str, author_id: int) -> Book | None:
    result = await db.execute(select(Book).where(Book.title == title, Book.author_id == author_id))
    return result.scalar_one_or_none()


async def unique_slug(db: AsyncSession, base: str) -> str:
    candidate = base
    suffix = 2
    while True:
        result = await db.execute(select(Book.id).where(Book.slug == candidate))
        if result.scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{suffix}"
        suffix += 1


def synth_format() -> BookFormat:
    return rng.choices(
        [BookFormat.PAPERBACK, BookFormat.HARDCOVER, BookFormat.EBOOK],
        weights=[0.55, 0.25, 0.20],
        k=1,
    )[0]


def synth_price(fmt: BookFormat) -> int:
    if fmt == BookFormat.EBOOK:
        return rng.randint(99, 299)
    if fmt == BookFormat.HARDCOVER:
        return rng.randint(349, 599)
    return rng.randint(149, 449)


def synth_language() -> str:
    return rng.choices(["English", "Hindi", "Spanish"], weights=[0.9, 0.05, 0.05], k=1)[0]


def synth_tags(category_name: str) -> list[str]:
    words = GENRE_WORDS.get(category_name, [])
    extra = rng.sample(words, k=min(len(words), rng.randint(0, 2)))
    return [category_name] + extra


async def seed_overrides(db: AsyncSession) -> int:
    count = 0
    for spec in OVERRIDE_BOOKS:
        category = await get_or_create_category(db, spec["category_name"])
        author = await get_or_create_author(db, spec["author_name"], bio=spec.get("author_bio"))

        book = await find_book(db, spec["title"], author.id)
        is_new = book is None
        if book is None:
            slug = await unique_slug(db, slugify(f"{spec['title']}-{spec['author_name']}"))
            book = Book(slug=slug, title=spec["title"], author_id=author.id)
            db.add(book)

        book.description = spec["description"]
        book.category_id = category.id
        book.format = spec["format"]
        book.language = "English"
        book.price = spec["price"]
        cover_path = write_cover(
            book.slug, spec["title"], spec["author_name"], spec["cover_bg"], spec["cover_fg"]
        )
        book.cover_image_url = f"{settings.PUBLIC_BASE_URL}{cover_path}"
        book.publisher = spec.get("publisher")
        book.delivery_days = book.delivery_days or 4
        book.rating_avg = book.rating_avg if book.rating_avg is not None else round(rng.uniform(4.0, 5.0), 1)
        book.units_sold = book.units_sold or rng.randint(50, 400)
        book.is_recommended = spec["section"] == "recommended"
        book.is_bestseller = spec["section"] == "bestseller"
        book.is_new_launch = spec["section"] == "new_launch"
        await db.flush()

        # Reset tags to the exact spec list.
        existing_tags = (await db.execute(select(BookTag).where(BookTag.book_id == book.id))).scalars().all()
        for t in existing_tags:
            await db.delete(t)
        await db.flush()
        for tag in spec["tags"]:
            db.add(BookTag(book_id=book.id, tag=tag))

        for review_spec in spec.get("reviews", []):
            existing_review = (
                await db.execute(
                    select(Review).where(
                        Review.book_id == book.id, Review.reviewer_name == review_spec["reviewer_name"]
                    )
                )
            ).scalar_one_or_none()
            if existing_review is None:
                db.add(
                    Review(
                        book_id=book.id,
                        reviewer_name=review_spec["reviewer_name"],
                        rating=review_spec["rating"],
                        comment=review_spec.get("comment"),
                    )
                )

        await db.commit()
        if is_new:
            count += 1
            logger.info("Seeded override book: %s", spec["title"])
        else:
            logger.info("Refreshed override book: %s", spec["title"])
    return count


async def seed_open_library(db: AsyncSession) -> dict[str, int]:
    inserted_by_category: dict[str, int] = {}

    for category_name, subject in CATEGORY_SUBJECTS.items():
        category = await get_or_create_category(db, category_name)
        await db.commit()

        inserted_by_category.setdefault(category_name, 0)

        books = fetch_subject_books(subject, limit=BOOKS_PER_SUBJECT)
        if not books:
            logger.warning("No books fetched for subject=%s (category=%s); continuing", subject, category_name)
            continue

        for ol_book in books:
            author = await get_or_create_author(db, ol_book.author_name)
            existing = await find_book(db, ol_book.title, author.id)
            if existing is not None:
                continue

            fmt = synth_format()
            price = synth_price(fmt)
            slug = await unique_slug(db, slugify(f"{ol_book.title}-{ol_book.author_name}"))

            book = Book(
                slug=slug,
                title=ol_book.title,
                description=f"{ol_book.title} by {ol_book.author_name} — a {category_name.lower()} pick for your shelf.",
                author_id=author.id,
                category_id=category.id,
                format=fmt,
                language=synth_language(),
                price=price,
                cover_image_url=cover_image_url(ol_book.cover_id),
                delivery_days=rng.randint(3, 7),
                units_sold=rng.randint(5, 400),
                rating_avg=round(rng.uniform(3.0, 5.0), 1),
                is_recommended=False,
                is_bestseller=False,
                is_new_launch=False,
            )
            db.add(book)
            await db.flush()

            for tag in synth_tags(category_name):
                db.add(BookTag(book_id=book.id, tag=tag))

            await db.commit()
            inserted_by_category[category_name] += 1

    return inserted_by_category


async def main() -> None:
    async with AsyncSessionLocal() as db:
        override_count = await seed_overrides(db)
        ol_counts = await seed_open_library(db)

    total_ol = sum(ol_counts.values())
    logger.info("=== Seed summary ===")
    logger.info("Override books seeded/refreshed: %d", override_count)
    logger.info("Open Library books inserted: %d", total_ol)
    for category_name, count in ol_counts.items():
        logger.info("  %-28s %d", category_name, count)
    logger.info("Total new books inserted this run: %d", override_count + total_ol)


if __name__ == "__main__":
    asyncio.run(main())
