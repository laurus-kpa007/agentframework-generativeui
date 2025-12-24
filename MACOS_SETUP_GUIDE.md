# macOS 설치 및 실행 가이드

Agent Framework + Generative UI를 macOS에서 설치하고 실행하는 완전한 가이드입니다.

---

## 목차
- [사전 요구사항](#사전-요구사항)
- [설치 방법 1: 로컬 개발 환경](#설치-방법-1-로컬-개발-환경-권장)
- [설치 방법 2: Docker 사용](#설치-방법-2-docker-사용)
- [실행하기](#실행하기)
- [테스트](#테스트)
- [문제 해결](#문제-해결)
- [유용한 팁](#유용한-팁)

---

## 사전 요구사항

### 시스템 요구사항
- **macOS**: 12.0 (Monterey) 이상
- **메모리**: 8GB RAM 이상 (16GB 권장)
- **저장공간**: 10GB 이상 (Ollama 모델 포함)
- **프로세서**: Apple Silicon (M1/M2/M3) 또는 Intel

---

## 설치 방법 1: 로컬 개발 환경 (권장)

### 1단계: Homebrew 설치

Homebrew는 macOS의 패키지 관리자입니다.

```bash
# Homebrew 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Apple Silicon (M1/M2/M3) 사용자:**
```bash
# Homebrew PATH 설정 추가
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

**설치 확인:**
```bash
brew --version
# 출력 예: Homebrew 4.x.x
```

### 2단계: Python 설치

> **중요**: Python 3.11 또는 3.12를 권장합니다. Python 3.13은 일부 라이브러리와 호환성 문제가 있습니다.

```bash
# Python 3.11 설치 (권장)
brew install python@3.11

# PATH 설정 (Apple Silicon)
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 설치 확인
python3.11 --version
# 출력: Python 3.11.x

pip3.11 --version
# 출력: pip 24.x.x
```

**별칭 설정 (선택사항):**
```bash
# python3 명령어를 python3.11로 설정
echo 'alias python3="python3.11"' >> ~/.zshrc
echo 'alias pip3="pip3.11"' >> ~/.zshrc
source ~/.zshrc
```

### 3단계: Node.js 설치

**방법 A: Homebrew 사용**
```bash
brew install node@20

# PATH 설정
echo 'export PATH="/opt/homebrew/opt/node@20/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**방법 B: nvm 사용 (권장)**
```bash
# nvm 설치
brew install nvm

# nvm 디렉토리 생성 및 설정
mkdir -p ~/.nvm
cat >> ~/.zshrc << 'EOF'
export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"
EOF
source ~/.zshrc

# Node.js 20 설치
nvm install 20
nvm use 20
nvm alias default 20
```

**설치 확인:**
```bash
node --version
# 출력: v20.x.x

npm --version
# 출력: 10.x.x
```

### 4단계: Git 설치

macOS에는 기본적으로 Git이 설치되어 있습니다.

```bash
# 설치 확인
git --version

# 설치되지 않은 경우
brew install git

# Git 초기 설정 (처음 사용하는 경우)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 5단계: Ollama 설치

Ollama는 로컬에서 LLM을 실행하는 도구입니다.

**방법 A: Homebrew 사용**
```bash
brew install ollama
```

**방법 B: 공식 설치 프로그램 사용**
1. https://ollama.ai/download/mac 접속
2. 다운로드 및 설치

**설치 확인:**
```bash
ollama --version
# 출력: ollama version x.x.x
```

### 6단계: 프로젝트 클론

```bash
# 프로젝트 디렉토리 생성 (원하는 위치)
mkdir -p ~/Projects
cd ~/Projects

# 저장소 클론
git clone https://github.com/laurus-kpa007/agentframework-generativeui.git

# 프로젝트 디렉토리로 이동
cd agentframework-generativeui
```

### 7단계: Backend 설정

```bash
# Backend 디렉토리로 이동
cd backend

# Python 가상 환경 생성
python3.11 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 파일 생성
cp .env.example .env
```

**.env 파일 내용 확인/수정:**
```bash
# 편집기로 열기
nano .env
# 또는
open -e .env
```

**기본 .env 설정:**
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
LOG_LEVEL=info
DEBUG=False
```

### 8단계: Frontend 설정

**새 터미널 탭을 열고 (Cmd + T):**

```bash
# 프로젝트 루트로 이동
cd ~/Projects/agentframework-generativeui/frontend

# 의존성 설치
npm install

# 환경 변수 파일 생성
cp .env.local.example .env.local
```

**.env.local 파일 확인:**
```bash
# 편집기로 열기
nano .env.local
# 또는
open -e .env.local
```

**기본 .env.local 설정:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_MCP_UI=true
```

### 9단계: Ollama 모델 다운로드

```bash
# Ollama 서비스 시작 (백그라운드에서 실행됨)
ollama serve &

# 기본 모델 다운로드 (약 4GB)
ollama pull qwen2.5:latest

# 다른 모델 옵션 (선택사항)
ollama pull llama3.2:latest    # Meta의 Llama 3.2
ollama pull mistral:latest     # Mistral AI

# 더 작은 모델 (빠른 테스트용)
ollama pull qwen2.5:7b         # 더 작은 버전
ollama pull llama3.2:3b        # 가장 작은 버전

# 설치된 모델 확인
ollama list
```

---

## 설치 방법 2: Docker 사용

Docker를 사용하면 모든 의존성을 컨테이너로 관리할 수 있습니다.

### 1단계: Docker Desktop 설치

```bash
# Homebrew로 설치
brew install --cask docker
```

또는 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) 에서 직접 다운로드

**설치 후:**
1. Applications에서 Docker 실행
2. Docker Desktop이 시작될 때까지 대기 (메뉴바에 고래 아이콘 확인)

**설치 확인:**
```bash
docker --version
# 출력: Docker version 24.x.x

docker-compose --version
# 출력: Docker Compose version 2.x.x
```

### 2단계: 프로젝트 클론 및 환경 설정

```bash
# 프로젝트 디렉토리로 이동
cd ~/Projects
git clone https://github.com/laurus-kpa007/agentframework-generativeui.git
cd agentframework-generativeui

# 환경 파일 생성
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

### 3단계: Docker Compose로 실행

```bash
# 모든 서비스 빌드 및 시작
docker-compose up -d

# 빌드 로그 확인
docker-compose logs -f
```

### 4단계: Ollama 모델 다운로드

```bash
# Ollama 컨테이너에서 모델 다운로드
docker exec agentframework-ollama ollama pull qwen2.5:latest
```

### Docker 명령어 참고

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f backend
docker-compose logs -f frontend

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart

# 이미지 재빌드 (코드 변경 시)
docker-compose build --no-cache
docker-compose up -d

# 볼륨 포함 완전 삭제
docker-compose down -v
```

---

## 실행하기

### 로컬 개발 환경에서 실행

**3개의 터미널 탭/창이 필요합니다.**

#### 터미널 1: Ollama

```bash
# Ollama 서비스 실행
ollama serve
```

> 참고: Ollama가 이미 백그라운드에서 실행 중이면 이 단계를 건너뛰어도 됩니다.

#### 터미널 2: Backend

```bash
# Backend 디렉토리로 이동
cd ~/Projects/agentframework-generativeui/backend

# 가상 환경 활성화
source venv/bin/activate

# FastAPI 서버 실행
python main.py
```

**성공 시 출력:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 터미널 3: Frontend

```bash
# Frontend 디렉토리로 이동
cd ~/Projects/agentframework-generativeui/frontend

# Next.js 개발 서버 실행
npm run dev
```

**성공 시 출력:**
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
  - Environments: .env.local
  ✓ Ready in 1234ms
```

### 접속 확인

| 서비스 | URL | 설명 |
|--------|-----|------|
| **Frontend** | http://localhost:3000 | 메인 웹 인터페이스 |
| **Backend API** | http://localhost:8000 | FastAPI 서버 |
| **API 문서** | http://localhost:8000/docs | Swagger UI |
| **Ollama** | http://localhost:11434 | LLM 서버 |

---

## 테스트

### API 테스트

```bash
# Health Check
curl http://localhost:8000/api/health

# 예상 응답:
# {"status":"healthy","timestamp":"...","ollama_connected":true,"model":"qwen2.5:latest"}

# Chat 테스트
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'

# Ollama 직접 테스트
curl http://localhost:11434/api/tags
```

### Frontend 테스트

1. 브라우저에서 http://localhost:3000 열기
2. 샘플 쿼리 버튼 클릭 또는 직접 입력:

| 카테고리 | 샘플 쿼리 |
|---------|---------|
| 주식 | "Show me AAPL stock price" |
| 날씨 | "What's the weather in Seoul?" |
| 항공편 | "Show flight KE001" |
| 호텔 | "Find hotels in Tokyo" |
| 레스토랑 | "Restaurant recommendations in New York" |
| 레시피 | "How to make pasta?" |
| 영화 | "Tell me about Inception movie" |
| 제품 | "Show iPhone 15 Pro details" |
| 도서 | "Book recommendation for programming" |
| 뉴스 | "Latest tech news" |
| 이벤트 | "Concerts in Seoul this week" |
| 운동 | "Home workout routine" |

---

## 문제 해결

### "Address already in use" 오류

```bash
# 포트 사용 확인
lsof -i :8000
lsof -i :3000
lsof -i :11434

# 프로세스 종료
kill -9 <PID>

# 또는 한 번에 종료
kill -9 $(lsof -t -i:8000)
kill -9 $(lsof -t -i:3000)
```

### Ollama 연결 실패

```bash
# Ollama 상태 확인
curl http://localhost:11434/api/tags

# Ollama 재시작
killall ollama
ollama serve

# 모델 확인
ollama list
```

### Python 가상 환경 오류

```bash
# 권한 문제 해결
chmod -R 755 backend/venv

# 가상 환경 재생성
cd backend
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### pydantic-core 설치 오류 (Python 3.13)

```bash
# 방법 1: 사전 빌드된 버전 사용
pip install --upgrade pip
pip install pydantic==2.5.3 --only-binary=:all:
pip install -r requirements.txt

# 방법 2: Python 3.11로 변경 (권장)
brew install python@3.11
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### npm install 오류

```bash
# npm 캐시 정리
npm cache clean --force

# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install

# 또는 yarn 사용
brew install yarn
rm -rf node_modules
yarn install
```

### CORS 오류

**backend/.env 파일 확인:**
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Next.js 빌드 오류

```bash
# Next.js 캐시 삭제
rm -rf .next
npm run dev
```

### Docker 관련 오류

```bash
# Docker Desktop이 실행 중인지 확인
docker ps

# 모든 컨테이너 및 이미지 정리 (주의: 다른 프로젝트에 영향)
docker system prune -a

# 특정 프로젝트만 정리
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 유용한 팁

### tmux 사용 (터미널 관리)

tmux를 사용하면 하나의 터미널에서 여러 창을 관리할 수 있습니다.

```bash
# tmux 설치
brew install tmux

# 새 세션 시작
tmux new -s agentframework

# 창 분할
# - 수평 분할: Ctrl + B, 그 다음 "
# - 수직 분할: Ctrl + B, 그 다음 %

# 창 간 이동: Ctrl + B, 그 다음 화살표 키

# 세션 분리 (백그라운드): Ctrl + B, 그 다음 d

# 세션 재연결
tmux attach -t agentframework

# 세션 목록
tmux ls

# 세션 종료
tmux kill-session -t agentframework
```

### VS Code 사용

```bash
# VS Code 설치
brew install --cask visual-studio-code

# 프로젝트 열기
cd ~/Projects/agentframework-generativeui
code .
```

**권장 확장 프로그램:**
- Python (Microsoft)
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Docker

### iTerm2 사용 (터미널 개선)

```bash
# iTerm2 설치
brew install --cask iterm2
```

### 자동 실행 스크립트

프로젝트 루트에 `start-dev.sh` 스크립트를 생성:

```bash
#!/bin/bash

# Agent Framework + Generative UI 개발 서버 시작 스크립트

PROJECT_DIR=~/Projects/agentframework-generativeui

echo "🚀 Starting Agent Framework + Generative UI..."

# Ollama 시작
echo "Starting Ollama..."
osascript -e "tell app \"Terminal\" to do script \"cd $PROJECT_DIR && ollama serve\""

sleep 2

# Backend 시작
echo "Starting Backend..."
osascript -e "tell app \"Terminal\" to do script \"cd $PROJECT_DIR/backend && source venv/bin/activate && python main.py\""

sleep 2

# Frontend 시작
echo "Starting Frontend..."
osascript -e "tell app \"Terminal\" to do script \"cd $PROJECT_DIR/frontend && npm run dev\""

echo ""
echo "✅ All services started!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
```

**스크립트 실행 권한 부여:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### 환경별 설정

**개발 환경:**
```env
# backend/.env
DEBUG=True
LOG_LEVEL=debug
```

**프로덕션 환경:**
```env
# backend/.env
DEBUG=False
LOG_LEVEL=info
```

---

## 다음 단계

설치 완료 후:

1. **브라우저에서 접속**: http://localhost:3000
2. **12개 샘플 쿼리 버튼** 테스트
3. **모델 선택**: 우측 상단 드롭다운에서 다른 모델 시도
4. **API 문서 탐색**: http://localhost:8000/docs
5. **코드 탐색**: VS Code에서 프로젝트 열기

---

## 추가 문서

- [README.md](README.md) - 프로젝트 개요
- [QUICKSTART.md](QUICKSTART.md) - 빠른 시작 가이드
- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Windows & macOS 통합 가이드
- [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) - 통합 계획서
- [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md) - 아키텍처 다이어그램

---

## 도움이 필요하신가요?

- **GitHub Issues**: [이슈 생성](https://github.com/laurus-kpa007/agentframework-generativeui/issues)
- **이메일**: kpa007@gmail.com

---

**문서 버전**: 1.0.0
**최종 업데이트**: 2025-12-10
**작성자**: Claude Code Integration Team
