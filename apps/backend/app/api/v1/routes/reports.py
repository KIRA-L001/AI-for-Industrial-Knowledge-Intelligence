"""Report generation endpoints (PDF export)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession
from app.services.analytics import AnalyticsService
from app.services.reports import REPORT_TITLES, ReportService, ReportType

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportRequest(BaseModel):
    report_type: ReportType


def get_report_service(db: DbSession) -> ReportService:
    return ReportService(AnalyticsService(db))


Reports = Annotated[ReportService, Depends(get_report_service)]


@router.get("/types")
async def list_report_types(_: CurrentUser) -> list[dict[str, str]]:
    return [{"key": k, "title": v} for k, v in REPORT_TITLES.items()]


@router.post("/generate")
async def generate_report(
    payload: ReportRequest, user: CurrentUser, service: Reports
) -> StreamingResponse:
    """Generate a PDF report and return it as a download."""
    pdf = await service.generate_pdf(
        user.organization_id, payload.report_type, generated_by=user.email
    )
    filename = f"kira-{payload.report_type}-report.pdf"
    return StreamingResponse(
        iter([pdf]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
