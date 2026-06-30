"""CRUD + tenant-isolation tests for projects and equipment."""

from fastapi.testclient import TestClient


def _register(client: TestClient, email: str, org: str) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": org,
            "email": email,
            "full_name": "Tester",
            "password": "supersecret1",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["tokens"]["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_project_crud_roundtrip(client: TestClient) -> None:
    token = _register(client, "a@acme.example.com", "Acme")
    created = client.post(
        "/api/v1/projects",
        json={"name": "Turnaround 2026", "description": "Major overhaul"},
        headers=_auth(token),
    )
    assert created.status_code == 201, created.text
    pid = created.json()["id"]
    assert created.json()["status"] == "planning"

    # list
    listed = client.get("/api/v1/projects", headers=_auth(token))
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    # update
    patched = client.patch(
        f"/api/v1/projects/{pid}", json={"status": "active"}, headers=_auth(token)
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "active"

    # delete
    assert client.delete(f"/api/v1/projects/{pid}", headers=_auth(token)).status_code == 204
    assert client.get(f"/api/v1/projects/{pid}", headers=_auth(token)).status_code == 404


def test_equipment_create_and_get(client: TestClient) -> None:
    token = _register(client, "b@acme.example.com", "Acme")
    created = client.post(
        "/api/v1/equipment",
        json={"tag": "P-101", "name": "Feed Pump", "criticality": "high"},
        headers=_auth(token),
    )
    assert created.status_code == 201, created.text
    eid = created.json()["id"]
    got = client.get(f"/api/v1/equipment/{eid}", headers=_auth(token))
    assert got.status_code == 200
    assert got.json()["tag"] == "P-101"
    assert got.json()["criticality"] == "high"


def test_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/projects").status_code == 401
    assert client.post("/api/v1/projects", json={"name": "x"}).status_code == 401


def test_tenant_isolation(client: TestClient) -> None:
    token_a = _register(client, "owner@acme.example.com", "Acme")
    token_b = _register(client, "owner@globex.example.com", "Globex")

    created = client.post(
        "/api/v1/equipment",
        json={"tag": "C-201", "name": "Compressor"},
        headers=_auth(token_a),
    )
    eid = created.json()["id"]

    # Org B cannot see or fetch Org A's equipment
    assert client.get("/api/v1/equipment", headers=_auth(token_b)).json()["total"] == 0
    assert client.get(f"/api/v1/equipment/{eid}", headers=_auth(token_b)).status_code == 404
    # Org A still can
    assert client.get(f"/api/v1/equipment/{eid}", headers=_auth(token_a)).status_code == 200
