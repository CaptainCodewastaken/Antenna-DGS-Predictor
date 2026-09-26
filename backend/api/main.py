"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
import logging
import json
import uuid
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.api.dependencies import load_models, get_registry
from backend.api.routes import router

# Configure structured JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        if hasattr(record, "path"):
            log_obj["path"] = record.path
        if hasattr(record, "status_code"):
            log_obj["status_code"] = record.status_code
            
        return json.dumps(log_obj)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)

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
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Observability Middleware: Request ID and RED logging
@app.middleware("http")
async def observability_middleware(request: Request, call_next: Callable):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.perf_counter()
    
    response = await call_next(request)
    
    process_time_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    
    # Log structured event
    log_extra = {
        "request_id": request_id,
        "duration_ms": round(process_time_ms, 2),
        "path": request.url.path,
        "status_code": response.status_code
    }
    
    if response.status_code >= 500:
        logger.error(f"Request failed", extra=log_extra)
    else:
        logger.info(f"Request processed", extra=log_extra)
        
    return response

@app.get("/health")
def health_check():
    """Health check endpoint for launch readiness."""
    return {"status": "ok", "service": "antenna-dgs-predictor"}

app.include_router(router, prefix="/api")
