"""Project ORM model (organization-scoped)."""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, OrgScopedMixin, TimestampMixin, UUIDMixin
from app.models.enums import ProjectStatus


class Project(UUIDMixin, OrgScopedMixin, TimestampMixin, Base):
    """A unit of work grouping documents and analysis."""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=ProjectStatus.PLANNING.value
    )
