# 시스템 아키텍처 다이어그램

본 문서는 Agent Framework와 Generative UI 통합 시스템의 상세한 아키텍처 다이어그램을 포함합니다.

---

## 1. 전체 시스템 아키텍처

```mermaid
graph TB
    subgraph "사용자 레이어"
        USER[👤 User]
    end

    subgraph "Frontend - Next.js Application"
        UI[🎨 Chat Interface]
        UICOMP[📦 UI Component Library]
        APICLIENT[🔌 API Client]
        SSE[📡 SSE Handler]

        UI --> APICLIENT
        UI --> SSE
        APICLIENT --> UICOMP
        SSE --> UICOMP
    end

    subgraph "API Gateway - FastAPI"
        ROUTER[🔀 API Router]
        AUTH[🔐 Auth Middleware]
        CORS[🌐 CORS Handler]
        WSHANDLER[⚡ WebSocket/SSE Handler]

        ROUTER --> WSHANDLER
        AUTH --> ROUTER
        CORS --> AUTH
    end

    subgraph "Core Backend - Python"
        AGENT[🤖 Agent Framework]
        ORCHESTRATOR[🎯 Agent Orchestrator]
        TOOLREG[🛠️ Tool Registry]
        MCPMGR[📋 MCP Manager]
        STREAM[🌊 Streaming Service]

        ORCHESTRATOR --> AGENT
        AGENT --> TOOLREG
        AGENT --> MCPMGR
        AGENT --> STREAM
    end

    subgraph "LLM Layer"
        OLLAMA[🧠 Ollama Server]
        MODELS[📚 Local Models<br/>qwen2.5, llama3.2, mistral]

        OLLAMA --> MODELS
    end

    subgraph "MCP Ecosystem"
        MCPGITHUB[🐙 GitHub MCP]
        MCPFS[📁 Filesystem MCP]
        MCPWEATHER[🌤️ Weather MCP]
        MCPCUSTOM[⚙️ Custom MCPs]

        MCPMGR --> MCPGITHUB
        MCPMGR --> MCPFS
        MCPMGR --> MCPWEATHER
        MCPMGR --> MCPCUSTOM
    end

    subgraph "UI Component Mapping"
        UIMAP[🗺️ Component Mapper]
        STOCK[📈 StockCard]
        WEATHER[🌡️ WeatherCard]
        FLIGHT[✈️ FlightCard]
        RECIPE[🍳 RecipeCard]
        MOVIE[🎬 MovieCard]
        MORE[📦 +7 more cards]

        UIMAP --> STOCK
        UIMAP --> WEATHER
        UIMAP --> FLIGHT
        UIMAP --> RECIPE
        UIMAP --> MOVIE
        UIMAP --> MORE
    end

    USER --> UI
    APICLIENT --> ROUTER
    SSE --> WSHANDLER
    ROUTER --> ORCHESTRATOR
    AGENT --> OLLAMA
    TOOLREG --> UIMAP
    UIMAP --> UICOMP

    style USER fill:#FFE5E5
    style UI fill:#E3F2FD
    style AGENT fill:#FFE0B2
    style OLLAMA fill:#C8E6C9
    style MCPMGR fill:#F3E5F5
    style UIMAP fill:#FFF9C4
```

---

## 2. 데이터 흐름 아키텍처

```mermaid
flowchart LR
    subgraph "Input"
        A[User Message]
    end

    subgraph "Processing Pipeline"
        B[FastAPI Router]
        C[Agent Orchestrator]
        D[Intent Analysis]
        E[LLM Processing]
        F[Tool Selection]
        G[MCP Execution]
        H[Response Generation]
        I[Component Selection]
    end

    subgraph "Output"
        J[Streaming Response]
        K[UI Component]
        L[Rendered UI]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L

    style A fill:#BBDEFB
    style E fill:#C8E6C9
    style G fill:#F8BBD0
    style I fill:#FFF9C4
    style L fill:#B2DFDB
```

---

## 3. 채팅 메시지 처리 시퀀스

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant NextJS as Next.js Frontend
    participant FastAPI as FastAPI Gateway
    participant Agent as Agent Framework
    participant LLM as Ollama LLM
    participant MCP as MCP Server
    participant ToolReg as Tool Registry
    participant UI as UI Component

    User->>NextJS: 입력: "Show me AAPL stock"
    NextJS->>FastAPI: POST /api/chat/stream
    FastAPI->>Agent: process_message()

    Agent->>LLM: analyze_intent()
    LLM-->>Agent: Intent: "stock_query"

    Agent->>ToolReg: get_tools_for_intent()
    ToolReg-->>Agent: Tools: ["financial_api"]

    Agent->>MCP: call_tool("financial_api", {symbol: "AAPL"})
    MCP-->>Agent: {price: 150.25, change: +2.5%}

    Agent->>LLM: generate_response()
    LLM-->>Agent: Response text

    Agent->>ToolReg: get_ui_component("stock_query")
    ToolReg-->>Agent: Component: "StockCard"

    Agent->>FastAPI: Stream: {type: "component", data: {...}}
    FastAPI-->>NextJS: SSE: Component data
    NextJS->>UI: Render StockCard
    UI-->>User: Display stock card

    Agent->>FastAPI: Stream: {type: "text", content: "..."}
    FastAPI-->>NextJS: SSE: Text content
    NextJS-->>User: Display message
```

---

## 4. MCP 서버 생명주기

```mermaid
stateDiagram-v2
    [*] --> Inactive: 시스템 시작

    Inactive --> Initializing: activate_mcp()
    Initializing --> Starting: 설정 로드
    Starting --> Connecting: Node.js 프로세스 시작
    Connecting --> Discovering: WebSocket 연결
    Discovering --> Active: 도구 등록

    Active --> Active: 도구 호출
    Active --> Suspending: 일시 중지 요청
    Suspending --> Suspended: 리소스 해제
    Suspended --> Active: 재활성화

    Active --> Stopping: deactivate_mcp()
    Stopping --> Inactive: 프로세스 종료

    Starting --> Error: 연결 실패
    Connecting --> Error: 타임아웃
    Discovering --> Error: 도구 로드 실패
    Error --> Inactive: 정리

    note right of Active
        도구 호출 가능
        모니터링 활성
    end note

    note right of Error
        로그 기록
        알림 발송
    end note
```

---

## 5. 컴포넌트 계층 구조

```mermaid
graph TD
    subgraph "Application Layer"
        APP[App Layout]
        PAGE[Chat Page]
    end

    subgraph "Container Components"
        CHATCONTAINER[Chat Container]
        MCPDASHBOARD[MCP Dashboard]
        SETTINGS[Settings Panel]
    end

    subgraph "Presentation Components"
        MSGLIST[Message List]
        MSGINPUT[Message Input]
        MCPCARD[MCP Card List]
    end

    subgraph "UI Component Library"
        direction LR
        subgraph "Financial"
            STOCK[StockCard]
            FLIGHT[FlightCard]
            HOTEL[HotelCard]
        end

        subgraph "Information"
            WEATHER[WeatherCard]
            NEWS[NewsCard]
            BOOK[BookCard]
        end

        subgraph "Entertainment"
            MOVIE[MovieCard]
            RECIPE[RecipeCard]
            EVENT[EventCard]
        end

        subgraph "Commerce"
            PRODUCT[ProductCard]
            RESTAURANT[RestaurantCard]
            EXERCISE[ExerciseCard]
        end
    end

    APP --> PAGE
    PAGE --> CHATCONTAINER
    PAGE --> MCPDASHBOARD
    PAGE --> SETTINGS

    CHATCONTAINER --> MSGLIST
    CHATCONTAINER --> MSGINPUT
    MCPDASHBOARD --> MCPCARD

    MSGLIST --> STOCK
    MSGLIST --> WEATHER
    MSGLIST --> MOVIE
    MSGLIST --> PRODUCT
    MSGLIST --> FLIGHT
    MSGLIST --> NEWS
    MSGLIST --> RECIPE
    MSGLIST --> HOTEL
    MSGLIST --> BOOK
    MSGLIST --> EVENT
    MSGLIST --> RESTAURANT
    MSGLIST --> EXERCISE

    style APP fill:#E1F5FE
    style CHATCONTAINER fill:#F3E5F5
    style STOCK fill:#C8E6C9
    style WEATHER fill:#FFECB3
    style MOVIE fill:#FFCCBC
    style PRODUCT fill:#B2DFDB
```

---

## 6. Backend 모듈 구조

```mermaid
graph LR
    subgraph "FastAPI Application"
        MAIN[main.py<br/>App Entry Point]
    end

    subgraph "Routers"
        R_CHAT[chat.py<br/>채팅 엔드포인트]
        R_MCP[mcp.py<br/>MCP 관리]
        R_TOOLS[ui_tools.py<br/>UI 도구 매핑]
        R_HEALTH[health.py<br/>헬스체크]
    end

    subgraph "Services"
        S_OLLAMA[ollama_service.py<br/>LLM 통신]
        S_STREAM[streaming_service.py<br/>SSE 스트리밍]
        S_SESSION[session_service.py<br/>세션 관리]
    end

    subgraph "Agents"
        A_BASE[base_agent.py<br/>기본 에이전트]
        A_CHAT[chat_agent.py<br/>채팅 에이전트]
        A_TOOL[tool_agent.py<br/>도구 에이전트]
    end

    subgraph "MCP Layer"
        M_MANAGER[server_manager.py<br/>서버 관리]
        M_REGISTRY[tool_registry.py<br/>도구 등록]
        M_CLIENT[mcp_client.py<br/>MCP 클라이언트]
    end

    subgraph "Models"
        MOD_SCHEMA[schemas.py<br/>Pydantic 모델]
        MOD_ENUM[enums.py<br/>상수 정의]
    end

    subgraph "Config"
        CFG_SETTINGS[settings.py<br/>환경 설정]
        CFG_MCP[mcp_servers.yaml<br/>MCP 설정]
    end

    MAIN --> R_CHAT
    MAIN --> R_MCP
    MAIN --> R_TOOLS
    MAIN --> R_HEALTH

    R_CHAT --> S_STREAM
    R_CHAT --> A_CHAT
    R_MCP --> M_MANAGER
    R_TOOLS --> M_REGISTRY

    A_CHAT --> A_BASE
    A_CHAT --> S_OLLAMA
    A_TOOL --> A_BASE
    A_TOOL --> M_MANAGER

    M_MANAGER --> M_CLIENT
    M_REGISTRY --> M_CLIENT

    S_OLLAMA --> CFG_SETTINGS
    M_MANAGER --> CFG_MCP

    A_BASE --> MOD_SCHEMA
    S_STREAM --> MOD_SCHEMA

    style MAIN fill:#FFD54F
    style R_CHAT fill:#81C784
    style A_CHAT fill:#64B5F6
    style M_MANAGER fill:#BA68C8
    style S_OLLAMA fill:#4DB6AC
```

---

## 7. MCP 도구 → UI 컴포넌트 매핑

```mermaid
graph TB
    subgraph "MCP Tools"
        T_FINANCE[Financial API Tool]
        T_WEATHER[Weather API Tool]
        T_SEARCH[Search API Tool]
        T_GITHUB[GitHub API Tool]
        T_FILE[File System Tool]
        T_CUSTOM[Custom Tools]
    end

    subgraph "Tool Registry<br/>매핑 로직"
        MAPPER{Component<br/>Mapper}
    end

    subgraph "UI Components"
        UI_STOCK[StockCard<br/>FlightCard<br/>HotelCard]
        UI_WEATHER[WeatherCard]
        UI_SEARCH[ProductCard<br/>RestaurantCard]
        UI_GITHUB[NewsCard<br/>EventCard]
        UI_FILE[RecipeCard<br/>BookCard]
        UI_CUSTOM[ExerciseCard<br/>MovieCard]
    end

    T_FINANCE --> MAPPER
    T_WEATHER --> MAPPER
    T_SEARCH --> MAPPER
    T_GITHUB --> MAPPER
    T_FILE --> MAPPER
    T_CUSTOM --> MAPPER

    MAPPER -->|금융 쿼리| UI_STOCK
    MAPPER -->|날씨 쿼리| UI_WEATHER
    MAPPER -->|검색 쿼리| UI_SEARCH
    MAPPER -->|GitHub 쿼리| UI_GITHUB
    MAPPER -->|파일 쿼리| UI_FILE
    MAPPER -->|기타 쿼리| UI_CUSTOM

    style MAPPER fill:#FFF59D
    style T_FINANCE fill:#C5E1A5
    style UI_STOCK fill:#90CAF9
```

---

## 8. 스트리밍 프로토콜 구조

```mermaid
sequenceDiagram
    participant Client as Next.js Client
    participant SSE as SSE Stream
    participant FastAPI as FastAPI Server
    participant Agent as Agent

    Client->>FastAPI: POST /api/chat/stream
    FastAPI->>Agent: start_processing()

    loop Streaming Loop
        Agent->>FastAPI: yield event

        alt Component Event
            FastAPI->>SSE: data: {"type": "component", ...}
            SSE->>Client: Render UI Component
        else Text Event
            FastAPI->>SSE: data: {"type": "text", ...}
            SSE->>Client: Append text
        else Tool Event
            FastAPI->>SSE: data: {"type": "tool_call", ...}
            SSE->>Client: Show tool status
        else Error Event
            FastAPI->>SSE: data: {"type": "error", ...}
            SSE->>Client: Display error
        end
    end

    Agent->>FastAPI: processing complete
    FastAPI->>SSE: data: {"type": "done"}
    SSE->>Client: Close stream

    Note over Client,Agent: 이벤트 타입별 처리
```

---

## 9. 보안 레이어 구조

```mermaid
graph TB
    subgraph "External"
        EXT[External Request]
    end

    subgraph "Security Layers"
        CORS[CORS Middleware<br/>Origin 검증]
        RATE[Rate Limiter<br/>요청 제한]
        AUTH[Auth Middleware<br/>토큰 검증]
        VALID[Input Validator<br/>Pydantic]
    end

    subgraph "Application"
        APP[Application Logic]
    end

    subgraph "MCP Security"
        SANDBOX[Sandbox Executor<br/>격리 실행]
        PERM[Permission Manager<br/>권한 관리]
        AUDIT[Audit Logger<br/>감사 로그]
    end

    subgraph "Data Protection"
        ENCRYPT[Data Encryption<br/>암호화]
        SANITIZE[Output Sanitizer<br/>XSS 방지]
    end

    EXT --> CORS
    CORS --> RATE
    RATE --> AUTH
    AUTH --> VALID
    VALID --> APP

    APP --> SANDBOX
    SANDBOX --> PERM
    PERM --> AUDIT

    APP --> ENCRYPT
    ENCRYPT --> SANITIZE
    SANITIZE --> EXT

    style CORS fill:#FFCDD2
    style RATE fill:#F8BBD0
    style AUTH fill:#E1BEE7
    style SANDBOX fill:#D1C4E9
    style ENCRYPT fill:#C5CAE9
```

---

## 10. 배포 아키텍처

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx / Traefik]
    end

    subgraph "Frontend Cluster"
        FE1[Next.js Instance 1]
        FE2[Next.js Instance 2]
        FE3[Next.js Instance 3]
    end

    subgraph "Backend Cluster"
        BE1[FastAPI Instance 1<br/>+ Agent Framework]
        BE2[FastAPI Instance 2<br/>+ Agent Framework]
        BE3[FastAPI Instance 3<br/>+ Agent Framework]
    end

    subgraph "LLM Service"
        OLLAMA1[Ollama Server 1<br/>GPU Node]
        OLLAMA2[Ollama Server 2<br/>GPU Node]
    end

    subgraph "MCP Services"
        MCP1[MCP Server Pool 1]
        MCP2[MCP Server Pool 2]
    end

    subgraph "Shared Storage"
        REDIS[Redis Cache<br/>세션/캐시]
        LOGS[Log Storage<br/>ELK/Loki]
        METRICS[Metrics DB<br/>Prometheus]
    end

    LB --> FE1
    LB --> FE2
    LB --> FE3

    FE1 --> BE1
    FE2 --> BE2
    FE3 --> BE3

    BE1 --> OLLAMA1
    BE2 --> OLLAMA1
    BE3 --> OLLAMA2

    BE1 --> MCP1
    BE2 --> MCP2
    BE3 --> MCP1

    BE1 --> REDIS
    BE2 --> REDIS
    BE3 --> REDIS

    BE1 --> LOGS
    BE2 --> LOGS
    BE3 --> LOGS

    BE1 --> METRICS
    BE2 --> METRICS
    BE3 --> METRICS

    style LB fill:#FFE082
    style OLLAMA1 fill:#A5D6A7
    style REDIS fill:#EF9A9A
    style LOGS fill:#90CAF9
    style METRICS fill:#CE93D8
```

---

## 11. 개발 환경 구조

```mermaid
graph LR
    subgraph "Developer Machine"
        DEV[Developer]
        IDE[VS Code / IDE]
        GIT[Git Client]
    end

    subgraph "Local Services"
        DOCKER[Docker Compose]

        subgraph "Containers"
            C_FE[Next.js<br/>:3000]
            C_BE[FastAPI<br/>:8000]
            C_OLLAMA[Ollama<br/>:11434]
        end
    end

    subgraph "External Services"
        GITHUB[GitHub Repo]
        REGISTRY[Docker Registry]
    end

    DEV --> IDE
    IDE --> GIT
    GIT --> GITHUB

    DEV --> DOCKER
    DOCKER --> C_FE
    DOCKER --> C_BE
    DOCKER --> C_OLLAMA

    C_FE --> C_BE
    C_BE --> C_OLLAMA

    IDE -.->|Hot Reload| C_FE
    IDE -.->|Hot Reload| C_BE

    DOCKER -.->|Pull Images| REGISTRY

    style DEV fill:#FFF59D
    style DOCKER fill:#81C784
    style C_FE fill:#64B5F6
    style C_BE fill:#FFB74D
    style C_OLLAMA fill:#4DB6AC
```

---

## 12. 성능 모니터링 플로우

```mermaid
graph TD
    subgraph "Application"
        APP[Application Events]
        METRICS[Metrics Collection]
        TRACES[Distributed Tracing]
        LOGS[Application Logs]
    end

    subgraph "Collection Layer"
        PROM[Prometheus<br/>Metrics]
        JAEGER[Jaeger<br/>Traces]
        LOKI[Loki<br/>Logs]
    end

    subgraph "Visualization"
        GRAFANA[Grafana Dashboards]
        ALERTS[Alert Manager]
    end

    subgraph "Key Metrics"
        TTFT[TTFT<br/>< 500ms]
        LATENCY[API Latency<br/>P95, P99]
        ERROR[Error Rate<br/>< 1%]
        THROUGHPUT[Throughput<br/>req/s]
    end

    APP --> METRICS
    APP --> TRACES
    APP --> LOGS

    METRICS --> PROM
    TRACES --> JAEGER
    LOGS --> LOKI

    PROM --> GRAFANA
    JAEGER --> GRAFANA
    LOKI --> GRAFANA

    PROM --> ALERTS

    GRAFANA --> TTFT
    GRAFANA --> LATENCY
    GRAFANA --> ERROR
    GRAFANA --> THROUGHPUT

    ALERTS -.->|Notification| APP

    style GRAFANA fill:#FFA726
    style TTFT fill:#66BB6A
    style LATENCY fill:#42A5F5
    style ERROR fill:#EF5350
    style THROUGHPUT fill:#AB47BC
```

---

## 다이어그램 설명

### 주요 아키텍처 패턴

1. **레이어드 아키텍처**: Frontend, API Gateway, Backend Core, LLM/MCP 계층 분리
2. **마이크로서비스 요소**: MCP 서버를 독립적인 서비스로 관리
3. **이벤트 드리븐**: SSE 기반 비동기 스트리밍
4. **플러그인 아키텍처**: MCP 도구를 동적으로 추가/제거
5. **컴포넌트 기반 UI**: 재사용 가능한 UI 컴포넌트 라이브러리

### 핵심 설계 원칙

- **느슨한 결합**: 각 레이어는 독립적으로 교체 가능
- **높은 응집도**: 관련 기능을 모듈로 그룹화
- **확장성**: 수평 확장 가능한 구조
- **관찰 가능성**: 로깅, 메트릭, 트레이싱 통합
- **보안 우선**: 다층 보안 레이어

---

**다이어그램 버전**: 1.0.0
**최종 업데이트**: 2025-11-21
