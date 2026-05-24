# AI Marketing Hub — Project Context (Master Reference)
<!-- Cập nhật lần cuối: 2026-05-22 | Phase 20 + SEO Integration -->
<!-- ĐỌC FILE NÀY ĐẦU TIÊN khi bắt đầu conversation mới -->

## 1. Tổng quan dự án

| Key | Value |
|-----|-------|
| **Tên** | AI Marketing Hub |
| **Tác giả** | Trần Như Ý |
| **Version** | v3.1.0 — Phase 20 + SEO Integration |
| **LOC** | ~30,000+ |
| **Mục đích** | Nền tảng AI-powered SEO & Marketing automation cho thị trường Việt Nam |
| **Test tenant** | binhphuocmitsubishi.com |
| **Repo path** | `c:\Users\199X\OneDrive\Máy tính\1\ai-marketing-hub` |

## 2. Tech Stack

```
Frontend:  React 19 + TypeScript 6 + Vite 8
           react-router-dom (URL routing, 22 routes)
           react-helmet-async (dynamic SEO meta tags)
           recharts (charts)
           Vanilla CSS (NO Tailwind) — dark glassmorphism UI
           Colors: purple #8b5cf6, cyan #06b6d4

Backend:   FastAPI (Python 3.12) + Uvicorn
           Groq LLaMA 3.3 70B (AI engine)
           SQLite × 4 databases
           httpx, beautifulsoup4, scikit-learn

CI/CD:     GitHub Actions (Lighthouse CI, linkinator, SEO audit)
           lighthouserc.js config
```

## 3. Cấu trúc thư mục

```
ai-marketing-hub/
├── frontend/                 # React SPA
│   ├── public/
│   │   ├── robots.txt        # SEO: crawler rules
│   │   ├── sitemap.xml       # SEO: 22 URLs
│   │   └── favicon.svg
│   ├── src/
│   │   ├── App.tsx           # Main app (70KB, routing + layout)
│   │   ├── main.tsx          # Entry (HelmetProvider + BrowserRouter)
│   │   ├── index.css         # Global styles (82KB+)
│   │   ├── components/       # 31 components
│   │   │   ├── SEO/          # SEOHead, JsonLd, seoConfig
│   │   │   ├── CoreWebVitals.tsx + .css
│   │   │   ├── BrokenLinkChecker.tsx
│   │   │   ├── SchemaValidator.tsx
│   │   │   ├── DashboardOverview.tsx
│   │   │   ├── GeoOptimizer.tsx (8-tab schema generator)
│   │   │   ├── RankTracker.tsx
│   │   │   ├── SpinEditor.tsx
│   │   │   ├── SatelliteManager.tsx
│   │   │   └── ... (28+ more)
│   │   ├── hooks/            # 6 custom hooks
│   │   ├── lib/              # apiConfig, history, i18n
│   │   └── types/            # TypeScript types
│   ├── index.html            # SEO-optimized (meta, OG, JSON-LD)
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── main.py               # FastAPI app, 15 routers, middleware
│   ├── routers/              # 15 router files
│   │   ├── api_seo.py        # SEO audit endpoints
│   │   ├── api_seo_tools.py  # CWV, broken links, schema validator, sitemap validator
│   │   ├── api_content.py    # Competitor gap, content planning
│   │   ├── api_content_writer.py # AI full article writing (Groq)
│   │   ├── api_new_features.py # Rank tracker, spin, GEO schemas (12 types)
│   │   ├── api_phase2.py     # Tech SEO, reports, backlinks
│   │   ├── api_phase3.py     # Calendar, sites, A/B testing
│   │   ├── api_satellite.py  # Satellite sites management
│   │   ├── api_data.py       # GSC/GA4 data connectors
│   │   ├── api_convert.py    # File conversion
│   │   ├── api_auth.py       # Google OAuth2
│   │   ├── api_user_auth.py  # JWT auth (login/register/RBAC)
│   │   ├── api_polish.py     # Content humanizer
│   │   ├── api_serp.py       # Live SERP
│   │   └── api_execution.py  # WordPress publish, opportunities
│   ├── core/                 # 47 core modules
│   │   ├── core_web_vitals.py
│   │   ├── broken_link_checker.py
│   │   ├── schema_validator.py
│   │   ├── sitemap_validator.py
│   │   ├── geo_analyzer.py (12 schema generators)
│   │   ├── seo_quality_rater.py
│   │   ├── keyword_analyzer.py
│   │   ├── technical_seo.py
│   │   ├── spin_editor.py
│   │   ├── rank_tracker.py
│   │   └── ... (37+ more)
│   ├── data/                 # Runtime data
│   ├── requirements.txt
│   └── *.db                  # SQLite databases
│
├── OpenSpec/                 # Project documentation
│   ├── PROJECT_CONTEXT.md    # ← BẠN ĐANG ĐỌC FILE NÀY
│   ├── SEO_INTEGRATION_SPEC.md  # SEO spec (35KB, 1100 dòng)
│   ├── PHAN_TICH_CHUC_NANG.md   # Functional analysis
│   ├── PHAN_TICH_PHAT_TRIEN.md  # Development plan
│   ├── CODEX_CONTEXT.md         # Full project context
│   ├── CLAUDE.md                # AI coding rules
│   └── ... (5 more docs)
│
├── .github/workflows/
│   └── seo-audit.yml         # CI: Lighthouse, linkinator, validation
├── scripts/
│   └── seo-check.ps1         # Local SEO checker
├── lighthouserc.js           # Lighthouse CI config
├── docs/                     # Architecture diagrams (PNG)
├── rules/                    # 15 language rule directories
└── skills/                   # 183 agentic skill directories
```

## 4. Modules đã hoàn thành (20+3 modules)

### SEO Analysis (5 + 3 new)
1. SEO Audit — keyword density, quality scoring A-F
2. Technical SEO Scanner — 8 criteria scan
3. CRO & Trust — CRO checklist, CTA, trust signals
4. Live SERP — DuckDuckGo / DataForSEO
5. Backlink Analyzer — internal/external links
6. **[NEW] Core Web Vitals** — PageSpeed Insights API (LCP, INP, CLS)
7. **[NEW] Broken Link Checker** — async crawl + health score
8. **[NEW] Schema Validator** — JSON-LD validation, 25+ types

### Keywords (3)
9. Rank Tracker — SQLite, CSV, GSC sync, alerts
10. AI Keyword Analysis — Groq + TF-IDF + KMeans
11. Competitor Gap — content gap analysis

### Content (4)
12. AI Content Planner — outline, sections, meta
13. Spin Editor — 4 tones, 3 levels, keyword preserve
14. GEO Optimizer — E-E-A-T, **12 Schema.org generators** (FAQ, LocalBusiness, Product, Article, Breadcrumb, Organization, WebSite, JobPosting, Event, HowTo, Video, Review)
15. Content Calendar — CRUD, AI topic suggestions

### Tools (4)
16. A/B Testing SEO — compare 2 versions
17. AI Report Generator
18. Campaign Tracker — 8-factor scoring
19. File Converter — PDF/Word/Excel/PPT → Markdown

### Data & Management (4)
20. Dashboard — GSC + GA4 charts
21. Multi-site Manager
22. WordPress Publisher + Yoast SEO
23. Google Search Console OAuth2

### Infrastructure
24. GEO Satellite Sites — blog network management
25. Usage History — API call logging

## 5. Routing Map (22 routes)

| Path | Component | Tab ID |
|------|-----------|--------|
| `/` | DashboardOverview | dashboard |
| `/seo-audit` | SEO Audit (inline) | seo |
| `/technical-seo` | TechnicalSeo | techseo |
| `/cro` | CroDashboard | cro |
| `/serp` | SerpResultsPanel | serp |
| `/backlinks` | BacklinkAnalyzer | backlinks |
| `/rank-tracker` | RankTracker | ranktracker |
| `/keywords` | AI Keywords (inline) | aikeys |
| `/competitor` | CompetitorRadar | competitor |
| `/content-planner` | ContentPlanner | planner |
| `/spin-editor` | SpinEditor | spineditor |
| `/geo-optimizer` | GeoOptimizer | geo |
| `/content-calendar` | ContentCalendarPanel | calendar |
| `/ab-testing` | AbTesting | abtest |
| `/report` | ReportGenerator | report |
| `/campaign` | CampaignTracker | tracker |
| `/file-converter` | FileConverter | fileconvert |
| `/sites` | SiteManager | sites |
| `/google-setup` | GoogleSetup | googlesetup |
| `/core-web-vitals` | CoreWebVitals | cwv |
| `/broken-links` | BrokenLinkChecker | brokenlinks |
| `/schema-validator` | SchemaValidator | schemavalidator |

## 6. API Endpoints (55+)

Backend chạy tại: `http://localhost:8000`
Tất cả API prefix: `/api/`

### SEO Tools (mới)
- `POST /api/seo-tools/core-web-vitals`
- `POST /api/seo-tools/validate-sitemap`
- `POST /api/seo-tools/broken-links`
- `POST /api/seo-tools/validate-schema`

### GEO Schema Generators (12)
- `POST /api/geo/analyze`
- `POST /api/geo/generate-faq`
- `POST /api/geo/generate-schema` (LocalBusiness)
- `POST /api/geo/generate-product-schema`
- `POST /api/geo/generate-article-schema`
- `POST /api/geo/generate-breadcrumb-schema`
- `POST /api/geo/generate-organization-schema`
- `POST /api/geo/generate-website-schema`
- `POST /api/geo/generate-jobposting-schema`
- `POST /api/geo/generate-event-schema`
- `POST /api/geo/generate-howto-schema`
- `POST /api/geo/generate-video-schema`
- `POST /api/geo/generate-review-schema`
- `POST /api/geo/validate-schema`

### (Xem CODEX_CONTEXT.md hoặc Spec cho danh sách đầy đủ 55+ endpoints)

## 7. Coding Rules (BẮT BUỘC)

- **UI text: Tiếng Việt** | Code comments: English
- **NO Tailwind** — vanilla CSS only, follow `index.css`
- **NO axios** — use `fetch()` frontend, `httpx` backend
- **NO mock data** — real data or error states
- **Lazy imports** in routers for fast startup
- **CPU-heavy** → `asyncio.to_thread()`
- **New feature pattern:** `core/` module → `routers/` endpoint → `components/` UI → `App.tsx` route
- **Groq** = primary AI (not Gemini)
- **Dark glassmorphism** UI — purple #8b5cf6, cyan #06b6d4

## 8. Development Progress

| Section | Progress |
|---------|----------|
| Core SEO Engine | 90% |
| SEO Tools (CWV, Links, Schema) | 95% |
| Content AI Engine | 85% |
| Data Connectors | 75% |
| Rank Tracking | 90% |
| File Processing | 90% |
| Publishing & Export | 85% |
| Frontend UI/UX | 90% |
| SEO Infrastructure | 95% |
| DevOps & Auth | **85%** |
| Database | **95%** |

## 9. TODO — High Priority

- [x] Auth system (login/signup/JWT/RBAC)
- [x] Docker containerization
- [x] OG image (1200×630px) for social sharing
- [x] GA4 real data (Service Account JSON)
- [x] Export PDF reports
- [x] Ranking chart (line graph)
- [x] AI full article writing (Groq LLaMA 3.3)
- [x] Update domain from placeholder `ai-marketing-hub.vn`
- [x] Core Web Vitals: PageSpeed API key
- [x] Database chuẩn hóa (6 databases + init script)
- [ ] PostgreSQL migration (optional for production)

## 10. Cách chạy local

```bash
# 1. Backend setup
cd backend
pip install -r requirements.txt
python init_database.py          # Khởi tạo 6 databases
uvicorn main:app --reload --port 8000

# 2. Frontend setup
cd frontend
npm install
npm run dev
# → http://localhost:5173

# 3. Build production
cd frontend
npm run build                    # → dist/

# 4. SEO Check
cd ai-marketing-hub
.\scripts\seo-check.ps1

# 5. Docker
docker-compose up --build        # Production
docker-compose -f docker-compose.dev.yml up  # Development
```

## 11. Env Variables

```env
# Frontend (.env.local)
VITE_API_BASE_URL=http://localhost:8000/api

# Backend (.env)
GROQ_API_KEY=...
GSC_CLIENT_ID=...
GSC_CLIENT_SECRET=...
GSC_REFRESH_TOKEN=...
GA4_PROPERTY_ID=...
DATAFORSEO_LOGIN=...
DATAFORSEO_PASSWORD=...
PAGESPEED_API_KEY=...    # cho Core Web Vitals
```
