"""Main FastAPI application for the dashboard."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .routes import router
from .websocket import websocket_endpoint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting dashboard application...")
    yield
    # Shutdown
    logger.info("Shutting down dashboard application...")


# Create FastAPI app
app = FastAPI(
    title="Kaggler Dashboard API",
    description="Real-time monitoring dashboard for GEPA evolution and competitions",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Kaggler Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "api": "/api",
            "websocket": "/ws/evolution/{competition_id}",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws/evolution/{competition_id}")
async def websocket_competition(websocket: WebSocket, competition_id: str):
    """WebSocket endpoint for competition-specific updates."""
    await websocket_endpoint(websocket, competition_id)


@app.websocket("/ws/evolution")
async def websocket_all(websocket: WebSocket):
    """WebSocket endpoint for all competitions."""
    await websocket_endpoint(websocket)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def main():
    """Run the application."""
    uvicorn.run(
        "kaggler.dashboard.backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
