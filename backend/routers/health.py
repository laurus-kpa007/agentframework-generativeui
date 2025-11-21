"""Health check router."""
from fastapi import APIRouter, Depends
from datetime import datetime
import sys

from models.schemas import HealthResponse
from services.ollama_service import OllamaService

router = APIRouter()


async def get_ollama_service():
    """Dependency for Ollama service."""
    service = OllamaService()
    try:
        yield service
    finally:
        await service.close()


@router.get("/health", response_model=HealthResponse)
async def health_check(ollama: OllamaService = Depends(get_ollama_service)):
    """Health check endpoint."""
    ollama_connected = await ollama.check_connection()

    return HealthResponse(
        status="healthy" if ollama_connected else "degraded",
        timestamp=datetime.now(),
        version="1.0.0",
        ollama_connected=ollama_connected
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready", "timestamp": datetime.now()}
