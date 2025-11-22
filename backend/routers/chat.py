"""Chat router with streaming support."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import logging
import re

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


def get_mcp_service():
    """Get the global MCP service instance."""
    from main import mcp_service
    if mcp_service is None:
        raise HTTPException(status_code=503, detail="MCP service not initialized")
    return mcp_service


def get_streaming_service():
    """Dependency for streaming service."""
    return StreamingService()


async def handle_mcp_filesearch(message: str) -> dict:
    """Handle file search using MCP tools."""
    mcp = get_mcp_service()

    # Extract directory and file pattern from message
    # Pattern: "g:/imsi" or "g:\imsi" and ".mp4" or "*.mp4"
    dir_match = re.search(r'([a-z]:[/\\][^\s]+)', message, re.IGNORECASE)
    pattern_match = re.search(r'\*?\.(\w+)', message)

    if not dir_match:
        return {
            'success': False,
            'error': '폴더 경로를 찾을 수 없습니다. 예: g:/imsi'
        }

    directory = dir_match.group(1).replace('\\', '/')
    pattern = f"*.{pattern_match.group(1)}" if pattern_match else "*"

    # Call MCP tool
    result = await mcp.call_tool('search_files', {
        'directory': directory,
        'pattern': pattern
    })

    return result


async def handle_mcp_websearch(message: str) -> dict:
    """Handle web search using MCP Tavily tool."""
    mcp = get_mcp_service()

    # Extract search query (remove common phrases)
    query = message
    for phrase in ["웹 검색", "인터넷 검색", "web search", "search web", "find on web", "google", "해줘", "알려줘"]:
        query = query.replace(phrase, "")
    query = query.strip()

    if not query:
        return {
            'success': False,
            'error': '검색어를 찾을 수 없습니다.'
        }

    # Call MCP Tavily search tool
    result = await mcp.call_tool('tavily_search', {
        'query': query,
        'max_results': 5
    })

    return result


async def handle_mcp_weather(message: str) -> dict:
    """Handle weather query using MCP weather tool."""
    mcp = get_mcp_service()

    # Korean city name mapping
    city_map = {
        '서울': 'Seoul',
        '부산': 'Busan',
        '인천': 'Incheon',
        '대구': 'Daegu',
        '대전': 'Daejeon',
        '광주': 'Gwangju',
        '울산': 'Ulsan',
        '제주': 'Jeju',
        '도쿄': 'Tokyo',
        '뉴욕': 'New York',
        '런던': 'London',
        '파리': 'Paris',
        '베이징': 'Beijing',
        '상하이': 'Shanghai',
        '홍콩': 'Hong Kong',
        '싱가포르': 'Singapore',
        '방콕': 'Bangkok',
        '시드니': 'Sydney'
    }

    # Extract city name from message (simple approach)
    city_patterns = [
        r'(\S+)\s*(?:날씨|weather)',
        r'(?:in|at)\s+(\w+)',
    ]

    city = None
    for pattern in city_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            city_raw = match.group(1)
            # Check if it's a Korean city name
            city = city_map.get(city_raw, city_raw)
            break

    # Default to Seoul if no city found
    if not city or city.lower() in ['현재', '실시간', 'current', 'now', '지금']:
        city = 'Seoul'

    # Call MCP weather tool
    result = await mcp.call_tool('get_current_weather', {
        'city': city
    })

    return result


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

            # Handle MCP file search intent
            if intent == "mcp_filesearch":
                # Call MCP tool
                mcp_result = await handle_mcp_filesearch(request.message)

                if mcp_result.get('success'):
                    files = mcp_result.get('files', [])
                    file_count = len(files)

                    # Generate response text
                    response_text = f"{mcp_result.get('result', '')}\n\n"
                    response_text += f"총 {file_count}개의 파일을 찾았습니다:\n\n"

                    # Show first 20 files
                    for i, file_info in enumerate(files[:20], 1):
                        file_name = file_info['name']
                        file_path = file_info['path']
                        file_size_mb = file_info['size'] / (1024 * 1024)
                        response_text += f"{i}. {file_name} ({file_size_mb:.2f} MB)\n   경로: {file_path}\n\n"

                    if file_count > 20:
                        response_text += f"\n...그 외 {file_count - 20}개 파일 더 있습니다."

                    # Add MCP tool info
                    response_text += f"\n\n---\n🔧 **사용된 MCP Tool:** `filesystem.search_files`"

                    yield StreamEvent.text(response_text)

                    # Add to conversation
                    conversations[conversation_id].append(
                        ChatMessage(role="assistant", content=response_text)
                    )
                else:
                    error_msg = f"파일 검색 실패: {mcp_result.get('error', '알 수 없는 오류')}"
                    yield StreamEvent.text(error_msg)
                    conversations[conversation_id].append(
                        ChatMessage(role="assistant", content=error_msg)
                    )

                yield StreamEvent.done()
                return

            # Handle MCP web search intent
            if intent == "mcp_websearch":
                # Call MCP Tavily search tool
                mcp_result = await handle_mcp_websearch(request.message)

                if mcp_result.get('success'):
                    answer = mcp_result.get('answer', '')
                    results = mcp_result.get('results', [])

                    # Generate summary text
                    response_text = f"🔍 웹 검색 결과:\n\n"
                    if answer:
                        response_text += f"**요약:** {answer}\n\n"

                    response_text += f"**{len(results)}개의 검색 결과를 찾았습니다:**\n\n"

                    # Add MCP tool info
                    response_text += f"\n---\n🔧 **사용된 MCP Tool:** `tavily.tavily_search`\n\n"

                    yield StreamEvent.text(response_text)

                    # Generate NewsCard components for each result
                    from datetime import datetime
                    for result in results[:5]:
                        news_card_props = {
                            'title': result.get('title', 'No title'),
                            'source': result.get('url', '').split('/')[2] if result.get('url') else 'Web',  # Extract domain
                            'author': '',
                            'publishedAt': datetime.now().isoformat(),
                            'description': result.get('content', '')[:200],
                            'url': result.get('url', ''),
                            'category': '검색'
                        }
                        yield StreamEvent.component('NewsCard', news_card_props)

                    # Add to conversation
                    conversations[conversation_id].append(
                        ChatMessage(role="assistant", content=response_text)
                    )
                else:
                    error_msg = f"웹 검색 실패: {mcp_result.get('error', '알 수 없는 오류')}"
                    yield StreamEvent.text(error_msg)
                    conversations[conversation_id].append(
                        ChatMessage(role="assistant", content=error_msg)
                    )

                yield StreamEvent.done()
                return

            # Handle MCP weather intent
            if intent == "mcp_weather":
                # Call MCP weather tool
                mcp_result = await handle_mcp_weather(request.message)

                if mcp_result.get('success'):
                    weather = mcp_result.get('weather', {})

                    # Generate response text with weather info
                    location = weather.get('location', 'Unknown')
                    temp = weather.get('temperature', 'N/A')
                    windspeed = weather.get('windspeed', 'N/A')

                    response_text = f"🌤️ {location} 현재 날씨\n\n"
                    response_text += f"🌡️ **온도:** {temp}°C\n"
                    response_text += f"💨 **풍속:** {windspeed} km/h\n"
                    response_text += f"🕐 **시간:** {weather.get('time', 'N/A')}\n"

                    # Add MCP tool info
                    response_text += f"\n---\n🔧 **사용된 MCP Tool:** `weather.get_current_weather`"

                    yield StreamEvent.text(response_text)

                    # Add to conversation
                    conversations[conversation_id].append(
                        ChatMessage(role="assistant", content=response_text)
                    )
                else:
                    error_msg = f"날씨 조회 실패: {mcp_result.get('error', '알 수 없는 오류')}"
                    yield StreamEvent.text(error_msg)
                    conversations[conversation_id].append(
                        ChatMessage(role="assistant", content=error_msg)
                    )

                yield StreamEvent.done()
                return

            # Handle other intents normally
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
            components = extract_component_from_response(response_text, intent)
            if components:
                for component_info in components:
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

    # MCP-related intents (파일/폴더 검색 등)
    if any(word in message_lower for word in ["파일", "file", "폴더", "folder", "디렉토리", "directory"]):
        return "mcp_filesearch"
    # MCP web search intent (웹 검색, 인터넷 검색) - must be explicit
    elif any(word in message_lower for word in ["웹 검색", "web search", "인터넷 검색", "search web", "find on web", "google"]):
        return "mcp_websearch"
    # Weather intent - smart routing between MCP and Generative UI
    elif any(word in message_lower for word in ["날씨", "weather", "temperature", "forecast", "climate", "기온", "예보"]):
        # Check if it's a forecast request (use Generative UI for forecasts)
        if any(word in message_lower for word in ["예보", "forecast", "climate"]):
            return "weather_query"

        # Check if it's a multi-city query (use Generative UI for multiple cities)
        # Look for commas or multiple city names
        if "," in message or len(message.split()) > 3:
            # Multiple cities or complex query -> use Generative UI cards
            return "weather_query"

        # Simple single-city current weather -> use MCP for real-time data
        # Common patterns: "서울 날씨", "tokyo weather", "weather in paris"
        return "mcp_weather"
    elif any(word in message_lower for word in ["stock", "share", "price", "aapl", "nasdaq", "trading", "주식", "애플", "삼성", "종목", "시세"]):
        return "stock_query"
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
        "stock_query": """주식 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 그 다음 줄바꿈 후 정확히 다음 형식의 JSON 블록 추가:

```json
{"symbol": "AAPL", "name": "Apple Inc.", "price": 150.25, "change": 2.5, "changePercent": 1.69}
```

중요: JSON의 모든 숫자 값은 따옴표 없이 숫자로만 작성해주세요.""",

        "weather_query": """날씨 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 요청된 각 도시마다 별도의 JSON 블록 추가 (도시가 하나면 하나만, 여러 개면 여러 개)

예시 (여러 도시):
```json
{"location": "서울, 대한민국", "temperature": 18, "condition": "맑음", "humidity": 60, "windSpeed": 10}
```

```json
{"location": "부산, 대한민국", "temperature": 20, "condition": "구름 조금", "humidity": 70, "windSpeed": 15}
```

```json
{"location": "인천, 대한민국", "temperature": 17, "condition": "흐림", "humidity": 65, "windSpeed": 12}
```

중요:
- 각 도시의 location 값을 정확히 다르게 작성해주세요
- temperature, humidity, windSpeed는 따옴표 없이 숫자로만 작성해주세요
- 각 JSON은 별도의 ```json ``` 블록으로 구분해주세요""",

        "flight_query": """항공편 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 그 다음 줄바꿈 후 정확히 하나의 JSON 블록만 추가:

```json
{"flightNumber": "KE001", "airline": "Korean Air", "departure": "ICN", "arrival": "JFK", "departureTime": "14:00", "arrivalTime": "16:30", "status": "On Time"}
```

중요:
- JSON 객체는 하나만 작성해주세요
- 문자열이 아닌 필드는 따옴표 없이 작성하지 마세요""",

        "recipe_query": """레시피 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 그 다음 줄바꿈 후 정확히 하나의 JSON 블록만 추가:

```json
{"title": "스파게티 카르보나라", "description": "달걀과 치즈로 만드는 파스타", "prepTime": 10, "cookTime": 20, "servings": 4, "difficulty": "쉬움", "ingredients": ["스파게티 400g", "베이컨 200g", "달걀 4개", "파마산 치즈 100g"]}
```

중요:
- JSON 객체는 하나만 작성해주세요
- prepTime, cookTime, servings는 따옴표 없이 숫자로만 작성해주세요
- ingredients는 문자열 배열로 작성해주세요""",

        "movie_query": """영화 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 그 다음 줄바꿈 후 정확히 하나의 JSON 블록만 추가:

```json
{"title": "쇼생크 탈출", "year": 1994, "rating": 9.3, "genre": ["드라마", "범죄"], "runtime": 142, "director": "프랭크 다라본트", "plot": "억울하게 투옥된 은행가의 희망 이야기"}
```

중요:
- JSON 객체는 하나만 작성해주세요
- year, rating, runtime은 따옴표 없이 숫자로만 작성해주세요
- genre는 문자열 배열로 작성해주세요""",

        "product_query": """상품 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 추천하는 각 상품마다 별도의 JSON 블록 추가 (상품이 하나면 하나만, 여러 개면 여러 개)

예시 (여러 상품):
```json
{"name": "소니 WH-1000XM5", "price": 299.99, "originalPrice": 399.99, "rating": 4.8, "reviews": 2341, "description": "업계 최고 노이즈 캔슬링", "category": "전자제품", "inStock": true}
```

```json
{"name": "보스 QuietComfort 45", "price": 279.99, "originalPrice": 329.99, "rating": 4.6, "reviews": 1876, "description": "편안한 착용감과 긴 배터리", "category": "전자제품", "inStock": true}
```

중요:
- 각 상품의 name을 정확히 다르게 작성해주세요
- price, originalPrice, rating, reviews는 따옴표 없이 숫자로만 작성해주세요
- inStock은 true 또는 false로 작성해주세요 (따옴표 없이)""",

        "hotel_query": """호텔 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 추천하는 각 호텔마다 별도의 JSON 블록 추가 (호텔이 하나면 하나만, 여러 개면 여러 개)

예시 (여러 호텔):
```json
{"name": "그랜드 하얏트 서울", "location": "서울 용산구", "rating": 5, "reviews": 1523, "pricePerNight": 280, "amenities": ["wifi", "breakfast", "tv", "gym", "pool"], "description": "남산 전망의 럭셔리 호텔"}
```

```json
{"name": "롯데호텔 서울", "location": "서울 중구", "rating": 5, "reviews": 2104, "pricePerNight": 320, "amenities": ["wifi", "breakfast", "tv", "gym", "spa"], "description": "명동 중심의 프리미엄 호텔"}
```

중요:
- 각 호텔의 name과 location을 정확히 다르게 작성해주세요
- rating, reviews, pricePerNight는 따옴표 없이 숫자로만 작성해주세요
- amenities는 문자열 배열로 작성해주세요""",

        "restaurant_query": """맛집 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 추천하는 각 맛집마다 별도의 JSON 블록 추가 (맛집이 하나면 하나만, 여러 개면 여러 개)

예시 (여러 맛집):
```json
{"name": "스시 마스터", "cuisine": "일식", "location": "서울시 강남구", "rating": 4.8, "reviews": 567, "priceRange": 3, "openNow": true, "hours": "오전 11:00 - 오후 10:00", "description": "정통 일본식 스시 전문점"}
```

```json
{"name": "육회나라", "cuisine": "한식", "location": "서울시 서초구", "rating": 4.6, "reviews": 432, "priceRange": 2, "openNow": true, "hours": "오전 10:00 - 오후 11:00", "description": "신선한 육회와 비빔밥 맛집"}
```

중요:
- 각 맛집의 name, cuisine, location을 정확히 다르게 작성해주세요
- rating, reviews, priceRange는 따옴표 없이 숫자로만 작성해주세요
- openNow는 true 또는 false로 작성해주세요 (따옴표 없이)""",

        "book_query": """도서 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 추천하는 각 도서마다 별도의 JSON 블록 추가 (도서가 하나면 하나만, 여러 개면 여러 개)

예시 (여러 도서):
```json
{"title": "1984", "author": "조지 오웰", "publishedYear": 1949, "rating": 4.6, "pages": 328, "genre": ["디스토피아", "SF"], "description": "전체주의의 위험성을 경고하는 디스토피아 소설"}
```

```json
{"title": "멋진 신세계", "author": "올더스 헉슬리", "publishedYear": 1932, "rating": 4.5, "pages": 311, "genre": ["디스토피아", "SF"], "description": "쾌락으로 통제되는 미래 사회"}
```

중요:
- 각 도서의 title과 author를 정확히 다르게 작성해주세요
- publishedYear, rating, pages는 따옴표 없이 숫자로만 작성해주세요
- genre는 문자열 배열로 작성해주세요""",

        "news_query": """뉴스 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 그 다음 줄바꿈 후 정확히 하나의 JSON 블록만 추가:

```json
{"title": "주요 기술 기업 신제품 발표", "source": "테크 뉴스 데일리", "author": "홍길동", "publishedAt": "2025-11-21T10:30:00Z", "description": "획기적인 신제품 발표", "category": "기술"}
```

중요:
- JSON 객체는 하나만 작성해주세요
- publishedAt은 ISO 8601 형식의 문자열로 작성해주세요""",

        "event_query": """이벤트 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 그 다음 줄바꿈 후 정확히 하나의 JSON 블록만 추가:

```json
{"name": "2025 여름 음악 페스티벌", "date": "2025년 7월 15-17일", "time": "오후 2:00 - 오후 11:00", "location": "서울, 대한민국", "venue": "올림픽 경기장", "attendees": 50000, "ticketPrice": 150, "category": "음악 페스티벌", "description": "3일간의 환상적인 음악 축제"}
```

중요:
- JSON 객체는 하나만 작성해주세요
- attendees, ticketPrice는 따옴표 없이 숫자로만 작성해주세요""",

        "exercise_query": """운동 정보를 제공할 때는 반드시 다음 형식을 지켜주세요:

1. 먼저 사용자에게 유용한 설명을 2-3문장으로 작성
2. 그 다음 줄바꿈 후 정확히 하나의 JSON 블록만 추가:

```json
{"name": "푸쉬업", "category": "근력 운동", "difficulty": "초급", "duration": 15, "caloriesBurned": 100, "equipment": [], "description": "가슴, 어깨, 삼두근을 단련하는 맨몸 운동", "sets": 3, "reps": 12}
```

중요:
- JSON 객체는 하나만 작성해주세요
- duration, caloriesBurned, sets, reps는 따옴표 없이 숫자로만 작성해주세요
- equipment는 문자열 배열로 작성해주세요 (없으면 빈 배열 [])"""
    }

    return prompts.get(intent, "")


def extract_component_from_response(response: str, intent: str) -> list[dict] | None:
    """Extract component data from LLM response. Returns list of components."""
    import json
    import re

    # Find all JSON blocks in response
    json_pattern = r'```json\s*(\{[^`]+?\})\s*```'
    matches = re.finditer(json_pattern, response, re.DOTALL)

    components = []

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
        logger.warning(f"No component mapping for intent: {intent}")
        return None

    for match in matches:
        try:
            data = json.loads(match.group(1))
            components.append({
                "name": component_name,
                "props": data
            })
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            continue

    if not components:
        logger.warning(f"No valid JSON found in response for intent: {intent}")
        return None

    logger.info(f"Extracted {len(components)} component(s) from response")
    return components
