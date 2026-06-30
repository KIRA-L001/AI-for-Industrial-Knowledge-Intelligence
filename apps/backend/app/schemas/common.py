"""Shared Pydantic schemas: pagination envelope and error shapes."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

ItemT = TypeVar("ItemT")


class PageParams(BaseModel):
    """Standard pagination query parameters."""

    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class Page(BaseModel, Generic[ItemT]):
    """Paginated response envelope."""

    items: list[ItemT]
    total: int
    limit: int
    offset: int


class ErrorBody(BaseModel):
    code: str
    message: str
    details: object | None = None


class ErrorResponse(BaseModel):
    """Standard error envelope returned by the API."""

    error: ErrorBody
