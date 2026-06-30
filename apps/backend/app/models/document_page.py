"""DocumentPage ORM model: per-page extracted text and layout blocks."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import GUID

# Use JSONB on PostgreSQL, generic JSON elsewhere (SQLite tests).
JsonType = JSON().with_variant(JSONB(), "postgresql")


class DocumentPage(UUIDMixin, TimestampMixin, Base):
    """Extracted text for a single page, with optional layout blocks/bboxes.

    `blocks` holds a list of {text, bbox:[x0,y0,x1,y1], type} entries produced
    by layout analysis / OCR for citation provenance.
    """

    __tablename__ = "document_pages"

    document_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    blocks: Mapped[list | None] = mapped_column(JsonType, nullable=True)
