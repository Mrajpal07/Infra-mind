"""Metric service with in-memory time-series store."""

from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Optional

from pydantic import BaseModel


class MetricEntry(BaseModel):
    """Single metric entry."""
    
    resource_id: str
    cpu_usage: float
    memory_usage: float
    gpu_usage: float
    timestamp: datetime


class MetricService:
    """Thread-safe in-memory time-series metric store."""
    
    def __init__(self):
        self._store: dict[str, list[MetricEntry]] = {}
        self._lock = Lock()
    
    def add_metric(self, metric: MetricEntry) -> None:
        """Add a metric entry to the store."""
        with self._lock:
            if metric.resource_id not in self._store:
                self._store[metric.resource_id] = []
            
            # Insert in order by timestamp
            entries = self._store[metric.resource_id]
            entries.append(metric)
            entries.sort(key=lambda x: x.timestamp)
    
    def get_latest_metric(self, resource_id: str) -> Optional[MetricEntry]:
        """Get the most recent metric for a resource."""
        with self._lock:
            entries = self._store.get(resource_id, [])
            if not entries:
                return None
            return entries[-1]
    
    def get_metrics_last_n_minutes(
        self, 
        resource_id: str, 
        minutes: int
    ) -> list[MetricEntry]:
        """Get all metrics from the last N minutes for a resource."""
        with self._lock:
            entries = self._store.get(resource_id, [])
            if not entries:
                return []
            
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            return [e for e in entries if e.timestamp >= cutoff]


# Singleton instance
metric_service = MetricService()
