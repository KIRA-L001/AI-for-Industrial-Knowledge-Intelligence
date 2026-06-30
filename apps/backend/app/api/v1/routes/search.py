"""Embedding + semantic search endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_embedding_service, require_role
from app.core.security import Role
from app.schemas.search import (
    EmbedResult,
    SearchHitOut,
    SearchRequest,
    SearchResponse,
)
from app.services.embedding import EmbeddingService

router = APIRouter(tags=["search"])

Embedding = Annotated[EmbeddingService, Depends(get_embedding_service)]
Engineer = Depends(require_role(Role.ENGINEER))


@router.post(
    "/documents/{document_id}/embed", response_model=EmbedResult, dependencies=[Engineer]
)
async def embed_document(
    document_id: uuid.UUID, user: CurrentUser, service: Embedding
) -> EmbedResult:
    """Index the document's chunks into the vector store."""
    count = await service.embed_document(user.organization_id, document_id)
    return EmbedResult(embedded_chunks=count)


@router.post("/search", response_model=SearchResponse)
async def search(
    payload: SearchRequest, user: CurrentUser, service: Embedding
) -> SearchResponse:
    """Semantic search over the organization's indexed chunks."""
    hits = await service.search(
        user.organization_id,
        payload.query,
        limit=payload.limit,
        document_id=payload.document_id,
    )
    return SearchResponse(
        query=payload.query,
        hits=[
            SearchHitOut(
                chunk_id=h.payload.get("chunk_id", h.id),
                document_id=h.payload.get("document_id", ""),
                page_number=h.payload.get("page_number"),
                score=h.score,
                text=h.payload.get("text", ""),
            )
            for h in hits
        ],
    )
