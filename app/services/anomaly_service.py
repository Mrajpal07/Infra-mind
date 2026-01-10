"""Anomaly detection service using Z-score rolling window analysis.

Algorithm: zscore_v1
- Uses sample standard deviation (n-1 denominator) for unbiased estimation
- Compares latest metric against a rolling window of historical data
- Window slicing excludes the latest metric to avoid data leakage

Z-score Behavior:
- When std=0 (constant baseline), z-score returns 0.0
- This means constant values are never flagged as anomalies
- A non-zero deviation from a constant baseline will be detected once
  variance exists in the historical window
"""

import math
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.services.metric_service import MetricEntry, metric_service


# Configuration
DEFAULT_WINDOW_SIZE = 10
DEFAULT_Z_THRESHOLD = 2.0
ALGORITHM_VERSION = "zscore_v1"


class AnomalyStatus(str, Enum):
    """Status of anomaly detection result."""
    OK = "OK"
    ANOMALY = "ANOMALY"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class AnomalyResult(BaseModel):
    """Result of anomaly detection analysis."""
    
    status: AnomalyStatus
    anomaly_detected: bool
    anomaly_metrics: list[str] = Field(default_factory=list)
    explanation: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    algorithm: str = ALGORITHM_VERSION


def _calculate_mean(values: list[float]) -> float:
    """Calculate arithmetic mean of values."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def _calculate_sample_std(values: list[float], mean: float) -> float:
    """Calculate sample standard deviation using (n-1) denominator.
    
    Uses Bessel's correction for unbiased estimation of population
    standard deviation from a sample.
    """
    n = len(values)
    if n < 2:
        return 0.0
    # Sample variance uses (n-1) denominator
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    return math.sqrt(variance)


def _calculate_z_score(value: float, mean: float, std: float) -> float:
    """Calculate Z-score for a value.
    
    Note: When std=0 (constant baseline), returns 0.0.
    This means a constant baseline will not trigger anomalies.
    """
    if std == 0:
        return 0.0
    return abs(value - mean) / std


def _z_score_to_confidence(z_score: float, threshold: float) -> float:
    """Convert Z-score to confidence score (0.0–1.0)."""
    if z_score <= threshold:
        return 0.0
    confidence = min((z_score - threshold) / threshold, 1.0)
    return round(confidence, 3)


def detect_anomaly(
    resource_id: str,
    window_size: int = DEFAULT_WINDOW_SIZE,
    z_threshold: float = DEFAULT_Z_THRESHOLD,
) -> AnomalyResult:
    """Detect anomalies in the latest metric using Z-score analysis.
    
    Args:
        resource_id: The resource to analyze
        window_size: Number of historical metrics for baseline (default: 10)
        z_threshold: Z-score threshold for anomaly detection (default: 2.0)
    
    Returns:
        AnomalyResult with status, detection flag, and explanation
    
    Raises:
        ValueError: If resource_id is empty or parameters are invalid
    """
    if not resource_id or not resource_id.strip():
        raise ValueError("resource_id must be non-empty")
    if window_size < 2:
        raise ValueError("window_size must be at least 2")
    if z_threshold <= 0:
        raise ValueError("z_threshold must be positive")
    
    # Get all historical metrics
    all_metrics = metric_service.get_metrics_last_n_minutes(resource_id, minutes=60)
    
    if not all_metrics:
        return AnomalyResult(
            status=AnomalyStatus.INSUFFICIENT_DATA,
            anomaly_detected=False,
            anomaly_metrics=[],
            explanation=f"No metrics available for resource '{resource_id}'",
            confidence_score=0.0,
        )
    
    # Need at least window_size + 1 entries (window + 1 to analyze)
    if len(all_metrics) < window_size + 1:
        return AnomalyResult(
            status=AnomalyStatus.INSUFFICIENT_DATA,
            anomaly_detected=False,
            anomaly_metrics=[],
            explanation=f"Insufficient data: {len(all_metrics)} metrics, need {window_size + 1}",
            confidence_score=0.0,
        )
    
    # Latest metric is the one we're analyzing
    latest = all_metrics[-1]
    
    # Window slicing: use previous N metrics, excluding latest
    # This avoids data leakage - we don't include the value we're testing
    # in the baseline statistics
    window = all_metrics[-(window_size + 1):-1]
    
    # Analyze each metric type
    anomalies: list[str] = []
    z_scores: dict[str, float] = {}
    details: dict[str, dict] = {}
    
    for metric_name in ["cpu_usage", "memory_usage", "gpu_usage"]:
        values = [getattr(m, metric_name) for m in window]
        current_value = getattr(latest, metric_name)
        
        mean = _calculate_mean(values)
        std = _calculate_sample_std(values, mean)
        z_score = _calculate_z_score(current_value, mean, std)
        
        z_scores[metric_name] = z_score
        details[metric_name] = {
            "current": current_value,
            "mean": round(mean, 2),
            "std": round(std, 2),
            "z_score": round(z_score, 2),
        }
        
        if z_score > z_threshold:
            anomalies.append(metric_name)
    
    # Determine status and confidence
    if anomalies:
        status = AnomalyStatus.ANOMALY
        max_z = max(z_scores[m] for m in anomalies)
        confidence = _z_score_to_confidence(max_z, z_threshold)
    else:
        status = AnomalyStatus.OK
        confidence = 0.0
    
    # Build explanation
    if anomalies:
        anomaly_details = []
        for m in anomalies:
            d = details[m]
            anomaly_details.append(
                f"{m}={d['current']} (mean={d['mean']}, std={d['std']}, z={d['z_score']})"
            )
        explanation = f"Anomaly detected: {'; '.join(anomaly_details)}. Threshold: {z_threshold}"
    else:
        max_z = max(z_scores.values()) if z_scores else 0
        explanation = f"All metrics normal. Max z-score: {max_z:.2f}, threshold: {z_threshold}"
    
    return AnomalyResult(
        status=status,
        anomaly_detected=len(anomalies) > 0,
        anomaly_metrics=anomalies,
        explanation=explanation,
        confidence_score=confidence,
    )
