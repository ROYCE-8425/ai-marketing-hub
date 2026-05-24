# AI Marketing Hub — Diagrams cho Báo cáo

> Copy trực tiếp Mermaid code vào slide hoặc dùng [mermaid.live](https://mermaid.live) để render.

---

## 1. Use Case Diagram

```mermaid
graph TB
    subgraph Actors
        U["👤 User<br/>(Editor/Viewer)"]
        A["👑 Admin"]
        AI["🤖 Groq LLaMA 3.3"]
        GSC["🔗 Google Search Console"]
        PSI["⚡ PageSpeed Insights"]
    end

    subgraph UC_SEO["Phân tích SEO"]
        UC1["SEO Audit<br/>(On-page)"]
        UC2["Technical SEO<br/>(8 tiêu chí)"]
        UC3["Core Web Vitals<br/>(LCP, INP, CLS)"]
        UC4["CRO & Trust<br/>Analysis"]
        UC5["SERP Live"]
        UC6["Backlink<br/>Analyzer"]
        UC7["Broken Link<br/>Checker"]
        UC8["Schema<br/>Validator"]
    end

    subgraph UC_KW["Từ khóa"]
        UC9["Rank Tracker"]
        UC10["AI Keyword<br/>Analysis"]
        UC11["Competitor Gap<br/>Analysis"]
    end

    subgraph UC_CONTENT["Nội dung AI"]
        UC12["AI Content<br/>Planner"]
        UC13["AI Article<br/>Writer"]
        UC14["Spin Editor"]
        UC15["Content<br/>Humanizer"]
    end

    subgraph UC_GEO["Tối ưu GEO"]
        UC16["GEO Optimizer<br/>(E-E-A-T)"]
        UC17["Schema.org<br/>Generator<br/>(12 types)"]
    end

    subgraph UC_TOOLS["Công cụ & Quản lý"]
        UC18["Content Calendar"]
        UC19["A/B Testing SEO"]
        UC20["Report Generator"]
        UC21["Campaign Tracker"]
        UC22["File Converter"]
        UC23["Multi-site Manager"]
    end

    subgraph UC_AUTH["Hệ thống"]
        UC24["Đăng ký /<br/>Đăng nhập"]
        UC25["Quản lý<br/>người dùng"]
        UC26["WordPress<br/>Publisher"]
    end

    U --> UC1 & UC2 & UC3 & UC4 & UC5 & UC6 & UC7 & UC8
    U --> UC9 & UC10 & UC11
    U --> UC12 & UC13 & UC14 & UC15
    U --> UC16 & UC17
    U --> UC18 & UC19 & UC20 & UC21 & UC22 & UC23
    U --> UC24 & UC26

    A --> UC25

    UC3 -.->|"API call"| PSI
    UC9 -.->|"Sync data"| GSC
    UC10 -.->|"AI analysis"| AI
    UC12 -.->|"Generate outline"| AI
    UC13 -.->|"Write article"| AI
    UC14 -.->|"Spin content"| AI
    UC16 -.->|"GEO analysis"| AI
    UC5 -.->|"Search data"| GSC
```

---

## 2. Sequence Diagram — Luồng AI Article Writer (luồng phức tạp nhất)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend<br/>(React SPA)
    participant BE as Backend<br/>(FastAPI)
    participant Groq as Groq API<br/>(LLaMA 3.3 70B)
    participant DB as SQLite<br/>(6 databases)

    Note over User, DB: Phase 1 — Đăng nhập
    User->>FE: Mở app
    FE->>FE: isAuthenticated()? → false
    FE->>FE: Redirect /login
    User->>FE: Nhập email + password
    FE->>BE: POST /api/auth/login
    BE->>DB: SELECT user WHERE email=?
    DB-->>BE: user row
    BE->>BE: verify_password(bcrypt)
    BE->>BE: create_access_token(JWT)
    BE->>DB: INSERT refresh_token
    BE-->>FE: {access_token, refresh_token, user}
    FE->>FE: setTokens(localStorage)
    FE->>FE: Navigate → Dashboard

    Note over User, DB: Phase 2 — Tạo Content Plan
    User->>FE: Click "Viết nội dung AI"
    User->>FE: Nhập keyword + audience
    FE->>BE: POST /api/plan-content<br/>{keyword, audience}
    BE->>Groq: POST /chat/completions<br/>System: "SEO content planner"<br/>User: keyword + audience
    Groq-->>BE: JSON outline<br/>{topic, sections[], meta}
    BE-->>FE: PlanContentResponse
    FE->>FE: Render outline + sections

    Note over User, DB: Phase 3 — Viết bài hoàn chỉnh
    User->>FE: Click "Viết toàn bộ bài"
    FE->>BE: POST /api/content/write-full<br/>{topic, sections[]}
    BE->>Groq: POST /chat/completions<br/>System: "Vietnamese SEO writer"<br/>User: outline + sections
    Note right of Groq: max_tokens: 8000<br/>temperature: 0.7<br/>timeout: 180s
    Groq-->>BE: Markdown article
    BE-->>FE: {content: "# Heading..."}
    FE->>FE: Render Markdown preview

    Note over User, DB: Phase 4 — Humanize & Polish
    User->>FE: Copy nội dung → Spin Editor
    FE->>BE: POST /api/content/polish<br/>{raw_content}
    BE->>BE: ContentScrubber.scrub()
    Note right of BE: Remove zero-width chars<br/>Replace AI phrases<br/>Fix em-dashes
    BE->>BE: ReadabilityScorer.analyze()
    BE->>BE: EngagementAnalyzer.analyze()
    BE-->>FE: PolishResponse<br/>{humanized, score, grade}
    FE->>FE: Show before/after comparison

    Note over User, DB: Phase 5 — Publish
    User->>FE: Click "Publish to WordPress"
    FE->>BE: POST /api/publish/wordpress<br/>{title, content, wp_url, credentials}
    BE->>BE: wordpress_publisher.publish()
    BE-->>FE: {status: "published", url}
```

---

## 3. Activity Diagram — Luồng SEO Audit

```mermaid
flowchart TD
    Start([User mở trang<br/>Kiểm tra SEO]) --> A[Nhập URL + Từ khóa]
    A --> B{URL hợp lệ?}
    B -->|Không| C[Hiển thị lỗi<br/>validation]
    C --> A
    B -->|Có| D[FE gọi POST<br/>/api/seo/audit]
    D --> E[Backend: httpx<br/>fetch HTML content]
    E --> F{Fetch thành công?}
    F -->|Không| G[Trả lỗi:<br/>Không truy cập được URL]
    G --> H[FE hiển thị error]
    F -->|Có| I[BeautifulSoup<br/>parse HTML]
    I --> J[seo_quality_rater:<br/>Chấm điểm 8 danh mục]
    J --> K[keyword_analyzer:<br/>Density, LSI, Heatmap]
    K --> L[cro_checker:<br/>CRO checklist]
    L --> M[trust_signal_analyzer:<br/>Trust signals]
    M --> N[Tổng hợp kết quả<br/>AuditResponse]
    N --> O[FE render:<br/>ScoreRing + CategoryBar<br/>+ Heatmap + Issues]
    O --> P{User muốn<br/>kiểm tra mới?}
    P -->|Có| Q[Click 'Kiểm tra mới']
    Q --> A
    P -->|Không| R[Chuyển sang<br/>CRO Analysis hoặc<br/>Content Planner]
    R --> End([Kết thúc])
    H --> End
```

---

## 4. ERD — Lược đồ quan hệ dữ liệu (6 SQLite databases)

```mermaid
erDiagram
    %% ─── auth.db ───
    users {
        int id PK
        text email UK "UNIQUE"
        text full_name
        text hashed_password
        text role "admin|editor|viewer"
        int is_active "0|1"
        text created_at
        text last_login
    }

    refresh_tokens {
        int id PK
        int user_id FK
        text token UK "UNIQUE"
        text expires_at
        text created_at
    }

    users ||--o{ refresh_tokens : "has"

    %% ─── sites.db ───
    managed_sites {
        int id PK
        text name
        text url UK "UNIQUE"
        text description
        text niche
        int is_active "0|1"
        int last_scan_score
        text last_scan_date
        text created_at
    }

    %% ─── rank_tracker.db ───
    tracked_keywords {
        int id PK
        text keyword
        text site_url
        text tag
        text created_at
    }

    ranking_history {
        int id PK
        text keyword
        text site_url
        real position
        int clicks
        int impressions
        real ctr
        text source "gsc|sample|csv"
        text checked_at
    }

    tracked_keywords ||--o{ ranking_history : "tracks"
    managed_sites ||--o{ tracked_keywords : "belongs to"

    %% ─── content_calendar.db ───
    content_items {
        int id PK
        text title
        text content_type "blog|page|promotion"
        text status "draft|scheduled|published|idea"
        text scheduled_date
        text published_date
        text primary_keyword
        text meta_description
        text notes
        text author
        text site_url
        text created_at
        text updated_at
    }

    managed_sites ||--o{ content_items : "has content"

    %% ─── ab_tests.db ───
    ab_tests {
        int id PK
        text name
        text url_a
        text url_b
        text primary_keyword
        text status "draft|running|completed"
        text result_a "JSON"
        text result_b "JSON"
        text winner
        text ai_analysis
        text created_at
        text completed_at
    }

    %% ─── usage_history.db ───
    usage_log {
        int id PK
        text endpoint
        text method
        text input_data "JSON"
        text output_data "JSON"
        int status_code
        real duration_ms
        text error
        text created_at
    }
```

---

## 5. Component Architecture Diagram

```mermaid
graph TB
    subgraph Frontend["Frontend (React 19 SPA)"]
        direction TB
        RT["react-router-dom<br/>22 routes"]
        APP["App.tsx<br/>(74KB, routing + layout)"]
        
        subgraph Components["37 Components"]
            C1["DashboardOverview"]
            C2["CoreWebVitals"]
            C3["BrokenLinkChecker"]
            C4["SchemaValidator"]
            C5["GeoOptimizer"]
            C6["RankTracker"]
            C7["SpinEditor"]
            C8["ContentPlanner"]
            C9["AuthPage"]
            C10["...28 more"]
        end

        subgraph Hooks["6 Custom Hooks"]
            H1["useSeoAudit"]
            H2["useSerpLive"]
            H3["useAutoFill"]
            H4["useOpportunities"]
            H5["usePolish"]
            H6["usePublish"]
        end

        subgraph Lib["Libraries"]
            L1["apiConfig.ts"]
            L2["auth.ts<br/>(authFetch, JWT)"]
            L3["history.ts"]
            L4["i18n.ts"]
        end

        subgraph SEO_Meta["SEO Infrastructure"]
            S1["SEOHead<br/>(react-helmet-async)"]
            S2["JsonLd<br/>(3 schema builders)"]
            S3["seoConfig<br/>(22 route metadata)"]
        end

        RT --> APP --> Components
        Components --> Hooks
        Hooks --> Lib
        APP --> SEO_Meta
    end

    subgraph Backend["Backend (FastAPI)"]
        direction TB
        MAIN["main.py<br/>(middleware + 15 routers)"]
        
        subgraph Routers["15 API Routers"]
            R1["api_seo.py"]
            R2["api_seo_tools.py"]
            R3["api_content.py"]
            R4["api_content_writer.py"]
            R5["api_new_features.py"]
            R6["api_user_auth.py"]
            R7["...9 more"]
        end

        subgraph Core["50 Core Modules"]
            M1["seo_quality_rater"]
            M2["keyword_analyzer"]
            M3["core_web_vitals"]
            M4["broken_link_checker"]
            M5["article_writer"]
            M6["content_scrubber"]
            M7["geo_analyzer"]
            M8["rank_tracker"]
            M9["auth / auth_db"]
            M10["...41 more"]
        end

        MAIN --> Routers --> Core
    end

    subgraph Data["Data Layer"]
        DB1[("auth.db")]
        DB2[("sites.db")]
        DB3[("rank_tracker.db")]
        DB4[("content_calendar.db")]
        DB5[("ab_tests.db")]
        DB6[("usage_history.db")]
    end

    subgraph External["External APIs"]
        E1["Groq API<br/>(LLaMA 3.3 70B)"]
        E2["Google PageSpeed<br/>Insights"]
        E3["Google Search<br/>Console"]
        E4["DataForSEO"]
    end

    Frontend -->|"fetch / authFetch<br/>localhost:8000/api"| Backend
    Core --> Data
    Core -->|"httpx async"| External
```

---

## 6. Deployment Architecture

```mermaid
graph LR
    subgraph Docker["Docker Compose"]
        FE_C["Frontend Container<br/>Node 22 + nginx<br/>:5173"]
        BE_C["Backend Container<br/>Python 3.13 + Uvicorn<br/>:8000"]
        VOL[("SQLite Volumes<br/>6 databases")]
    end

    USER["🌐 Browser"] -->|":5173"| FE_C
    FE_C -->|"API proxy<br/>:8000"| BE_C
    BE_C --> VOL
    BE_C -->|"HTTPS"| GROQ["Groq API"]
    BE_C -->|"HTTPS"| GSC["Google APIs"]
```

---

## 7. Auth Flow — JWT Token Lifecycle

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant BE as Backend
    participant DB as auth.db

    User->>FE: POST /login {email, password}
    FE->>BE: POST /api/auth/login
    BE->>DB: get_user_by_email()
    DB-->>BE: user row
    BE->>BE: bcrypt.verify(password)
    BE->>BE: create_access_token(30min)
    BE->>BE: create_refresh_token(7d)
    BE->>DB: store_refresh_token()
    BE-->>FE: {access_token, refresh_token, user}
    FE->>FE: localStorage.set(tokens)

    Note over User, DB: Subsequent API calls
    FE->>BE: GET /api/... + Authorization: Bearer <access_token>
    BE->>BE: decode_token() → user_id

    Note over User, DB: Token expired (401)
    FE->>BE: GET /api/... → 401
    FE->>BE: POST /api/auth/refresh {refresh_token}
    BE->>DB: verify_refresh_token()
    BE->>DB: revoke old token (rotation)
    BE->>BE: create new token pair
    BE->>DB: store new refresh_token
    BE-->>FE: {new access_token, new refresh_token}
    FE->>FE: Update localStorage
    FE->>BE: Retry original request
```

