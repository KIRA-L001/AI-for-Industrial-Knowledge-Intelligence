"""ORM models package.

Importing this package imports every model module so that `Base.metadata`
is fully populated for Alembic autogenerate. Add new models here as phases land.
"""

from app.db.base import Base
from app.models.document import Document
from app.models.document_page import DocumentPage
from app.models.equipment import Equipment
from app.models.knowledge import Chunk, Entity, Relationship
from app.models.organization import Organization
from app.models.plant import Department, Plant
from app.models.project import Project
from app.models.user import User

__all__ = [
    "Base",
    "Chunk",
    "Department",
    "Document",
    "DocumentPage",
    "Entity",
    "Equipment",
    "Organization",
    "Plant",
    "Project",
    "Relationship",
    "User",
]
