"""Knowledge models: chunks, entities, and relationships."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, OrgScopedMixin, TimestampMixin, UUIDMixin
from app.db.types import GUID


class Chunk(UUIDMixin, OrgScopedMixin, TimestampMixin, Base):
    """A retrievable text chunk derived from a document page."""

    __tablename__ = "chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    char_start: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    char_end: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Set once the chunk has been embedded into Qdrant (Phase 8).
    embedded: Mapped[bool] = mapped_column(default=False, nullable=False)


class Entity(UUIDMixin, OrgScopedMixin, TimestampMixin, Base):
    """A named industrial entity (equipment, standard, organization, ...)."""

    __tablename__ = "entities"
    __table_args__ = (
        UniqueConstraint("organization_id", "normalized", "entity_type", name="uq_entity_norm"),
    )

    name: Mapped[str] = mapped_column(String(512), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    normalized: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )


class Relationship(UUIDMixin, OrgScopedMixin, TimestampMixin, Base):
    """A directed relationship between two entities."""

    __tablename__ = "relationships"

    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rel_type: Mapped[str] = mapped_column(String(64), nullable=False)
