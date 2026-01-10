"""Metrics API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.metric import MetricCreate, MetricList, MetricResponse, MetricUpdate
from app.services.metric_service import metric_service

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.post(
    "",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a metric",
    description="Create a new metric record.",
)
async def create_metric(metric: MetricCreate) -> MetricResponse:
    """Create a new metric."""
    return await metric_service.create_metric(metric)


@router.get(
    "",
    response_model=MetricList,
    summary="List metrics",
    description="Get a paginated list of metrics with optional filtering.",
)
async def list_metrics(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by metric name"),
) -> MetricList:
    """Get paginated list of metrics."""
    metrics, total = await metric_service.get_metrics(
        page=page,
        page_size=page_size,
        name_filter=name,
    )
    return MetricList(
        metrics=metrics,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{metric_id}",
    response_model=MetricResponse,
    summary="Get a metric",
    description="Get a specific metric by ID.",
)
async def get_metric(metric_id: str) -> MetricResponse:
    """Get a metric by ID."""
    metric = await metric_service.get_metric(metric_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metric with ID '{metric_id}' not found",
        )
    return metric


@router.patch(
    "/{metric_id}",
    response_model=MetricResponse,
    summary="Update a metric",
    description="Update an existing metric.",
)
async def update_metric(metric_id: str, metric_update: MetricUpdate) -> MetricResponse:
    """Update a metric."""
    metric = await metric_service.update_metric(metric_id, metric_update)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metric with ID '{metric_id}' not found",
        )
    return metric


@router.delete(
    "/{metric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a metric",
    description="Delete a metric by ID.",
)
async def delete_metric(metric_id: str) -> None:
    """Delete a metric."""
    deleted = await metric_service.delete_metric(metric_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metric with ID '{metric_id}' not found",
        )
