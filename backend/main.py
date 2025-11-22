"""FastAPI main application."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from routers import health, chat, models, mcp
from services.ollama_service import OllamaService
from services.mcp_service import MCPService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
ollama_service = None
mcp_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global ollama_service, mcp_service
    logger.info("Starting application...")

    # Initialize and warmup Ollama
    ollama_service = OllamaService()
    await ollama_service.warmup()

    # Initialize MCP service
    mcp_service = MCPService()
    logger.info("MCP service initialized")

    yield

    # Cleanup
    logger.info("Shutting down application...")
    if mcp_service:
        await mcp_service.close()
    if ollama_service:
        await ollama_service.close()


# Create FastAPI app
app = FastAPI(
    title="Agent Framework + Generative UI",
    description="Integrated AI agent system with dynamic UI generation",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agent Framework + Generative UI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
