"""Embedding + semantic search tests (hashing embedder + in-memory store)."""

from fastapi.testclient import TestClient

from app.ai.embeddings import HashingEmbedder
from app.ai.vectorstore import InMemoryVectorStore, VectorPoint


def test_hashing_embedder_is_deterministic_and_normalized() -> None:
    emb = HashingEmbedder(dim=64)
    a = emb.embed_one("pump failure analysis")
    b = emb.embed_one("pump failure analysis")
    assert a == b
    assert abs(sum(x * x for x in a) ** 0.5 - 1.0) < 1e-6


def test_inmemory_vector_store_filters_and_ranks() -> None:
    store = InMemoryVectorStore()
    emb = HashingEmbedder(dim=64)
    store.upsert(
        [
            VectorPoint("1", emb.embed_one("pump seal leak"), {"organization_id": "o1"}),
            VectorPoint("2", emb.embed_one("compressor vibration"), {"organization_id": "o1"}),
            VectorPoint("3", emb.embed_one("pump seal leak"), {"organization_id": "o2"}),
        ]
    )
    hits = store.search(emb.embed_one("pump seal"), limit=5, filters={"organization_id": "o1"})
    assert hits and hits[0].id == "1"
    assert all(h.payload["organization_id"] == "o1" for h in hits)


def _token(client: TestClient) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme",
            "email": "search@acme.example.com",
            "full_name": "Search Tester",
            "password": "supersecret1",
        },
    )
    return resp.json()["tokens"]["access_token"]


def test_embed_and_search_flow(client: TestClient) -> None:
    token = _token(client)
    auth = {"Authorization": f"Bearer {token}"}

    text = b"The centrifugal pump P-101 suffered a mechanical seal failure during startup."
    up = client.post(
        "/api/v1/documents/upload",
        headers=auth,
        files={"file": ("note.csv", text, "text/csv")},
    )
    doc_id = up.json()["id"]
    client.post(f"/api/v1/documents/{doc_id}/process", headers=auth)
    client.post(f"/api/v1/documents/{doc_id}/analyze", headers=auth)

    embedded = client.post(f"/api/v1/documents/{doc_id}/embed", headers=auth)
    assert embedded.status_code == 200, embedded.text
    assert embedded.json()["embedded_chunks"] >= 1

    found = client.post(
        "/api/v1/search", headers=auth, json={"query": "pump seal failure", "limit": 5}
    )
    assert found.status_code == 200, found.text
    body = found.json()
    assert len(body["hits"]) >= 1
    assert "pump" in body["hits"][0]["text"].lower()
