# Kaggler Dashboard Documentation

Real-time monitoring dashboard for GEPA evolution and competition progress tracking.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [WebSocket Protocol](#websocket-protocol)
- [Deployment Guide](#deployment-guide)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Overview

The Kaggler Dashboard provides real-time visualization and monitoring capabilities for genetic evolution competitions, including:

- **Real-time Evolution Charts**: Track best/mean scores, diversity metrics
- **Pareto Frontier Visualization**: Interactive scatter plots showing multi-objective optimization
- **Competition Management**: Start, stop, and monitor multiple competitions
- **Performance Metrics**: System resource usage and evaluation statistics
- **Responsive Design**: Modern dark theme with mobile support

## Architecture

### Tech Stack

**Backend (FastAPI)**:
- FastAPI for REST API and WebSocket support
- Pydantic for data validation
- asyncio for concurrent operations
- psutil for system metrics

**Frontend (React + TypeScript)**:
- React 18 with TypeScript
- Plotly.js for interactive charts
- TanStack Query for data fetching
- Zustand for state management
- Tailwind CSS for styling
- Vite for development and building

**Deployment**:
- Docker multi-stage builds
- Nginx reverse proxy
- Docker Compose orchestration

### Directory Structure

```
src/kaggler/dashboard/
├── backend/
│   ├── __init__.py
│   ├── app.py              # FastAPI application
│   ├── models.py           # Pydantic models
│   ├── routes.py           # API endpoints
│   └── websocket.py        # WebSocket handlers
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── EvolutionChart.tsx
│   │   │   ├── ParetoChart.tsx
│   │   │   └── CompetitionList.tsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts
│   │   ├── api.ts
│   │   ├── types.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── deployment/
│   └── nginx.conf
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Setup Instructions

### Local Development

#### Backend Setup

1. **Install Python dependencies**:

```bash
cd src/kaggler/dashboard
pip install -r requirements.txt
```

2. **Run the backend**:

```bash
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

3. **Access API documentation**:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

#### Frontend Setup

1. **Install Node dependencies**:

```bash
cd frontend
npm install
```

2. **Create environment file**:

```bash
cp .env.example .env
```

Edit `.env` to configure API endpoints:

```bash
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

3. **Run development server**:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Docker Deployment

#### Quick Start

1. **Build and run with Docker Compose**:

```bash
cd src/kaggler/dashboard
docker-compose up -d
```

2. **Access the dashboard**:
   - Frontend: `http://localhost`
   - API: `http://localhost:8000`

3. **View logs**:

```bash
docker-compose logs -f dashboard
```

4. **Stop services**:

```bash
docker-compose down
```

#### Production Deployment

1. **Update environment variables**:

Create a `.env` file:

```bash
# API Configuration
LOG_LEVEL=info
CORS_ORIGINS=https://your-domain.com

# Database (if using)
DB_PASSWORD=secure_password_here
```

2. **Configure SSL** (optional):

Place SSL certificates in `./ssl/`:
- `cert.pem`
- `key.pem`

Update `deployment/nginx.conf` to enable HTTPS.

3. **Build and deploy**:

```bash
docker-compose -f docker-compose.yml up -d --build
```

## API Documentation

### Base URL

```
http://localhost:8000/api
```

### Endpoints

#### GET `/competitions`

List all competitions with optional filtering.

**Query Parameters**:
- `status` (optional): Filter by status (`running`, `completed`, `stopped`, `failed`)
- `limit` (default: 100): Maximum number of results
- `offset` (default: 0): Offset for pagination

**Response**:
```json
[
  {
    "id": "uuid",
    "name": "Competition Name",
    "status": "running",
    "start_time": "2024-01-01T00:00:00",
    "end_time": null,
    "current_generation": 50,
    "total_generations": 100,
    "best_score": 0.9234,
    "pareto_size": 15
  }
]
```

#### GET `/competitions/{competition_id}`

Get detailed information about a specific competition.

**Response**:
```json
{
  "id": "uuid",
  "name": "Competition Name",
  "status": "running",
  "start_time": "2024-01-01T00:00:00",
  "current_generation": 50,
  "total_generations": 100,
  "best_score": 0.9234,
  "pareto_size": 15
}
```

#### GET `/evolution/{competition_id}`

Get evolution progress data for a competition.

**Query Parameters**:
- `start_generation` (default: 0): Start generation
- `end_generation` (optional): End generation

**Response**:
```json
{
  "competition_id": "uuid",
  "competition_name": "Competition Name",
  "current_generation": 50,
  "total_generations": 100,
  "is_running": true,
  "metrics_history": [
    {
      "generation": 0,
      "timestamp": "2024-01-01T00:00:00",
      "best_score": 0.85,
      "mean_score": 0.70,
      "std_score": 0.12,
      "diversity": 0.65,
      "pareto_size": 10,
      "computation_time": 2.34
    }
  ],
  "pareto_frontier": [
    {
      "id": "solution_id",
      "scores": {
        "accuracy": 0.92,
        "complexity": 0.78
      },
      "hyperparameters": {
        "learning_rate": 0.01,
        "max_depth": 5
      },
      "generation": 45,
      "dominated_count": 3
    }
  ]
}
```

#### POST `/compete`

Start a new competition.

**Request Body**:
```json
{
  "competition_name": "My Competition",
  "dataset_path": "/path/to/dataset",
  "population_size": 50,
  "generations": 100,
  "objectives": ["accuracy", "complexity"],
  "time_limit": 3600,
  "config": {
    "mutation_rate": 0.1
  }
}
```

**Response**:
```json
{
  "competition_id": "uuid",
  "status": "running",
  "message": "Competition started successfully"
}
```

#### POST `/compete/{competition_id}/stop`

Stop a running competition.

**Response**:
```json
{
  "message": "Competition stopped successfully"
}
```

#### DELETE `/compete/{competition_id}`

Delete a competition and its data.

**Response**:
```json
{
  "message": "Competition deleted successfully"
}
```

#### GET `/metrics`

Get system performance metrics.

**Response**:
```json
{
  "cpu_usage": 45.2,
  "memory_usage": 62.8,
  "active_competitions": 3,
  "total_evaluations": 15000,
  "uptime_seconds": 3600
}
```

## WebSocket Protocol

### Connection

**URL Pattern**:
- Competition-specific: `ws://localhost:8000/ws/evolution/{competition_id}`
- All competitions: `ws://localhost:8000/ws/evolution`

### Message Types

#### Client → Server

**Subscribe**:
```json
{
  "type": "subscribe",
  "competition_id": "uuid"
}
```

**Unsubscribe**:
```json
{
  "type": "unsubscribe",
  "competition_id": "uuid"
}
```

**Ping**:
```json
{
  "type": "ping"
}
```

#### Server → Client

**Connected**:
```json
{
  "type": "connected",
  "competition_id": "uuid",
  "timestamp": "2024-01-01T00:00:00"
}
```

**Generation Complete**:
```json
{
  "type": "generation_complete",
  "competition_id": "uuid",
  "generation": 50,
  "metrics": {
    "best_score": 0.92,
    "mean_score": 0.78,
    "diversity": 0.65
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

**Pareto Update**:
```json
{
  "type": "pareto_update",
  "competition_id": "uuid",
  "pareto_frontier": [...],
  "timestamp": "2024-01-01T00:00:00"
}
```

**Competition Complete**:
```json
{
  "type": "competition_complete",
  "competition_id": "uuid",
  "final_metrics": {
    "total_generations": 100,
    "best_score": 0.95,
    "pareto_size": 20
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

**Status Change**:
```json
{
  "type": "status_change",
  "competition_id": "uuid",
  "status": "stopped",
  "details": {
    "message": "Competition stopped by user"
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

**Error**:
```json
{
  "type": "error",
  "competition_id": "uuid",
  "error": "Error message",
  "timestamp": "2024-01-01T00:00:00"
}
```

### Connection Management

- **Reconnection**: Automatic reconnection with exponential backoff (max 5 attempts)
- **Keep-alive**: Ping/pong messages every 30 seconds
- **Timeout**: WebSocket connections timeout after 7 days of inactivity

## Deployment Guide

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

### Environment Configuration

Create `.env` file:

```bash
# Backend
LOG_LEVEL=info
CORS_ORIGINS=*

# Database (optional)
DB_PASSWORD=secure_password

# Frontend
VITE_API_URL=/api
VITE_WS_URL=/ws
```

### SSL Configuration

For HTTPS in production:

1. Obtain SSL certificates (Let's Encrypt, etc.)
2. Place certificates in `./ssl/`:
   - `cert.pem`
   - `key.pem`
3. Uncomment HTTPS server block in `deployment/nginx.conf`
4. Update frontend `.env`:
   ```bash
   VITE_API_URL=https://your-domain.com/api
   VITE_WS_URL=wss://your-domain.com
   ```

### Scaling

For high-traffic deployments:

1. **Horizontal scaling**:
   ```yaml
   # docker-compose.yml
   dashboard:
     deploy:
       replicas: 3
   ```

2. **Load balancing**: Configure Nginx upstream with multiple backend instances

3. **Database**: Enable PostgreSQL for persistent storage

4. **Caching**: Enable Redis for API response caching

### Monitoring

**Logs**:
```bash
docker-compose logs -f dashboard
docker-compose logs -f nginx
```

**Health checks**:
```bash
curl http://localhost:8000/health
curl http://localhost/health
```

**Metrics**:
```bash
curl http://localhost:8000/api/metrics
```

## Development

### Frontend Development

**Hot reload**:
```bash
cd frontend
npm run dev
```

**Type checking**:
```bash
npm run type-check
```

**Linting**:
```bash
npm run lint
```

**Build**:
```bash
npm run build
npm run preview  # Preview production build
```

### Backend Development

**Hot reload**:
```bash
uvicorn backend.app:app --reload
```

**Testing**:
```bash
pytest
pytest --cov=backend  # With coverage
```

### Adding New Features

#### New API Endpoint

1. Add Pydantic model to `backend/models.py`
2. Add route handler to `backend/routes.py`
3. Add API client method to `frontend/src/api.ts`
4. Add TypeScript types to `frontend/src/types.ts`

#### New Chart Component

1. Create component in `frontend/src/components/`
2. Use Plotly.js for visualization
3. Add to Dashboard component
4. Update types in `types.ts`

## Troubleshooting

### Common Issues

**WebSocket connection fails**:
- Check firewall settings
- Verify Nginx WebSocket proxy configuration
- Check browser console for CORS errors

**Charts not rendering**:
- Verify Plotly.js is loaded
- Check data format matches expected schema
- Inspect browser console for errors

**API returns 502 Bad Gateway**:
- Check backend is running: `docker-compose ps`
- View backend logs: `docker-compose logs dashboard`
- Verify Nginx configuration

**Frontend build fails**:
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (requires 18+)
- Verify TypeScript compilation: `npm run type-check`

**Docker container crashes**:
- Check logs: `docker-compose logs dashboard`
- Verify resource limits
- Check environment variables

### Performance Optimization

1. **Large datasets**: Implement pagination and data streaming
2. **Many competitions**: Use virtualized lists in React
3. **High-frequency updates**: Throttle WebSocket messages
4. **Chart performance**: Reduce data points for old generations

### Support

For issues and questions:
- GitHub Issues: [kagglerboze/issues](https://github.com/your-repo/kagglerboze/issues)
- Documentation: This file
- API Docs: `http://localhost:8000/docs`

---

**Version**: 1.0.0
**Last Updated**: 2024-01-13
