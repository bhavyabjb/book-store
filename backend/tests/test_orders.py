import datetime as dt

from sqlalchemy import select

from app.models.order import Order, OrderStatus
from tests.factories import auth_headers, make_author, make_book, make_category

ADDRESS_PAYLOAD = {
    "firstName": "Alice",
    "lastName": "Doe",
    "line1": "123 Main St",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pin": "400001",
    "country": "India",
    "phone": "9999999999",
}


async def _setup_cart_and_address(client, db_session, headers, price=300):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author, price=price)
    await client.post("/cart/items", json={"bookId": book.id, "quantity": 1}, headers=headers)
    addr_resp = await client.post("/addresses", json=ADDRESS_PAYLOAD, headers=headers)
    address_id = addr_resp.json()["id"]
    return book, address_id


async def test_create_order_requires_auth(client, db_session):
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author)
    await client.post("/cart/items", json={"bookId": book.id, "quantity": 1})

    resp = await client.post("/orders", json={"addressId": 1})
    assert resp.status_code == 401


async def test_create_order_from_cart(client, db_session):
    headers = await auth_headers(client, email="checkout@example.com")
    book, address_id = await _setup_cart_and_address(client, db_session, headers, price=300)

    resp = await client.post("/orders", json={"addressId": address_id}, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "PLACED"
    assert body["subtotal"] == 300.0
    assert body["tax"] == 30.0
    assert body["deliveryCharge"] == 49.0
    assert body["total"] == 379.0
    assert body["items"][0]["book"]["id"] == book.id
    assert body["address"]["city"] == "Mumbai"

    # Cart should now be empty.
    cart_resp = await client.get("/cart", headers=headers)
    assert cart_resp.json()["items"] == []

    # Order should show up in history and be independently fetchable.
    list_resp = await client.get("/orders", headers=headers)
    assert len(list_resp.json()) == 1

    get_resp = await client.get(f"/orders/{body['id']}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == body["id"]


async def test_create_order_empty_cart_rejected(client, db_session):
    headers = await auth_headers(client, email="emptycart@example.com")
    addr_resp = await client.post("/addresses", json=ADDRESS_PAYLOAD, headers=headers)
    address_id = addr_resp.json()["id"]

    resp = await client.post("/orders", json={"addressId": address_id}, headers=headers)
    assert resp.status_code == 422


async def test_create_order_with_coupon_applies_discount(client, db_session):
    headers = await auth_headers(client, email="coupon@example.com")
    book, address_id = await _setup_cart_and_address(client, db_session, headers, price=300)

    resp = await client.post(
        "/orders", json={"addressId": address_id, "couponCode": "SAVE100"}, headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["discount"] == 100.0
    assert body["couponCode"] == "SAVE100"
    assert body["total"] == 279.0


async def test_cancel_order_within_window(client, db_session):
    headers = await auth_headers(client, email="cancelme@example.com")
    book, address_id = await _setup_cart_and_address(client, db_session, headers)

    create_resp = await client.post("/orders", json={"addressId": address_id}, headers=headers)
    order_id = create_resp.json()["id"]

    cancel_resp = await client.post(f"/orders/{order_id}/cancel", headers=headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"


async def test_cancel_order_after_window_rejected(client, db_session):
    headers = await auth_headers(client, email="toolate@example.com")
    book, address_id = await _setup_cart_and_address(client, db_session, headers)

    create_resp = await client.post("/orders", json={"addressId": address_id}, headers=headers)
    order_id = create_resp.json()["id"]

    # Backdate the order directly in the DB so the 48h cancel window has passed.
    result = await db_session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    order.placed_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=72)
    order.cancel_by = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)
    await db_session.commit()

    cancel_resp = await client.post(f"/orders/{order_id}/cancel", headers=headers)
    assert cancel_resp.status_code == 422
    assert "detail" in cancel_resp.json()


async def test_cancel_already_cancelled_order_rejected(client, db_session):
    headers = await auth_headers(client, email="doublecancel@example.com")
    book, address_id = await _setup_cart_and_address(client, db_session, headers)

    create_resp = await client.post("/orders", json={"addressId": address_id}, headers=headers)
    order_id = create_resp.json()["id"]

    first_cancel = await client.post(f"/orders/{order_id}/cancel", headers=headers)
    assert first_cancel.status_code == 200

    second_cancel = await client.post(f"/orders/{order_id}/cancel", headers=headers)
    assert second_cancel.status_code == 422
