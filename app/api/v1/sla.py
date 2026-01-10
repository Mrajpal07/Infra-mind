"""SLA API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.schemas.sla import SLACreate, SLAList, SLAResponse, SLAStatus, SLAUpdate
from app.services.sla_service import sla_service

router = APIRouter(prefix="/sla", tags=["SLA"])


class ComplianceCheckRequest(BaseModel):
    """Request schema for compliance check."""
    
    current_value: float


@router.post(
    "",
    response_model=SLAResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an SLA",
    description="Create a new Service Level Agreement.",
)
async def create_sla(sla: SLACreate) -> SLAResponse:
    """Create a new SLA."""
    return await sla_service.create_sla(sla)


@router.get(
    "",
    response_model=SLAList,
    summary="List SLAs",
    description="Get a paginated list of SLAs with optional status filtering.",
)
async def list_slas(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[SLAStatus] = Query(None, description="Filter by SLA status"),
) -> SLAList:
    """Get paginated list of SLAs."""
    slas, total = await sla_service.get_slas(
        page=page,
        page_size=page_size,
        status_filter=status,
    )
    return SLAList(
        slas=slas,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{sla_id}",
    response_model=SLAResponse,
    summary="Get an SLA",
    description="Get a specific SLA by ID.",
)
async def get_sla(sla_id: str) -> SLAResponse:
    """Get an SLA by ID."""
    sla = await sla_service.get_sla(sla_id)
    if not sla:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SLA with ID '{sla_id}' not found",
        )
    return sla


@router.patch(
    "/{sla_id}",
    response_model=SLAResponse,
    summary="Update an SLA",
    description="Update an existing SLA.",
)
async def update_sla(sla_id: str, sla_update: SLAUpdate) -> SLAResponse:
    """Update an SLA."""
    sla = await sla_service.update_sla(sla_id, sla_update)
    if not sla:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SLA with ID '{sla_id}' not found",
        )
    return sla


@router.delete(
    "/{sla_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an SLA",
    description="Delete an SLA by ID.",
)
async def delete_sla(sla_id: str) -> None:
    """Delete an SLA."""
    deleted = await sla_service.delete_sla(sla_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SLA with ID '{sla_id}' not found",
        )


@router.post(
    "/{sla_id}/check",
    response_model=SLAResponse,
    summary="Check SLA compliance",
    description="Check and update SLA compliance based on current metric value.",
)
async def check_compliance(sla_id: str, request: ComplianceCheckRequest) -> SLAResponse:
    """Check SLA compliance."""
    sla = await sla_service.check_sla_compliance(sla_id, request.current_value)
    if not sla:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SLA with ID '{sla_id}' not found",
        )
    return sla


# ============================================================================
# Additional SLA Placeholder Endpoints
# ============================================================================


@router.get(
    "/{sla_id}/history",
    status_code=status.HTTP_200_OK,
    summary="Get SLA compliance history",
    description="Get historical compliance data for an SLA.",
)
async def get_sla_history(
    sla_id: str,
    days: int = Query(7, ge=1, le=90, description="Number of days of history"),
) -> dict:
    """Get SLA compliance history (placeholder)."""
    sla = await sla_service.get_sla(sla_id)
    if not sla:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SLA with ID '{sla_id}' not found",
        )
    
    # Placeholder response
    return {
        "sla_id": sla_id,
        "sla_name": sla.name,
        "period_days": days,
        "data_points": [],
        "average_compliance": None,
        "breach_count": 0,
    }


@router.get(
    "/{sla_id}/breaches",
    status_code=status.HTTP_200_OK,
    summary="Get SLA breach events",
    description="Get a list of breach events for an SLA.",
)
async def get_sla_breaches(
    sla_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict:
    """Get SLA breach events (placeholder)."""
    sla = await sla_service.get_sla(sla_id)
    if not sla:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SLA with ID '{sla_id}' not found",
        )
    
    # Placeholder response
    return {
        "sla_id": sla_id,
        "breaches": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/reports/summary",
    status_code=status.HTTP_200_OK,
    summary="Get SLA summary report",
    description="Get a summary report of all SLAs.",
)
async def get_sla_summary_report() -> dict:
    """Get SLA summary report (placeholder)."""
    slas, total = await sla_service.get_slas(page=1, page_size=100)
    
    status_counts = {"active": 0, "warning": 0, "breached": 0, "inactive": 0}
    for sla in slas:
        status_counts[sla.status.value] = status_counts.get(sla.status.value, 0) + 1
    
    return {
        "total_slas": total,
        "status_breakdown": status_counts,
        "overall_health": "healthy" if status_counts.get("breached", 0) == 0 else "degraded",
        "generated_at": None,
    }


@router.post(
    "/{sla_id}/acknowledge",
    status_code=status.HTTP_200_OK,
    summary="Acknowledge SLA breach",
    description="Acknowledge a breach event for an SLA.",
)
async def acknowledge_breach(sla_id: str) -> dict:
    """Acknowledge an SLA breach (placeholder)."""
    sla = await sla_service.get_sla(sla_id)
    if not sla:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SLA with ID '{sla_id}' not found",
        )
    
    # Placeholder - would update breach acknowledgment status
    return {
        "sla_id": sla_id,
        "acknowledged": True,
        "acknowledged_at": None,
        "acknowledged_by": None,
    }

