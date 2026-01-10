"""Metrics ingestion API endpoints for bulk data intake."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.schemas.metric import MetricCreate, MetricResponse
from app.services.metric_service import metric_service

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


class MetricDataPoint(BaseModel):
    """Single metric data point for ingestion."""
    
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    tags: Optional[dict[str, str]] = Field(default_factory=dict, description="Metric tags")
    timestamp: Optional[datetime] = Field(None, description="Optional timestamp override")


class BatchIngestionRequest(BaseModel):
    """Request schema for batch metric ingestion."""
    
    source: str = Field(..., description="Source system identifier")
    metrics: list[MetricDataPoint] = Field(..., description="List of metrics to ingest")


class IngestionResult(BaseModel):
    """Result of a single metric ingestion."""
    
    name: str
    success: bool
    metric_id: Optional[str] = None
    error: Optional[str] = None


class BatchIngestionResponse(BaseModel):
    """Response schema for batch ingestion."""
    
    source: str
    total_received: int
    successful: int
    failed: int
    results: list[IngestionResult]
    ingested_at: datetime


class StreamIngestionRequest(BaseModel):
    """Request schema for streaming metric ingestion."""
    
    source: str = Field(..., description="Source system identifier")
    metric: MetricDataPoint = Field(..., description="Single metric to ingest")


@router.post(
    "/metrics",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest single metric",
    description="Ingest a single metric data point.",
)
async def ingest_single_metric(request: StreamIngestionRequest) -> MetricResponse:
    """Ingest a single metric from a streaming source."""
    metric_create = MetricCreate(
        name=request.metric.name,
        value=request.metric.value,
        unit=request.metric.unit,
        tags={**(request.metric.tags or {}), "source": request.source},
    )
    return await metric_service.create_metric(metric_create)


@router.post(
    "/metrics/batch",
    response_model=BatchIngestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Batch ingest metrics",
    description="Ingest multiple metrics in a single batch request.",
)
async def ingest_batch_metrics(request: BatchIngestionRequest) -> BatchIngestionResponse:
    """Ingest a batch of metrics."""
    results: list[IngestionResult] = []
    successful = 0
    failed = 0
    
    for metric_data in request.metrics:
        try:
            metric_create = MetricCreate(
                name=metric_data.name,
                value=metric_data.value,
                unit=metric_data.unit,
                tags={**(metric_data.tags or {}), "source": request.source},
            )
            created_metric = await metric_service.create_metric(metric_create)
            results.append(IngestionResult(
                name=metric_data.name,
                success=True,
                metric_id=created_metric.id,
            ))
            successful += 1
        except Exception as e:
            results.append(IngestionResult(
                name=metric_data.name,
                success=False,
                error=str(e),
            ))
            failed += 1
    
    return BatchIngestionResponse(
        source=request.source,
        total_received=len(request.metrics),
        successful=successful,
        failed=failed,
        results=results,
        ingested_at=datetime.now(timezone.utc),
    )


@router.post(
    "/metrics/validate",
    status_code=status.HTTP_200_OK,
    summary="Validate metrics batch",
    description="Validate a batch of metrics without ingesting them.",
)
async def validate_metrics(request: BatchIngestionRequest) -> dict:
    """Validate metrics without ingesting."""
    valid_count = 0
    invalid_metrics: list[dict] = []
    
    for i, metric in enumerate(request.metrics):
        # Placeholder validation logic
        if not metric.name or metric.name.strip() == "":
            invalid_metrics.append({
                "index": i,
                "name": metric.name,
                "error": "Metric name cannot be empty",
            })
        elif metric.value is None:
            invalid_metrics.append({
                "index": i,
                "name": metric.name,
                "error": "Metric value is required",
            })
        else:
            valid_count += 1
    
    return {
        "valid": len(invalid_metrics) == 0,
        "total_metrics": len(request.metrics),
        "valid_count": valid_count,
        "invalid_count": len(invalid_metrics),
        "invalid_metrics": invalid_metrics,
    }


@router.get(
    "/sources",
    status_code=status.HTTP_200_OK,
    summary="List ingestion sources",
    description="Get a list of known metric ingestion sources.",
)
async def list_sources() -> dict:
    """List known ingestion sources (placeholder)."""
    # Placeholder - would query database for unique sources
    return {
        "sources": [
            {"name": "prometheus", "last_seen": None, "metric_count": 0},
            {"name": "telegraf", "last_seen": None, "metric_count": 0},
            {"name": "custom-agent", "last_seen": None, "metric_count": 0},
        ],
        "total": 3,
    }


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Ingestion pipeline status",
    description="Get the current status of the ingestion pipeline.",
)
async def ingestion_status() -> dict:
    """Get ingestion pipeline status (placeholder)."""
    return {
        "status": "operational",
        "queue_depth": 0,
        "processing_rate": 0.0,
        "last_ingestion": None,
        "errors_last_hour": 0,
    }
