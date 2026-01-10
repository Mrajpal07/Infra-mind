"""Prometheus metrics middleware for FastAPI."""

import time

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


# HTTP request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Custom business metrics
METRICS_INGESTED = Counter(
    "metrics_ingested_total",
    "Total metrics ingested",
)

ANOMALY_CHECKS = Counter(
    "anomaly_checks_total",
    "Total anomaly detection checks",
)

SLA_RISK_CHECKS = Counter(
    "sla_risk_checks_total",
    "Total SLA risk assessments",
)

SLA_HIGH_RISK = Counter(
    "sla_high_risk_total",
    "Total high risk SLA assessments",
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request metrics."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip metrics endpoint to avoid self-tracking
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Normalize path to avoid high cardinality
        path = self._normalize_path(request.url.path)
        method = request.method
        
        # Track request timing
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=method,
            path=path,
            status_code=response.status_code,
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=method,
            path=path,
        ).observe(duration)
        
        return response
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path to reduce cardinality.
        
        Replaces dynamic path segments with placeholders.
        """
        parts = path.split("/")
        normalized = []
        
        for part in parts:
            # Replace UUIDs and numeric IDs with placeholder
            if part and (self._is_uuid(part) or part.isdigit()):
                normalized.append("{id}")
            else:
                normalized.append(part)
        
        return "/".join(normalized)
    
    def _is_uuid(self, value: str) -> bool:
        """Check if value looks like a UUID."""
        # Simple check for UUID-like strings
        if len(value) == 36 and value.count("-") == 4:
            return True
        # Also match resource IDs that contain hyphens
        if "-" in value and len(value) > 10:
            return True
        return False


def get_metrics() -> StarletteResponse:
    """Generate Prometheus metrics response."""
    return StarletteResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
