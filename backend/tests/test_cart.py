from tests.factories import make_author, make_book, make_category


async def test_get_empty_cart_sets_guest_token_cookie(client):
    resp = await client.get("/cart")
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["subtotal"] == 0
    assert body["total"] == 0
    assert "cart_token" in resp.cookies


async def test_add_item_computes_totals_with_delivery_fee(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author, price=199)

    resp = await client.post("/cart/items", json={"bookId": book.id, "quantity": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert body["subtotal"] == 398.0
    assert body["tax"] == 39.8
    assert body["deliveryCharge"] == 49.0  # under the 499 free-delivery threshold
    assert body["total"] == 486.8
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 2
    assert body["items"][0]["lineTotal"] == 398.0


async def test_cart_over_threshold_has_free_delivery(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author, price=600)

    resp = await client.post("/cart/items", json={"bookId": book.id, "quantity": 1})
    body = resp.json()
    assert body["subtotal"] == 600.0
    assert body["deliveryCharge"] == 0.0


async def test_add_item_twice_increments_quantity(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author, price=100)

    await client.post("/cart/items", json={"bookId": book.id, "quantity": 1})
    resp = await client.post("/cart/items", json={"bookId": book.id, "quantity": 2})
    body = resp.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 3


async def test_update_cart_item_quantity(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author, price=100)

    await client.post("/cart/items", json={"bookId": book.id, "quantity": 1})
    resp = await client.patch(f"/cart/items/{book.id}", json={"quantity": 5})
    assert resp.status_code == 200
    assert resp.json()["items"][0]["quantity"] == 5


async def test_update_cart_item_to_zero_removes_it(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author, price=100)

    await client.post("/cart/items", json={"bookId": book.id, "quantity": 1})
    resp = await client.patch(f"/cart/items/{book.id}", json={"quantity": 0})
    assert resp.status_code == 200
    assert resp.json()["items"] == []


async def test_remove_cart_item(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author, price=100)

    await client.post("/cart/items", json={"bookId": book.id, "quantity": 1})
    resp = await client.delete(f"/cart/items/{book.id}")
    assert resp.status_code == 200
    assert resp.json()["items"] == []
