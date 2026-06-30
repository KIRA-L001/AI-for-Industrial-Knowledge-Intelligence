"""Search request/response schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class EmbedResult(BaseModel):
    embedded_chunks: int


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=10, ge=1, le=50)
    document_id: uuid.UUID | None = None


class SearchHitOut(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int | None = None
    score: float
    text: str


class SearchResponse(BaseModel):
    query: str
    hits: list[SearchHitOut]
