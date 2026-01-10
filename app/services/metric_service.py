"""Metric service with in-memory time-series store.

Behavior Notes:
- Duplicate timestamps are allowed and stored in insertion order
- Metrics are stored per resource_id with a maximum retention limit
- Timestamps are normalized to timezone-aware UTC
"""

from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Optional

from pydantic import BaseModel, field_validator

# Configuration
MAX_ENTRIES_PER_RESOURCE = 10000


def _find_insertion_index(entries: list, timestamp: datetime) -> int:
    """Binary search to find insertion index for a timestamp.
    
    Returns the index where the entry should be inserted to maintain
    chronological order. For duplicate timestamps, returns the position
    after existing entries with the same timestamp.
    
    Args:
        entries: List of MetricEntry objects sorted by timestamp
        timestamp: The timestamp to find insertion position for
    
    Returns:
        Index where new entry should be inserted
    """
    left = 0
    right = len(entries)
    
    while left < right:
        mid = (left + right) // 2
        if entries[mid].timestamp <= timestamp:
            left = mid + 1
        else:
            right = mid
    
    return left


def _find_cutoff_index(entries: list, cutoff: datetime) -> int:
    """Binary search to find first entry at or after cutoff timestamp.
    
    Args:
        entries: List of MetricEntry objects sorted by timestamp
        cutoff: The minimum timestamp to include
    
    Returns:
        Index of first entry with timestamp >= cutoff
    """
    left = 0
    right = len(entries)
    
    while left < right:
        mid = (left + right) // 2
        if entries[mid].timestamp < cutoff:
            left = mid + 1
        else:
            right = mid
    
    return left


class MetricEntry(BaseModel):
    """Single metric entry with UTC timestamp validation."""
    
    resource_id: str
    cpu_usage: float
    memory_usage: float
    gpu_usage: float
    timestamp: datetime
    
    @field_validator("timestamp")
    @classmethod
    def normalize_to_utc(cls, v: datetime) -> datetime:
        """Normalize timestamp to timezone-aware UTC."""
        if v.tzinfo is None:
            # Naive datetime - assume UTC
            return v.replace(tzinfo=timezone.utc)
        # Convert to UTC
        return v.astimezone(timezone.utc)


class MetricService:
    """Thread-safe in-memory time-series metric store.
    
    Features:
    - Optimized insertion (append for chronological, binary search for out-of-order)
    - Retention policy limiting entries per resource
    - UTC timestamp normalization
    - Basic validation for resource_id and query parameters
    """
    
    def __init__(self):
        self._store: dict[str, list[MetricEntry]] = {}
        self._lock = Lock()
    
    def add_metric(self, metric: MetricEntry) -> None:
        """Add a metric entry to the store.
        
        Optimized for chronological insertion order.
        Duplicate timestamps are allowed.
        
        Raises:
            ValueError: If resource_id is empty
        """
        if not metric.resource_id or not metric.resource_id.strip():
            raise ValueError("resource_id must be non-empty")
        
        with self._lock:
            if metric.resource_id not in self._store:
                self._store[metric.resource_id] = []
            
            entries = self._store[metric.resource_id]
            
            # Optimized insertion: append if chronological, binary search if out-of-order
            if not entries or metric.timestamp >= entries[-1].timestamp:
                entries.append(metric)
            else:
                # Out-of-order: use binary search to find insertion position
                pos = _find_insertion_index(entries, metric.timestamp)
                entries.insert(pos, metric)
            
            # Enforce retention policy: keep only most recent entries
            if len(entries) > MAX_ENTRIES_PER_RESOURCE:
                self._store[metric.resource_id] = entries[-MAX_ENTRIES_PER_RESOURCE:]
    
    def get_latest_metric(self, resource_id: str) -> Optional[MetricEntry]:
        """Get the most recent metric for a resource.
        
        Raises:
            ValueError: If resource_id is empty
        """
        if not resource_id or not resource_id.strip():
            raise ValueError("resource_id must be non-empty")
        
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
        """Get all metrics from the last N minutes for a resource.
        
        Raises:
            ValueError: If resource_id is empty or minutes <= 0
        """
        if not resource_id or not resource_id.strip():
            raise ValueError("resource_id must be non-empty")
        if minutes <= 0:
            raise ValueError("minutes must be greater than 0")
        
        with self._lock:
            entries = self._store.get(resource_id, [])
            if not entries:
                return []
            
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            
            # Use binary search to find start position efficiently
            start_idx = _find_cutoff_index(entries, cutoff)
            
            return entries[start_idx:]


# Singleton instance
metric_service = MetricService()
