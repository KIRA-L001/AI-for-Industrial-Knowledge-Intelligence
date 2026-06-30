"""Per-store health checks used by the readiness endpoint.

Each check returns ("ok"|"error", detail). Failures are caught and reported
rather than raised so a single down store does not crash the probe.
"""

from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine
from app.infra.clients import get_minio, get_neo4j_driver, get_qdrant, get_redis

StoreStatus = tuple[str, str]


async def check_postgres() -> StoreStatus:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "ok", "reachable"
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


async def check_redis() -> StoreStatus:
    try:
        client = get_redis()
        await client.ping()
        return "ok", "reachable"
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


async def check_neo4j() -> StoreStatus:
    try:
        driver = get_neo4j_driver()
        await driver.verify_connectivity()
        return "ok", "reachable"
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


async def check_qdrant() -> StoreStatus:
    def _probe() -> None:
        get_qdrant().get_collections()

    try:
        await asyncio.to_thread(_probe)
        return "ok", "reachable"
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


async def check_minio() -> StoreStatus:
    settings = get_settings()

    def _probe() -> bool:
        return get_minio().bucket_exists(settings.minio_bucket)

    try:
        await asyncio.to_thread(_probe)
        return "ok", "reachable"
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


async def gather_health() -> dict[str, dict[str, str]]:
    """Run all store checks concurrently and return a status map."""
    names = ["postgres", "redis", "neo4j", "qdrant", "minio"]
    checks = [
        check_postgres(),
        check_redis(),
        check_neo4j(),
        check_qdrant(),
        check_minio(),
    ]
    results = await asyncio.gather(*checks, return_exceptions=False)
    return {
        name: {"status": status, "detail": detail}
        for name, (status, detail) in zip(names, results, strict=True)
    }
