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

    if any(word in message_lower for word in ["stock", "share", "price", "aapl", "nasdaq", "trading"]):
        return "stock_query"
    elif any(word in message_lower for word in ["weather", "temperature", "forecast", "climate"]):
        return "weather_query"
    elif any(word in message_lower for word in ["flight", "airplane", "airport", "airline"]):
        return "flight_query"
    elif any(word in message_lower for word in ["recipe", "cook", "cooking", "food", "dish", "ingredient"]):
        return "recipe_query"
    elif any(word in message_lower for word in ["movie", "film", "cinema", "actor", "director"]):
        return "movie_query"
    elif any(word in message_lower for word in ["product", "buy", "shop", "shopping", "purchase"]):
        return "product_query"
    elif any(word in message_lower for word in ["hotel", "accommodation", "booking", "stay"]):
        return "hotel_query"
    elif any(word in message_lower for word in ["restaurant", "dine", "dining", "eat", "reservation"]):
        return "restaurant_query"
    elif any(word in message_lower for word in ["book", "read", "reading", "author", "novel"]):
        return "book_query"
    elif any(word in message_lower for word in ["news", "article", "headline", "breaking"]):
        return "news_query"
    elif any(word in message_lower for word in ["event", "concert", "show", "performance", "ticket"]):
        return "event_query"
    elif any(word in message_lower for word in ["exercise", "workout", "fitness", "gym", "training"]):
        return "exercise_query"
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
        },
        "recipe_query": {
            "name": "RecipeCard",
            "props": {
                "title": "Spaghetti Carbonara",
                "description": "Classic Italian pasta dish with eggs, cheese, and bacon",
                "prepTime": 10,
                "cookTime": 20,
                "servings": 4,
                "difficulty": "Easy",
                "ingredients": [
                    "400g spaghetti",
                    "200g bacon",
                    "4 eggs",
                    "100g Parmesan cheese",
                    "Black pepper",
                    "Salt"
                ]
            }
        },
        "movie_query": {
            "name": "MovieCard",
            "props": {
                "title": "The Shawshank Redemption",
                "year": 1994,
                "rating": 9.3,
                "genre": ["Drama", "Crime"],
                "runtime": 142,
                "director": "Frank Darabont",
                "plot": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency."
            }
        },
        "product_query": {
            "name": "ProductCard",
            "props": {
                "name": "Wireless Bluetooth Headphones",
                "price": 79.99,
                "originalPrice": 129.99,
                "rating": 4.5,
                "reviews": 1234,
                "description": "Premium noise-cancelling headphones with 30-hour battery life",
                "category": "Electronics",
                "inStock": True
            }
        },
        "hotel_query": {
            "name": "HotelCard",
            "props": {
                "name": "Grand Plaza Hotel",
                "location": "Seoul, South Korea",
                "rating": 5,
                "reviews": 892,
                "pricePerNight": 150,
                "amenities": ["wifi", "breakfast", "tv", "gym", "pool"],
                "description": "Luxury hotel in the heart of Seoul with stunning city views"
            }
        },
        "restaurant_query": {
            "name": "RestaurantCard",
            "props": {
                "name": "Sushi Master",
                "cuisine": "Japanese",
                "location": "123 Main St, Tokyo",
                "rating": 4.8,
                "reviews": 567,
                "priceRange": 3,
                "openNow": True,
                "hours": "11:00 AM - 10:00 PM",
                "description": "Authentic Japanese sushi restaurant with fresh seafood daily"
            }
        },
        "book_query": {
            "name": "BookCard",
            "props": {
                "title": "1984",
                "author": "George Orwell",
                "publishedYear": 1949,
                "rating": 4.6,
                "pages": 328,
                "genre": ["Dystopian", "Science Fiction", "Political Fiction"],
                "description": "A dystopian social science fiction novel and cautionary tale about the dangers of totalitarianism"
            }
        },
        "news_query": {
            "name": "NewsCard",
            "props": {
                "title": "Breaking: Major Tech Announcement",
                "source": "Tech News Daily",
                "author": "John Smith",
                "publishedAt": "2025-11-21T10:30:00Z",
                "description": "A major technology company announces groundbreaking new product that could revolutionize the industry",
                "category": "Technology"
            }
        },
        "event_query": {
            "name": "EventCard",
            "props": {
                "name": "Summer Music Festival 2025",
                "date": "July 15-17, 2025",
                "time": "2:00 PM - 11:00 PM",
                "location": "Seoul, South Korea",
                "venue": "Olympic Stadium",
                "attendees": 50000,
                "ticketPrice": 150,
                "category": "Music Festival",
                "description": "Three days of incredible music featuring international and local artists"
            }
        },
        "exercise_query": {
            "name": "ExerciseCard",
            "props": {
                "name": "Push-ups",
                "category": "Strength Training",
                "difficulty": "Beginner",
                "duration": 15,
                "caloriesBurned": 100,
                "equipment": [],
                "description": "Classic bodyweight exercise for chest, shoulders, and triceps",
                "sets": 3,
                "reps": 12
            }
        }
    }

    return component_map.get(intent)
