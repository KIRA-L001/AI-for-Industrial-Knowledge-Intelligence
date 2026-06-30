"""Celery tasks for the document processing pipeline."""

from __future__ import annotations

import asyncio
import uuid

from app.db.session import SessionFactory
from app.infra.storage import MinioStorage
from app.repositories.document import DocumentPageRepository, DocumentRepository
from app.services.processing import DocumentProcessingService
from app.worker import celery_app


async def _run(document_id: uuid.UUID) -> int:
    async with SessionFactory() as session:
        service = DocumentProcessingService(
            DocumentRepository(session),
            DocumentPageRepository(session),
            MinioStorage(),
        )
        try:
            count = await service.process(document_id)
            await session.commit()
            return count
        except Exception:
            await session.commit()  # persist the FAILED status set by the service
            raise


@celery_app.task(name="kira.process_document", bind=True, max_retries=3, default_retry_delay=10)
def process_document(self, document_id: str) -> int:  # type: ignore[no-untyped-def]
    """Run OCR/extraction for a document; retries on transient failures."""
    try:
        return asyncio.run(_run(uuid.UUID(document_id)))
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc) from exc
