"""Hybrid retrieval tests: lexical reranker + fused, cited context."""

from fastapi.testclient import TestClient

from app.ai.rerank import LexicalReranker


def test_lexical_reranker_orders_by_overlap() -> None:
    r = LexicalReranker()
    scores = r.score(
        "pump seal failure",
        ["mechanical seal failure on the pump", "compressor vibration report"],
    )
    assert scores[0] > scores[1]


def _token(client: TestClient) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme",
            "email": "retr@acme.example.com",
            "full_name": "Retr Tester",
            "password": "supersecret1",
        },
    )
    return resp.json()["tokens"]["access_token"]


def test_retrieve_returns_cited_context(client: TestClient) -> None:
    token = _token(client)
    auth = {"Authorization": f"Bearer {token}"}

    content = (
        b"Pump P-101 mechanical seal failed during startup due to dry running. "
        b"The compressor C-200 reported high vibration unrelated to the pump."
    )
    up = client.post(
        "/api/v1/documents/upload",
        headers=auth,
        files={"file": ("rca.csv", content, "text/csv")},
    )
    doc_id = up.json()["id"]
    client.post(f"/api/v1/documents/{doc_id}/process", headers=auth)
    client.post(f"/api/v1/documents/{doc_id}/analyze", headers=auth)
    client.post(f"/api/v1/documents/{doc_id}/embed", headers=auth)

    resp = client.post(
        "/api/v1/retrieve",
        headers=auth,
        json={"query": "why did the pump seal fail", "limit": 3},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["citations"], "expected at least one citation"
    assert body["context"]
    # Provenance present on each citation.
    for c in body["citations"]:
        assert c["chunk_id"]
        assert c["document_id"] == doc_id
