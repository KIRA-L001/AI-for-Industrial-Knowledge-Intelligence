"""Equipment CRUD endpoints (organization-scoped, RBAC-guarded)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import CurrentUser, get_equipment_service, require_role
from app.core.security import Role
from app.models.equipment import Equipment
from app.schemas.catalog import EquipmentCreate, EquipmentOut, EquipmentUpdate
from app.schemas.common import Page
from app.services.crud import CrudService

router = APIRouter(prefix="/equipment", tags=["equipment"])

Service = Annotated[CrudService[Equipment], Depends(get_equipment_service)]
Engineer = Depends(require_role(Role.ENGINEER))


@router.get("", response_model=Page[EquipmentOut])
async def list_equipment(
    user: CurrentUser,
    service: Service,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[EquipmentOut]:
    items, total = await service.list(user.organization_id, limit=limit, offset=offset)
    return Page(
        items=[EquipmentOut.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "", response_model=EquipmentOut, status_code=status.HTTP_201_CREATED, dependencies=[Engineer]
)
async def create_equipment(
    payload: EquipmentCreate, user: CurrentUser, service: Service
) -> EquipmentOut:
    entity = await service.create(user.organization_id, payload.model_dump())
    return EquipmentOut.model_validate(entity)


@router.get("/{equipment_id}", response_model=EquipmentOut)
async def get_equipment(
    equipment_id: uuid.UUID, user: CurrentUser, service: Service
) -> EquipmentOut:
    entity = await service.get(user.organization_id, equipment_id)
    return EquipmentOut.model_validate(entity)


@router.patch("/{equipment_id}", response_model=EquipmentOut, dependencies=[Engineer])
async def update_equipment(
    equipment_id: uuid.UUID, payload: EquipmentUpdate, user: CurrentUser, service: Service
) -> EquipmentOut:
    entity = await service.update(
        user.organization_id, equipment_id, payload.model_dump(exclude_unset=True)
    )
    return EquipmentOut.model_validate(entity)


@router.delete(
    "/{equipment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Engineer],
)
async def delete_equipment(
    equipment_id: uuid.UUID, user: CurrentUser, service: Service
) -> Response:
    await service.delete(user.organization_id, equipment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
