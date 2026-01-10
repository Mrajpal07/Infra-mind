"""Metrics API endpoints."""

from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/metrics", tags=["Metrics"])


class MetricIngest(BaseModel):
    """Schema for metrics ingestion with validation."""
    
    resource_id: str
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage (0-100)")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage (0-100)")
    gpu_usage: float = Field(..., ge=0, le=100, description="GPU usage percentage (0-100)")
    timestamp: datetime


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str


@router.post(
    "/ingest",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest metrics",
    description="Accept resource metrics for ingestion.",
)
async def ingest_metrics(metrics: MetricIngest) -> MessageResponse:
    """Placeholder endpoint for metrics ingestion."""
    return MessageResponse(message="Metrics received")
