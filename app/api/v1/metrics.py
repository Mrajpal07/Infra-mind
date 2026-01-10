"""Metrics API endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.anomaly_service import AnomalyResult, detect_anomaly
from app.services.metric_service import MetricEntry, metric_service

router = APIRouter(prefix="/metrics", tags=["Metrics"])


class MetricIngest(BaseModel):
    """Schema for metrics ingestion with validation."""
    
    resource_id: str
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage (0-100)")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage (0-100)")
    gpu_usage: float = Field(..., ge=0, le=100, description="GPU usage percentage (0-100)")
    timestamp: datetime


class IngestResponse(BaseModel):
    """Response for metric ingestion."""
    
    message: str
    resource_id: str


class MetricResponse(BaseModel):
    """Response for metric data."""
    
    resource_id: str
    cpu_usage: float
    memory_usage: float
    gpu_usage: float
    timestamp: datetime


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest metrics",
    description="Accept resource metrics for ingestion.",
)
async def ingest_metrics(metrics: MetricIngest) -> IngestResponse:
    """Ingest a metric into the time-series store."""
    entry = MetricEntry(
        resource_id=metrics.resource_id,
        cpu_usage=metrics.cpu_usage,
        memory_usage=metrics.memory_usage,
        gpu_usage=metrics.gpu_usage,
        timestamp=metrics.timestamp,
    )
    metric_service.add_metric(entry)
    
    return IngestResponse(
        message="Metric ingested",
        resource_id=metrics.resource_id,
    )


@router.get(
    "/{resource_id}/latest",
    response_model=MetricResponse,
    status_code=status.HTTP_200_OK,
    summary="Get latest metric",
    description="Get the most recent metric for a resource.",
)
async def get_latest_metric(resource_id: str) -> MetricResponse:
    """Get latest metric for a resource."""
    metric = metric_service.get_latest_metric(resource_id)
    
    if metric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No metrics found for resource '{resource_id}'",
        )
    
    return MetricResponse(
        resource_id=metric.resource_id,
        cpu_usage=metric.cpu_usage,
        memory_usage=metric.memory_usage,
        gpu_usage=metric.gpu_usage,
        timestamp=metric.timestamp,
    )


@router.get(
    "/{resource_id}/analyze",
    response_model=AnomalyResult,
    status_code=status.HTTP_200_OK,
    summary="Analyze metrics for anomalies",
    description="Run anomaly detection on recent metrics using Z-score analysis.",
)
async def analyze_metrics(
    resource_id: str,
    window_size: int = Query(10, ge=2, le=100, description="Rolling window size"),
) -> AnomalyResult:
    """Analyze metrics for anomalies."""
    result = detect_anomaly(resource_id, window_size=window_size)
    
    # Return 404 if insufficient data
    if "Insufficient" in result.explanation or "No metrics" in result.explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.explanation,
        )
    
    return result

