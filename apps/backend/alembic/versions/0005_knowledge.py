"""knowledge: chunks, entities, relationships + document summary

Revision ID: 0005_knowledge
Revises: 0004_document_pages
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0005_knowledge"
down_revision: str | None = "0004_document_pages"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _ts() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.add_column("documents", sa.Column("summary", sa.Text(), nullable=True))

    op.create_table(
        "chunks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", UUID(as_uuid=True), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("char_start", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("char_end", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("embedded", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_ts(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chunks_organization_id", "chunks", ["organization_id"])
    op.create_index("ix_chunks_document_id", "chunks", ["document_id"])

    op.create_table(
        "entities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("normalized", sa.String(length=512), nullable=False),
        sa.Column("document_id", UUID(as_uuid=True), nullable=True),
        *_ts(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("organization_id", "normalized", "entity_type", name="uq_entity_norm"),
    )
    op.create_index("ix_entities_organization_id", "entities", ["organization_id"])
    op.create_index("ix_entities_entity_type", "entities", ["entity_type"])
    op.create_index("ix_entities_normalized", "entities", ["normalized"])
    op.create_index("ix_entities_document_id", "entities", ["document_id"])

    op.create_table(
        "relationships",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", UUID(as_uuid=True), nullable=False),
        sa.Column("source_entity_id", UUID(as_uuid=True), nullable=False),
        sa.Column("target_entity_id", UUID(as_uuid=True), nullable=False),
        sa.Column("rel_type", sa.String(length=64), nullable=False),
        *_ts(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_entity_id"], ["entities.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_relationships_organization_id", "relationships", ["organization_id"])
    op.create_index("ix_relationships_source_entity_id", "relationships", ["source_entity_id"])
    op.create_index("ix_relationships_target_entity_id", "relationships", ["target_entity_id"])


def downgrade() -> None:
    op.drop_table("relationships")
    op.drop_table("entities")
    op.drop_table("chunks")
    op.drop_column("documents", "summary")
