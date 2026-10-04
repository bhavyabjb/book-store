from tests.factories import auth_headers, make_author, make_book, make_category


async def test_wishlist_requires_auth(client):
    resp = await client.get("/wishlist")
    assert resp.status_code == 401


async def test_add_list_remove_wishlist(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author)
    headers = await auth_headers(client)

    add_resp = await client.post(f"/wishlist/{book.id}", headers=headers)
    assert add_resp.status_code == 204

    list_resp = await client.get("/wishlist", headers=headers)
    assert list_resp.status_code == 200
    titles = [b["title"] for b in list_resp.json()]
    assert book.title in titles

    # Adding again is idempotent, not an error.
    add_again = await client.post(f"/wishlist/{book.id}", headers=headers)
    assert add_again.status_code == 204

    remove_resp = await client.delete(f"/wishlist/{book.id}", headers=headers)
    assert remove_resp.status_code == 204

    list_after = await client.get("/wishlist", headers=headers)
    assert list_after.json() == []
