# 설치 및 실행 가이드

Agent Framework + Generative UI를 Windows 11과 macOS에서 설치하고 실행하는 상세 가이드입니다.

---

## 목차
- [Windows 11 설치 가이드](#windows-11-설치-가이드)
- [macOS 설치 가이드](#macos-설치-가이드)
- [공통 문제 해결](#공통-문제-해결)

---

# Windows 11 설치 가이드

## 📋 사전 요구사항

### 1. Python 3.11 이상 설치

**다운로드 및 설치:**
1. [Python 공식 웹사이트](https://www.python.org/downloads/) 접속
2. "Download Python 3.11.x" 버튼 클릭
3. 설치 프로그램 실행
4. ⚠️ **중요**: "Add Python to PATH" 체크박스 선택
5. "Install Now" 클릭

**설치 확인:**
```powershell
# PowerShell 또는 CMD 열기 (Win + R → cmd)
python --version
# 출력: Python 3.11.x

pip --version
# 출력: pip 23.x.x
```

### 2. Node.js 20 이상 설치

**다운로드 및 설치:**
1. [Node.js 공식 웹사이트](https://nodejs.org/) 접속
2. "LTS" 버전 다운로드 (권장)
3. 설치 프로그램 실행
4. 기본 설정으로 설치 진행

**설치 확인:**
```powershell
node --version
# 출력: v20.x.x

npm --version
# 출력: 10.x.x
```

### 3. Git 설치

**다운로드 및 설치:**
1. [Git for Windows](https://git-scm.com/download/win) 다운로드
2. 설치 프로그램 실행
3. 기본 설정으로 설치 진행

**설치 확인:**
```powershell
git --version
# 출력: git version 2.x.x
```

### 4. Ollama 설치

**다운로드 및 설치:**
1. [Ollama Windows Preview](https://ollama.ai/download/windows) 다운로드
2. `OllamaSetup.exe` 실행
3. 설치 완료 후 자동으로 실행됨

**설치 확인:**
```powershell
# 새 PowerShell 창 열기
ollama --version
# 출력: ollama version x.x.x
```

---

## 🚀 프로젝트 설치 (Windows)

### 1. 저장소 클론

```powershell
# 원하는 디렉토리로 이동
cd D:\Python

# 저장소 클론
git clone https://github.com/laurus-kpa007/agentframework-generativeui.git

# 프로젝트 디렉토리로 이동
cd agentframework-generativeui
```

### 2. Backend 설정

```powershell
# Backend 디렉토리로 이동
cd backend

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (PowerShell)
.\venv\Scripts\Activate.ps1

# 가상 환경 활성화 (CMD)
# venv\Scripts\activate.bat

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 파일 생성
copy .env.example .env

# .env 파일 확인 및 수정 (필요시)
notepad .env
```

**PowerShell 실행 정책 오류 발생 시:**
```powershell
# 관리자 권한으로 PowerShell 실행 후
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 그 후 다시 활성화 시도
.\venv\Scripts\Activate.ps1
```

### 3. Frontend 설정

**새 PowerShell/CMD 창 열기**

```powershell
# 프로젝트 루트에서
cd frontend

# 의존성 설치
npm install

# 환경 변수 파일 생성
copy .env.local.example .env.local

# .env.local 파일 확인 (필요시)
notepad .env.local
```

### 4. Ollama 모델 다운로드

**새 PowerShell/CMD 창 열기**

```powershell
# Ollama 서비스 시작 (자동으로 시작되지 않은 경우)
ollama serve

# 새 창에서 모델 다운로드
ollama pull qwen2.5:latest

# 다른 모델도 설치 가능 (선택사항)
ollama pull llama3.2:latest
ollama pull mistral:latest

# 설치된 모델 확인
ollama list
```

---

## ▶️ 실행 방법 (Windows)

### 방법 1: 각 서비스를 별도 터미널에서 실행

#### Terminal 1: Ollama
```powershell
# Ollama 서비스 실행 (백그라운드에서 자동 실행되므로 보통 필요 없음)
ollama serve
```

#### Terminal 2: Backend
```powershell
cd D:\Python\agentframework-generativeui\backend

# 가상 환경 활성화
.\venv\Scripts\Activate.ps1

# FastAPI 서버 실행
python main.py

# 또는 uvicorn으로 직접 실행
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**실행 확인:**
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

#### Terminal 3: Frontend
```powershell
cd D:\Python\agentframework-generativeui\frontend

# Next.js 개발 서버 실행
npm run dev
```

**실행 확인:**
- Frontend: http://localhost:3000

### 방법 2: VS Code에서 실행

**VS Code 설치:**
1. [Visual Studio Code](https://code.visualstudio.com/) 다운로드 및 설치

**프로젝트 열기:**
```powershell
cd D:\Python\agentframework-generativeui
code .
```

**통합 터미널 사용:**
1. `Ctrl + Shift + `` ` (백틱) - 터미널 열기
2. `+` 아이콘 클릭하여 새 터미널 추가
3. 각 터미널에서 Backend, Frontend 실행

---

# macOS 설치 가이드

## 📋 사전 요구사항

### 1. Homebrew 설치

```bash
# Homebrew 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 설치 확인
brew --version
```

### 2. Python 3.11 이상 설치

```bash
# Homebrew로 Python 설치
brew install python@3.11

# PATH 설정 (필요시)
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 설치 확인
python3 --version
# 출력: Python 3.11.x

pip3 --version
# 출력: pip 23.x.x
```

### 3. Node.js 20 이상 설치

```bash
# Homebrew로 Node.js 설치
brew install node@20

# 또는 nvm 사용 (권장)
brew install nvm

# nvm 설정
mkdir ~/.nvm
echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshrc
echo '[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"' >> ~/.zshrc
source ~/.zshrc

# Node.js 설치
nvm install 20
nvm use 20

# 설치 확인
node --version
# 출력: v20.x.x

npm --version
# 출력: 10.x.x
```

### 4. Git 설치

```bash
# Git 설치 (보통 macOS에 기본 설치됨)
git --version

# 설치되지 않은 경우
brew install git
```

### 5. Ollama 설치

```bash
# Homebrew로 Ollama 설치
brew install ollama

# 또는 공식 웹사이트에서 설치
# https://ollama.ai/download/mac

# 설치 확인
ollama --version
```

---

## 🚀 프로젝트 설치 (macOS)

### 1. 저장소 클론

```bash
# 원하는 디렉토리로 이동
cd ~/Projects

# 저장소 클론
git clone https://github.com/laurus-kpa007/agentframework-generativeui.git

# 프로젝트 디렉토리로 이동
cd agentframework-generativeui
```

### 2. Backend 설정

```bash
# Backend 디렉토리로 이동
cd backend

# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 파일 생성
cp .env.example .env

# .env 파일 수정 (필요시)
nano .env
# 또는
open -e .env
```

### 3. Frontend 설정

**새 터미널 탭/창 열기 (Cmd + T)**

```bash
# 프로젝트 루트에서
cd frontend

# 의존성 설치
npm install

# 환경 변수 파일 생성
cp .env.local.example .env.local

# .env.local 파일 수정 (필요시)
nano .env.local
# 또는
open -e .env.local
```

### 4. Ollama 모델 다운로드

**새 터미널 탭/창 열기**

```bash
# Ollama 서비스 시작
ollama serve

# 새 탭에서 모델 다운로드
ollama pull qwen2.5:latest

# 다른 모델도 설치 가능 (선택사항)
ollama pull llama3.2:latest
ollama pull mistral:latest

# 설치된 모델 확인
ollama list
```

---

## ▶️ 실행 방법 (macOS)

### 방법 1: 각 서비스를 별도 터미널에서 실행

#### Terminal Tab 1: Ollama
```bash
# Ollama 서비스 실행
ollama serve
```

#### Terminal Tab 2: Backend
```bash
cd ~/Projects/agentframework-generativeui/backend

# 가상 환경 활성화
source venv/bin/activate

# FastAPI 서버 실행
python main.py

# 또는 uvicorn으로 직접 실행
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**실행 확인:**
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

#### Terminal Tab 3: Frontend
```bash
cd ~/Projects/agentframework-generativeui/frontend

# Next.js 개발 서버 실행
npm run dev
```

**실행 확인:**
- Frontend: http://localhost:3000

### 방법 2: tmux 사용 (권장)

```bash
# tmux 설치
brew install tmux

# 프로젝트 디렉토리로 이동
cd ~/Projects/agentframework-generativeui

# tmux 세션 시작
tmux new -s agentframework

# 창 분할 (수평)
# Ctrl + B, 그 다음 %

# 창 분할 (수직)
# Ctrl + B, 그 다음 "

# 창 간 이동
# Ctrl + B, 그 다음 화살표 키

# 각 창에서 서비스 실행
# 창 1: ollama serve
# 창 2: cd backend && source venv/bin/activate && python main.py
# 창 3: cd frontend && npm run dev

# tmux 세션 종료
# Ctrl + B, 그 다음 d (detach)

# tmux 세션 다시 연결
# tmux attach -t agentframework
```

### 방법 3: VS Code 사용

```bash
# VS Code 설치
brew install --cask visual-studio-code

# 프로젝트 열기
cd ~/Projects/agentframework-generativeui
code .
```

**통합 터미널 사용:**
1. `Cmd + Shift + `` ` (백틱) - 터미널 열기
2. `+` 아이콘 클릭하여 새 터미널 추가
3. 각 터미널에서 Backend, Frontend 실행

---

## 🐳 Docker 사용 (Windows & macOS 공통)

### Docker 설치

**Windows:**
1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 다운로드
2. WSL 2 활성화 (설치 중 안내됨)
3. Docker Desktop 실행

**macOS:**
```bash
# Homebrew로 설치
brew install --cask docker

# 또는 공식 웹사이트에서 다운로드
# https://www.docker.com/products/docker-desktop/
```

### Docker로 실행

```bash
# 프로젝트 디렉토리로 이동
cd agentframework-generativeui

# 환경 변수 파일 생성
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Docker Compose로 모든 서비스 시작
docker-compose up -d

# Ollama 모델 다운로드
docker exec agentframework-ollama ollama pull qwen2.5:latest

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down

# 완전 삭제 (볼륨 포함)
docker-compose down -v
```

**접속:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Ollama: http://localhost:11434

---

## 공통 문제 해결

### 1. "Address already in use" 오류

**Windows:**
```powershell
# 포트 사용 확인
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 프로세스 종료 (PID 확인 후)
taskkill /PID <PID> /F
```

**macOS:**
```bash
# 포트 사용 확인
lsof -i :8000
lsof -i :3000

# 프로세스 종료
kill -9 <PID>
```

### 2. Ollama 연결 실패

```bash
# Ollama 상태 확인
curl http://localhost:11434/api/tags

# Ollama 재시작
# Windows: 작업 관리자에서 Ollama 종료 후 재실행
# macOS: killall ollama && ollama serve
```

### 3. Python 가상 환경 활성화 오류

**Windows (PowerShell 실행 정책):**
```powershell
# 관리자 권한으로 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS (권한 오류):**
```bash
# 가상 환경 디렉토리 권한 수정
chmod -R 755 venv
```

### 4. npm install 오류

```bash
# npm 캐시 정리
npm cache clean --force

# node_modules 삭제 후 재설치
rm -rf node_modules
npm install

# 또는 yarn 사용
npm install -g yarn
yarn install
```

### 5. CORS 오류

**backend/.env 파일 확인:**
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 6. Ollama 모델 다운로드 느림

```bash
# 더 작은 모델 사용
ollama pull qwen2.5:7b

# 또는
ollama pull llama3.2:3b
```

### 7. Backend 실행 시 모듈 오류

```bash
# 가상 환경에서 다시 설치
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 8. Frontend 빌드 오류

```bash
# Next.js 캐시 삭제
rm -rf .next
npm run dev
```

---

## 📝 추가 팁

### Windows 터미널 개선

**Windows Terminal 설치 (권장):**
1. Microsoft Store에서 "Windows Terminal" 검색 및 설치
2. 기본 프로필을 PowerShell 또는 CMD로 설정
3. 탭으로 여러 터미널 관리 가능

### macOS 터미널 개선

**iTerm2 설치 (권장):**
```bash
brew install --cask iterm2
```

**Oh My Zsh 설치:**
```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

### VS Code 확장 프로그램

추천 확장 프로그램:
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Docker

### 자동 실행 스크립트 생성

**Windows (PowerShell 스크립트):**
```powershell
# start-dev.ps1 생성
$scriptContent = @'
# Backend 실행
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; python main.py"

# Frontend 실행
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

# Ollama는 백그라운드에서 자동 실행됨
Write-Host "모든 서비스가 시작되었습니다!"
'@

$scriptContent | Out-File -FilePath "start-dev.ps1" -Encoding UTF8
```

**macOS (Bash 스크립트):**
```bash
# start-dev.sh 생성
cat > start-dev.sh << 'EOF'
#!/bin/bash

# Backend 실행
osascript -e 'tell app "Terminal" to do script "cd ~/Projects/agentframework-generativeui/backend && source venv/bin/activate && python main.py"'

# Frontend 실행
osascript -e 'tell app "Terminal" to do script "cd ~/Projects/agentframework-generativeui/frontend && npm run dev"'

# Ollama 실행
osascript -e 'tell app "Terminal" to do script "ollama serve"'

echo "모든 서비스가 시작되었습니다!"
EOF

chmod +x start-dev.sh
```

---

## 🎯 다음 단계

설치 완료 후:

1. **브라우저에서 접속**: http://localhost:3000
2. **샘플 쿼리 테스트**: 12개 버튼 클릭
3. **모델 선택**: 우측 상단에서 다른 모델 시도
4. **API 문서 확인**: http://localhost:8000/docs

---

## 📞 도움이 필요하신가요?

- **GitHub Issues**: [이슈 생성](https://github.com/laurus-kpa007/agentframework-generativeui/issues)
- **문서**: [README.md](README.md)
- **빠른 시작**: [QUICKSTART.md](QUICKSTART.md)

---

**문서 버전**: 1.0.0
**최종 업데이트**: 2025-11-21
**작성자**: Claude Code Integration Team
