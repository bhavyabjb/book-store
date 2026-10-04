import pytest


async def test_register_creates_user_and_returns_token(client):
    resp = await client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "password": "password123",
            "firstName": "Alice",
            "lastName": "Doe",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["accessToken"]
    assert body["tokenType"] == "bearer"
    assert body["user"]["email"] == "alice@example.com"
    assert body["user"]["firstName"] == "Alice"
    assert body["user"]["giftPointsBalance"] == 0


async def test_register_duplicate_email_conflicts(client):
    payload = {
        "email": "bob@example.com",
        "password": "password123",
        "firstName": "Bob",
        "lastName": "Smith",
    }
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/auth/register", json=payload)
    assert second.status_code == 409
    assert "detail" in second.json()


async def test_login_success(client):
    await client.post(
        "/auth/register",
        json={
            "email": "carol@example.com",
            "password": "password123",
            "firstName": "Carol",
            "lastName": "Lee",
        },
    )
    resp = await client.post("/auth/login", json={"email": "carol@example.com", "password": "password123"})
    assert resp.status_code == 200
    assert resp.json()["accessToken"]


async def test_login_invalid_credentials(client):
    resp = await client.post("/auth/login", json={"email": "nobody@example.com", "password": "wrong"})
    assert resp.status_code == 401


async def test_me_requires_auth(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_returns_current_user(client):
    register_resp = await client.post(
        "/auth/register",
        json={
            "email": "dave@example.com",
            "password": "password123",
            "firstName": "Dave",
            "lastName": "King",
        },
    )
    token = register_resp.json()["accessToken"]
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "dave@example.com"
