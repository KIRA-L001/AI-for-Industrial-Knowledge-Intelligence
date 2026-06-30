"""Document intelligence: chunking, entity/relationship extraction, summary.

Consumes extracted pages (Phase 5) and produces retrievable chunks plus a
knowledge graph of entities and relationships, advancing the document toward
the `extracted` → graphed/embedded stages. Entities are upserted per org so the
graph accumulates across documents.
"""

from __future__ import annotations

import uuid

from app.ai.chunking import chunk_text
from app.ai.extraction import ExtractionStrategy, get_extractor
from app.core.logging import get_logger
from app.models.knowledge import Chunk, Entity, Relationship
from app.repositories.document import DocumentPageRepository, DocumentRepository
from app.repositories.knowledge import (
    ChunkRepository,
    EntityRepository,
    RelationshipRepository,
)

logger = get_logger("kira.intelligence")

SUMMARY_MAX_CHARS = 600


class IntelligenceService:
    """Builds chunks + entity/relationship graph from a processed document."""

    def __init__(
        self,
        documents: DocumentRepository,
        pages: DocumentPageRepository,
        chunks: ChunkRepository,
        entities: EntityRepository,
        relationships: RelationshipRepository,
        extractor: ExtractionStrategy | None = None,
    ) -> None:
        self.documents = documents
        self.pages = pages
        self.chunks = chunks
        self.entities = entities
        self.relationships = relationships
        self.extractor = extractor or get_extractor()

    async def analyze(self, organization_id: uuid.UUID, document_id: uuid.UUID) -> dict[str, int]:
        document = await self.documents.get_for_org(document_id, organization_id)
        if document is None:
            raise ValueError("Document not found.")

        pages = await self.pages.list_for_document(document_id)
        full_text = "\n\n".join(p.text for p in pages)

        # 1) Chunking (re-run idempotently).
        await self.chunks.delete_for_document(document_id)
        chunk_count = 0
        next_index = 0
        for page in pages:
            for tc in chunk_text(page.text, page.page_number, start_index=next_index):
                await self.chunks.add(
                    Chunk(
                        organization_id=organization_id,
                        document_id=document_id,
                        page_number=tc.page_number,
                        chunk_index=tc.index,
                        text=tc.text,
                        char_start=tc.char_start,
                        char_end=tc.char_end,
                    )
                )
                next_index = tc.index + 1
                chunk_count += 1

        # 2) Entity + relationship extraction with per-org upsert.
        result = self.extractor.extract(full_text)
        norm_to_id: dict[str, uuid.UUID] = {}
        for ent in result.entities:
            existing = await self.entities.get_by_normalized(
                organization_id, ent.normalized, ent.entity_type
            )
            if existing is None:
                existing = await self.entities.add(
                    Entity(
                        organization_id=organization_id,
                        name=ent.name,
                        entity_type=ent.entity_type,
                        normalized=ent.normalized,
                        document_id=document_id,
                    )
                )
            norm_to_id[ent.normalized] = existing.id

        rel_count = 0
        for rel in result.relationships:
            src = norm_to_id.get(rel.source)
            tgt = norm_to_id.get(rel.target)
            if src is None or tgt is None:
                continue
            await self.relationships.add(
                Relationship(
                    organization_id=organization_id,
                    source_entity_id=src,
                    target_entity_id=tgt,
                    rel_type=rel.rel_type,
                )
            )
            rel_count += 1

        # 3) Summary (heuristic; LLM-backed summarizer wired in Phase 10).
        document.summary = full_text.strip()[:SUMMARY_MAX_CHARS] or None
        await self.documents.add(document)

        logger.info(
            "analyzed",
            document_id=str(document_id),
            chunks=chunk_count,
            entities=len(result.entities),
            relationships=rel_count,
        )
        return {
            "chunks": chunk_count,
            "entities": len(result.entities),
            "relationships": rel_count,
        }
