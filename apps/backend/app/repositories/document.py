"""Document data access (organization-scoped)."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import delete, select

from app.models.document import Document
from app.models.document_page import DocumentPage
from app.repositories.base import BaseRepository, OrgScopedRepository


class DocumentRepository(OrgScopedRepository[Document]):
    model = Document


class DocumentPageRepository(BaseRepository[DocumentPage]):
    model = DocumentPage

    async def delete_for_document(self, document_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(DocumentPage).where(DocumentPage.document_id == document_id)
        )

    async def list_for_document(
        self, document_id: uuid.UUID
    ) -> Sequence[DocumentPage]:
        result = await self.session.execute(
            select(DocumentPage)
            .where(DocumentPage.document_id == document_id)
            .order_by(DocumentPage.page_number)
        )
        return result.scalars().all()
