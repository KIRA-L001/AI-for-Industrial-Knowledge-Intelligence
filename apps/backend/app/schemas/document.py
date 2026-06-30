"""Document schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    status: str
    page_count: int | None
    project_id: uuid.UUID | None
    error_message: str | None
    created_at: datetime


class DocumentDownload(BaseModel):
    """A short-lived presigned URL to fetch the original object."""

    url: str
    expires_seconds: int


class DocumentPageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page_number: int
    text: str
    blocks: list | None
