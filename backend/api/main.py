"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.dependencies import load_models, get_registry
from backend.api.routes import router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML models on startup
    logger.info("Starting up FastAPI - loading ML models...")
    load_models()
    registry = get_registry()
    if not registry.models:
        logger.warning("No ML models loaded! Ensure they are trained and in backend/data/models/")
    yield
    # Cleanup on shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Antenna DGS Predictor API",
    description="Physics engine and ML models for Microstrip Antenna design with Defected Ground Structures.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
