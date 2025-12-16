"""FastAPI server for QuantStream RTQAE."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.logger import get_logger
from core.config import get_config

logger = get_logger("api.server")

# Global app state - shared across API routes
app_state = {
    'ws_client': None,
    'buffer': None,
    'analytics_engine': None,
    'alert_engine': None,
    'db_client': None,
    'resampler': None
}


def set_app_state(**kwargs):
    """Set application state components."""
    app_state.update(kwargs)


def get_app_state():
    """Get application state."""
    return app_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up QuantStream API server...")
    yield
    logger.info("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    # Import routers here to avoid circular imports
    from api.routes_ingestion import router as ingestion_router
    from api.routes_analytics import router as analytics_router
    from api.routes_export import router as export_router
    
    config = get_config().api

    app = FastAPI(
        title="QuantStream RTQAE API",
        description="Real-Time Quantitative Analytics Engine API",
        version="1.0.0",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(ingestion_router, prefix="/ingestion", tags=["Ingestion"])
    app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
    app.include_router(export_router, prefix="/export", tags=["Export"])

    @app.get("/health", tags=["System"])
    async def health_check():
        state = get_app_state()
        return {
            "status": "healthy",
            "ws_client_running": state.get('ws_client') is not None,
            "analytics_active": state.get('analytics_engine') is not None,
            "database_connected": state.get('db_client') is not None
        }

    @app.get("/", tags=["System"])
    async def root():
        return {"service": "QuantStream RTQAE", "version": "1.0.0", "status": "running"}

    logger.info("FastAPI application created")
    return app
