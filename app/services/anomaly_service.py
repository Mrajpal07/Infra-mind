"""Anomaly detection service using Z-score rolling window analysis.

Stateless and synchronous anomaly detection for CPU, memory, and GPU metrics.
No ML libraries or persistence required.
"""

import math
from typing import Optional

from pydantic import BaseModel, Field

from app.services.metric_service import MetricEntry, metric_service


# Default configuration
DEFAULT_WINDOW_SIZE = 10
DEFAULT_Z_THRESHOLD = 3.0


class AnomalyResult(BaseModel):
    """Result of anomaly detection analysis."""
    
    anomaly_detected: bool
    anomaly_metrics: list[str] = Field(default_factory=list)
    explanation: str
    confidence_score: float = Field(ge=0.0, le=1.0)


def _calculate_mean(values: list[float]) -> float:
    """Calculate arithmetic mean of values."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def _calculate_std(values: list[float], mean: float) -> float:
    """Calculate standard deviation of values."""
    if len(values) < 2:
        return 0.0
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


def _calculate_z_score(value: float, mean: float, std: float) -> float:
    """Calculate Z-score for a value."""
    if std == 0:
        return 0.0
    return abs(value - mean) / std


def _z_score_to_confidence(z_score: float, threshold: float) -> float:
    """Convert Z-score to confidence score (0.0–1.0).
    
    Higher Z-scores above threshold result in higher confidence.
    """
    if z_score <= threshold:
        return 0.0
    # Scale confidence: z_score at threshold = 0, z_score at 2x threshold = 1.0
    confidence = min((z_score - threshold) / threshold, 1.0)
    return round(confidence, 3)


def detect_anomaly(
    resource_id: str,
    window_size: int = DEFAULT_WINDOW_SIZE,
    z_threshold: float = DEFAULT_Z_THRESHOLD,
) -> AnomalyResult:
    """Detect anomalies in the latest metric using Z-score analysis.
    
    Analyzes CPU, memory, and GPU usage against a rolling window of
    historical metrics.
    
    Args:
        resource_id: The resource to analyze
        window_size: Number of historical metrics to use (default: 10)
        z_threshold: Z-score threshold for anomaly detection (default: 3.0)
    
    Returns:
        AnomalyResult with detection status, flagged metrics, and explanation
    
    Raises:
        ValueError: If resource_id is empty or parameters are invalid
    """
    if not resource_id or not resource_id.strip():
        raise ValueError("resource_id must be non-empty")
    if window_size < 2:
        raise ValueError("window_size must be at least 2")
    if z_threshold <= 0:
        raise ValueError("z_threshold must be positive")
    
    # Get latest metric
    latest = metric_service.get_latest_metric(resource_id)
    if latest is None:
        return AnomalyResult(
            anomaly_detected=False,
            anomaly_metrics=[],
            explanation=f"No metrics available for resource '{resource_id}'",
            confidence_score=0.0,
        )
    
    # Get historical metrics for rolling window
    # Use a large time window and limit by window_size
    historical = metric_service.get_metrics_last_n_minutes(resource_id, minutes=60)
    
    # Need at least window_size entries for meaningful analysis
    if len(historical) < window_size:
        return AnomalyResult(
            anomaly_detected=False,
            anomaly_metrics=[],
            explanation=f"Insufficient data: {len(historical)} metrics available, need {window_size}",
            confidence_score=0.0,
        )
    
    # Use the last window_size entries (excluding the latest for baseline)
    window = historical[-(window_size + 1):-1] if len(historical) > window_size else historical[:-1]
    
    if len(window) < 2:
        return AnomalyResult(
            anomaly_detected=False,
            anomaly_metrics=[],
            explanation="Insufficient baseline data for analysis",
            confidence_score=0.0,
        )
    
    # Analyze each metric type
    anomalies: list[str] = []
    z_scores: dict[str, float] = {}
    
    for metric_name in ["cpu_usage", "memory_usage", "gpu_usage"]:
        values = [getattr(m, metric_name) for m in window]
        current_value = getattr(latest, metric_name)
        
        mean = _calculate_mean(values)
        std = _calculate_std(values, mean)
        z_score = _calculate_z_score(current_value, mean, std)
        
        z_scores[metric_name] = z_score
        
        if z_score > z_threshold:
            anomalies.append(metric_name)
    
    # Calculate overall confidence score
    if anomalies:
        max_z = max(z_scores[m] for m in anomalies)
        confidence = _z_score_to_confidence(max_z, z_threshold)
    else:
        confidence = 0.0
    
    # Build explanation
    if anomalies:
        details = ", ".join(
            f"{m}: z={z_scores[m]:.2f}" for m in anomalies
        )
        explanation = f"Anomaly detected in {', '.join(anomalies)}. Z-scores: {details}. Threshold: {z_threshold}"
    else:
        explanation = f"All metrics within normal range (z-threshold: {z_threshold})"
    
    return AnomalyResult(
        anomaly_detected=len(anomalies) > 0,
        anomaly_metrics=anomalies,
        explanation=explanation,
        confidence_score=confidence,
    )
