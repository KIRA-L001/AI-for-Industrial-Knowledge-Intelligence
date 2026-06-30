"""Document intelligence tests: chunking, extraction, and the analyze flow."""

from fastapi.testclient import TestClient

from app.ai.chunking import chunk_text
from app.ai.extraction import HeuristicExtractor


def test_chunk_text_overlapping_and_bounded() -> None:
    text = "word " * 600  # ~3000 chars
    chunks = chunk_text(text, page_number=2, chunk_size=1000, overlap=100)
    assert len(chunks) >= 3
    assert all(c.page_number == 2 for c in chunks)
    assert all(len(c.text) <= 1000 for c in chunks)
    # Indices are contiguous and increasing.
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_heuristic_extractor_finds_tags_and_standards() -> None:
    text = "Pump P-101 must comply with OISD-STD-105 and PESO regulations."
    result = HeuristicExtractor().extract(text)
    norms = {e.normalized for e in result.entities}
    assert "P-101" in norms
    assert any("OISD" in n for n in norms)
    assert any(r.rel_type == "governed_by" for r in result.relationships)


def _token(client: TestClient) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme",
            "email": "intel@acme.example.com",
            "full_name": "Intel Tester",
            "password": "supersecret1",
        },
    )
    return resp.json()["tokens"]["access_token"]


def test_analyze_produces_chunks_and_entities(client: TestClient) -> None:
    token = _token(client)
    auth = {"Authorization": f"Bearer {token}"}

    content = b"Equipment P-101 inspection per OISD-STD-105.\nValve V-2003 checked."
    up = client.post(
        "/api/v1/documents/upload",
        headers=auth,
        files={"file": ("report.csv", content, "text/csv")},
    )
    doc_id = up.json()["id"]
    client.post(f"/api/v1/documents/{doc_id}/process", headers=auth)

    analyzed = client.post(f"/api/v1/documents/{doc_id}/analyze", headers=auth)
    assert analyzed.status_code == 200, analyzed.text
    body = analyzed.json()
    assert body["chunks"] >= 1
    assert body["entities"] >= 2  # P-101, V-2003, OISD-STD-105

    entities = client.get("/api/v1/entities", headers=auth)
    assert entities.status_code == 200
    assert entities.json()["total"] >= 2

    chunks = client.get(f"/api/v1/documents/{doc_id}/chunks", headers=auth)
    assert chunks.status_code == 200
    assert len(chunks.json()) >= 1
