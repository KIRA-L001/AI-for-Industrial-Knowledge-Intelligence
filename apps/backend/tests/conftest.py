"""Pytest fixtures: a SQLite-backed app client with the DB dependency overridden.

Uses a temporary file SQLite database (via the portable GUID type) so the full
API can be exercised without a running PostgreSQL instance. A file DB (rather
than :memory:) keeps the schema visible across connections and event loops.
"""

from __future__ import annotations

import asyncio
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.ai.embeddings import HashingEmbedder
from app.ai.graph.backend import InMemoryGraph
from app.ai.llm.providers import StubLLM
from app.ai.os.orchestrator import AIOrchestrator
from app.ai.rerank import LexicalReranker
from app.ai.vectorstore import InMemoryVectorStore
from app.api.deps import (
    get_copilot_service,
    get_document_service,
    get_embedding_service,
    get_graph_service,
    get_processing_service,
    get_retrieval_service,
)
from app.db.base import Base
from app.db.session import get_db
from app.infra.storage import InMemoryStorage
from app.main import app
from app.repositories.document import DocumentPageRepository, DocumentRepository
from app.repositories.knowledge import EntityRepository, RelationshipRepository
from app.services.copilot import CopilotService
from app.services.document import DocumentService
from app.services.embedding import EmbeddingService
from app.services.graph import GraphService
from app.services.processing import DocumentProcessingService
from app.services.retrieval import RetrievalService


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """A TestClient backed by a fresh temporary SQLite database."""
    tmp_dir = tempfile.TemporaryDirectory()
    db_path = Path(tmp_dir.name) / "test.db"
    url = f"sqlite+aiosqlite:///{db_path.as_posix()}"

    engine = create_async_engine(url)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _create() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(_create())

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # Swap MinIO for an in-memory storage backend shared across the test.
    storage = InMemoryStorage()

    def _override_document_service(
        session: AsyncSession = Depends(get_db),
    ) -> DocumentService:
        return DocumentService(DocumentRepository(session), storage)

    def _override_processing_service(
        session: AsyncSession = Depends(get_db),
    ) -> DocumentProcessingService:
        return DocumentProcessingService(
            DocumentRepository(session), DocumentPageRepository(session), storage
        )

    # Shared in-memory graph backend (persists across requests in a test).
    graph_backend = InMemoryGraph()

    def _override_graph_service(
        session: AsyncSession = Depends(get_db),
    ) -> GraphService:
        return GraphService(
            EntityRepository(session), RelationshipRepository(session), graph_backend
        )

    # Shared in-memory vector store + deterministic embedder.
    vector_store = InMemoryVectorStore()
    embedder = HashingEmbedder(dim=64)

    def _override_embedding_service(
        session: AsyncSession = Depends(get_db),
    ) -> EmbeddingService:
        from app.repositories.knowledge import ChunkRepository

        return EmbeddingService(ChunkRepository(session), embedder, vector_store)

    def _override_retrieval_service(
        session: AsyncSession = Depends(get_db),
    ) -> RetrievalService:
        from app.repositories.knowledge import ChunkRepository

        repo = ChunkRepository(session)
        return RetrievalService(
            EmbeddingService(repo, embedder, vector_store), repo, LexicalReranker()
        )

    def _override_copilot_service(
        session: AsyncSession = Depends(get_db),
    ) -> CopilotService:
        from app.repositories.knowledge import ChunkRepository

        repo = ChunkRepository(session)
        retrieval = RetrievalService(
            EmbeddingService(repo, embedder, vector_store), repo, LexicalReranker()
        )
        return CopilotService(AIOrchestrator(retrieval, StubLLM()))

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_document_service] = _override_document_service
    app.dependency_overrides[get_processing_service] = _override_processing_service
    app.dependency_overrides[get_graph_service] = _override_graph_service
    app.dependency_overrides[get_embedding_service] = _override_embedding_service
    app.dependency_overrides[get_retrieval_service] = _override_retrieval_service
    app.dependency_overrides[get_copilot_service] = _override_copilot_service
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        tmp_dir.cleanup()
