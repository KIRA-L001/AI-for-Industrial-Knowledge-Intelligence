"""OCR/extraction tests: pure extractor unit tests + API process flow."""

from fastapi.testclient import TestClient

from app.ai.ocr.extractor import extract


def test_extract_csv_produces_tab_separated_text() -> None:
    pages = extract(b"a,b,c\n1,2,3", "text/csv")
    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert "a\tb\tc" in pages[0].text
    assert "1\t2\t3" in pages[0].text


def test_extract_unknown_falls_back_to_utf8() -> None:
    pages = extract(b"hello world", "text/plain")
    assert pages[0].text == "hello world"


def _token(client: TestClient) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme",
            "email": "ocr@acme.example.com",
            "full_name": "OCR Tester",
            "password": "supersecret1",
        },
    )
    return resp.json()["tokens"]["access_token"]


def test_process_extracts_pages_and_sets_status(client: TestClient) -> None:
    token = _token(client)
    auth = {"Authorization": f"Bearer {token}"}

    up = client.post(
        "/api/v1/documents/upload",
        headers=auth,
        files={"file": ("rows.csv", b"tag,desc\nP-101,Pump", "text/csv")},
    )
    doc_id = up.json()["id"]
    assert up.json()["status"] == "uploaded"

    processed = client.post(f"/api/v1/documents/{doc_id}/process", headers=auth)
    assert processed.status_code == 200, processed.text
    assert processed.json()["status"] == "extracted"
    assert processed.json()["page_count"] == 1

    pages = client.get(f"/api/v1/documents/{doc_id}/pages", headers=auth)
    assert pages.status_code == 200
    body = pages.json()
    assert len(body) == 1
    assert "P-101" in body[0]["text"]
