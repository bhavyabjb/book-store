from tests.factories import make_author, make_book, make_category


async def test_apply_valid_coupon(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author, price=300)
    await client.post("/cart/items", json={"bookId": book.id, "quantity": 1})

    resp = await client.post("/coupons/apply", json={"code": "SAVE100"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SAVE100"
    assert body["discount"] == 100.0
    # subtotal 300 + tax 30 + delivery 49 - discount 100 = 279
    assert body["newTotal"] == 279.0


async def test_apply_invalid_coupon(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author, price=300)
    await client.post("/cart/items", json={"bookId": book.id, "quantity": 1})

    resp = await client.post("/coupons/apply", json={"code": "NOPE"})
    assert resp.status_code == 404
    assert "detail" in resp.json()
