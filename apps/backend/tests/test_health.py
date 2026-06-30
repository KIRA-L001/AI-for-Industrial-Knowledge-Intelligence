"""Smoke tests for liveness and root endpoints (no external stores required)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok() -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "kira-backend"


def test_root_ok() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["service"] == "kira-backend"


def test_openapi_available() -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert resp.json()["info"]["title"].startswith("KIRA")
