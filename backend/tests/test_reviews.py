from tests.factories import auth_headers, make_author, make_book, make_category


async def test_list_reviews_empty(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author)

    resp = await client.get(f"/books/{book.id}/reviews")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_review_requires_auth(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author)

    resp = await client.post(f"/books/{book.id}/reviews", json={"rating": 5})
    assert resp.status_code == 401


async def test_create_and_list_review(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author)
    headers = await auth_headers(client)

    resp = await client.post(
        f"/books/{book.id}/reviews",
        json={"rating": 4, "comment": "Pretty good read."},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["rating"] == 4
    assert body["comment"] == "Pretty good read."
    assert body["bookId"] == book.id

    list_resp = await client.get(f"/books/{book.id}/reviews")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    detail_resp = await client.get(f"/books/{book.id}")
    assert detail_resp.json()["ratingAvg"] == 4.0
