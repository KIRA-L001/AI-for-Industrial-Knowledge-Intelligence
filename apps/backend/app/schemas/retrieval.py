"""Retrieval response schemas."""

from __future__ import annotations

from pydantic import BaseModel


class CitationOut(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int | None
    text: str
    score: float


class RetrievalResponse(BaseModel):
    query: str
    context: str
    citations: list[CitationOut]
