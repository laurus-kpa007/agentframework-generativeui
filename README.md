# Agent Framework + Generative UI

통합 AI 에이전트 시스템 - 로컬 LLM 기반 대화형 UI 생성 플랫폼

## 📋 프로젝트 개요

본 프로젝트는 두 개의 강력한 시스템을 통합합니다:

1. **Agent Framework**: Python/FastAPI 기반 로컬 LLM + MCP + Microsoft Agent Framework
2. **Generative UI**: Next.js/TypeScript 기반 동적 UI 컴포넌트 생성 시스템

### 주요 특징

✨ **완전한 로컬 실행**: Ollama 기반으로 프라이버시 보장
🎨 **동적 UI 생성**: 12개의 전문 카드 컴포넌트 (주식, 날씨, 영화 등)
🔌 **확장 가능한 도구**: Model Context Protocol (MCP) 지원
⚡ **실시간 스트리밍**: Server-Sent Events 기반 대화형 UI
🚀 **고성능**: TTFT (Time to First Token) < 500ms 목표
🐳 **Docker 지원**: 간편한 배포 및 관리

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Chat Interface│  │ Generative UI│  │  MCP UI      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ REST API + SSE
┌────────────────────────┴────────────────────────────────┐
│              Backend (FastAPI + Python)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Agent        │  │ MCP Manager  │  │ Streaming    │  │
│  │ Framework    │  │              │  │ Service      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘  │
└─────────┼──────────────────┼──────────────────────────┘
          │                  │
┌─────────┴────────┐  ┌──────┴─────────┐
│  Ollama Server   │  │  MCP Ecosystem │
│  (Local LLM)     │  │  (Tools)       │
└──────────────────┘  └────────────────┘
```

## 📚 문서

- **[통합 계획서](INTEGRATION_PLAN.md)**: 전체 통합 전략 및 상세 가이드
- **[아키텍처 다이어그램](ARCHITECTURE_DIAGRAMS.md)**: 12개의 Mermaid 다이어그램
- **[구현 작업 체크리스트](IMPLEMENTATION_TODOS.md)**: Phase별 상세 작업 목록

## 🚀 빠른 시작

### 전제 조건

- Python 3.10+
- Node.js 20+
- Docker & Docker Compose (권장)
- Ollama (로컬 실행 시)

### Docker를 사용한 실행 (권장)

```bash
# 저장소 클론
git clone https://github.com/laurus-kpa007/agentframework-generativeui.git
cd agentframework-generativeui

# Docker Compose로 모든 서비스 실행
docker-compose up -d

# Ollama 모델 다운로드 (첫 실행 시)
docker exec agentframework-ollama ollama pull qwen2.5:latest

# 접속
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 로컬 개발 환경

#### Backend 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

#### Ollama 실행

```bash
# Ollama 설치 (https://ollama.ai)
ollama pull qwen2.5:latest
ollama serve
```

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **LLM**: Ollama (qwen2.5, llama3.2, mistral)
- **Agent**: Microsoft Agent Framework
- **Tools**: Model Context Protocol (MCP)

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Query
- **UI**: 12 Specialized Components

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions (계획 중)

## 🎨 UI 컴포넌트

12개의 전문 카드 컴포넌트:

| 카테고리 | 컴포넌트 |
|---------|---------|
| **금융** | StockCard, FlightCard, HotelCard |
| **정보** | WeatherCard, NewsCard, BookCard |
| **엔터테인먼트** | MovieCard, RecipeCard, EventCard |
| **커머스** | ProductCard, RestaurantCard, ExerciseCard |

## 🔧 설정

### Backend 환경 변수 (.env)

```bash
# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest

# FastAPI 설정
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info

# MCP 설정
MCP_CONFIG_PATH=./config/mcp_servers.yaml

# 보안
API_SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
```

### Frontend 환경 변수 (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_ENABLE_MCP_UI=true
```

## 📊 개발 로드맵

- [x] **Phase 0**: 프로젝트 계획 및 문서화 (완료)
- [ ] **Phase 1**: 기반 구축 (Week 1-2)
  - [ ] 프로젝트 구조 생성
  - [ ] Backend/Frontend 기본 설정
  - [ ] Docker 환경 구성
- [ ] **Phase 2**: 핵심 통합 (Week 3-4)
  - [ ] Agent Framework 통합
  - [ ] Ollama LLM 연결
  - [ ] MCP 서버 관리
  - [ ] Generative UI 컴포넌트
  - [ ] SSE 스트리밍
- [ ] **Phase 3**: 기능 확장 (Week 5-6)
  - [ ] 12개 UI 컴포넌트 완전 통합
  - [ ] MCP-UI 매핑 시스템
  - [ ] MCP 관리 UI
  - [ ] 성능 최적화
- [ ] **Phase 4**: 안정화 (Week 7-8)
  - [ ] 테스트 작성
  - [ ] 보안 강화
  - [ ] 문서화 완료
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

## 📖 API 문서

FastAPI 자동 생성 문서:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 기여

기여를 환영합니다! 다음 단계를 따라주세요:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

본 프로젝트는 원본 프로젝트의 라이선스를 따릅니다.

## 🙏 감사의 말

- [Agent Framework](https://github.com/laurus-kpa007/agent-framework)
- [Generative UI](https://github.com/laurus-kpa007/Generative-UI)
- [Ollama](https://ollama.ai)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Vercel AI SDK](https://sdk.vercel.ai)

## 📞 문의

- GitHub Issues: [이슈 생성](https://github.com/laurus-kpa007/agentframework-generativeui/issues)
- GitHub Discussions: [토론 참여](https://github.com/laurus-kpa007/agentframework-generativeui/discussions)

---

**Made with ❤️ by the Integration Team**
