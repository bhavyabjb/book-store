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


async def _place_order(client, db_session, email, price=300):
    headers = await auth_headers(client, email=email)
    category = await make_category(db_session)
    author = await make_author(db_session)
    book = await make_book(db_session, category, author, price=price)
    await client.post("/cart/items", json={"bookId": book.id, "quantity": 1}, headers=headers)
    addr_resp = await client.post("/addresses", json=ADDRESS_PAYLOAD, headers=headers)
    address_id = addr_resp.json()["id"]
    order_resp = await client.post("/orders", json={"addressId": address_id}, headers=headers)
    return headers, order_resp.json()


async def test_payment_success(client, db_session):
    headers, order = await _place_order(client, db_session, "paysuccess@example.com")

    resp = await client.post(
        f"/orders/{order['id']}/payment",
        json={"method": "CARD", "cardNumber": "4111111111111111", "nameOnCard": "Alice Doe"},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "SUCCESS"
    assert body["orderId"] == order["id"]
    assert body["amount"] == order["total"]
    assert body["transactionRef"]
    assert body["failureReason"] is None

    order_resp = await client.get(f"/orders/{order['id']}", headers=headers)
    assert order_resp.json()["status"] == "PAID"


async def test_payment_declined_for_card_ending_0000(client, db_session):
    headers, order = await _place_order(client, db_session, "paydecline@example.com")

    resp = await client.post(
        f"/orders/{order['id']}/payment",
        json={"method": "CARD", "cardNumber": "4111111110000", "nameOnCard": "Alice Doe"},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "FAILED"
    assert body["transactionRef"] is None
    assert body["failureReason"]

    order_resp = await client.get(f"/orders/{order['id']}", headers=headers)
    assert order_resp.json()["status"] == "PLACED"  # unchanged, can retry


async def test_payment_declined_for_upi_ending_0000(client, db_session):
    headers, order = await _place_order(client, db_session, "upidecline@example.com")

    resp = await client.post(
        f"/orders/{order['id']}/payment",
        json={"method": "UPI", "upiId": "someone@okbank0000"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "FAILED"
