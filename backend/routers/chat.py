"""Chat router with streaming support."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import logging

from models.schemas import ChatRequest, ChatMessage
from services.streaming_service import StreamingService, StreamEvent

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple in-memory conversation storage (use Redis in production)
conversations: dict[str, List[ChatMessage]] = {}


def get_ollama_service():
    """Get the global Ollama service instance."""
    from main import ollama_service
    if ollama_service is None:
        raise HTTPException(status_code=503, detail="Ollama service not initialized")
    return ollama_service


def get_streaming_service():
    """Dependency for streaming service."""
    return StreamingService()


@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """Stream chat response with SSE."""
    logger.info(f"Chat request: {request.message[:50]}...")

    ollama = get_ollama_service()
    streaming = get_streaming_service()

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
async def send_message(request: ChatRequest):
    """Send chat message (non-streaming)."""
    ollama = get_ollama_service()
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

    if any(word in message_lower for word in ["stock", "share", "price", "aapl", "nasdaq", "trading", "주식", "애플", "삼성", "종목", "시세"]):
        return "stock_query"
    elif any(word in message_lower for word in ["weather", "temperature", "forecast", "climate", "날씨", "기온", "예보"]):
        return "weather_query"
    elif any(word in message_lower for word in ["flight", "airplane", "airport", "airline", "항공", "비행기", "공항"]):
        return "flight_query"
    elif any(word in message_lower for word in ["recipe", "cook", "cooking", "food", "dish", "ingredient", "레시피", "요리", "음식"]):
        return "recipe_query"
    elif any(word in message_lower for word in ["movie", "film", "cinema", "actor", "director", "영화", "배우", "감독"]):
        return "movie_query"
    elif any(word in message_lower for word in ["product", "buy", "shop", "shopping", "purchase", "상품", "제품", "구매", "쇼핑", "추천"]):
        return "product_query"
    elif any(word in message_lower for word in ["hotel", "accommodation", "booking", "stay", "호텔", "숙소", "예약"]):
        return "hotel_query"
    elif any(word in message_lower for word in ["restaurant", "dine", "dining", "eat", "reservation", "맛집", "식당", "레스토랑"]):
        return "restaurant_query"
    elif any(word in message_lower for word in ["book", "read", "reading", "author", "novel", "책", "도서", "독서", "작가"]):
        return "book_query"
    elif any(word in message_lower for word in ["news", "article", "headline", "breaking", "뉴스", "기사", "속보"]):
        return "news_query"
    elif any(word in message_lower for word in ["event", "concert", "show", "performance", "ticket", "이벤트", "공연", "행사", "티켓"]):
        return "event_query"
    elif any(word in message_lower for word in ["exercise", "workout", "fitness", "gym", "training", "운동", "헬스", "트레이닝", "루틴"]):
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
                "location": "서울, 대한민국",
                "temperature": 15,
                "condition": "구름 조금",
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
                "title": "스파게티 카르보나라",
                "description": "달걀, 치즈, 베이컨으로 만드는 클래식 이탈리안 파스타",
                "prepTime": 10,
                "cookTime": 20,
                "servings": 4,
                "difficulty": "쉬움",
                "ingredients": [
                    "스파게티 400g",
                    "베이컨 200g",
                    "달걀 4개",
                    "파마산 치즈 100g",
                    "후추",
                    "소금"
                ]
            }
        },
        "movie_query": {
            "name": "MovieCard",
            "props": {
                "title": "쇼생크 탈출",
                "year": 1994,
                "rating": 9.3,
                "genre": ["드라마", "범죄"],
                "runtime": 142,
                "director": "프랭크 다라본트",
                "plot": "억울하게 투옥된 은행가가 희망을 잃지 않고 자유를 향한 탈출을 준비하는 이야기"
            }
        },
        "product_query": {
            "name": "ProductCard",
            "props": {
                "name": "무선 블루투스 헤드폰",
                "price": 79.99,
                "originalPrice": 129.99,
                "rating": 4.5,
                "reviews": 1234,
                "description": "30시간 배터리 수명의 프리미엄 노이즈 캔슬링 헤드폰",
                "category": "전자제품",
                "inStock": True
            }
        },
        "hotel_query": {
            "name": "HotelCard",
            "props": {
                "name": "그랜드 플라자 호텔",
                "location": "서울, 대한민국",
                "rating": 5,
                "reviews": 892,
                "pricePerNight": 150,
                "amenities": ["wifi", "breakfast", "tv", "gym", "pool"],
                "description": "서울 중심부에 위치한 멋진 시티뷰를 자랑하는 럭셔리 호텔"
            }
        },
        "restaurant_query": {
            "name": "RestaurantCard",
            "props": {
                "name": "스시 마스터",
                "cuisine": "일식",
                "location": "서울시 강남구 123번길",
                "rating": 4.8,
                "reviews": 567,
                "priceRange": 3,
                "openNow": True,
                "hours": "오전 11:00 - 오후 10:00",
                "description": "매일 신선한 해산물로 만드는 정통 일본식 스시 전문점"
            }
        },
        "book_query": {
            "name": "BookCard",
            "props": {
                "title": "1984",
                "author": "조지 오웰",
                "publishedYear": 1949,
                "rating": 4.6,
                "pages": 328,
                "genre": ["디스토피아", "SF", "정치 소설"],
                "description": "전체주의의 위험성을 경고하는 디스토피아 사회과학 소설"
            }
        },
        "news_query": {
            "name": "NewsCard",
            "props": {
                "title": "속보: 주요 기술 기업 신제품 발표",
                "source": "테크 뉴스 데일리",
                "author": "홍길동",
                "publishedAt": "2025-11-21T10:30:00Z",
                "description": "주요 기술 기업이 산업을 혁신할 수 있는 획기적인 신제품을 발표했습니다",
                "category": "기술"
            }
        },
        "event_query": {
            "name": "EventCard",
            "props": {
                "name": "2025 여름 음악 페스티벌",
                "date": "2025년 7월 15-17일",
                "time": "오후 2:00 - 오후 11:00",
                "location": "서울, 대한민국",
                "venue": "올림픽 경기장",
                "attendees": 50000,
                "ticketPrice": 150,
                "category": "음악 페스티벌",
                "description": "국내외 아티스트들이 선사하는 3일간의 환상적인 음악 축제"
            }
        },
        "exercise_query": {
            "name": "ExerciseCard",
            "props": {
                "name": "푸쉬업",
                "category": "근력 운동",
                "difficulty": "초급",
                "duration": 15,
                "caloriesBurned": 100,
                "equipment": [],
                "description": "가슴, 어깨, 삼두근을 단련하는 클래식 맨몸 운동",
                "sets": 3,
                "reps": 12
            }
        }
    }

    return component_map.get(intent)
