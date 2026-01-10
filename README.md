# Infra-Mind

Infrastructure monitoring and SLA management API built with FastAPI.

## Features

- **Metrics Ingestion** - Collect CPU, memory, and GPU usage metrics
- **Time-Series Storage** - In-memory store with timestamp ordering
- **SLA Monitoring** - Track SLA status for resources
- **Health Checks** - API health monitoring

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run the server
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** for interactive API documentation.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/metrics/ingest` | Ingest resource metrics |
| GET | `/api/v1/metrics/{resource_id}/latest` | Get latest metric |
| GET | `/api/v1/sla/{resource_id}` | Get SLA status |

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

**Validation:**
- `cpu_usage`, `memory_usage`, `gpu_usage`: 0-100 range
- `timestamp`: ISO 8601 datetime format

## Project Structure

```
infra-mind/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/v1/
│   │   ├── health.py        # Health endpoint
│   │   ├── metrics.py       # Metrics endpoints
│   │   └── sla.py           # SLA endpoint
│   ├── core/
│   │   └── config.py        # Environment config
│   └── services/
│       └── metric_service.py # Time-series store
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | infra-mind-api | Application name |
| `ENV` | development | Environment |
| `DEBUG` | true | Debug mode |

## License

MIT
