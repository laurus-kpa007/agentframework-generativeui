"""Chat router with streaming support."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import logging

from models.schemas import ChatRequest, ChatMessage
from services.ollama_service import OllamaService
from services.streaming_service import StreamingService, StreamEvent

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple in-memory conversation storage (use Redis in production)
conversations: dict[str, List[ChatMessage]] = {}


async def get_ollama_service():
    """Dependency for Ollama service."""
    service = OllamaService()
    try:
        yield service
    finally:
        await service.close()


async def get_streaming_service():
    """Dependency for streaming service."""
    return StreamingService()


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    ollama: OllamaService = Depends(get_ollama_service),
    streaming: StreamingService = Depends(get_streaming_service)
):
    """Stream chat response with SSE."""
    logger.info(f"Chat request: {request.message[:50]}...")

    # Get or create conversation
    conversation_id = request.conversation_id or "default"
    if conversation_id not in conversations:
        conversations[conversation_id] = []

    # Add user message
    conversations[conversation_id].append(
        ChatMessage(role="user", content=request.message)
    )

    # Prepare messages for Ollama
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in conversations[conversation_id]
    ]

    async def event_generator():
        """Generate SSE events."""
        try:
            # Analyze intent (simplified for now)
            intent = await analyze_intent(request.message)
            logger.info(f"Detected intent: {intent}")

            # Generate UI component if applicable
            component_info = get_component_for_intent(intent)
            if component_info:
                yield StreamEvent.component(
                    component_info["name"],
                    component_info["props"]
                )

            # Stream text response
            response_text = ""
            async for chunk in ollama.stream_chat(messages):
                response_text += chunk
                yield StreamEvent.text(chunk)

            # Add assistant response to conversation
            conversations[conversation_id].append(
                ChatMessage(role="assistant", content=response_text)
            )

            yield StreamEvent.done()

        except Exception as e:
            logger.error(f"Chat streaming error: {e}")
            yield StreamEvent.error(str(e))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/message")
async def send_message(
    request: ChatRequest,
    ollama: OllamaService = Depends(get_ollama_service)
):
    """Send chat message (non-streaming)."""
    conversation_id = request.conversation_id or "default"
    if conversation_id not in conversations:
        conversations[conversation_id] = []

    # Add user message
    conversations[conversation_id].append(
        ChatMessage(role="user", content=request.message)
    )

    # Prepare messages
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in conversations[conversation_id]
    ]

    try:
        # Get response
        response_text = await ollama.chat(messages)

        # Add assistant response
        conversations[conversation_id].append(
            ChatMessage(role="assistant", content=response_text)
        )

        # Analyze intent and get component
        intent = await analyze_intent(request.message)
        component_info = get_component_for_intent(intent)

        return {
            "message": response_text,
            "conversation_id": conversation_id,
            "component": component_info,
            "metadata": {"intent": intent}
        }

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history."""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversation cleared"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


async def analyze_intent(message: str) -> str:
    """Analyze user intent (simplified)."""
    message_lower = message.lower()

    if any(word in message_lower for word in ["stock", "share", "price", "aapl", "nasdaq"]):
        return "stock_query"
    elif any(word in message_lower for word in ["weather", "temperature", "forecast"]):
        return "weather_query"
    elif any(word in message_lower for word in ["flight", "airplane", "airport"]):
        return "flight_query"
    elif any(word in message_lower for word in ["recipe", "cook", "food"]):
        return "recipe_query"
    elif any(word in message_lower for word in ["movie", "film", "cinema"]):
        return "movie_query"
    else:
        return "general"


def get_component_for_intent(intent: str) -> dict | None:
    """Get UI component info for intent."""
    component_map = {
        "stock_query": {
            "name": "StockCard",
            "props": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 150.25,
                "change": 2.5,
                "changePercent": 1.69
            }
        },
        "weather_query": {
            "name": "WeatherCard",
            "props": {
                "location": "Seoul, South Korea",
                "temperature": 15,
                "condition": "Partly cloudy",
                "humidity": 65,
                "windSpeed": 12
            }
        },
        "flight_query": {
            "name": "FlightCard",
            "props": {
                "flightNumber": "KE001",
                "airline": "Korean Air",
                "departure": "ICN",
                "arrival": "JFK",
                "departureTime": "14:00",
                "arrivalTime": "16:30",
                "status": "On Time"
            }
        }
    }

    return component_map.get(intent)
