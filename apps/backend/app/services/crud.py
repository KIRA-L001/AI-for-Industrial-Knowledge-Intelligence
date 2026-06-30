"""Generic organization-scoped CRUD service.

Wraps an OrgScopedRepository to provide create/get/list/update/delete with
tenant isolation and consistent not-found handling, so per-entity routers
stay thin and free of duplicated logic.
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from app.core.errors import NotFoundError
from app.db.base import Base
from app.repositories.base import OrgScopedRepository

ModelT = TypeVar("ModelT", bound=Base)


class CrudService(Generic[ModelT]):
    """Reusable CRUD use-cases over a tenant-scoped repository."""

    def __init__(self, repo: OrgScopedRepository[ModelT], entity_name: str) -> None:
        self.repo = repo
        self.entity_name = entity_name

    async def create(self, organization_id: uuid.UUID, data: dict[str, Any]) -> ModelT:
        entity = self.repo.model(organization_id=organization_id, **data)
        return await self.repo.add(entity)

    async def get(self, organization_id: uuid.UUID, entity_id: uuid.UUID) -> ModelT:
        entity = await self.repo.get_for_org(entity_id, organization_id)
        if entity is None:
            raise NotFoundError(f"{self.entity_name} not found.")
        return entity

    async def list(
        self,
        organization_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[ModelT], int]:
        """Return (items, total) for the org; routers wrap into a typed Page."""
        items = await self.repo.list_for_org(
            organization_id, limit=limit, offset=offset, filters=filters
        )
        total = await self.repo.count_for_org(organization_id, filters=filters)
        return list(items), total

    async def update(
        self, organization_id: uuid.UUID, entity_id: uuid.UUID, data: dict[str, Any]
    ) -> ModelT:
        entity = await self.get(organization_id, entity_id)
        for key, value in data.items():
            setattr(entity, key, value)
        return await self.repo.add(entity)

    async def delete(self, organization_id: uuid.UUID, entity_id: uuid.UUID) -> None:
        deleted = await self.repo.delete_for_org(entity_id, organization_id)
        if not deleted:
            raise NotFoundError(f"{self.entity_name} not found.")
