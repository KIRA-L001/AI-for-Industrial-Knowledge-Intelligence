"""Equipment ORM model (organization-scoped, optionally under a plant)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, OrgScopedMixin, TimestampMixin, UUIDMixin
from app.db.types import GUID
from app.models.enums import Criticality, EquipmentStatus

if TYPE_CHECKING:
    from app.models.plant import Plant


class Equipment(UUIDMixin, OrgScopedMixin, TimestampMixin, Base):
    """An industrial asset (pump, vessel, compressor, ...)."""

    __tablename__ = "equipment"

    tag: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    equipment_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=EquipmentStatus.OPERATIONAL.value
    )
    criticality: Mapped[str] = mapped_column(
        String(32), nullable=False, default=Criticality.MEDIUM.value
    )

    plant_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("plants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    plant: Mapped[Plant | None] = relationship(back_populates="equipment")
