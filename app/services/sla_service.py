"""SLA service for business logic."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.schemas.sla import SLACreate, SLAResponse, SLAStatus, SLAUpdate


class SLAService:
    """Service class for SLA operations."""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # Replace with actual database in production
        self._slas: dict[str, dict] = {}
    
    async def create_sla(self, sla: SLACreate) -> SLAResponse:
        """Create a new SLA."""
        sla_id = str(uuid4())
        now = datetime.now(timezone.utc)
        
        sla_data = {
            "id": sla_id,
            "name": sla.name,
            "description": sla.description,
            "target_value": sla.target_value,
            "warning_threshold": sla.warning_threshold,
            "metric_name": sla.metric_name,
            "status": SLAStatus.ACTIVE,
            "current_value": None,
            "compliance_percentage": None,
            "created_at": now,
            "updated_at": now,
        }
        self._slas[sla_id] = sla_data
        return SLAResponse(**sla_data)
    
    async def get_sla(self, sla_id: str) -> Optional[SLAResponse]:
        """Get an SLA by ID."""
        sla_data = self._slas.get(sla_id)
        if sla_data:
            return SLAResponse(**sla_data)
        return None
    
    async def get_slas(
        self, 
        page: int = 1, 
        page_size: int = 20,
        status_filter: Optional[SLAStatus] = None
    ) -> tuple[list[SLAResponse], int]:
        """Get paginated list of SLAs."""
        slas = list(self._slas.values())
        
        # Apply status filter if provided
        if status_filter:
            slas = [s for s in slas if s["status"] == status_filter]
        
        total = len(slas)
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated = slas[start:end]
        
        return [SLAResponse(**s) for s in paginated], total
    
    async def update_sla(
        self, 
        sla_id: str, 
        sla_update: SLAUpdate
    ) -> Optional[SLAResponse]:
        """Update an SLA."""
        if sla_id not in self._slas:
            return None
        
        update_data = sla_update.model_dump(exclude_unset=True)
        self._slas[sla_id].update(update_data)
        self._slas[sla_id]["updated_at"] = datetime.now(timezone.utc)
        
        return SLAResponse(**self._slas[sla_id])
    
    async def delete_sla(self, sla_id: str) -> bool:
        """Delete an SLA."""
        if sla_id in self._slas:
            del self._slas[sla_id]
            return True
        return False
    
    async def check_sla_compliance(self, sla_id: str, current_value: float) -> Optional[SLAResponse]:
        """Check SLA compliance and update status."""
        if sla_id not in self._slas:
            return None
        
        sla = self._slas[sla_id]
        sla["current_value"] = current_value
        
        # Calculate compliance percentage
        if sla["target_value"] > 0:
            compliance = (current_value / sla["target_value"]) * 100
            sla["compliance_percentage"] = min(compliance, 100.0)
        
        # Update status based on compliance
        if compliance >= 100:
            sla["status"] = SLAStatus.ACTIVE
        elif compliance >= sla["warning_threshold"]:
            sla["status"] = SLAStatus.WARNING
        else:
            sla["status"] = SLAStatus.BREACHED
        
        sla["updated_at"] = datetime.now(timezone.utc)
        
        return SLAResponse(**sla)


# Singleton instance
sla_service = SLAService()
