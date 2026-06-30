"""Document endpoints: upload (multipart), list, get, download URL, delete."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status

from app.api.deps import (
    CurrentUser,
    get_document_page_repository,
    get_document_service,
    get_processing_service,
    require_role,
)
from app.core.security import Role
from app.repositories.document import DocumentPageRepository
from app.schemas.common import Page
from app.schemas.document import (
    DocumentDownload,
    DocumentOut,
    DocumentPageOut,
)
from app.services.document import DocumentService
from app.services.processing import DocumentProcessingService

router = APIRouter(prefix="/documents", tags=["documents"])

Service = Annotated[DocumentService, Depends(get_document_service)]
Processing = Annotated[DocumentProcessingService, Depends(get_processing_service)]
PageRepo = Annotated[DocumentPageRepository, Depends(get_document_page_repository)]
Engineer = Depends(require_role(Role.ENGINEER))

# Reject excessively large uploads early (50 MB default ceiling).
MAX_UPLOAD_BYTES = 50 * 1024 * 1024


@router.post(
    "/upload",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Engineer],
)
async def upload_document(
    user: CurrentUser,
    service: Service,
    file: Annotated[UploadFile, File(...)],
    project_id: Annotated[uuid.UUID | None, Form()] = None,
) -> DocumentOut:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        from app.core.errors import AppError

        raise AppError("File exceeds the 50 MB upload limit.")
    document = await service.upload(
        organization_id=user.organization_id,
        filename=file.filename or "upload",
        content_type=file.content_type or "application/octet-stream",
        data=data,
        project_id=project_id,
    )
    return DocumentOut.model_validate(document)


@router.get("", response_model=Page[DocumentOut])
async def list_documents(
    user: CurrentUser,
    service: Service,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[DocumentOut]:
    items, total = await service.list(user.organization_id, limit=limit, offset=offset)
    return Page(
        items=[DocumentOut.model_validate(d) for d in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: uuid.UUID, user: CurrentUser, service: Service
) -> DocumentOut:
    document = await service.get(user.organization_id, document_id)
    return DocumentOut.model_validate(document)


@router.post("/{document_id}/process", response_model=DocumentOut, dependencies=[Engineer])
async def process_document(
    document_id: uuid.UUID, user: CurrentUser, service: Service, processing: Processing
) -> DocumentOut:
    """Run OCR/extraction for the document and return its updated state.

    Runs inline (extraction is cheap for text formats); the Celery task
    `kira.process_document` exists for heavy async processing at scale.
    """
    document = await service.get(user.organization_id, document_id)
    await processing.process(document.id)
    refreshed = await service.get(user.organization_id, document_id)
    return DocumentOut.model_validate(refreshed)


@router.get("/{document_id}/pages", response_model=list[DocumentPageOut])
async def get_document_pages(
    document_id: uuid.UUID, user: CurrentUser, service: Service, pages: PageRepo
) -> list[DocumentPageOut]:
    document = await service.get(user.organization_id, document_id)
    rows = await pages.list_for_document(document.id)
    return [DocumentPageOut.model_validate(p) for p in rows]


@router.get("/{document_id}/download", response_model=DocumentDownload)
async def download_document(
    document_id: uuid.UUID, user: CurrentUser, service: Service
) -> DocumentDownload:
    document = await service.get(user.organization_id, document_id)
    url = service.download_url(document)
    return DocumentDownload(url=url, expires_seconds=3600)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Engineer],
)
async def delete_document(
    document_id: uuid.UUID, user: CurrentUser, service: Service
) -> Response:
    await service.delete(user.organization_id, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
