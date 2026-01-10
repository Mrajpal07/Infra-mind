# Infra-Mind

Infrastructure monitoring, metrics ingestion, and anomaly detection API.

## Features

- **Metrics Ingestion** - Collect CPU, memory, GPU usage with validation
- **Time-Series Storage** - In-memory store with binary search optimization
- **Anomaly Detection** - Z-score based detection with configurable thresholds
- **SLA Monitoring** - Track SLA status for resources

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** for API documentation.

## API Endpoints

### Health
```
GET /api/v1/health
```

### Metrics
```
POST /api/v1/metrics/ingest          # Ingest metrics
GET  /api/v1/metrics/{id}/latest     # Get latest metric
GET  /api/v1/metrics/{id}/analyze    # Anomaly detection
GET  /api/v1/metrics/{id}/debug      # Debug: view stored metrics
```

### SLA
```
GET /api/v1/sla/{resource_id}        # Get SLA status
```

## Metrics Ingestion

**POST** `/api/v1/metrics/ingest`
```json
{
  "resource_id": "server-001",
  "cpu_usage": 45.5,
  "memory_usage": 60.2,
  "gpu_usage": 30.0,
  "timestamp": "2026-01-10T09:30:00Z"
}
```

Validation: `cpu_usage`, `memory_usage`, `gpu_usage` must be 0-100.

## Anomaly Detection

**GET** `/api/v1/metrics/{resource_id}/analyze?window_size=10`

```json
{
  "status": "ANOMALY",
  "anomaly_detected": true,
  "anomaly_metrics": ["cpu_usage"],
  "explanation": "Anomaly detected: cpu_usage=95 (mean=47.5, std=2.5, z=19.0)",
  "confidence_score": 1.0,
  "algorithm": "zscore_v1"
}
```

**Algorithm**: Z-score with sample standard deviation (n-1)  
**Status values**: `OK`, `ANOMALY`, `INSUFFICIENT_DATA`

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | infra-mind-api | Application name |
| `ENV` | development | Environment |
| `DEBUG` | true | Debug mode |

## License

MIT
