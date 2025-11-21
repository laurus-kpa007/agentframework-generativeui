"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "info"

    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:latest"
    OLLAMA_TIMEOUT: int = 60

    # MCP Settings
    MCP_CONFIG_PATH: str = "./config/mcp_servers.yaml"
    NODE_PATH: Optional[str] = None

    # Security
    API_SECRET_KEY: str = "change-this-in-production-use-secrets"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # Performance
    TTFT_TARGET_MS: int = 500  # Time to First Token target

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


settings = Settings()
