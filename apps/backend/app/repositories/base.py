"""Generic async repository implementing common CRUD over SQLAlchemy models.

Concrete repositories subclass `BaseRepository[Model]` and add query methods.
This keeps data-access logic out of services and routes (Repository pattern).
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Reusable async data-access object for a single ORM model."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, entity_id: uuid.UUID) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> Sequence[ModelT]:
        stmt = select(self.model)
        for field, value in (filters or {}).items():
            stmt = stmt.where(getattr(self.model, field) == value)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        for field, value in (filters or {}).items():
            stmt = stmt.where(getattr(self.model, field) == value)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        )


class OrgScopedRepository(BaseRepository[ModelT]):
    """Repository for tenant-owned models; every query is filtered by org.

    Guarantees a user can only read/mutate rows in their own organization.
    """

    async def get_for_org(
        self, entity_id: uuid.UUID, organization_id: uuid.UUID
    ) -> ModelT | None:
        stmt = select(self.model).where(
            self.model.id == entity_id,  # type: ignore[attr-defined]
            self.model.organization_id == organization_id,  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_org(
        self,
        organization_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> Sequence[ModelT]:
        merged = {"organization_id": organization_id, **(filters or {})}
        return await self.list(limit=limit, offset=offset, filters=merged)

    async def count_for_org(
        self, organization_id: uuid.UUID, filters: dict[str, Any] | None = None
    ) -> int:
        merged = {"organization_id": organization_id, **(filters or {})}
        return await self.count(merged)

    async def delete_for_org(
        self, entity_id: uuid.UUID, organization_id: uuid.UUID
    ) -> bool:
        entity = await self.get_for_org(entity_id, organization_id)
        if entity is None:
            return False
        await self.session.delete(entity)
        return True
