"""Thin synchronous client for the Open Library "subjects" API.

Used only by the one-off seeding script (app/seed/seed_catalog.py). Not
imported anywhere in the running application, so a flaky/offline network
never affects `uvicorn app.main:app`.
"""

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger("openlibrary_client")

BASE_URL = "https://openlibrary.org"
COVERS_URL = "https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
REQUEST_TIMEOUT = 15.0


@dataclass
class OpenLibraryBook:
    title: str
    author_name: str
    cover_id: int
    first_publish_year: int | None


def cover_image_url(cover_id: int) -> str:
    return COVERS_URL.format(cover_id=cover_id)


def fetch_subject_books(subject: str, limit: int = 12) -> list[OpenLibraryBook]:
    """Fetch up to `limit` usable books (has cover + author) for a subject slug.

    Tolerant of network hiccups: logs and returns an empty list rather than
    raising, so the caller can skip this subject and continue with others.
    """
    url = f"{BASE_URL}/subjects/{subject}.json"
    params = {"limit": max(limit * 3, limit + 10)}  # over-fetch to allow for skips

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except (httpx.TimeoutException, httpx.HTTPError) as exc:
        logger.warning("Open Library fetch failed for subject=%s: %s", subject, exc)
        return []
    except Exception as exc:  # noqa: BLE001 - defensive: never crash the whole import
        logger.warning("Unexpected error fetching subject=%s: %s", subject, exc)
        return []

    works = data.get("works", [])
    books: list[OpenLibraryBook] = []
    for work in works:
        if len(books) >= limit:
            break
        cover_id = work.get("cover_id")
        authors = work.get("authors") or []
        title = work.get("title")
        if not cover_id or not authors or not title:
            continue
        author_name = authors[0].get("name")
        if not author_name:
            continue
        books.append(
            OpenLibraryBook(
                title=title,
                author_name=author_name,
                cover_id=cover_id,
                first_publish_year=work.get("first_publish_year"),
            )
        )
    return books
