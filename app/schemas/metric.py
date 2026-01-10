"""Pydantic schemas for metrics."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MetricBase(BaseModel):
    """Base schema for metrics."""
    
    name: str = Field(..., description="Name of the metric")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    tags: Optional[dict[str, str]] = Field(default_factory=dict, description="Metric tags")


class MetricCreate(MetricBase):
    """Schema for creating a new metric."""
    pass


class MetricUpdate(BaseModel):
    """Schema for updating a metric."""
    
    name: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    tags: Optional[dict[str, str]] = None


class MetricResponse(MetricBase):
    """Schema for metric response."""
    
    id: str = Field(..., description="Unique metric identifier")
    timestamp: datetime = Field(..., description="When the metric was recorded")
    
    model_config = {"from_attributes": True}


class MetricList(BaseModel):
    """Schema for list of metrics."""
    
    metrics: list[MetricResponse]
    total: int
    page: int = 1
    page_size: int = 20
