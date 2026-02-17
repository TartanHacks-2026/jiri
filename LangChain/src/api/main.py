"""Jiri - FastAPI Voice Backend."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.session import session_store

from .turn import router as turn_router

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup: Connect to Redis
    await session_store.connect()
    yield
    # Shutdown: Close Redis connection
    await session_store.close()


app = FastAPI(
    title="Jiri Voice Backend",
    description="Voice-first agentic bridge with Siri Shortcut integration",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS - allow all for demo/hackathon
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(turn_router)


@app.get("/health")
async def health():
    """Health check endpoint for Docker and load balancers."""
    return {"status": "healthy", "service": "jiri"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Jiri Voice Backend",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "POST /turn": "Main conversation endpoint for Siri Shortcut",
            "GET /health": "Health check",
        },
    }
