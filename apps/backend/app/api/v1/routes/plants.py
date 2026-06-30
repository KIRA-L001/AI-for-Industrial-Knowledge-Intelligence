"""Plant and Department CRUD endpoints (organization-scoped, RBAC-guarded)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import (
    CurrentUser,
    get_department_service,
    get_plant_service,
    require_role,
)
from app.core.security import Role
from app.models.plant import Department, Plant
from app.schemas.catalog import (
    DepartmentCreate,
    DepartmentOut,
    DepartmentUpdate,
    PlantCreate,
    PlantOut,
    PlantUpdate,
)
from app.schemas.common import Page
from app.services.crud import CrudService

router = APIRouter(tags=["plants"])

PlantService = Annotated[CrudService[Plant], Depends(get_plant_service)]
DeptService = Annotated[CrudService[Department], Depends(get_department_service)]
Engineer = Depends(require_role(Role.ENGINEER))


# --- Plants --------------------------------------------------------------
@router.get("/plants", response_model=Page[PlantOut])
async def list_plants(
    user: CurrentUser,
    service: PlantService,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[PlantOut]:
    items, total = await service.list(user.organization_id, limit=limit, offset=offset)
    return Page(
        items=[PlantOut.model_validate(i) for i in items], total=total, limit=limit, offset=offset
    )


@router.post(
    "/plants", response_model=PlantOut, status_code=status.HTTP_201_CREATED, dependencies=[Engineer]
)
async def create_plant(payload: PlantCreate, user: CurrentUser, service: PlantService) -> PlantOut:
    entity = await service.create(user.organization_id, payload.model_dump())
    return PlantOut.model_validate(entity)


@router.get("/plants/{plant_id}", response_model=PlantOut)
async def get_plant(plant_id: uuid.UUID, user: CurrentUser, service: PlantService) -> PlantOut:
    return PlantOut.model_validate(await service.get(user.organization_id, plant_id))


@router.patch("/plants/{plant_id}", response_model=PlantOut, dependencies=[Engineer])
async def update_plant(
    plant_id: uuid.UUID, payload: PlantUpdate, user: CurrentUser, service: PlantService
) -> PlantOut:
    entity = await service.update(
        user.organization_id, plant_id, payload.model_dump(exclude_unset=True)
    )
    return PlantOut.model_validate(entity)


@router.delete(
    "/plants/{plant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Engineer],
)
async def delete_plant(plant_id: uuid.UUID, user: CurrentUser, service: PlantService) -> Response:
    await service.delete(user.organization_id, plant_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Departments ---------------------------------------------------------
@router.get("/departments", response_model=Page[DepartmentOut])
async def list_departments(
    user: CurrentUser,
    service: DeptService,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[DepartmentOut]:
    items, total = await service.list(user.organization_id, limit=limit, offset=offset)
    return Page(
        items=[DepartmentOut.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/departments",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Engineer],
)
async def create_department(
    payload: DepartmentCreate, user: CurrentUser, service: DeptService
) -> DepartmentOut:
    entity = await service.create(user.organization_id, payload.model_dump())
    return DepartmentOut.model_validate(entity)


@router.patch("/departments/{department_id}", response_model=DepartmentOut, dependencies=[Engineer])
async def update_department(
    department_id: uuid.UUID, payload: DepartmentUpdate, user: CurrentUser, service: DeptService
) -> DepartmentOut:
    entity = await service.update(
        user.organization_id, department_id, payload.model_dump(exclude_unset=True)
    )
    return DepartmentOut.model_validate(entity)


@router.delete(
    "/departments/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Engineer],
)
async def delete_department(
    department_id: uuid.UUID, user: CurrentUser, service: DeptService
) -> Response:
    await service.delete(user.organization_id, department_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
