"""Embedding service: index chunks into the vector store and search them.

Embeds a document's chunks (Phase 6 output) and upserts them with tenant +
source metadata so semantic search can filter by organization and document.
Marks chunks as embedded so re-runs are cheap.
"""

from __future__ import annotations

import uuid

from app.ai.embeddings import EmbeddingProvider
from app.ai.vectorstore import SearchHit, VectorPoint, VectorStore
from app.core.logging import get_logger
from app.repositories.knowledge import ChunkRepository

logger = get_logger("kira.embedding")


class EmbeddingService:
    """Indexes and searches chunk embeddings."""

    def __init__(
        self,
        chunks: ChunkRepository,
        embedder: EmbeddingProvider,
        store: VectorStore,
    ) -> None:
        self.chunks = chunks
        self.embedder = embedder
        self.store = store

    async def embed_document(
        self, organization_id: uuid.UUID, document_id: uuid.UUID
    ) -> int:
        rows = await self.chunks.list_for_document(document_id)
        rows = [c for c in rows if c.organization_id == organization_id]
        if not rows:
            return 0

        self.store.ensure_collection(self.embedder.dim)
        vectors = self.embedder.embed([c.text for c in rows])
        points = [
            VectorPoint(
                id=str(chunk.id),
                vector=vector,
                payload={
                    "organization_id": str(organization_id),
                    "document_id": str(document_id),
                    "chunk_id": str(chunk.id),
                    "page_number": chunk.page_number,
                    "text": chunk.text,
                },
            )
            for chunk, vector in zip(rows, vectors, strict=True)
        ]
        self.store.upsert(points)

        for chunk in rows:
            chunk.embedded = True
            await self.chunks.add(chunk)

        logger.info("embedded", document_id=str(document_id), chunks=len(points))
        return len(points)

    async def search(
        self,
        organization_id: uuid.UUID,
        query: str,
        *,
        limit: int = 10,
        document_id: uuid.UUID | None = None,
    ) -> list[SearchHit]:
        self.store.ensure_collection(self.embedder.dim)
        vector = self.embedder.embed_one(query)
        filters: dict[str, object] = {"organization_id": str(organization_id)}
        if document_id is not None:
            filters["document_id"] = str(document_id)
        return self.store.search(vector, limit=limit, filters=filters)
