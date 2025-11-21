"""Ollama LLM service."""
import httpx
from typing import Optional, AsyncGenerator, List, Dict, Any
import logging
import time

from config.settings import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama LLM."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout)
        )
        self._warmed_up = False
        logger.info(f"Initialized Ollama service: {self.base_url}, model: {self.model}")

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """Generate text completion."""
        start_time = time.time()

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }

        if system:
            payload["system"] = system

        try:
            response = await self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Generate completed in {elapsed:.0f}ms")

            return data.get("response", "")

        except httpx.HTTPError as e:
            logger.error(f"Ollama request failed: {e}")
            raise

    async def stream_generate(
        self,
        prompt: str,
        system: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream text completion."""
        start_time = time.time()
        first_token = True

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }

        if system:
            payload["system"] = system

        try:
            async with self.client.stream("POST", "/api/generate", json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)

                        if first_token:
                            ttft = (time.time() - start_time) * 1000
                            logger.info(f"TTFT: {ttft:.0f}ms (target: {settings.TTFT_TARGET_MS}ms)")
                            first_token = False

                        if "response" in data:
                            yield data["response"]

        except httpx.HTTPError as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """Chat completion."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }

        try:
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            return data.get("message", {}).get("content", "")

        except httpx.HTTPError as e:
            logger.error(f"Ollama chat failed: {e}")
            raise

    async def stream_chat(
        self,
        messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion."""
        start_time = time.time()
        first_token = True

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        try:
            async with self.client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)

                        if first_token:
                            ttft = (time.time() - start_time) * 1000
                            logger.info(f"TTFT: {ttft:.0f}ms")
                            first_token = False

                        if "message" in data:
                            content = data["message"].get("content", "")
                            if content:
                                yield content

        except httpx.HTTPError as e:
            logger.error(f"Ollama streaming chat failed: {e}")
            raise

    async def check_connection(self) -> bool:
        """Check Ollama connection."""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            logger.error(f"Ollama connection check failed: {e}")
            return False

    async def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except httpx.HTTPError as e:
            logger.error(f"Failed to list models: {e}")
            return []

    async def list_models_detailed(self) -> List[Dict[str, Any]]:
        """List available models with details."""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except httpx.HTTPError as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def set_model(self, model: str):
        """Set the active model."""
        self.model = model
        self._warmed_up = False  # Reset warmup state
        logger.info(f"Model set to: {model}")

    async def warmup(self):
        """Warm up the model for faster first response."""
        if self._warmed_up:
            logger.info("Model already warmed up")
            return

        logger.info("Warming up Ollama model...")
        try:
            start = time.time()
            await self.generate(
                prompt="Hi",
                system="Respond with just 'Hello'"
            )
            elapsed = (time.time() - start) * 1000
            logger.info(f"Warmup complete in {elapsed:.0f}ms")
            self._warmed_up = True
        except Exception as e:
            logger.error(f"Warmup failed: {e}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("Ollama service closed")
