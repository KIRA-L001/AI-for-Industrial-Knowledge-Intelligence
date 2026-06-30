"""Object storage abstraction with a MinIO implementation.

Services depend on the `StorageBackend` protocol (DIP), so tests can swap an
in-memory backend without touching MinIO.
"""

from __future__ import annotations

import io
from datetime import timedelta
from typing import Protocol, runtime_checkable

from app.core.config import get_settings


@runtime_checkable
class StorageBackend(Protocol):
    """Minimal object-storage surface used by the document pipeline."""

    def put(self, key: str, data: bytes, content_type: str) -> None: ...

    def get(self, key: str) -> bytes: ...

    def delete(self, key: str) -> None: ...

    def presigned_url(self, key: str, expires_seconds: int = 3600) -> str: ...


class MinioStorage:
    """MinIO-backed implementation of `StorageBackend`."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._bucket = self._settings.minio_bucket

    @property
    def _client(self):  # type: ignore[no-untyped-def]
        from app.infra.clients import get_minio

        return get_minio()

    def ensure_bucket(self) -> None:
        client = self._client
        if not client.bucket_exists(self._bucket):
            client.make_bucket(self._bucket)

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self.ensure_bucket()
        self._client.put_object(
            self._bucket,
            key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    def get(self, key: str) -> bytes:
        response = self._client.get_object(self._bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete(self, key: str) -> None:
        self._client.remove_object(self._bucket, key)

    def presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        return self._client.presigned_get_object(
            self._bucket, key, expires=timedelta(seconds=expires_seconds)
        )


class InMemoryStorage:
    """Process-local storage backend for tests."""

    def __init__(self) -> None:
        self._objects: dict[str, tuple[bytes, str]] = {}

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self._objects[key] = (data, content_type)

    def get(self, key: str) -> bytes:
        return self._objects[key][0]

    def delete(self, key: str) -> None:
        self._objects.pop(key, None)

    def presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        return f"memory://{key}"


def get_storage() -> StorageBackend:
    """Default storage backend dependency (MinIO)."""
    return MinioStorage()
