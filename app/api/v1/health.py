"""Health check API endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str
    app_name: str
    version: str
    environment: str
    timestamp: datetime


class DetailedHealthResponse(HealthResponse):
    """Detailed health check response with component status."""
    
    components: dict[str, str]


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic application health status.",
)
async def health_check() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed health check",
    description="Returns detailed health status including component checks.",
)
async def detailed_health_check() -> DetailedHealthResponse:
    """Detailed health check with component status."""
    components = {
        "api": "healthy",
        "database": "healthy" if settings.database_url else "not_configured",
        "cache": "healthy" if settings.redis_url else "not_configured",
    }
    
    # Determine overall status
    overall_status = "healthy"
    if any(v == "unhealthy" for v in components.values()):
        overall_status = "unhealthy"
    elif any(v == "degraded" for v in components.values()):
        overall_status = "degraded"
    
    return DetailedHealthResponse(
        status=overall_status,
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
        components=components,
    )


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Kubernetes readiness probe endpoint.",
)
async def readiness_probe() -> dict:
    """Readiness probe for container orchestration."""
    return {"ready": True}


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Kubernetes liveness probe endpoint.",
)
async def liveness_probe() -> dict:
    """Liveness probe for container orchestration."""
    return {"alive": True}
