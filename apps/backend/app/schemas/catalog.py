"""Pydantic schemas for plant/department/project/equipment CRUD."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Criticality, EquipmentStatus, ProjectStatus


# --- Plant ---------------------------------------------------------------
class PlantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str | None = Field(default=None, max_length=64)
    location: str | None = Field(default=None, max_length=255)


class PlantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, max_length=64)
    location: str | None = Field(default=None, max_length=255)


class PlantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str | None
    location: str | None
    created_at: datetime


# --- Department ----------------------------------------------------------
class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    plant_id: uuid.UUID


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    plant_id: uuid.UUID | None = None


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    plant_id: uuid.UUID
    created_at: datetime


# --- Project -------------------------------------------------------------
class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: ProjectStatus = ProjectStatus.PLANNING


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    status: str
    created_at: datetime


# --- Equipment -----------------------------------------------------------
class EquipmentCreate(BaseModel):
    tag: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=255)
    equipment_type: str | None = Field(default=None, max_length=128)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    description: str | None = None
    status: EquipmentStatus = EquipmentStatus.OPERATIONAL
    criticality: Criticality = Criticality.MEDIUM
    plant_id: uuid.UUID | None = None


class EquipmentUpdate(BaseModel):
    tag: str | None = Field(default=None, min_length=1, max_length=128)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    equipment_type: str | None = Field(default=None, max_length=128)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    description: str | None = None
    status: EquipmentStatus | None = None
    criticality: Criticality | None = None
    plant_id: uuid.UUID | None = None


class EquipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    tag: str
    name: str
    equipment_type: str | None
    manufacturer: str | None
    model: str | None
    description: str | None
    status: str
    criticality: str
    plant_id: uuid.UUID | None
    created_at: datetime
