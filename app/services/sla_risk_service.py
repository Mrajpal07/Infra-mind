"""SLA Risk assessment service.

This service provides PREDICTIVE RISK assessment, not SLA compliance measurement.
It estimates the likelihood of future SLA breaches based on recent metrics patterns.

Risk is computed from:
- Anomaly presence from anomaly_service (40% weight)
- Threshold breach rate in recent metrics (60% weight)

Risk scoring is deterministic and explainable.
No persistence or ML models used.
"""

from enum import Enum

from pydantic import BaseModel, Field

from app.services.anomaly_service import detect_anomaly, AnomalyStatus
from app.services.metric_service import metric_service


# SLA Thresholds (configurable)
DEFAULT_CPU_THRESHOLD = 80.0
DEFAULT_MEMORY_THRESHOLD = 85.0
DEFAULT_GPU_THRESHOLD = 90.0

# Risk level boundaries
RISK_LOW_THRESHOLD = 0.3
RISK_HIGH_THRESHOLD = 0.6


class RiskStatus(str, Enum):
    """Status of risk assessment."""
    OK = "OK"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class RiskLevel(str, Enum):
    """SLA risk level classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskSignal(BaseModel):
    """Individual signal contributing to risk score."""
    
    name: str
    value: float
    weight: float
    contribution: float


class SLARiskResult(BaseModel):
    """Result of SLA risk assessment.
    
    Note: This is predictive risk, not SLA compliance.
    """
    
    status: RiskStatus
    resource_id: str
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    signals: list[RiskSignal] = Field(default_factory=list)
    explanation: str


def _calculate_threshold_breach_rate(
    metrics: list,
    cpu_threshold: float,
    memory_threshold: float,
    gpu_threshold: float,
) -> tuple[float, dict]:
    """Calculate percentage of metrics exceeding thresholds."""
    if not metrics:
        return 0.0, {"samples_checked": 0}
    
    cpu_breaches = sum(1 for m in metrics if m.cpu_usage > cpu_threshold)
    memory_breaches = sum(1 for m in metrics if m.memory_usage > memory_threshold)
    gpu_breaches = sum(1 for m in metrics if m.gpu_usage > gpu_threshold)
    
    total_checks = len(metrics) * 3
    total_breaches = cpu_breaches + memory_breaches + gpu_breaches
    
    breach_rate = total_breaches / total_checks if total_checks > 0 else 0.0
    
    details = {
        "cpu_breach_pct": round(cpu_breaches / len(metrics) * 100, 1),
        "memory_breach_pct": round(memory_breaches / len(metrics) * 100, 1),
        "gpu_breach_pct": round(gpu_breaches / len(metrics) * 100, 1),
        "samples_checked": len(metrics),
    }
    
    return breach_rate, details


def compute_sla_risk(
    resource_id: str,
    lookback_minutes: int = 10,
    cpu_threshold: float = DEFAULT_CPU_THRESHOLD,
    memory_threshold: float = DEFAULT_MEMORY_THRESHOLD,
    gpu_threshold: float = DEFAULT_GPU_THRESHOLD,
) -> SLARiskResult:
    """Compute predictive SLA risk score for a resource.
    
    This estimates future SLA breach likelihood, not current compliance.
    
    Args:
        resource_id: Resource to assess
        lookback_minutes: Minutes of history to analyze
        cpu_threshold: CPU usage threshold (default: 80%)
        memory_threshold: Memory usage threshold (default: 85%)
        gpu_threshold: GPU usage threshold (default: 90%)
    
    Returns:
        SLARiskResult with status, score, level, signals, and explanation
    
    Raises:
        ValueError: If resource_id is empty or parameters invalid
    """
    if not resource_id or not resource_id.strip():
        raise ValueError("resource_id must be non-empty")
    if lookback_minutes <= 0:
        raise ValueError("lookback_minutes must be positive")
    
    # Get metrics for analysis
    metrics = metric_service.get_metrics_last_n_minutes(resource_id, lookback_minutes)
    
    # Check for sufficient data
    if not metrics:
        return SLARiskResult(
            status=RiskStatus.INSUFFICIENT_DATA,
            resource_id=resource_id,
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            signals=[],
            explanation=f"No metrics available for resource '{resource_id}'",
        )
    
    signals: list[RiskSignal] = []
    
    # Signal 1: Anomaly presence (40% weight)
    # INSUFFICIENT_DATA from anomaly detection is treated as non-anomalous
    anomaly_weight = 0.4
    anomaly_result = detect_anomaly(resource_id)
    
    if anomaly_result.status == AnomalyStatus.ANOMALY:
        anomaly_score = anomaly_result.confidence_score
    else:
        # OK or INSUFFICIENT_DATA treated as no anomaly
        anomaly_score = 0.0
    
    anomaly_contribution = anomaly_score * anomaly_weight
    signals.append(RiskSignal(
        name="anomaly_presence",
        value=round(anomaly_score, 3),
        weight=anomaly_weight,
        contribution=round(anomaly_contribution, 3),
    ))
    
    # Signal 2: Threshold breach rate (60% weight)
    breach_weight = 0.6
    breach_rate, breach_details = _calculate_threshold_breach_rate(
        metrics, cpu_threshold, memory_threshold, gpu_threshold
    )
    
    breach_contribution = breach_rate * breach_weight
    signals.append(RiskSignal(
        name="threshold_breach_rate",
        value=round(breach_rate, 3),
        weight=breach_weight,
        contribution=round(breach_contribution, 3),
    ))
    
    # Calculate total risk score
    risk_score = min(anomaly_contribution + breach_contribution, 1.0)
    risk_score = round(risk_score, 3)
    
    # Map to risk level
    if risk_score < RISK_LOW_THRESHOLD:
        risk_level = RiskLevel.LOW
    elif risk_score < RISK_HIGH_THRESHOLD:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.HIGH
    
    # Build explanation
    explanation_parts = []
    
    if anomaly_score > 0:
        explanation_parts.append(f"Anomaly detected (confidence: {anomaly_score:.0%})")
    
    samples = breach_details.get("samples_checked", 0)
    cpu_pct = breach_details.get("cpu_breach_pct", 0)
    mem_pct = breach_details.get("memory_breach_pct", 0)
    gpu_pct = breach_details.get("gpu_breach_pct", 0)
    
    if breach_rate > 0:
        explanation_parts.append(
            f"Threshold breaches in {samples} samples: "
            f"CPU>{cpu_threshold}%: {cpu_pct}%, "
            f"Memory>{memory_threshold}%: {mem_pct}%, "
            f"GPU>{gpu_threshold}%: {gpu_pct}%"
        )
    else:
        explanation_parts.append(f"No threshold breaches in {samples} samples")
    
    explanation = f"Predictive risk {risk_level.value} ({risk_score:.0%}). " + "; ".join(explanation_parts)
    
    return SLARiskResult(
        status=RiskStatus.OK,
        resource_id=resource_id,
        risk_score=risk_score,
        risk_level=risk_level,
        signals=signals,
        explanation=explanation,
    )
