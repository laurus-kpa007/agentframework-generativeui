# Agent Framework + Generative UI

통합 AI 에이전트 시스템 - 로컬 LLM 기반 대화형 UI 생성 플랫폼

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node](https://img.shields.io/badge/node-20+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)

## 📋 프로젝트 개요

본 프로젝트는 두 개의 강력한 시스템을 통합합니다:

1. **Agent Framework**: Python/FastAPI 기반 로컬 LLM + MCP + Microsoft Agent Framework
2. **Generative UI**: Next.js/TypeScript 기반 동적 UI 컴포넌트 생성 시스템

### ✨ 주요 특징

- 🔒 **완전한 로컬 실행**: Ollama 기반으로 프라이버시 보장
- 🎨 **동적 UI 생성**: 12개의 전문 카드 컴포넌트 (주식, 날씨, 항공편 등)
- 🔌 **확장 가능한 도구**: Model Context Protocol (MCP) 지원
- ⚡ **실시간 스트리밍**: Server-Sent Events 기반 대화형 UI
- 🚀 **고성능**: TTFT (Time to First Token) < 500ms 목표
- 🐳 **Docker 지원**: 간편한 배포 및 관리
- 📚 **Vercel AI SDK**: 통합된 스트리밍 및 UI 생성

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│              Frontend (Next.js + Vercel AI SDK)          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Chat UI      │  │ 12 UI Cards  │  │  SSE Stream  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ REST API + SSE
┌────────────────────────┴────────────────────────────────┐
│              Backend (FastAPI + Python)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Chat Router  │  │ Intent       │  │ Streaming    │  │
│  │              │  │ Analysis     │  │ Service      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘  │
└─────────┼──────────────────┼──────────────────────────┘
          │                  │
┌─────────┴────────┐  ┌──────┴─────────┐
│  Ollama Server   │  │  MCP Servers   │
│  (qwen2.5)       │  │  (Future)      │
└──────────────────┘  └────────────────┘
```

## 🚀 빠른 시작

### Docker Compose (권장)

```bash
# 저장소 클론
git clone https://github.com/laurus-kpa007/agentframework-generativeui.git
cd agentframework-generativeui

# 환경 파일 생성
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# 모든 서비스 시작
docker-compose up -d

# Ollama 모델 다운로드 (첫 실행 시)
docker exec agentframework-ollama ollama pull qwen2.5:latest
```

**접속**: http://localhost:3000

자세한 내용은 [QUICKSTART.md](QUICKSTART.md)를 참조하세요.

### 로컬 개발

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Frontend (새 터미널)
cd frontend
npm install
npm run dev

# Ollama (새 터미널)
ollama serve
ollama pull qwen2.5:latest
```

## 📚 문서

- **[설치 가이드](INSTALLATION_GUIDE.md)**: Windows & macOS 상세 설치 가이드 ⭐ NEW
- **[빠른 시작 가이드](QUICKSTART.md)**: Docker를 이용한 빠른 시작
- **[통합 계획서](INTEGRATION_PLAN.md)**: 전체 통합 전략 및 상세 가이드
- **[아키텍처 다이어그램](ARCHITECTURE_DIAGRAMS.md)**: 12개의 Mermaid 다이어그램
- **[구현 작업 체크리스트](IMPLEMENTATION_TODOS.md)**: Phase별 상세 작업 목록

## 🛠️ 기술 스택

### Backend
| 구성요소 | 기술 |
|---------|------|
| **Framework** | FastAPI 0.104+ |
| **Language** | Python 3.11+ |
| **LLM** | Ollama (qwen2.5, llama3.2, mistral) |
| **Async** | asyncio, httpx |
| **Validation** | Pydantic 2.5+ |

### Frontend
| 구성요소 | 기술 |
|---------|------|
| **Framework** | Next.js 15 (App Router) |
| **Language** | TypeScript 5.3+ |
| **Styling** | Tailwind CSS 3.4+ |
| **AI SDK** | Vercel AI SDK (planned) |
| **Icons** | Lucide React |

### Infrastructure
| 구성요소 | 기술 |
|---------|------|
| **Containerization** | Docker |
| **Orchestration** | Docker Compose |
| **Streaming** | Server-Sent Events (SSE) |

## 🎨 UI 컴포넌트

현재 구현된 3개의 카드 컴포넌트:

| 컴포넌트 | 설명 | 상태 |
|---------|------|------|
| **StockCard** | 주식 정보 (가격, 변동률) | ✅ 완료 |
| **WeatherCard** | 날씨 정보 (온도, 습도, 풍속) | ✅ 완료 |
| **FlightCard** | 항공편 정보 (출발/도착, 상태) | ✅ 완료 |

추가 예정: RecipeCard, MovieCard, ProductCard, HotelCard, RestaurantCard, BookCard, NewsCard, EventCard, ExerciseCard

## 📊 프로젝트 구조

```
agentframework-generativeui/
├── backend/                 # FastAPI 백엔드
│   ├── config/             # 설정
│   ├── models/             # Pydantic 모델
│   ├── routers/            # API 라우터
│   ├── services/           # 비즈니스 로직
│   └── main.py             # 진입점
├── frontend/               # Next.js 프론트엔드
│   ├── app/                # App Router 페이지
│   ├── components/         # React 컴포넌트
│   │   └── ui/            # UI 카드 컴포넌트
│   └── lib/                # 유틸리티
├── config/                 # 전역 설정
├── docker/                 # Dockerfile들
├── scripts/                # 실행 스크립트
└── docs/                   # 문서
```

## 🔧 환경 설정

### Backend (.env)

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_MCP_UI=true
```

## 🧪 API 엔드포인트

### Health Check
```bash
GET /api/health
```

### Chat (Streaming)
```bash
POST /api/chat/stream
Content-Type: application/json

{
  "message": "Show me AAPL stock price"
}
```

### Chat (Non-streaming)
```bash
POST /api/chat/message
Content-Type: application/json

{
  "message": "Hello!",
  "conversation_id": "optional"
}
```

**API 문서**: http://localhost:8000/docs

## 💡 사용 예시

### 주식 정보 조회
```
User: Show me AAPL stock price
AI: [StockCard 렌더링]
    Here's the current Apple stock information.
```

### 날씨 정보 조회
```
User: What's the weather in Seoul?
AI: [WeatherCard 렌더링]
    The current weather in Seoul is 15°C with partly cloudy skies.
```

### 항공편 정보 조회
```
User: Show flight KE001
AI: [FlightCard 렌더링]
    Korean Air flight KE001 from ICN to JFK is on time.
```

## 📈 개발 로드맵

- [x] **Phase 0**: 프로젝트 계획 및 문서화
- [x] **Phase 1**: 기본 구현
  - [x] Backend 기본 설정
  - [x] Frontend 기본 설정
  - [x] Docker 환경 구성
  - [x] 3개 UI 컴포넌트 구현
  - [x] SSE 스트리밍 구현
- [ ] **Phase 2**: 기능 확장
  - [ ] 나머지 9개 UI 컴포넌트
  - [ ] MCP 서버 통합
  - [ ] 고급 의도 분석
  - [ ] 성능 최적화
- [ ] **Phase 3**: 안정화
  - [ ] 테스트 작성
  - [ ] 보안 강화
  - [ ] 프로덕션 배포

자세한 내용은 [IMPLEMENTATION_TODOS.md](IMPLEMENTATION_TODOS.md)를 참조하세요.

## 🧪 테스트

```bash
# Backend 테스트
cd backend
pytest

# Frontend 테스트
cd frontend
npm test

# E2E 테스트
npm run test:e2e
```

## 🤝 기여

기여를 환영합니다! 다음 단계를 따라주세요:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- [Agent Framework](https://github.com/laurus-kpa007/agent-framework) - 원본 프로젝트
- [Generative UI](https://github.com/laurus-kpa007/Generative-UI) - 원본 프로젝트
- [Ollama](https://ollama.ai) - 로컬 LLM 런타임
- [FastAPI](https://fastapi.tiangolo.com) - 현대적인 Python 웹 프레임워크
- [Next.js](https://nextjs.org) - React 프레임워크
- [Vercel AI SDK](https://sdk.vercel.ai) - AI 통합 SDK
- [Model Context Protocol](https://modelcontextprotocol.io) - 확장 가능한 도구 프로토콜

## 📞 문의

- **GitHub Issues**: [이슈 생성](https://github.com/laurus-kpa007/agentframework-generativeui/issues)
- **GitHub Discussions**: [토론 참여](https://github.com/laurus-kpa007/agentframework-generativeui/discussions)
- **Email**: kpa007@gmail.com

---

**Made with ❤️ by Shawn**

⭐ 이 프로젝트가 유용하다면 Star를 눌러주세요!
