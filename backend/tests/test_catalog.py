from app.models.book import BookFormat
from tests.factories import make_author, make_book, make_category


async def test_list_categories(client, db_session):
    await make_category(db_session, "Romance", "romance")
    await make_category(db_session, "Mystery", "mystery")

    resp = await client.get("/categories")
    assert resp.status_code == 200
    names = {c["name"] for c in resp.json()}
    assert {"Romance", "Mystery"} <= names


async def test_list_books_basic(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session, "Jane Austen")
    await make_book(db_session, category, author, title="Pride", slug="pride", price=199)
    await make_book(db_session, category, author, title="Prejudice", slug="prejudice", price=299)

    resp = await client.get("/books")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["pageSize"] == 12
    assert len(body["items"]) == 2
    item = body["items"][0]
    assert "author" in item and item["author"]["name"] == "Jane Austen"
    assert "deliveryDate" in item


async def test_list_books_filters_by_price_and_format(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    await make_book(db_session, category, author, title="Cheap Paperback", slug="cheap", price=100, format=BookFormat.PAPERBACK)
    await make_book(db_session, category, author, title="Pricey Hardcover", slug="pricey", price=550, format=BookFormat.HARDCOVER)

    resp = await client.get("/books", params={"minPrice": 500, "format": "Hardcover"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Pricey Hardcover"


async def test_list_books_search_query(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session, "Stephen King")
    await make_book(db_session, category, author, title="The Shining", slug="the-shining")
    await make_book(db_session, category, author, title="Unrelated Title", slug="unrelated")

    resp = await client.get("/books", params={"q": "Shining"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "The Shining"


async def test_list_books_section_filter(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    await make_book(
        db_session, category, author, title="Bestseller Book", slug="bestseller-book", is_bestseller=True
    )
    await make_book(db_session, category, author, title="Plain Book", slug="plain-book")

    resp = await client.get("/books", params={"section": "bestsellers"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Bestseller Book"


async def test_get_book_detail(client, db_session):
    category = await make_category(db_session, "Sci-Fi", "sci-fi")
    author = await make_author(db_session, "Isaac Asimov")
    book = await make_book(db_session, category, author, title="Foundation", slug="foundation", tags=["Sci-Fi", "Classic"])

    resp = await client.get(f"/books/{book.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Foundation"
    assert body["category"]["slug"] == "sci-fi"
    assert set(body["tags"]) == {"Sci-Fi", "Classic"}
    assert body["unitsSold"] == 10


async def test_get_book_not_found(client):
    resp = await client.get("/books/999999")
    assert resp.status_code == 404


async def test_related_books(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book1 = await make_book(db_session, category, author, title="Book One", slug="book-one")
    await make_book(db_session, category, author, title="Book Two", slug="book-two")
    await make_book(db_session, category, author, title="Book Three", slug="book-three")

    resp = await client.get(f"/books/{book1.id}/related")
    assert resp.status_code == 200
    related_titles = {b["title"] for b in resp.json()}
    assert "Book One" not in related_titles
    assert related_titles == {"Book Two", "Book Three"}
