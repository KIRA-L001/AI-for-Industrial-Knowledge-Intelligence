"""Report generation service: renders organization reports to PDF (reportlab).

Supports the five report types from the spec (maintenance, compliance,
executive, knowledge, RCA). Content is assembled from analytics + knowledge
aggregates and rendered to a PDF byte stream for download.
"""

from __future__ import annotations

import io
import uuid
from datetime import UTC, datetime
from typing import Literal

from app.services.analytics import AnalyticsService

ReportType = Literal["maintenance", "compliance", "executive", "knowledge", "rca"]

REPORT_TITLES: dict[str, str] = {
    "maintenance": "Maintenance Intelligence Report",
    "compliance": "Compliance Status Report",
    "executive": "Executive Summary Report",
    "knowledge": "Knowledge Base Report",
    "rca": "Root Cause Analysis Report",
}


class ReportService:
    """Builds PDF reports from organization data."""

    def __init__(self, analytics: AnalyticsService) -> None:
        self.analytics = analytics

    async def generate_pdf(
        self, organization_id: uuid.UUID, report_type: ReportType, *, generated_by: str
    ) -> bytes:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        overview = await self.analytics.overview(organization_id)
        kpis: dict[str, int] = overview["kpis"]  # type: ignore[assignment]

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, title=REPORT_TITLES[report_type])
        styles = getSampleStyleSheet()
        story: list[object] = []

        story.append(Paragraph(f"KIRA — {REPORT_TITLES[report_type]}", styles["Title"]))
        story.append(
            Paragraph(
                f"Generated {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')} by {generated_by}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 18))

        story.append(Paragraph("Key Metrics", styles["Heading2"]))
        kpi_rows = [["Metric", "Count"], *[[k.title(), str(v)] for k, v in kpis.items()]]
        table = Table(kpi_rows, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 18))

        story.append(Paragraph("Distributions", styles["Heading2"]))
        for label, key in (
            ("Equipment by status", "equipment_status"),
            ("Equipment by criticality", "equipment_criticality"),
            ("Documents by status", "document_status"),
        ):
            dist: dict[str, int] = overview[key]  # type: ignore[assignment]
            story.append(Paragraph(label, styles["Heading3"]))
            if dist:
                rows = [["Category", "Count"], *[[k, str(v)] for k, v in dist.items()]]
                t = Table(rows, hAlign="LEFT")
                t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
                story.append(t)
            else:
                story.append(Paragraph("No data.", styles["Normal"]))
            story.append(Spacer(1, 10))

        doc.build(story)
        return buffer.getvalue()
