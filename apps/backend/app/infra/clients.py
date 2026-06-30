"""Lazy singleton clients for external infrastructure (Redis, Neo4j, Qdrant, MinIO).

Clients are created on first use so the app can boot even if a backing store is
temporarily unreachable; health checks report per-store status.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from app.core.config import get_settings

if TYPE_CHECKING:
    from minio import Minio
    from neo4j import AsyncDriver
    from qdrant_client import QdrantClient
    from redis.asyncio import Redis


@lru_cache
def get_redis() -> Redis:
    """Return a cached async Redis client."""
    from redis.asyncio import Redis

    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


@lru_cache
def get_neo4j_driver() -> AsyncDriver:
    """Return a cached async Neo4j driver."""
    from neo4j import AsyncGraphDatabase

    settings = get_settings()
    return AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )


@lru_cache
def get_qdrant() -> QdrantClient:
    """Return a cached Qdrant client."""
    from qdrant_client import QdrantClient

    settings = get_settings()
    return QdrantClient(url=settings.qdrant_url)


@lru_cache
def get_minio() -> Minio:
    """Return a cached MinIO client."""
    from minio import Minio

    settings = get_settings()
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )
