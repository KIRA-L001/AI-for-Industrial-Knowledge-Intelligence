"""Schemas for document intelligence: analysis result, chunks, entities."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnalyzeResult(BaseModel):
    chunks: int
    entities: int
    relationships: int


class ChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    page_number: int
    chunk_index: int
    text: str
    embedded: bool


class EntityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    entity_type: str
    normalized: str
    document_id: uuid.UUID | None
    created_at: datetime
