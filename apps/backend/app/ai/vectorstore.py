"""Vector store abstraction with Qdrant and in-memory implementations.

`VectorStore` is the surface the embedding/retrieval services depend on. Points
carry org_id/document_id/chunk metadata so search can filter by tenant and
source. `InMemoryVectorStore` provides exact cosine search for tests; the
Qdrant store backs production.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Protocol

from app.core.config import get_settings


@dataclass
class VectorPoint:
    id: str
    vector: list[float]
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    id: str
    score: float
    payload: dict[str, Any]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class VectorStore(Protocol):
    def ensure_collection(self, dim: int) -> None: ...

    def upsert(self, points: list[VectorPoint]) -> None: ...

    def search(
        self, vector: list[float], *, limit: int, filters: dict[str, Any] | None = None
    ) -> list[SearchHit]: ...

    def delete_by_filter(self, filters: dict[str, Any]) -> None: ...


class InMemoryVectorStore:
    """Exact cosine-similarity store for tests/offline use."""

    def __init__(self) -> None:
        self._points: dict[str, VectorPoint] = {}

    def ensure_collection(self, dim: int) -> None:  # noqa: D401 - no-op for memory
        return None

    def upsert(self, points: list[VectorPoint]) -> None:
        for p in points:
            self._points[p.id] = p

    @staticmethod
    def _matches(payload: dict[str, Any], filters: dict[str, Any] | None) -> bool:
        if not filters:
            return True
        return all(payload.get(k) == v for k, v in filters.items())

    def search(
        self, vector: list[float], *, limit: int, filters: dict[str, Any] | None = None
    ) -> list[SearchHit]:
        scored = [
            SearchHit(id=p.id, score=_cosine(vector, p.vector), payload=p.payload)
            for p in self._points.values()
            if self._matches(p.payload, filters)
        ]
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:limit]

    def delete_by_filter(self, filters: dict[str, Any]) -> None:
        to_delete = [
            pid for pid, p in self._points.items() if self._matches(p.payload, filters)
        ]
        for pid in to_delete:
            self._points.pop(pid, None)


class QdrantVectorStore:
    """Qdrant-backed vector store (production)."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._collection = self._settings.qdrant_collection

    @property
    def _client(self):  # type: ignore[no-untyped-def]
        from app.infra.clients import get_qdrant

        return get_qdrant()

    def ensure_collection(self, dim: int) -> None:
        from qdrant_client.models import Distance, VectorParams

        client = self._client
        existing = {c.name for c in client.get_collections().collections}
        if self._collection not in existing:
            client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(self, points: list[VectorPoint]) -> None:
        from qdrant_client.models import PointStruct

        self._client.upsert(
            collection_name=self._collection,
            points=[
                PointStruct(id=p.id, vector=p.vector, payload=p.payload) for p in points
            ],
        )

    def search(
        self, vector: list[float], *, limit: int, filters: dict[str, Any] | None = None
    ) -> list[SearchHit]:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        q_filter = None
        if filters:
            q_filter = Filter(
                must=[
                    FieldCondition(key=k, match=MatchValue(value=v))
                    for k, v in filters.items()
                ]
            )
        results = self._client.search(
            collection_name=self._collection,
            query_vector=vector,
            limit=limit,
            query_filter=q_filter,
        )
        return [
            SearchHit(id=str(r.id), score=float(r.score), payload=dict(r.payload or {}))
            for r in results
        ]

    def delete_by_filter(self, filters: dict[str, Any]) -> None:
        from qdrant_client.models import FieldCondition, Filter, FilterSelector, MatchValue

        self._client.delete(
            collection_name=self._collection,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(key=k, match=MatchValue(value=v))
                        for k, v in filters.items()
                    ]
                )
            ),
        )


@lru_cache
def get_vector_store() -> VectorStore:
    """Default vector store (Qdrant), cached as a singleton."""
    return QdrantVectorStore()
