"""Project CRUD endpoints (organization-scoped, RBAC-guarded)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import CurrentUser, get_project_service, require_role
from app.core.security import Role
from app.models.project import Project
from app.schemas.catalog import ProjectCreate, ProjectOut, ProjectUpdate
from app.schemas.common import Page
from app.services.crud import CrudService

router = APIRouter(prefix="/projects", tags=["projects"])

Service = Annotated[CrudService[Project], Depends(get_project_service)]
Engineer = Depends(require_role(Role.ENGINEER))


@router.get("", response_model=Page[ProjectOut])
async def list_projects(
    user: CurrentUser,
    service: Service,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[ProjectOut]:
    items, total = await service.list(user.organization_id, limit=limit, offset=offset)
    return Page(
        items=[ProjectOut.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "", response_model=ProjectOut, status_code=status.HTTP_201_CREATED, dependencies=[Engineer]
)
async def create_project(
    payload: ProjectCreate, user: CurrentUser, service: Service
) -> ProjectOut:
    entity = await service.create(user.organization_id, payload.model_dump())
    return ProjectOut.model_validate(entity)


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: uuid.UUID, user: CurrentUser, service: Service
) -> ProjectOut:
    entity = await service.get(user.organization_id, project_id)
    return ProjectOut.model_validate(entity)


@router.patch("/{project_id}", response_model=ProjectOut, dependencies=[Engineer])
async def update_project(
    project_id: uuid.UUID, payload: ProjectUpdate, user: CurrentUser, service: Service
) -> ProjectOut:
    entity = await service.update(
        user.organization_id, project_id, payload.model_dump(exclude_unset=True)
    )
    return ProjectOut.model_validate(entity)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Engineer],
)
async def delete_project(
    project_id: uuid.UUID, user: CurrentUser, service: Service
) -> Response:
    await service.delete(user.organization_id, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
