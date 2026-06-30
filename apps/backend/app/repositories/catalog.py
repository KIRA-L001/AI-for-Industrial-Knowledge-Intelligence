"""Org-scoped repositories for plant/department/project/equipment entities."""

from __future__ import annotations

from app.models.equipment import Equipment
from app.models.plant import Department, Plant
from app.models.project import Project
from app.repositories.base import OrgScopedRepository


class PlantRepository(OrgScopedRepository[Plant]):
    model = Plant


class DepartmentRepository(OrgScopedRepository[Department]):
    model = Department


class ProjectRepository(OrgScopedRepository[Project]):
    model = Project


class EquipmentRepository(OrgScopedRepository[Equipment]):
    model = Equipment
