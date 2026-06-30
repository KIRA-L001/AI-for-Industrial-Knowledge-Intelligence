"""Document upload/list/get/download/delete tests (in-memory storage)."""

from fastapi.testclient import TestClient


def _token(client: TestClient, email: str = "doc@acme.example.com") -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme",
            "email": email,
            "full_name": "Doc Tester",
            "password": "supersecret1",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["tokens"]["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_upload_pdf_creates_document_in_uploaded_state(client: TestClient) -> None:
    token = _token(client)
    resp = client.post(
        "/api/v1/documents/upload",
        headers=_auth(token),
        files={"file": ("manual.pdf", b"%PDF-1.4 fake content", "application/pdf")},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["filename"] == "manual.pdf"
    assert body["status"] == "uploaded"
    assert body["size_bytes"] > 0


def test_upload_rejects_unsupported_type(client: TestClient) -> None:
    token = _token(client)
    resp = client.post(
        "/api/v1/documents/upload",
        headers=_auth(token),
        files={"file": ("evil.exe", b"MZ", "application/x-msdownload")},
    )
    assert resp.status_code == 415
    assert resp.json()["error"]["code"] == "unsupported_media_type"


def test_list_get_download_delete(client: TestClient) -> None:
    token = _token(client)
    up = client.post(
        "/api/v1/documents/upload",
        headers=_auth(token),
        files={"file": ("data.csv", b"a,b,c\n1,2,3", "text/csv")},
    )
    doc_id = up.json()["id"]

    listed = client.get("/api/v1/documents", headers=_auth(token))
    assert listed.json()["total"] == 1

    got = client.get(f"/api/v1/documents/{doc_id}", headers=_auth(token))
    assert got.status_code == 200

    dl = client.get(f"/api/v1/documents/{doc_id}/download", headers=_auth(token))
    assert dl.status_code == 200
    assert dl.json()["url"].startswith("memory://")

    assert client.delete(f"/api/v1/documents/{doc_id}", headers=_auth(token)).status_code == 204
    assert client.get(f"/api/v1/documents/{doc_id}", headers=_auth(token)).status_code == 404


def test_upload_requires_auth(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("x.pdf", b"x", "application/pdf")},
    )
    assert resp.status_code == 401
