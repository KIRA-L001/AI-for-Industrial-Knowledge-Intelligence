"""Integration tests for the auth flow: register → me → login → refresh → reset."""

from fastapi.testclient import TestClient

REGISTER = {
    "organization_name": "Acme Refinery",
    "email": "owner@acme.example.com",
    "full_name": "Owner One",
    "password": "supersecret1",
}


def _register(client: TestClient) -> dict:
    resp = client.post("/api/v1/auth/register", json=REGISTER)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_register_creates_owner_and_tokens(client: TestClient) -> None:
    data = _register(client)
    assert data["user"]["email"] == "owner@acme.example.com"
    assert data["user"]["role"] == "owner"
    assert data["tokens"]["access_token"]
    assert data["tokens"]["refresh_token"]


def test_register_duplicate_email_conflicts(client: TestClient) -> None:
    _register(client)
    resp = client.post("/api/v1/auth/register", json=REGISTER)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "conflict"


def test_me_requires_token_and_returns_user(client: TestClient) -> None:
    tokens = _register(client)["tokens"]
    # No token → 401
    assert client.get("/api/v1/auth/me").status_code == 401
    # With token → 200
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "owner@acme.example.com"


def test_login_and_refresh(client: TestClient) -> None:
    _register(client)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@acme.example.com", "password": "supersecret1"},
    )
    assert login.status_code == 200
    refresh_token = login.json()["tokens"]["refresh_token"]

    refreshed = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]


def test_login_wrong_password_unauthorized(client: TestClient) -> None:
    _register(client)
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@acme.example.com", "password": "nope"},
    )
    assert resp.status_code == 401


def test_password_reset_flow(client: TestClient) -> None:
    _register(client)
    issued = client.post(
        "/api/v1/auth/password-reset/request", json={"email": "owner@acme.example.com"}
    )
    assert issued.status_code == 200
    reset_token = issued.json()["reset_token"]
    assert reset_token  # exposed outside production

    confirmed = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": reset_token, "new_password": "brandnewpass9"},
    )
    assert confirmed.status_code == 204

    # Old password fails, new password works
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "owner@acme.example.com", "password": "supersecret1"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "owner@acme.example.com", "password": "brandnewpass9"},
        ).status_code
        == 200
    )
