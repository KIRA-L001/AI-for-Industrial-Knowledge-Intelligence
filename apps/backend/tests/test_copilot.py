"""AI OS + agents tests: planner routing, confidence, and the chat endpoint."""

from fastapi.testclient import TestClient

from app.ai.agents.registry import Planner
from app.ai.os.confidence import compute_confidence, confidence_label
from app.services.retrieval import Citation


def test_planner_routes_by_intent() -> None:
    p = Planner()
    assert p.plan("What is the root cause of the pump failure?").key == "rca"
    assert p.plan("Are we compliant with OISD standards?").key == "compliance"
    assert p.plan("Summarize this document").key == "document"
    assert p.plan("Tell me about equipment P-101").key == "knowledge"


def test_confidence_scales_with_evidence() -> None:
    none = compute_confidence([])
    assert none == 0.0 and confidence_label(none) == "low"

    strong = compute_confidence(
        [Citation("c1", "d1", 1, "t", 5.0), Citation("c2", "d1", 1, "t", 4.0)]
    )
    assert strong > none


def _token(client: TestClient) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme",
            "email": "cop@acme.example.com",
            "full_name": "Copilot Tester",
            "password": "supersecret1",
        },
    )
    return resp.json()["tokens"]["access_token"]


def test_agents_listed(client: TestClient) -> None:
    token = _token(client)
    resp = client.get("/api/v1/agents", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    keys = {a["key"] for a in resp.json()}
    assert {"knowledge", "maintenance", "compliance", "rca", "lessons", "document"} <= keys


def test_chat_returns_cited_answer(client: TestClient) -> None:
    token = _token(client)
    auth = {"Authorization": f"Bearer {token}"}

    content = b"Pump P-101 seal failed due to dry running during startup per OISD-STD-105."
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
        "/api/v1/chat",
        headers=auth,
        json={"message": "What is the root cause of the pump seal failure?"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["agent"] == "rca"  # planner routed to RCA
    assert body["answer"]
    assert body["citations"]
    assert 0.0 <= body["confidence"] <= 1.0
