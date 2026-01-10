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
│   ├── main.py              # FastAPI app, router mounting, startup logs
│   ├── api/v1/
│   │   ├── health.py        # GET /health
│   │   ├── metrics.py       # POST /metrics/ingest
│   │   └── sla.py           # GET /sla/{resource_id}
│   └── core/
│       └── config.py        # Environment config (APP_NAME, ENV, DEBUG)
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration

Environment variables loaded via pydantic-settings in `app/core/config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | infra-mind-api | Application name |
| `ENV` | development | Environment |
| `DEBUG` | true | Debug mode |

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/metrics/ingest` | Ingest resource metrics |
| GET | `/api/v1/sla/{resource_id}` | Get SLA status |

## Running Locally

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs
