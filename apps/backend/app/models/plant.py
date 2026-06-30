"""Plant and Department ORM models (organization-scoped)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, OrgScopedMixin, TimestampMixin, UUIDMixin
from app.db.types import GUID

if TYPE_CHECKING:
    from app.models.equipment import Equipment


class Plant(UUIDMixin, OrgScopedMixin, TimestampMixin, Base):
    """A physical industrial plant/site within an organization."""

    __tablename__ = "plants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    departments: Mapped[list[Department]] = relationship(
        back_populates="plant", cascade="all, delete-orphan"
    )
    equipment: Mapped[list[Equipment]] = relationship(back_populates="plant")


class Department(UUIDMixin, OrgScopedMixin, TimestampMixin, Base):
    """A department/unit within a plant."""

    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plant: Mapped[Plant] = relationship(back_populates="departments")
