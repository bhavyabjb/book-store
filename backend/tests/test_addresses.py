from tests.factories import auth_headers

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


async def test_addresses_require_auth(client):
    resp = await client.get("/addresses")
    assert resp.status_code == 401


async def test_create_and_list_address(client):
    headers = await auth_headers(client)

    create_resp = await client.post("/addresses", json=ADDRESS_PAYLOAD, headers=headers)
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["city"] == "Mumbai"
    assert body["isDefault"] is False

    list_resp = await client.get("/addresses", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


async def test_setting_new_default_unsets_old_default(client):
    headers = await auth_headers(client)

    first = await client.post("/addresses", json={**ADDRESS_PAYLOAD, "isDefault": True}, headers=headers)
    assert first.json()["isDefault"] is True

    second = await client.post(
        "/addresses", json={**ADDRESS_PAYLOAD, "line1": "456 Other St", "isDefault": True}, headers=headers
    )
    assert second.json()["isDefault"] is True

    list_resp = await client.get("/addresses", headers=headers)
    defaults = [a["isDefault"] for a in list_resp.json()]
    assert defaults.count(True) == 1
