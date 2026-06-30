"""Liveness and readiness endpoints.

- /health  : process is up (liveness) — cheap, never touches dependencies.
- /ready   : all backing stores reachable (readiness) — used by orchestrators.
"""

from fastapi import APIRouter, Response, status

from app import __version__
from app.infra.health import gather_health

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
async def health() -> dict[str, str]:
    """Return process liveness."""
    return {"status": "ok", "service": "kira-backend", "version": __version__}


@router.get("/ready", summary="Readiness probe")
async def ready(response: Response) -> dict[str, object]:
    """Return readiness, aggregating per-store health checks."""
    stores = await gather_health()
    all_ok = all(s["status"] == "ok" for s in stores.values())
    if not all_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ok" if all_ok else "degraded", "stores": stores}
