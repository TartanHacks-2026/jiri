"""Health check endpoints.

Provides:
- Simple liveness check
- Detailed readiness check with DB/Redis connectivity
"""

from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel
from sqlalchemy import text

from jiri.core.database import get_session
from jiri.core.logging import logger
from jiri.core.redis_client import get_redis

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str = "0.1.0"
    checks: dict[str, Any] | None = None


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns OK if the service is running.",
)
async def health_check() -> HealthResponse:
    """Basic liveness check."""
    return HealthResponse(status="ok")


@router.get(
    "/health/ready",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Checks connectivity to all dependencies (DB, Redis).",
)
async def readiness_check() -> HealthResponse:
    """Detailed readiness check with dependency status."""
    checks: dict[str, Any] = {}
    all_healthy = True

    # Check database
    try:
        async with get_session() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        checks["database"] = {"status": "ok", "type": "timescaledb"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["database"] = {"status": "error", "error": str(e)}
        all_healthy = False

    # Check Redis
    try:
        redis = get_redis()
        await redis.ping()
        checks["redis"] = {"status": "ok"}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        checks["redis"] = {"status": "error", "error": str(e)}
        all_healthy = False

    return HealthResponse(
        status="ok" if all_healthy else "degraded",
        checks=checks,
    )


@router.get(
    "/",
    response_model=HealthResponse,
    include_in_schema=False,
)
async def root() -> HealthResponse:
    """Root endpoint redirects to health check."""
    return HealthResponse(status="ok")
