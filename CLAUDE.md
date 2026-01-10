# Infra-Mind

Infrastructure monitoring and SLA management API built with FastAPI.

## Tech Stack

- **Framework**: FastAPI
- **Validation**: Pydantic + pydantic-settings
- **Server**: Uvicorn

## Project Structure

```
infra-mind/
├── app/
│   ├── main.py              # FastAPI app, router mounting
│   ├── api/v1/
│   │   ├── health.py        # GET /health
│   │   ├── metrics.py       # POST /ingest, GET /latest
│   │   └── sla.py           # GET /sla/{resource_id}
│   ├── core/
│   │   └── config.py        # Environment config
│   └── services/
│       └── metric_service.py # In-memory time-series store
├── requirements.txt
└── .env.example
```

## Configuration

Environment variables in `app/core/config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | infra-mind-api | Application name |
| `ENV` | development | Environment |
| `DEBUG` | true | Debug mode |

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/metrics/ingest` | Ingest metrics |
| GET | `/api/v1/metrics/{id}/latest` | Latest metric |
| GET | `/api/v1/sla/{resource_id}` | SLA status |

## Metric Service

Thread-safe in-memory store in `app/services/metric_service.py`:

```python
from app.services.metric_service import metric_service

metric_service.add_metric(entry)
metric_service.get_latest_metric(resource_id)
metric_service.get_metrics_last_n_minutes(resource_id, 5)
```

## Running Locally

```bash
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs
