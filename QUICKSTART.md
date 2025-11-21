# 빠른 시작 가이드

Agent Framework + Generative UI를 실행하는 방법입니다.

## 🚀 방법 1: Docker Compose (권장)

가장 간단한 방법입니다. Docker만 설치되어 있으면 됩니다.

### 사전 요구사항
- Docker 20.10+
- Docker Compose 2.0+

### 실행 단계

```bash
# 1. 저장소 클론
git clone https://github.com/laurus-kpa007/agentframework-generativeui.git
cd agentframework-generativeui

# 2. 환경 파일 생성
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# 3. 모든 서비스 시작
docker-compose up -d

# 4. Ollama 모델 다운로드 (첫 실행 시만)
docker exec agentframework-ollama ollama pull qwen2.5:latest

# 5. 로그 확인
docker-compose logs -f
```

### 접속

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

### 중지

```bash
docker-compose down
```

---

## 💻 방법 2: 로컬 개발 환경

개발 중이거나 세부 설정을 원하는 경우 사용합니다.

### 사전 요구사항
- Python 3.11+
- Node.js 20+
- Ollama (https://ollama.ai 에서 설치)

### Backend 실행

```bash
# 1. Backend 디렉토리로 이동
cd backend

# 2. 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env

# 5. 서버 실행
python main.py
```

Backend가 http://localhost:8000 에서 실행됩니다.

### Frontend 실행

새 터미널을 열고:

```bash
# 1. Frontend 디렉토리로 이동
cd frontend

# 2. 의존성 설치
npm install

# 3. 환경 변수 설정
cp .env.local.example .env.local

# 4. 개발 서버 실행
npm run dev
```

Frontend가 http://localhost:3000 에서 실행됩니다.

### Ollama 실행

새 터미널을 열고:

```bash
# 1. Ollama 시작
ollama serve

# 2. 모델 다운로드 (새 터미널에서)
ollama pull qwen2.5:latest
```

---

## 🧪 테스트

### API 테스트

```bash
# Health check
curl http://localhost:8000/api/health

# Chat 테스트
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### Frontend 테스트

브라우저에서 http://localhost:3000 열고:

1. **주식 정보**: "Show me AAPL stock price" 입력
2. **날씨 정보**: "What is the weather in Seoul?" 입력
3. **항공편 정보**: "Show flight KE001" 입력

---

## 🔧 문제 해결

### Ollama 연결 실패

```bash
# Ollama가 실행 중인지 확인
curl http://localhost:11434/api/tags

# 모델이 다운로드되었는지 확인
ollama list
```

### CORS 에러

`backend/.env` 파일의 `CORS_ORIGINS`에 Frontend URL이 포함되어 있는지 확인:

```
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Port 충돌

다른 애플리케이션이 포트를 사용 중일 수 있습니다:

```bash
# 포트 사용 확인
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Linux/Mac
lsof -i :8000
lsof -i :3000
```

### Docker 이미지 재빌드

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📖 다음 단계

- [통합 계획서](INTEGRATION_PLAN.md) 읽기
- [아키텍처 다이어그램](ARCHITECTURE_DIAGRAMS.md) 확인
- [구현 작업 체크리스트](IMPLEMENTATION_TODOS.md) 살펴보기
- API 문서 탐색: http://localhost:8000/docs

---

## 💡 샘플 쿼리

시스템을 테스트하기 위한 샘플 쿼리들:

### 주식 정보
- "Show me AAPL stock price"
- "What's the current price of Apple?"
- "NASDAQ stock information"

### 날씨 정보
- "What's the weather in Seoul?"
- "Show me the temperature in New York"
- "Weather forecast for Tokyo"

### 항공편 정보
- "Show flight KE001"
- "Flight information for Korean Air"
- "Airport departure status"

### 일반 대화
- "Hello, how are you?"
- "Tell me a joke"
- "What can you do?"

---

## 🆘 도움이 필요하신가요?

- **GitHub Issues**: [이슈 생성](https://github.com/laurus-kpa007/agentframework-generativeui/issues)
- **문서**: [README.md](README.md)
- **로그 확인**: `docker-compose logs -f` 또는 `backend/logs/app.log`
