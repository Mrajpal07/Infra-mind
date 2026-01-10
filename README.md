# Infra-Mind

Infrastructure monitoring and SLA management API built with FastAPI.

## Features

- **Versioned API** - All endpoints under `/api/v1`
- **Health Checks** - Basic, detailed, and Kubernetes probe endpoints
- **Authentication** - JWT-based OAuth2 authentication
- **Metrics API** - CRUD operations for infrastructure metrics
- **SLA Management** - Create, monitor, and check SLA compliance
- **Environment Config** - Pydantic-based configuration from environment variables

## Project Structure

```
infra-mind/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── metrics.py   # Metrics CRUD endpoints
│   │       ├── sla.py       # SLA management endpoints
│   │       └── health.py    # Health check endpoints
│   ├── core/
│   │   ├── config.py        # Application configuration
│   │   └── security.py      # Security utilities
│   ├── schemas/
│   │   ├── metric.py        # Metric Pydantic schemas
│   │   └── sla.py           # SLA Pydantic schemas
│   └── services/
│       ├── metric_service.py # Metric business logic
│       └── sla_service.py    # SLA business logic
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python -m app.main
```

### 5. Access the API

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### Health
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health with components
- `GET /api/v1/health/ready` - Kubernetes readiness probe
- `GET /api/v1/health/live` - Kubernetes liveness probe

### Authentication
- `POST /api/v1/auth/login` - Get access token
- `POST /api/v1/auth/register` - Register new user
- `GET /api/v1/auth/me` - Get current user info

### Metrics
- `POST /api/v1/metrics` - Create metric
- `GET /api/v1/metrics` - List metrics (paginated)
- `GET /api/v1/metrics/{id}` - Get metric by ID
- `PATCH /api/v1/metrics/{id}` - Update metric
- `DELETE /api/v1/metrics/{id}` - Delete metric

### SLA
- `POST /api/v1/sla` - Create SLA
- `GET /api/v1/sla` - List SLAs (paginated)
- `GET /api/v1/sla/{id}` - Get SLA by ID
- `PATCH /api/v1/sla/{id}` - Update SLA
- `DELETE /api/v1/sla/{id}` - Delete SLA
- `POST /api/v1/sla/{id}/check` - Check SLA compliance

## Demo Credentials

```
Email: admin@example.com
Password: admin123
```

## License

MIT
