"""catalog: plants, departments, projects, equipment

Revision ID: 0002_catalog
Revises: 0001_initial_auth
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0002_catalog"
down_revision: str | None = "0001_initial_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _org_fk() -> sa.Column:
    return sa.Column("organization_id", UUID(as_uuid=True), nullable=False)


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "plants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        _org_fk(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_plants_organization_id", "plants", ["organization_id"])

    op.create_table(
        "departments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        _org_fk(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("plant_id", UUID(as_uuid=True), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_departments_organization_id", "departments", ["organization_id"])
    op.create_index("ix_departments_plant_id", "departments", ["plant_id"])

    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        _org_fk(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planning"),
        *_timestamps(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_projects_organization_id", "projects", ["organization_id"])

    op.create_table(
        "equipment",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        _org_fk(),
        sa.Column("tag", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("equipment_type", sa.String(length=128), nullable=True),
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="operational"),
        sa.Column("criticality", sa.String(length=32), nullable=False, server_default="medium"),
        sa.Column("plant_id", UUID(as_uuid=True), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_equipment_organization_id", "equipment", ["organization_id"])
    op.create_index("ix_equipment_tag", "equipment", ["tag"])
    op.create_index("ix_equipment_plant_id", "equipment", ["plant_id"])


def downgrade() -> None:
    op.drop_table("equipment")
    op.drop_table("projects")
    op.drop_table("departments")
    op.drop_table("plants")
