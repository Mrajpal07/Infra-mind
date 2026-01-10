# Infra-Mind

Infrastructure monitoring and SLA management API built with FastAPI.

## Project Overview

This is a Python FastAPI application for infrastructure monitoring with:
- RESTful API with versioning (`/api/v1`)
- JWT-based authentication
- Metrics collection and ingestion
- SLA (Service Level Agreement) management and compliance tracking

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Validation**: Pydantic 2.5+ with pydantic-settings
- **Auth**: JWT tokens via python-jose, password hashing via passlib
- **Server**: Uvicorn ASGI server

## Project Structure

```
infra-mind/
├── app/
│   ├── main.py                 # FastAPI app entry point, router mounting
│   ├── __init__.py
│   ├── api/v1/                 # API v1 endpoints
│   │   ├── auth.py             # Authentication (login, register, /me)
│   │   ├── health.py           # Health checks, K8s probes
│   │   ├── metrics.py          # Metrics CRUD
│   │   ├── sla.py              # SLA CRUD + compliance
│   │   └── ingestion.py        # Bulk metrics ingestion
│   ├── core/
│   │   ├── config.py           # Pydantic Settings (env-based config)
│   │   └── security.py         # JWT tokens, password hashing
│   ├── schemas/                # Pydantic request/response models
│   │   ├── metric.py
│   │   └── sla.py
│   └── services/               # Business logic layer
│       ├── metric_service.py
│       └── sla_service.py
├── requirements.txt
├── .env.example
└── README.md
```

## Key Patterns

### Configuration
All config via environment variables, loaded in `app/core/config.py`:
```python
from app.core.config import settings
settings.app_name  # "Infra-Mind"
settings.api_v1_prefix  # "/api/v1"
```

### Router Structure
Routers are mounted in `main.py` with versioned prefix:
```python
app.include_router(health.router, prefix=settings.api_v1_prefix)
```

### Service Layer
Business logic lives in `services/`. Services use in-memory storage (replace with DB):
```python
from app.services.metric_service import metric_service
await metric_service.create_metric(metric_data)
```

### Authentication
OAuth2 password flow with JWT:
```python
from app.api.v1.auth import get_current_user
@router.get("/protected")
async def protected(user: Annotated[UserResponse, Depends(get_current_user)]):
    ...
```

## API Endpoints

| Route | Description |
|-------|-------------|
| `GET /api/v1/health` | Health check |
| `POST /api/v1/auth/login` | Get JWT token |
| `POST /api/v1/auth/register` | Create user |
| `GET /api/v1/metrics` | List metrics |
| `POST /api/v1/metrics` | Create metric |
| `GET /api/v1/sla` | List SLAs |
| `POST /api/v1/sla/{id}/check` | Check SLA compliance |
| `POST /api/v1/ingest/metrics/batch` | Bulk ingest metrics |

## Running Locally

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

## Demo Credentials

```
Email: admin@example.com
Password: admin123
```

## Development Notes

- In-memory storage in services (replace with actual DB)
- Password hashing uses pbkdf2_sha256 (passlib)
- All datetime uses UTC timezone
- Schemas use `model_config = {"from_attributes": True}` for ORM compatibility
