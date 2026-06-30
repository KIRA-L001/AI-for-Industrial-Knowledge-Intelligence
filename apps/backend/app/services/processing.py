"""Document processing service: OCR/extraction stage of the pipeline.

Drives the status state machine uploaded → ocr → extracted, loading the
original from storage, running the extractor, and persisting per-page text
(with layout blocks for citation provenance). Idempotent: re-running clears
prior pages first.
"""

from __future__ import annotations

import uuid

from app.ai.ocr.extractor import extract
from app.core.logging import get_logger
from app.infra.storage import StorageBackend
from app.models.document_page import DocumentPage
from app.models.enums import DocumentStatus
from app.repositories.document import DocumentPageRepository, DocumentRepository

logger = get_logger("kira.processing")


class DocumentProcessingService:
    """Runs OCR/extraction for a single document."""

    def __init__(
        self,
        documents: DocumentRepository,
        pages: DocumentPageRepository,
        storage: StorageBackend,
    ) -> None:
        self.documents = documents
        self.pages = pages
        self.storage = storage

    async def process(self, document_id: uuid.UUID) -> int:
        """Extract text for the document; return the number of pages produced."""
        document = await self.documents.get(document_id)
        if document is None:
            raise ValueError(f"Document {document_id} not found.")

        document.status = DocumentStatus.OCR.value
        await self.documents.add(document)

        try:
            data = self.storage.get(document.storage_key)
            extracted = extract(data, document.content_type, document.filename)

            await self.pages.delete_for_document(document_id)
            for page in extracted:
                await self.pages.add(
                    DocumentPage(
                        document_id=document_id,
                        page_number=page.page_number,
                        text=page.text,
                        blocks=page.blocks or None,
                    )
                )

            document.page_count = len(extracted)
            document.status = DocumentStatus.EXTRACTED.value
            document.error_message = None
            await self.documents.add(document)
            logger.info("extracted", document_id=str(document_id), pages=len(extracted))
            return len(extracted)
        except Exception as exc:  # noqa: BLE001
            document.status = DocumentStatus.FAILED.value
            document.error_message = str(exc)[:1000]
            await self.documents.add(document)
            logger.error("extract_failed", document_id=str(document_id), error=str(exc))
            raise
