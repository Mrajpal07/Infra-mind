"""Pydantic schemas for SLA (Service Level Agreement)."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SLAStatus(str, Enum):
    """SLA status enumeration."""
    
    ACTIVE = "active"
    BREACHED = "breached"
    WARNING = "warning"
    INACTIVE = "inactive"


class SLABase(BaseModel):
    """Base schema for SLA."""
    
    name: str = Field(..., description="SLA name")
    description: Optional[str] = Field(None, description="SLA description")
    target_value: float = Field(..., description="Target metric value")
    warning_threshold: float = Field(..., description="Warning threshold percentage")
    metric_name: str = Field(..., description="Associated metric name")


class SLACreate(SLABase):
    """Schema for creating a new SLA."""
    pass


class SLAUpdate(BaseModel):
    """Schema for updating an SLA."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    metric_name: Optional[str] = None
    status: Optional[SLAStatus] = None


class SLAResponse(SLABase):
    """Schema for SLA response."""
    
    id: str = Field(..., description="Unique SLA identifier")
    status: SLAStatus = Field(..., description="Current SLA status")
    current_value: Optional[float] = Field(None, description="Current metric value")
    compliance_percentage: Optional[float] = Field(None, description="SLA compliance %")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {"from_attributes": True}


class SLAList(BaseModel):
    """Schema for list of SLAs."""
    
    slas: list[SLAResponse]
    total: int
    page: int = 1
    page_size: int = 20
