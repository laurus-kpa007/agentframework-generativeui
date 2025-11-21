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
            # Analyze intent
            intent = await analyze_intent(request.message)
            logger.info(f"Detected intent: {intent}")

            # Add system prompt for structured response
            if intent != "general":
                system_message = get_system_prompt_for_intent(intent)
                messages_with_system = [
                    {"role": "system", "content": system_message}
                ] + messages
            else:
                messages_with_system = messages

            # Stream text response
            response_text = ""
            async for chunk in ollama.stream_chat(messages_with_system):
                response_text += chunk
                yield StreamEvent.text(chunk)

            # Parse response and extract UI data
            component_info = extract_component_from_response(response_text, intent)
            if component_info:
                yield StreamEvent.component(
                    component_info["name"],
                    component_info["props"]
                )

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


def get_system_prompt_for_intent(intent: str) -> str:
    """Get system prompt for specific intent to guide LLM response."""
    prompts = {
        "stock_query": """주식 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"symbol": "종목코드", "name": "회사명", "price": 가격, "change": 변동금액, "changePercent": 변동률}
```""",

        "weather_query": """날씨 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"location": "지역명", "temperature": 온도, "condition": "날씨상태", "humidity": 습도, "windSpeed": 풍속}
```""",

        "flight_query": """항공편 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"flightNumber": "항공편명", "airline": "항공사", "departure": "출발지", "arrival": "도착지", "departureTime": "출발시간", "arrivalTime": "도착시간", "status": "상태"}
```""",

        "recipe_query": """레시피를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"title": "요리명", "description": "설명", "prepTime": 준비시간(분), "cookTime": 조리시간(분), "servings": 인분, "difficulty": "난이도", "ingredients": ["재료1", "재료2"]}
```""",

        "movie_query": """영화 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"title": "영화제목", "year": 개봉연도, "rating": 평점, "genre": ["장르1", "장르2"], "runtime": 러닝타임(분), "director": "감독명", "plot": "줄거리"}
```""",

        "product_query": """상품 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"name": "상품명", "price": 가격, "originalPrice": 원가, "rating": 평점, "reviews": 리뷰수, "description": "설명", "category": "카테고리", "inStock": true}
```""",

        "hotel_query": """호텔 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"name": "호텔명", "location": "위치", "rating": 평점, "reviews": 리뷰수, "pricePerNight": 1박가격, "amenities": ["편의시설1", "편의시설2"], "description": "설명"}
```""",

        "restaurant_query": """맛집 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"name": "식당명", "cuisine": "음식종류", "location": "위치", "rating": 평점, "reviews": 리뷰수, "priceRange": 가격대(1-4), "openNow": true, "hours": "영업시간", "description": "설명"}
```""",

        "book_query": """도서 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"title": "책제목", "author": "저자", "publishedYear": 출판연도, "rating": 평점, "pages": 페이지수, "genre": ["장르1", "장르2"], "description": "설명"}
```""",

        "news_query": """뉴스 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"title": "뉴스제목", "source": "출처", "author": "기자명", "publishedAt": "발행시간(ISO)", "description": "요약", "category": "카테고리"}
```""",

        "event_query": """이벤트 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"name": "이벤트명", "date": "날짜", "time": "시간", "location": "지역", "venue": "장소", "attendees": 참석자수, "ticketPrice": 티켓가격, "category": "카테고리", "description": "설명"}
```""",

        "exercise_query": """운동 정보를 제공할 때는 다음 형식으로 답변해주세요:
답변 끝에 반드시 다음 JSON을 포함해주세요:
```json
{"name": "운동명", "category": "카테고리", "difficulty": "난이도", "duration": 시간(분), "caloriesBurned": 소모칼로리, "equipment": ["장비1", "장비2"], "description": "설명", "sets": 세트수, "reps": 반복횟수}
```"""
    }

    return prompts.get(intent, "")


def extract_component_from_response(response: str, intent: str) -> dict | None:
    """Extract component data from LLM response."""
    import json
    import re

    # Find JSON block in response
    json_pattern = r'```json\s*(\{[^`]+\})\s*```'
    match = re.search(json_pattern, response, re.DOTALL)

    if not match:
        logger.warning(f"No JSON found in response for intent: {intent}")
        return None

    try:
        data = json.loads(match.group(1))

        # Map intent to component name
        component_names = {
            "stock_query": "StockCard",
            "weather_query": "WeatherCard",
            "flight_query": "FlightCard",
            "recipe_query": "RecipeCard",
            "movie_query": "MovieCard",
            "product_query": "ProductCard",
            "hotel_query": "HotelCard",
            "restaurant_query": "RestaurantCard",
            "book_query": "BookCard",
            "news_query": "NewsCard",
            "event_query": "EventCard",
            "exercise_query": "ExerciseCard"
        }

        component_name = component_names.get(intent)
        if not component_name:
            return None

        return {
            "name": component_name,
            "props": data
        }

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from response: {e}")
        return None
