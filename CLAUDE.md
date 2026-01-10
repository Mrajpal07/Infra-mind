# Infra-Mind

Infrastructure monitoring, metrics ingestion, and anomaly detection API built with FastAPI.

## Tech Stack

- **Framework**: FastAPI
- **Validation**: Pydantic + pydantic-settings
- **Server**: Uvicorn

## Project Structure

```
infra-mind/
├── app/
│   ├── main.py                  # FastAPI app, router mounting
│   ├── api/v1/
│   │   ├── health.py            # GET /health
│   │   ├── metrics.py           # Metrics ingestion & analysis
│   │   └── sla.py               # GET /sla/{resource_id}
│   ├── core/
│   │   └── config.py            # Environment config
│   └── services/
│       ├── metric_service.py    # In-memory time-series store
│       └── anomaly_service.py   # Z-score anomaly detection
├── requirements.txt
└── .env.example
```

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/metrics/ingest` | Ingest metrics |
| GET | `/api/v1/metrics/{id}/latest` | Latest metric |
| GET | `/api/v1/metrics/{id}/analyze` | Anomaly detection |
| GET | `/api/v1/metrics/{id}/debug` | Debug: view stored metrics |
| GET | `/api/v1/sla/{resource_id}` | SLA status |

## Anomaly Detection

**Algorithm**: `zscore_v1`
- Rolling window Z-score analysis
- Sample standard deviation (n-1 denominator)
- Configurable window_size and z_threshold

**Status values**: `OK`, `ANOMALY`, `INSUFFICIENT_DATA`

```python
from app.services.anomaly_service import detect_anomaly

result = detect_anomaly("server-001", window_size=10, z_threshold=2.0)
# result.status, result.anomaly_detected, result.algorithm
```

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs
