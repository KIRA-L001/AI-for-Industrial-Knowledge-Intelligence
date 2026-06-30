"""Analytics overview tests."""

from fastapi.testclient import TestClient


def _token(client: TestClient) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme",
            "email": "ana@acme.example.com",
            "full_name": "Ana Tester",
            "password": "supersecret1",
        },
    )
    return resp.json()["tokens"]["access_token"]


def test_overview_reflects_created_entities(client: TestClient) -> None:
    token = _token(client)
    auth = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/equipment",
        headers=auth,
        json={"tag": "P-101", "name": "Pump", "criticality": "high"},
    )
    client.post("/api/v1/projects", headers=auth, json={"name": "TA-2026"})

    resp = client.get("/api/v1/analytics/overview", headers=auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["kpis"]["equipment"] == 1
    assert body["kpis"]["projects"] == 1
    assert body["equipment_criticality"].get("high") == 1


def test_overview_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/analytics/overview").status_code == 401
