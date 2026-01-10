"""Metric service for business logic."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.schemas.metric import MetricCreate, MetricResponse, MetricUpdate


class MetricService:
    """Service class for metric operations."""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # Replace with actual database in production
        self._metrics: dict[str, dict] = {}
    
    async def create_metric(self, metric: MetricCreate) -> MetricResponse:
        """Create a new metric."""
        metric_id = str(uuid4())
        metric_data = {
            "id": metric_id,
            "name": metric.name,
            "value": metric.value,
            "unit": metric.unit,
            "tags": metric.tags or {},
            "timestamp": datetime.now(timezone.utc),
        }
        self._metrics[metric_id] = metric_data
        return MetricResponse(**metric_data)
    
    async def get_metric(self, metric_id: str) -> Optional[MetricResponse]:
        """Get a metric by ID."""
        metric_data = self._metrics.get(metric_id)
        if metric_data:
            return MetricResponse(**metric_data)
        return None
    
    async def get_metrics(
        self, 
        page: int = 1, 
        page_size: int = 20,
        name_filter: Optional[str] = None
    ) -> tuple[list[MetricResponse], int]:
        """Get paginated list of metrics."""
        metrics = list(self._metrics.values())
        
        # Apply name filter if provided
        if name_filter:
            metrics = [m for m in metrics if name_filter.lower() in m["name"].lower()]
        
        total = len(metrics)
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated = metrics[start:end]
        
        return [MetricResponse(**m) for m in paginated], total
    
    async def update_metric(
        self, 
        metric_id: str, 
        metric_update: MetricUpdate
    ) -> Optional[MetricResponse]:
        """Update a metric."""
        if metric_id not in self._metrics:
            return None
        
        update_data = metric_update.model_dump(exclude_unset=True)
        self._metrics[metric_id].update(update_data)
        
        return MetricResponse(**self._metrics[metric_id])
    
    async def delete_metric(self, metric_id: str) -> bool:
        """Delete a metric."""
        if metric_id in self._metrics:
            del self._metrics[metric_id]
            return True
        return False


# Singleton instance
metric_service = MetricService()
