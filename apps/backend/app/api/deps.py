"""Shared FastAPI dependencies: DB session, repositories, services, auth guards."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Annotated, Any

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import ROLE_RANK, Role, decode_token
from app.db.session import get_db
from app.models.equipment import Equipment
from app.models.plant import Department, Plant
from app.models.project import Project
from app.models.user import User
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.crud import CrudService

if TYPE_CHECKING:
    from app.repositories.document import DocumentPageRepository
    from app.repositories.knowledge import ChunkRepository, EntityRepository
    from app.services.copilot import CopilotService
    from app.services.document import DocumentService
    from app.services.embedding import EmbeddingService
    from app.services.graph import GraphService
    from app.services.intelligence import IntelligenceService
    from app.services.processing import DocumentProcessingService
    from app.services.retrieval import RetrievalService

DbSession = Annotated[AsyncSession, Depends(get_db)]

_bearer = HTTPBearer(auto_error=False)


# --- repositories / services ------------------------------------------
def get_user_repository(db: DbSession) -> UserRepository:
    return UserRepository(db)


def get_org_repository(db: DbSession) -> OrganizationRepository:
    return OrganizationRepository(db)


def get_auth_service(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    orgs: Annotated[OrganizationRepository, Depends(get_org_repository)],
) -> AuthService:
    return AuthService(users, orgs)


# --- catalog CRUD services (plant/department/project/equipment) --------
def get_plant_service(db: DbSession) -> CrudService[Plant]:
    from app.repositories.catalog import PlantRepository

    return CrudService(PlantRepository(db), "Plant")


def get_department_service(db: DbSession) -> CrudService[Department]:
    from app.repositories.catalog import DepartmentRepository

    return CrudService(DepartmentRepository(db), "Department")


def get_project_service(db: DbSession) -> CrudService[Project]:
    from app.repositories.catalog import ProjectRepository

    return CrudService(ProjectRepository(db), "Project")


def get_equipment_service(db: DbSession) -> CrudService[Equipment]:
    from app.repositories.catalog import EquipmentRepository

    return CrudService(EquipmentRepository(db), "Equipment")


def get_document_service(db: DbSession) -> DocumentService:
    from app.infra.storage import get_storage
    from app.repositories.document import DocumentRepository
    from app.services.document import DocumentService

    return DocumentService(DocumentRepository(db), get_storage())


def get_processing_service(db: DbSession) -> DocumentProcessingService:
    from app.infra.storage import get_storage
    from app.repositories.document import DocumentPageRepository, DocumentRepository
    from app.services.processing import DocumentProcessingService

    return DocumentProcessingService(
        DocumentRepository(db), DocumentPageRepository(db), get_storage()
    )


def get_document_page_repository(db: DbSession) -> DocumentPageRepository:
    from app.repositories.document import DocumentPageRepository

    return DocumentPageRepository(db)


def get_intelligence_service(db: DbSession) -> IntelligenceService:
    from app.repositories.document import DocumentPageRepository, DocumentRepository
    from app.repositories.knowledge import (
        ChunkRepository,
        EntityRepository,
        RelationshipRepository,
    )
    from app.services.intelligence import IntelligenceService

    return IntelligenceService(
        DocumentRepository(db),
        DocumentPageRepository(db),
        ChunkRepository(db),
        EntityRepository(db),
        RelationshipRepository(db),
    )


def get_entity_repository(db: DbSession) -> EntityRepository:
    from app.repositories.knowledge import EntityRepository

    return EntityRepository(db)


def get_chunk_repository(db: DbSession) -> ChunkRepository:
    from app.repositories.knowledge import ChunkRepository

    return ChunkRepository(db)


def get_graph_service(db: DbSession) -> GraphService:
    from app.ai.graph.backend import get_graph_backend
    from app.repositories.knowledge import EntityRepository, RelationshipRepository
    from app.services.graph import GraphService

    return GraphService(
        EntityRepository(db), RelationshipRepository(db), get_graph_backend()
    )


def get_embedding_service(db: DbSession) -> EmbeddingService:
    from app.ai.embeddings import get_embedder
    from app.ai.vectorstore import get_vector_store
    from app.repositories.knowledge import ChunkRepository
    from app.services.embedding import EmbeddingService

    return EmbeddingService(ChunkRepository(db), get_embedder(), get_vector_store())


def get_retrieval_service(db: DbSession) -> RetrievalService:
    from app.ai.rerank import get_reranker
    from app.repositories.knowledge import ChunkRepository
    from app.services.retrieval import RetrievalService

    return RetrievalService(
        get_embedding_service(db), ChunkRepository(db), get_reranker()
    )


def get_copilot_service(db: DbSession) -> CopilotService:
    from app.ai.llm.providers import get_llm
    from app.ai.os.orchestrator import AIOrchestrator
    from app.services.copilot import CopilotService

    orchestrator = AIOrchestrator(get_retrieval_service(db), get_llm())
    return CopilotService(orchestrator)


# --- authentication ---------------------------------------------------
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """Resolve and validate the bearer access token into the current User."""
    if credentials is None:
        raise UnauthorizedError("Missing authentication credentials.")
    try:
        payload = decode_token(credentials.credentials, expected_type="access")
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired access token.") from exc

    user = await users.get(uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(
    minimum: Role,
) -> Callable[[User], Coroutine[Any, Any, User]]:
    """Dependency factory enforcing a minimum hierarchical RBAC role."""

    async def _guard(user: CurrentUser) -> User:
        if ROLE_RANK.get(user.role, -1) < ROLE_RANK[minimum]:
            raise ForbiddenError(f"Requires '{minimum}' role or higher.")
        return user

    return _guard
