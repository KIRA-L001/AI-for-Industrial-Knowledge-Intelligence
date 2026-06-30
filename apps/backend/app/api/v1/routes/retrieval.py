"""Hybrid retrieval endpoint: fused, reranked, citation-backed context."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_retrieval_service
from app.schemas.retrieval import CitationOut, RetrievalResponse
from app.schemas.search import SearchRequest
from app.services.retrieval import RetrievalService

router = APIRouter(tags=["retrieval"])

Retrieval = Annotated[RetrievalService, Depends(get_retrieval_service)]


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve(
    payload: SearchRequest, user: CurrentUser, service: Retrieval
) -> RetrievalResponse:
    """Hybrid retrieval (semantic + keyword + rerank) returning cited context."""
    result = await service.retrieve(
        user.organization_id, payload.query, limit=payload.limit
    )
    return RetrievalResponse(
        query=result.query,
        context=result.context,
        citations=[
            CitationOut(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                page_number=c.page_number,
                text=c.text,
                score=c.score,
            )
            for c in result.citations
        ],
    )
