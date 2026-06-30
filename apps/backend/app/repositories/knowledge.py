"""Data access for chunks, entities, and relationships."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import delete, or_, select

from app.models.knowledge import Chunk, Entity, Relationship
from app.repositories.base import OrgScopedRepository


class ChunkRepository(OrgScopedRepository[Chunk]):
    model = Chunk

    async def delete_for_document(self, document_id: uuid.UUID) -> None:
        await self.session.execute(delete(Chunk).where(Chunk.document_id == document_id))

    async def list_for_document(self, document_id: uuid.UUID) -> Sequence[Chunk]:
        result = await self.session.execute(
            select(Chunk).where(Chunk.document_id == document_id).order_by(Chunk.chunk_index)
        )
        return result.scalars().all()

    async def keyword_search(
        self, organization_id: uuid.UUID, terms: list[str], *, limit: int = 20
    ) -> Sequence[Chunk]:
        """Case-insensitive LIKE search over chunk text for the given terms.

        Portable across PostgreSQL and SQLite (uses ILIKE-equivalent ``ilike``).
        """
        if not terms:
            return []
        stmt = select(Chunk).where(Chunk.organization_id == organization_id)
        conditions = [Chunk.text.ilike(f"%{t}%") for t in terms]
        stmt = stmt.where(or_(*conditions)).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class EntityRepository(OrgScopedRepository[Entity]):
    model = Entity

    async def get_by_normalized(
        self, organization_id: uuid.UUID, normalized: str, entity_type: str
    ) -> Entity | None:
        result = await self.session.execute(
            select(Entity).where(
                Entity.organization_id == organization_id,
                Entity.normalized == normalized,
                Entity.entity_type == entity_type,
            )
        )
        return result.scalar_one_or_none()


class RelationshipRepository(OrgScopedRepository[Relationship]):
    model = Relationship
