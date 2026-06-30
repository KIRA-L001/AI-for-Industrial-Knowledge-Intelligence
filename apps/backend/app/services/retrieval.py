"""Hybrid retrieval service.

Fuses semantic (vector), keyword (SQL LIKE), and metadata signals via Reciprocal
Rank Fusion, reranks the merged candidates with a cross-encoder (or lexical
fallback), and builds a citation-tagged context block for the AI layer. Every
returned passage carries its chunk/document/page provenance.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field

from app.ai.rerank import Reranker, get_reranker
from app.repositories.knowledge import ChunkRepository
from app.services.embedding import EmbeddingService

_WORD_RE = re.compile(r"[A-Za-z0-9]{3,}")
RRF_K = 60  # Reciprocal Rank Fusion constant.


@dataclass
class Citation:
    chunk_id: str
    document_id: str
    page_number: int | None
    text: str
    score: float


@dataclass
class RetrievalResult:
    query: str
    context: str
    citations: list[Citation] = field(default_factory=list)


def _keywords(query: str) -> list[str]:
    seen: list[str] = []
    for token in _WORD_RE.findall(query.lower()):
        if token not in seen:
            seen.append(token)
    return seen[:10]


class RetrievalService:
    """Produces a reranked, citation-backed context for a query."""

    def __init__(
        self,
        embedding: EmbeddingService,
        chunks: ChunkRepository,
        reranker: Reranker | None = None,
    ) -> None:
        self.embedding = embedding
        self.chunks = chunks
        self.reranker = reranker or get_reranker()

    async def retrieve(
        self,
        organization_id: uuid.UUID,
        query: str,
        *,
        limit: int = 6,
        candidate_pool: int = 20,
    ) -> RetrievalResult:
        # --- 1) semantic candidates ---
        semantic = await self.embedding.search(
            organization_id, query, limit=candidate_pool
        )
        # candidate registry: id -> {text, document_id, page}
        registry: dict[str, dict[str, object]] = {}
        ranks: dict[str, list[int]] = {}

        for rank, hit in enumerate(semantic):
            cid = hit.payload.get("chunk_id", hit.id)
            registry[cid] = {
                "text": hit.payload.get("text", ""),
                "document_id": hit.payload.get("document_id", ""),
                "page_number": hit.payload.get("page_number"),
            }
            ranks.setdefault(cid, []).append(rank)

        # --- 2) keyword candidates ---
        keyword_rows = await self.chunks.keyword_search(
            organization_id, _keywords(query), limit=candidate_pool
        )
        for rank, chunk in enumerate(keyword_rows):
            cid = str(chunk.id)
            registry.setdefault(
                cid,
                {
                    "text": chunk.text,
                    "document_id": str(chunk.document_id),
                    "page_number": chunk.page_number,
                },
            )
            ranks.setdefault(cid, []).append(rank)

        if not registry:
            return RetrievalResult(query=query, context="", citations=[])

        # --- 3) Reciprocal Rank Fusion ---
        fused = {
            cid: sum(1.0 / (RRF_K + r) for r in rs) for cid, rs in ranks.items()
        }
        ordered = sorted(fused, key=lambda c: fused[c], reverse=True)[:candidate_pool]

        # --- 4) cross-encoder rerank ---
        passages = [str(registry[c]["text"]) for c in ordered]
        rerank_scores = self.reranker.score(query, passages)
        reranked = sorted(
            zip(ordered, rerank_scores, strict=True), key=lambda x: x[1], reverse=True
        )[:limit]

        # --- 5) build citations + context block ---
        citations: list[Citation] = []
        context_parts: list[str] = []
        for idx, (cid, score) in enumerate(reranked, start=1):
            meta = registry[cid]
            text = str(meta["text"])
            citations.append(
                Citation(
                    chunk_id=cid,
                    document_id=str(meta["document_id"]),
                    page_number=meta["page_number"],  # type: ignore[arg-type]
                    text=text,
                    score=float(score),
                )
            )
            context_parts.append(f"[{idx}] {text}")

        return RetrievalResult(
            query=query, context="\n\n".join(context_parts), citations=citations
        )
