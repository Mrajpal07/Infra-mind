"""SLA API endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/sla", tags=["SLA"])


class SLAResponse(BaseModel):
    """SLA status response schema."""
    
    resource_id: str
    sla_target: str
    current_status: str


@router.get(
    "/{resource_id}",
    response_model=SLAResponse,
    status_code=status.HTTP_200_OK,
    summary="Get SLA status",
    description="Get SLA status for a resource.",
)
async def get_sla(resource_id: str) -> SLAResponse:
    """Get SLA status for a resource (placeholder)."""
    return SLAResponse(
        resource_id=resource_id,
        sla_target="99.9%",
        current_status="OK",
    )
