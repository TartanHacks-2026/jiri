"""Jiri FastAPI Application.

Main entrypoint for the voice-first agentic bridge.
Provides:
- Health check endpoint
- WebSocket endpoints for voice streaming (future)
- RESTful API for tool management (future)
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from jiri.core.config import get_settings
from jiri.core.database import close_db, init_db
from jiri.core.logging import RequestLogger, logger, setup_logging
from jiri.core.redis_client import close_redis, init_redis
from jiri.routers import health, session, voice_turn

from session.store import session_store
>>>>>>> refs/remotes/origin/main


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Initializes and cleans up resources:
    - Database connection
    - Redis connection
    - Logging
    - Session Store (Legacy/Remote)
    """
    # Startup
    setup_logging()
    logger.info("Starting Jiri backend...")

    await init_db()
    logger.info("Database initialized")

    await init_redis()
    logger.info("Redis initialized")

    await session_store.connect()
    logger.info("Session store initialized")

    logger.info("Jiri backend started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Jiri backend...")
    await session_store.close()
    await close_redis()
    await close_db()
    logger.info("Jiri backend stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Jiri",
        description="Voice-first agentic bridge with MCP tool discovery",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # CORS middleware for development
    if settings.debug:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Request logging middleware
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next: any) -> Response:
        """Log all requests with timing and trace ID."""
        trace_id = request.headers.get("X-Trace-ID", str(uuid4())[:8])

        RequestLogger.log_request(
            method=request.method,
            path=request.url.path,
            trace_id=trace_id,
        )

        import time

        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000

        RequestLogger.log_response(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            trace_id=trace_id,
        )

        # Add trace ID to response headers
        response.headers["X-Trace-ID"] = trace_id

        return response

    # Include routers
    app.include_router(health.router)
<<<<<<< HEAD
    app.include_router(voice_turn.router)
=======
    app.include_router(turn.router)
>>>>>>> refs/remotes/origin/main

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
