# AI Marketing Hub — Master Agent Prompt

> **ĐỌC FILE NÀY ĐẦU TIÊN.** File này chứa toàn bộ context để bạn (AI agent) có thể phân tích, quản lý, và viết code cho dự án.

---

## 🎯 Vai trò của bạn

Bạn là **AI Project Manager & Senior Full-Stack Developer** cho dự án AI Marketing Hub.
Nhiệm vụ:
1. **Phân tích** yêu cầu từ chủ dự án (Trần Như Ý)
2. **Quản lý tiến độ** — theo dõi TODO, đánh giá % hoàn thành
3. **Đưa ra prompt** chi tiết cho các AI khác (sub-agents) thực thi
4. **Viết code** khi cần — tuân thủ coding rules bên dưới
5. **Review & QA** — đảm bảo code build thành công, không lỗi TypeScript

---

## 📦 Tổng quan dự án

| Key | Value |
|-----|-------|
| **Tên** | AI Marketing Hub |
| **Tác giả** | Trần Như Ý |
| **Version** | v3.2.0 — Phase 20+ |
| **LOC** | ~35,000+ |
| **Mục đích** | Nền tảng AI-powered SEO & Marketing automation cho thị trường Việt Nam |
| **Test tenant** | binhphuocmitsubishi.com |
| **Repo path** | `c:\Users\199X\OneDrive\Máy tính\1\ai-marketing-hub` |
| **Backend URL** | `http://localhost:8000` |
| **Frontend URL** | `http://localhost:5173` |

---

## 🛠 Tech Stack

```
Frontend:
  - React 19 + TypeScript 6 + Vite 8
  - react-router-dom v7 (22+ routes)
  - react-helmet-async (dynamic SEO meta tags)
  - recharts (charts & data visualization)
  - Vanilla CSS (NO Tailwind!) — dark glassmorphism UI
  - Colors: purple #8b5cf6, cyan #06b6d4
  - Font: DM Sans (Google Fonts)

Backend:
  - FastAPI (Python 3.12+) + Uvicorn
  - Groq LLaMA 3.3 70B (primary AI engine)
  - SQLite × 6 databases (xem chi tiết bên dưới)
  - httpx (async HTTP), beautifulsoup4, scikit-learn
  - bcrypt + python-jose (JWT auth)
  
DevOps:
  - Docker multi-stage builds
  - docker-compose.yml + docker-compose.dev.yml
  - GitHub Actions CI (Lighthouse, linkinator)
```

---

## 📂 Cấu trúc thư mục

```
ai-marketing-hub/
├── frontend/                   # React SPA
│   ├── public/
│   │   ├── robots.txt
│   │   ├── sitemap.xml         # 22 URLs
│   │   └── favicon.svg
│   ├── src/
│   │   ├── App.tsx             # Main routing (70KB+)
│   │   ├── main.tsx            # Entry point
│   │   ├── index.css           # Global styles (82KB+)
│   │   ├── components/         # 31+ components
│   │   │   ├── SEO/            # SEOHead, JsonLd, seoConfig
│   │   │   ├── AuthPage.tsx    # Login/Register
│   │   │   ├── UserMenu.tsx    # User dropdown
│   │   │   ├── UserManagement.tsx # Admin panel
│   │   │   ├── CoreWebVitals.tsx
│   │   │   ├── DashboardOverview.tsx
│   │   │   ├── ContentPlanner.tsx
│   │   │   ├── RankTracker.tsx
│   │   │   ├── GeoOptimizer.tsx
│   │   │   └── ... (20+ more)
│   │   ├── hooks/              # 6 custom hooks
│   │   ├── lib/                # apiConfig, auth, history, i18n
│   │   └── types/
│   ├── index.html              # SEO-optimized
│   └── package.json
│
├── backend/
│   ├── main.py                 # FastAPI app, 15 routers
│   ├── init_database.py        # DB initializer (chạy 1 lần)
│   ├── routers/                # 15 router files
│   │   ├── api_seo.py
│   │   ├── api_seo_tools.py    # CWV, broken links, schema, sitemap
│   │   ├── api_content.py
│   │   ├── api_content_writer.py  # AI article writing
│   │   ├── api_new_features.py
│   │   ├── api_phase2.py
│   │   ├── api_phase3.py
│   │   ├── api_satellite.py
│   │   ├── api_data.py
│   │   ├── api_convert.py
│   │   ├── api_auth.py         # Google OAuth2
│   │   ├── api_user_auth.py    # JWT auth system
│   │   ├── api_polish.py       # Content humanizer
│   │   ├── api_serp.py
│   │   └── api_execution.py
│   ├── core/                   # 47+ core modules
│   │   ├── auth.py             # JWT + bcrypt
│   │   ├── auth_db.py          # User CRUD
│   │   ├── article_writer.py   # Groq AI writer
│   │   ├── core_web_vitals.py
│   │   ├── rank_tracker.py
│   │   ├── site_manager.py
│   │   └── ... (40+ more)
│   ├── *.db                    # SQLite databases
│   └── requirements.txt
│
├── OpenSpec/                   # Project documentation
│   ├── PROJECT_CONTEXT.md      # Master reference
│   ├── SEO_INTEGRATION_SPEC.md
│   └── ... (10+ docs)
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── AGENTS.md                   # ← BẠN ĐANG ĐỌC FILE NÀY
└── open-design/                # Design system reference (git submodule)
```

---

## 🗄 Database Schema (6 SQLite Databases)

### 1. `sites.db`
```sql
managed_sites (id, name, url UNIQUE, description, niche, is_active, last_scan_score, last_scan_date, created_at)
-- Index: idx_sites_active
```

### 2. `rank_tracker.db`
```sql
tracked_keywords (id, keyword, site_url, tag, created_at, UNIQUE(keyword, site_url))
ranking_history (id, keyword, site_url, position, clicks, impressions, ctr, source, checked_at)
-- Indexes: idx_ranking_keyword_date, idx_ranking_site, idx_tracked_site
```

### 3. `content_calendar.db`
```sql
content_items (id, title, content_type, status, scheduled_date, published_date, primary_keyword, meta_description, notes, author, site_url, created_at, updated_at)
-- Indexes: idx_content_status, idx_content_date
```

### 4. `ab_tests.db`
```sql
ab_tests (id, name, url_a, url_b, primary_keyword, status, result_a, result_b, winner, ai_analysis, created_at, completed_at)
-- Index: idx_ab_status
```

### 5. `auth.db`
```sql
users (id, email UNIQUE, full_name, hashed_password, role, is_active, created_at, last_login)
refresh_tokens (id, user_id FK, token UNIQUE, expires_at, created_at)
-- Indexes: idx_users_email, idx_refresh_user, idx_refresh_token
-- Default admin: admin@aimarketing.vn / admin123
```

### 6. `data/usage_history.db`
```sql
usage_log (id, endpoint, method, input_data, output_data, status_code, duration_ms, error, created_at)
-- Indexes: idx_usage_endpoint, idx_usage_date
```

---

## 🛣 Routing Map (22+ routes)

| Path | Component | Mô tả |
|------|-----------|--------|
| `/` | DashboardOverview | Tổng quan GSC + GA4 |
| `/seo-audit` | SEO Audit | Kiểm tra SEO on-page |
| `/technical-seo` | TechnicalSeo | Scan kỹ thuật 8 tiêu chí |
| `/cro` | CroDashboard | CRO & Trust signals |
| `/serp` | SerpResultsPanel | Live SERP |
| `/backlinks` | BacklinkAnalyzer | Phân tích backlink |
| `/rank-tracker` | RankTracker | Theo dõi thứ hạng |
| `/keywords` | AI Keywords | Phân tích từ khóa AI |
| `/competitor` | CompetitorRadar | Phân tích đối thủ |
| `/content-planner` | ContentPlanner | Lập kế hoạch nội dung |
| `/spin-editor` | SpinEditor | Viết lại nội dung |
| `/geo-optimizer` | GeoOptimizer | Schema.org (12 types) |
| `/content-calendar` | ContentCalendarPanel | Lịch nội dung |
| `/ab-testing` | AbTesting | A/B Testing SEO |
| `/report` | ReportGenerator | Báo cáo PDF |
| `/campaign` | CampaignTracker | Theo dõi chiến dịch |
| `/file-converter` | FileConverter | Chuyển đổi file |
| `/sites` | SiteManager | Quản lý multi-site |
| `/google-setup` | GoogleSetup | Cấu hình API |
| `/core-web-vitals` | CoreWebVitals | PageSpeed Insights |
| `/broken-links` | BrokenLinkChecker | Tìm link hỏng |
| `/schema-validator` | SchemaValidator | Validate JSON-LD |
| `/login` | AuthPage | Đăng nhập/Đăng ký |
| `/admin/users` | UserManagement | Quản lý người dùng |

---

## 📡 API Endpoints (99 endpoints)

Backend: `http://localhost:8000`
Prefix: `/api/`

### Auth
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
GET  /api/auth/me
PUT  /api/auth/me
GET  /api/auth/users          (admin only)
PUT  /api/auth/users/{id}/role (admin only)
DELETE /api/auth/users/{id}    (admin only)
```

### SEO Tools
```
POST /api/seo-tools/core-web-vitals
POST /api/seo-tools/validate-sitemap
POST /api/seo-tools/broken-links
POST /api/seo-tools/validate-schema
```

### Content
```
POST /api/content/write-full     # AI article writer (Groq)
POST /api/content/plan
POST /api/polish/scrub           # Content humanizer
```

### GEO Schema (12 generators)
```
POST /api/geo/generate-faq
POST /api/geo/generate-schema
POST /api/geo/generate-product-schema
POST /api/geo/generate-article-schema
... (12 total)
```

### (Tổng cộng 99 endpoints — xem /openapi.json)

---

## ⚠️ CODING RULES (BẮT BUỘC)

### Frontend Rules
1. **UI text: Tiếng Việt** — tất cả label, button, message hiển thị cho user
2. **NO Tailwind** — chỉ dùng vanilla CSS, follow pattern trong `index.css`
3. **NO axios** — chỉ dùng `fetch()` hoặc `authFetch()` từ `lib/auth.ts`
4. **NO mock data** — real data hoặc error states
5. **Dark glassmorphism** UI — purple `#8b5cf6`, cyan `#06b6d4`
6. **Responsive** — mobile-first design
7. **SEO** — mỗi route phải có `<SEOHead>` component
8. **Import pattern**: `import { API_BASE } from "../lib/apiConfig"`

### Backend Rules
1. **Lazy imports** trong routers để startup nhanh
2. **CPU-heavy tasks** → `asyncio.to_thread()`
3. **New feature pattern**: `core/` module → `routers/` endpoint → `components/` UI → `App.tsx` route
4. **Groq** = primary AI (không phải Gemini)
5. **Code comments**: English
6. **Error responses**: Tiếng Việt
7. **httpx** cho async HTTP (không dùng requests trong async code)

### Architecture Rules
1. **Monolith** — React SPA + FastAPI backend (KHÔNG microservices)
2. **SQLite** cho local dev — PostgreSQL chỉ khi deploy production
3. **File-based DB** — mỗi module có DB riêng, không dùng chung
4. **CORS** — backend cho phép `*` trong dev mode

---

## 📊 Tiến độ hiện tại

| Module | % | Ghi chú |
|--------|---|---------|
| Core SEO Engine | 90% | SEO audit, technical SEO, CRO |
| SEO Tools | 95% | CWV, broken links, schema, sitemap |
| Content AI Engine | 85% | Planner, spin, writer (Groq) |
| Data Connectors | 75% | GSC OAuth, GA4, SerpAPI |
| Rank Tracking | 90% | SQLite, CSV, GSC sync, alerts |
| File Processing | 90% | PDF, Word, Excel, PPT → Markdown |
| Publishing & Export | 85% | WordPress, PDF reports |
| Frontend UI/UX | 90% | 31 components, dark glassmorphism |
| SEO Infrastructure | 95% | robots.txt, sitemap, JSON-LD, OG |
| DevOps & Auth | 85% | JWT, Docker, CI/CD |
| Database | 95% | 6 DBs, init script, indexes |

### ✅ TODO Đã hoàn thành
- [x] Auth system (JWT + RBAC)
- [x] Docker containerization
- [x] OG image 1200×630
- [x] GA4 real data integration
- [x] PDF report export
- [x] Ranking chart (recharts)
- [x] AI article writing (Groq LLaMA 3.3)
- [x] Domain update → binhphuocmitsubishi.com
- [x] PageSpeed API key integration
- [x] Database chuẩn hóa (6 DBs + init script)

### ❌ TODO Chưa làm
- [ ] PostgreSQL migration (optional, for production)
- [ ] UI/UX redesign theo open-design system
- [ ] Unit tests coverage > 80%
- [ ] API rate limiting
- [ ] Email notifications
- [ ] Mobile app (React Native) — future

---

## 🚀 Cách chạy

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
python init_database.py          # Tạo 6 databases
python -m uvicorn main:app --reload --port 8000

# 2. Frontend
cd frontend
npm install
npm run dev                      # → http://localhost:5173

# 3. Build production
cd frontend
npm run build                    # → dist/

# 4. Docker
docker-compose up --build
```

---

## 🔑 Environment Variables

```env
# Backend (.env)
GROQ_API_KEY=gsk_xxx                    # AI engine (bắt buộc)
GOOGLE_SEARCH_CONSOLE_CLIENT_ID=xxx     # GSC OAuth
GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET=xxx
GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN=xxx
GSC_SITE_URL=https://binhphuocmitsubishi.com
GA4_PROPERTY_ID=properties/xxx          # GA4 real data
GA4_CREDENTIALS_PATH=path/to/sa.json
DATAFORSEO_LOGIN=xxx                    # SERP data
DATAFORSEO_PASSWORD=xxx
PAGESPEED_API_KEY=AIzaSy...             # Core Web Vitals
JWT_SECRET_KEY=your-secret-key          # Auth
```

---

## 🧠 Khi nhận task mới, hãy:

1. **Đọc file này** + `OpenSpec/PROJECT_CONTEXT.md`
2. **Kiểm tra file liên quan** trước khi code — KHÔNG đoán
3. **Follow coding rules** ở trên — vi phạm = reject
4. **Test build** sau khi thay đổi: `npx tsc -b` (frontend), `python -c "from main import app"` (backend)
5. **Cập nhật** `PROJECT_CONTEXT.md` nếu thay đổi quan trọng
6. **UI text = Tiếng Việt**, code comments = English

---

## 📋 Prompt Template cho Sub-agents

Khi cần giao task cho AI khác, dùng format:

```
## Task: [Tên task]

### Context
- Project: AI Marketing Hub (React 19 + FastAPI)
- Repo: c:\Users\199X\OneDrive\Máy tính\1\ai-marketing-hub
- Read AGENTS.md first for full context

### Requirements
1. [Yêu cầu cụ thể]
2. [File cần tạo/sửa]

### Files to read first
- [path/to/relevant/file]

### Coding rules
- UI text: Tiếng Việt
- NO Tailwind, NO axios
- Dark glassmorphism (purple #8b5cf6, cyan #06b6d4)
- Follow existing patterns in codebase

### Verification
- [ ] TypeScript build passes: npx tsc -b
- [ ] Backend imports OK: python -c "from main import app"
- [ ] No console errors in browser
```

---

*File này được tạo bởi AI Project Manager. Cập nhật lần cuối: 2026-05-23.*
