"""Document intelligence endpoints: analyze, chunks, entities."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    CurrentUser,
    get_chunk_repository,
    get_entity_repository,
    get_intelligence_service,
    require_role,
)
from app.core.security import Role
from app.repositories.knowledge import ChunkRepository, EntityRepository
from app.schemas.common import Page
from app.schemas.knowledge import AnalyzeResult, ChunkOut, EntityOut
from app.services.intelligence import IntelligenceService

router = APIRouter(tags=["knowledge"])

Intelligence = Annotated[IntelligenceService, Depends(get_intelligence_service)]
Entities = Annotated[EntityRepository, Depends(get_entity_repository)]
Chunks = Annotated[ChunkRepository, Depends(get_chunk_repository)]
Engineer = Depends(require_role(Role.ENGINEER))


@router.post(
    "/documents/{document_id}/analyze", response_model=AnalyzeResult, dependencies=[Engineer]
)
async def analyze_document(
    document_id: uuid.UUID, user: CurrentUser, service: Intelligence
) -> AnalyzeResult:
    """Chunk the document and extract its entity/relationship graph."""
    result = await service.analyze(user.organization_id, document_id)
    return AnalyzeResult(**result)


@router.get("/documents/{document_id}/chunks", response_model=list[ChunkOut])
async def list_document_chunks(
    document_id: uuid.UUID, user: CurrentUser, chunks: Chunks
) -> list[ChunkOut]:
    rows = await chunks.list_for_document(document_id)
    # Tenant guard: only return chunks for the caller's org.
    return [
        ChunkOut.model_validate(c) for c in rows if c.organization_id == user.organization_id
    ]


@router.get("/entities", response_model=Page[EntityOut])
async def list_entities(
    user: CurrentUser,
    entities: Entities,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[EntityOut]:
    items = await entities.list_for_org(user.organization_id, limit=limit, offset=offset)
    total = await entities.count_for_org(user.organization_id)
    return Page(
        items=[EntityOut.model_validate(e) for e in items],
        total=total,
        limit=limit,
        offset=offset,
    )
