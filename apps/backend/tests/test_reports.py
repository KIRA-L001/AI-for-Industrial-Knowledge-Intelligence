"""Report generation tests (PDF export)."""

from fastapi.testclient import TestClient


def _token(client: TestClient) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme",
            "email": "rep@acme.example.com",
            "full_name": "Report Tester",
            "password": "supersecret1",
        },
    )
    return resp.json()["tokens"]["access_token"]


def test_report_types_listed(client: TestClient) -> None:
    token = _token(client)
    resp = client.get("/api/v1/reports/types", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    keys = {r["key"] for r in resp.json()}
    assert {"maintenance", "compliance", "executive", "knowledge", "rca"} == keys


def test_generate_pdf(client: TestClient) -> None:
    token = _token(client)
    auth = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/api/v1/reports/generate", headers=auth, json={"report_type": "executive"}
    )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"  # valid PDF magic bytes
