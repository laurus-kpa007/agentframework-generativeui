"""Streaming service for SSE events."""
import json
from typing import Dict, Any, AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class StreamEvent:
    """Helper class for creating SSE events."""

    @staticmethod
    def text(content: str) -> str:
        """Create text event."""
        event = {"type": "text", "content": content}
        return f"data: {json.dumps(event)}\n\n"

    @staticmethod
    def component(component: str, props: Dict[str, Any]) -> str:
        """Create component event."""
        event = {"type": "component", "component": component, "props": props}
        return f"data: {json.dumps(event)}\n\n"

    @staticmethod
    def tool_call(tool: str, status: str) -> str:
        """Create tool call event."""
        event = {"type": "tool_call", "tool": tool, "status": status}
        return f"data: {json.dumps(event)}\n\n"

    @staticmethod
    def error(message: str) -> str:
        """Create error event."""
        event = {"type": "error", "message": message}
        return f"data: {json.dumps(event)}\n\n"

    @staticmethod
    def done() -> str:
        """Create done event."""
        event = {"type": "done"}
        return f"data: {json.dumps(event)}\n\n"


class StreamingService:
    """Service for handling streaming responses."""

    async def stream_text_response(
        self,
        text_generator: AsyncGenerator[str, None]
    ) -> AsyncGenerator[str, None]:
        """Stream text chunks as SSE events."""
        try:
            async for chunk in text_generator:
                yield StreamEvent.text(chunk)

            yield StreamEvent.done()

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield StreamEvent.error(str(e))

    async def stream_chat_response(
        self,
        text_generator: AsyncGenerator[str, None],
        component: str = None,
        props: Dict[str, Any] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat response with optional UI component."""
        try:
            # Send UI component first if provided
            if component and props:
                yield StreamEvent.component(component, props)

            # Stream text content
            async for chunk in text_generator:
                yield StreamEvent.text(chunk)

            yield StreamEvent.done()

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield StreamEvent.error(str(e))
