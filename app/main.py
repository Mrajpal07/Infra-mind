"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import health, metrics, sla
from app.core.config import settings
from app.core.prometheus import PrometheusMiddleware, get_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup log message
    print(f"Starting {settings.app_name}")
    print(f"Environment: {settings.env}")
    print(f"Debug: {settings.debug}")
    yield
    # Shutdown
    print(f"Shutting down {settings.app_name}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Infrastructure monitoring and SLA management API",
    docs_url="/docs",
    lifespan=lifespan,
)

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Mount API v1 routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")
app.include_router(sla.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": "/api/v1/health",
        "metrics": "/metrics",
    }


@app.get("/metrics", tags=["Monitoring"], include_in_schema=False)
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return get_metrics()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
