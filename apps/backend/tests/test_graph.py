"""Knowledge graph tests: in-memory backend + sync/overview/neighbors API."""

import asyncio

from fastapi.testclient import TestClient

from app.ai.graph.backend import GraphEdge, GraphNode, InMemoryGraph


def test_inmemory_graph_neighbors() -> None:
    g = InMemoryGraph()

    async def scenario() -> None:
        await g.upsert_node("o1", GraphNode(id="a", label="equipment", name="P-101"))
        await g.upsert_node("o1", GraphNode(id="b", label="standard", name="OISD-105"))
        await g.upsert_node("o1", GraphNode(id="c", label="equipment", name="V-200"))
        await g.upsert_edge("o1", GraphEdge(source="a", target="b", rel_type="governed_by"))
        view = await g.neighbors("o1", "a", depth=1)
        assert {n.id for n in view.nodes} == {"a", "b"}
        assert len(view.edges) == 1

    asyncio.run(scenario())


def _token(client: TestClient) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme",
            "email": "graph@acme.example.com",
            "full_name": "Graph Tester",
            "password": "supersecret1",
        },
    )
    return resp.json()["tokens"]["access_token"]


def test_sync_and_overview(client: TestClient) -> None:
    token = _token(client)
    auth = {"Authorization": f"Bearer {token}"}

    up = client.post(
        "/api/v1/documents/upload",
        headers=auth,
        files={"file": ("r.csv", b"P-101 governed by OISD-STD-105", "text/csv")},
    )
    doc_id = up.json()["id"]
    client.post(f"/api/v1/documents/{doc_id}/process", headers=auth)
    client.post(f"/api/v1/documents/{doc_id}/analyze", headers=auth)

    synced = client.post("/api/v1/graph/sync", headers=auth)
    assert synced.status_code == 200, synced.text
    assert synced.json()["nodes"] >= 2

    overview = client.get("/api/v1/graph", headers=auth)
    assert overview.status_code == 200
    body = overview.json()
    assert len(body["nodes"]) >= 2
    assert any(e["rel_type"] == "governed_by" for e in body["edges"])
