"""Models router for LLM management."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
import logging

from services.ollama_service import OllamaService

router = APIRouter()
logger = logging.getLogger(__name__)


class ModelInfo(BaseModel):
    """Model information."""
    name: str
    size: int | str  # Can be int (bytes) or str
    modified_at: str


class ModelsListResponse(BaseModel):
    """Models list response."""
    models: List[ModelInfo]
    current_model: str


class ModelSelectRequest(BaseModel):
    """Model selection request."""
    model: str


async def get_ollama_service():
    """Dependency for Ollama service."""
    service = OllamaService()
    try:
        yield service
    finally:
        await service.close()


@router.get("/list", response_model=ModelsListResponse)
async def list_models(ollama: OllamaService = Depends(get_ollama_service)):
    """List available Ollama models."""
    try:
        models_data = await ollama.list_models_detailed()

        return ModelsListResponse(
            models=[
                ModelInfo(
                    name=model["name"],
                    size=str(model.get("size", "unknown")),
                    modified_at=model.get("modified_at", "")
                )
                for model in models_data
            ],
            current_model=ollama.model
        )
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select")
async def select_model(
    request: ModelSelectRequest,
    ollama: OllamaService = Depends(get_ollama_service)
):
    """Select active model."""
    try:
        # Verify model exists
        available_models = await ollama.list_models()

        if request.model not in available_models:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{request.model}' not found. Available models: {', '.join(available_models)}"
            )

        # Set model
        ollama.set_model(request.model)

        logger.info(f"Model changed to: {request.model}")

        return {
            "success": True,
            "message": f"Model changed to {request.model}",
            "model": request.model
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to select model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current")
async def get_current_model(ollama: OllamaService = Depends(get_ollama_service)):
    """Get currently selected model."""
    return {
        "model": ollama.model,
        "base_url": ollama.base_url
    }
