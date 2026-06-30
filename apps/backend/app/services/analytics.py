"""Analytics service: organization-scoped aggregates for the dashboard.

Computes KPI counts and categorical distributions with grouped COUNT queries so
the dashboard renders real data (no client-side scanning).
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.equipment import Equipment
from app.models.knowledge import Entity
from app.models.project import Project


class AnalyticsService:
    """Read-only aggregate queries scoped to an organization."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _count(self, model: type, organization_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(model).where(
                model.organization_id == organization_id  # type: ignore[attr-defined]
            )
        )
        return int(result.scalar_one())

    async def _distribution(
        self, model: type, field: str, organization_id: uuid.UUID
    ) -> dict[str, int]:
        column = getattr(model, field)
        result = await self.session.execute(
            select(column, func.count())
            .where(model.organization_id == organization_id)  # type: ignore[attr-defined]
            .group_by(column)
        )
        return {str(key): int(count) for key, count in result.all()}

    async def overview(self, organization_id: uuid.UUID) -> dict[str, object]:
        return {
            "kpis": {
                "documents": await self._count(Document, organization_id),
                "equipment": await self._count(Equipment, organization_id),
                "projects": await self._count(Project, organization_id),
                "entities": await self._count(Entity, organization_id),
            },
            "document_status": await self._distribution(
                Document, "status", organization_id
            ),
            "equipment_status": await self._distribution(
                Equipment, "status", organization_id
            ),
            "equipment_criticality": await self._distribution(
                Equipment, "criticality", organization_id
            ),
        }
