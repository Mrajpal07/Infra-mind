"""SLA API endpoints.

Note: The /risk endpoint provides PREDICTIVE risk assessment,
not SLA compliance measurement.
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.core.prometheus import SLA_RISK_CHECKS, SLA_HIGH_RISK
from app.services.sla_risk_service import RiskLevel, RiskStatus, SLARiskResult, compute_sla_risk

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


@router.get(
    "/{resource_id}/risk",
    response_model=SLARiskResult,
    status_code=status.HTTP_200_OK,
    summary="Get SLA risk assessment",
    description="Compute predictive SLA risk based on recent metrics and anomaly detection. "
                "This estimates future breach likelihood, not current compliance.",
)
async def get_sla_risk(
    resource_id: str,
    lookback_minutes: int = Query(10, ge=1, le=60, description="Minutes of history to analyze"),
) -> SLARiskResult:
    """Compute predictive SLA risk for a resource.
    
    Raises:
        HTTPException 400: Invalid parameters
        HTTPException 404: Insufficient data
    """
    result = compute_sla_risk(resource_id, lookback_minutes=lookback_minutes)
    
    SLA_RISK_CHECKS.inc()
    
    if result.risk_level == RiskLevel.HIGH:
        SLA_HIGH_RISK.inc()
    
    if result.status == RiskStatus.INSUFFICIENT_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.explanation,
        )
    
    return result
