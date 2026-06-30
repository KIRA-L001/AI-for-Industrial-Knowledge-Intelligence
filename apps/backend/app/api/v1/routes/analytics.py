"""Analytics endpoints for the dashboard."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DbSession
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(db: DbSession) -> AnalyticsService:
    return AnalyticsService(db)


Analytics = Annotated[AnalyticsService, Depends(get_analytics_service)]


@router.get("/overview")
async def analytics_overview(user: CurrentUser, service: Analytics) -> dict[str, object]:
    """KPI counts and categorical distributions for the organization."""
    return await service.overview(user.organization_id)
