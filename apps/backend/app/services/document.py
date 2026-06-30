"""Document service: upload to object storage + metadata persistence.

Owns the rules for accepting a file (type allow-list), computing a checksum,
writing the original to storage, and recording the row in `uploaded` state.
Downstream processing (OCR → ... → ready) is enqueued in later phases.
"""

from __future__ import annotations

import hashlib
import uuid

from app.core.errors import NotFoundError
from app.infra.storage import StorageBackend
from app.models.document import Document
from app.models.enums import DocumentStatus
from app.repositories.document import DocumentRepository

# Allow-list of accepted upload content types (PROJECT_SPEC Phase 4).
ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "text/csv": "csv",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/tiff": "tiff",
}


class UnsupportedMediaTypeError(NotFoundError):
    status_code = 415
    code = "unsupported_media_type"


class DocumentService:
    """Coordinates the document repository and the storage backend."""

    def __init__(self, repo: DocumentRepository, storage: StorageBackend) -> None:
        self.repo = repo
        self.storage = storage

    async def upload(
        self,
        *,
        organization_id: uuid.UUID,
        filename: str,
        content_type: str,
        data: bytes,
        project_id: uuid.UUID | None = None,
    ) -> Document:
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise UnsupportedMediaTypeError(
                f"Unsupported content type: {content_type!r}."
            )

        checksum = hashlib.sha256(data).hexdigest()
        ext = ALLOWED_CONTENT_TYPES[content_type]
        storage_key = f"{organization_id}/{uuid.uuid4()}.{ext}"

        self.storage.put(storage_key, data, content_type)

        document = Document(
            organization_id=organization_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            checksum_sha256=checksum,
            storage_key=storage_key,
            status=DocumentStatus.UPLOADED.value,
            project_id=project_id,
        )
        return await self.repo.add(document)

    async def get(self, organization_id: uuid.UUID, document_id: uuid.UUID) -> Document:
        document = await self.repo.get_for_org(document_id, organization_id)
        if document is None:
            raise NotFoundError("Document not found.")
        return document

    async def list(
        self, organization_id: uuid.UUID, *, limit: int, offset: int
    ) -> tuple[list[Document], int]:
        items = await self.repo.list_for_org(organization_id, limit=limit, offset=offset)
        total = await self.repo.count_for_org(organization_id)
        return list(items), total

    async def delete(self, organization_id: uuid.UUID, document_id: uuid.UUID) -> None:
        document = await self.get(organization_id, document_id)
        self.storage.delete(document.storage_key)
        await self.repo.delete_for_org(document_id, organization_id)

    def download_url(self, document: Document, expires_seconds: int = 3600) -> str:
        return self.storage.presigned_url(document.storage_key, expires_seconds)
