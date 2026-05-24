# AI Marketing Hub — Báo cáo dự án

> **Nền tảng AI-powered SEO & Marketing Automation cho thị trường Việt Nam**

---

## 1. Thông tin chung

| Mục | Chi tiết |
|-----|---------|
| **Tên dự án** | AI Marketing Hub |
| **Tác giả** | Trần Như Ý |
| **Phiên bản** | v3.2.0 — Phase 20+ |
| **Tổng dòng code** | ~37,600+ dòng (LOC) |
| **Số file source** | 125 files (67 backend + 58 frontend) |
| **Ngôn ngữ** | TypeScript, Python, CSS |
| **Demo URL** | https://trannhuy.online |
| **Test tenant** | binhphuocmitsubishi.com |
| **Repository** | GitHub — ai-marketing-hub |

---

## 2. Mục tiêu dự án

AI Marketing Hub là một nền tảng **all-in-one** giúp doanh nghiệp Việt Nam tối ưu SEO và marketing trực tuyến bằng trí tuệ nhân tạo. Hệ thống cung cấp:

- **Phân tích SEO tự động** — đánh giá on-page, technical SEO, Core Web Vitals
- **AI Content Writer** — viết bài chuẩn SEO bằng Groq LLaMA 3.3 70B
- **Theo dõi thứ hạng** — rank tracker với biểu đồ lịch sử
- **Quản lý nội dung** — content calendar, planner, spin editor
- **Phân tích đối thủ** — competitor gap analysis
- **CRO & Trust Analysis** — đánh giá chuyển đổi và tín hiệu tin cậy
- **Multi-site Management** — quản lý nhiều website từ 1 dashboard

---

## 3. Công nghệ sử dụng (Tech Stack)

### 3.1 Frontend

| Công nghệ | Phiên bản | Vai trò |
|-----------|----------|---------|
| **React** | 19 | UI framework chính |
| **TypeScript** | 6 | Type safety |
| **Vite** | 8 | Build tool & dev server |
| **react-router-dom** | v7 | Client-side routing (22+ routes) |
| **react-helmet-async** | — | Dynamic SEO meta tags |
| **recharts** | — | Charts & data visualization |
| **Vanilla CSS** | — | Dark glassmorphism UI design |

**Thiết kế giao diện:**
- Font chính: **Inter** (Google Fonts)
- Màu chủ đạo: Green `#16a34a`, Accent `#059669`
- Phong cách: Clean, professional, responsive
- Micro-animations: hover lift, focus ring, gradient overlays

### 3.2 Backend

| Công nghệ | Phiên bản | Vai trò |
|-----------|----------|---------|
| **FastAPI** | — | REST API framework |
| **Python** | 3.12+ | Backend language |
| **Uvicorn** | — | ASGI server |
| **Groq** (LLaMA 3.3 70B) | — | AI engine chính |
| **SQLite** | — | Database (6 databases) |
| **httpx** | — | Async HTTP client |
| **beautifulsoup4** | — | Web scraping |
| **scikit-learn** | — | ML algorithms |
| **bcrypt + python-jose** | — | JWT authentication |

### 3.3 DevOps

| Công nghệ | Vai trò |
|-----------|---------|
| **Docker** | Multi-stage containerization |
| **docker-compose** | Service orchestration |
| **Nginx** | Reverse proxy & static files |
| **GitHub Actions** | CI/CD (Lighthouse, linkinator) |
| **VPS** | Production deployment |

---

## 4. Kiến trúc hệ thống

### 4.1 Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────┐
│                    Client (Browser)                  │
│                  https://trannhuy.online              │
└────────────────────────┬────────────────────────────┘
                         │ HTTPS
┌────────────────────────┴────────────────────────────┐
│                    Nginx Proxy                       │
│              (SSL termination, static files)         │
└────────┬───────────────────────────────┬────────────┘
         │ /api/*                        │ /*
┌────────┴────────────┐     ┌───────────┴────────────┐
│   FastAPI Backend    │     │   React SPA (Vite)     │
│   Port 8000          │     │   Static dist/          │
│   15 routers         │     │   22+ routes            │
│   50+ core modules   │     │   38 components         │
│   99 API endpoints   │     │   6 custom hooks        │
└────────┬────────────┘     └────────────────────────┘
         │
┌────────┴────────────────────────────────────────────┐
│                  Data Layer                          │
├──────────────┬──────────────┬───────────────────────┤
│  sites.db    │ rank.db      │ content.db            │
│  auth.db     │ ab_tests.db  │ usage_history.db      │
└──────────────┴──────────────┴───────────────────────┘
         │
┌────────┴────────────────────────────────────────────┐
│              External Services                       │
├──────────────┬──────────────┬───────────────────────┤
│  Groq AI     │ Google APIs  │ DataForSEO            │
│  (LLaMA 3.3) │ (GSC, GA4)  │ (SERP data)           │
│              │ (PageSpeed)  │                       │
└──────────────┴──────────────┴───────────────────────┘
```

### 4.2 Monolith Architecture

Dự án sử dụng kiến trúc **Monolith** (React SPA + FastAPI backend) — phù hợp cho:
- Giai đoạn phát triển nhanh
- Team nhỏ (1-2 developers)
- Deploy đơn giản trên VPS

---

## 5. Cấu trúc thư mục

```
ai-marketing-hub/
├── frontend/                   # React SPA
│   ├── public/                 # Static assets
│   │   ├── robots.txt
│   │   ├── sitemap.xml         # 22 URLs
│   │   └── favicon.svg
│   ├── src/
│   │   ├── App.tsx             # Main routing (~2,500 lines)
│   │   ├── main.tsx            # Entry point
│   │   ├── index.css           # Global styles (~3,000 lines)
│   │   ├── components/         # 38 component files
│   │   │   ├── SEO/            # SEOHead, JsonLd, seoConfig
│   │   │   ├── AuthPage.tsx    # Login/Register
│   │   │   ├── DashboardOverview.tsx  # Trang chủ
│   │   │   ├── GoogleSetup.tsx # Cấu hình API
│   │   │   └── ... (35+ more)
│   │   ├── hooks/              # 6 custom hooks
│   │   ├── lib/                # apiConfig, auth, history, i18n
│   │   └── types/              # TypeScript definitions
│   ├── index.html              # SEO-optimized
│   └── package.json
│
├── backend/
│   ├── main.py                 # FastAPI app (254 lines)
│   ├── init_database.py        # DB initializer (370 lines)
│   ├── routers/                # 15 router files (3,454 lines)
│   │   ├── api_seo.py          # SEO audit endpoints
│   │   ├── api_seo_tools.py    # CWV, broken links, schema
│   │   ├── api_content.py      # Content spin/polish
│   │   ├── api_content_writer.py  # AI article writing
│   │   ├── api_user_auth.py    # JWT auth system
│   │   ├── api_serp.py         # SERP analysis
│   │   └── ... (9 more)
│   ├── core/                   # 50 core modules (15,938 lines)
│   │   ├── auth.py             # JWT + bcrypt
│   │   ├── auth_db.py          # User CRUD
│   │   ├── article_writer.py   # Groq AI writer
│   │   ├── core_web_vitals.py  # PageSpeed API
│   │   ├── rank_tracker.py     # Ranking database
│   │   ├── content_scorer.py   # AI content scoring
│   │   ├── keyword_analyzer.py # AI keyword analysis
│   │   ├── technical_seo.py    # Tech SEO scanner
│   │   └── ... (42 more)
│   ├── *.db                    # 6 SQLite databases
│   └── requirements.txt
│
├── docker-compose.yml          # Production config
├── docker-compose.dev.yml      # Development config
├── .env.example                # Environment template
├── AGENTS.md                   # AI agent instructions
├── Makefile                    # Build shortcuts
└── PROJECT_REPORT.md           # ← File này
```

---

## 6. Cơ sở dữ liệu

Hệ thống sử dụng **6 SQLite databases** riêng biệt:

### 6.1 sites.db — Quản lý website
```sql
managed_sites (
  id INTEGER PRIMARY KEY,
  name TEXT,
  url TEXT UNIQUE,
  description TEXT,
  niche TEXT,
  is_active BOOLEAN,
  last_scan_score REAL,
  last_scan_date TEXT,
  created_at TEXT
)
```

### 6.2 rank_tracker.db — Theo dõi thứ hạng
```sql
tracked_keywords (
  id INTEGER PRIMARY KEY,
  keyword TEXT,
  site_url TEXT,
  tag TEXT,
  created_at TEXT,
  UNIQUE(keyword, site_url)
)

ranking_history (
  id INTEGER PRIMARY KEY,
  keyword TEXT,
  site_url TEXT,
  position INTEGER,
  clicks INTEGER,
  impressions INTEGER,
  ctr REAL,
  source TEXT,
  checked_at TEXT
)
```

### 6.3 content_calendar.db — Lịch nội dung
```sql
content_items (
  id INTEGER PRIMARY KEY,
  title TEXT,
  content_type TEXT,
  status TEXT,              -- draft, scheduled, published
  scheduled_date TEXT,
  published_date TEXT,
  primary_keyword TEXT,
  meta_description TEXT,
  notes TEXT,
  author TEXT,
  site_url TEXT,
  created_at TEXT,
  updated_at TEXT
)
```

### 6.4 ab_tests.db — A/B Testing
```sql
ab_tests (
  id INTEGER PRIMARY KEY,
  name TEXT,
  url_a TEXT,
  url_b TEXT,
  primary_keyword TEXT,
  status TEXT,
  result_a TEXT,
  result_b TEXT,
  winner TEXT,
  ai_analysis TEXT,
  created_at TEXT,
  completed_at TEXT
)
```

### 6.5 auth.db — Xác thực người dùng
```sql
users (
  id INTEGER PRIMARY KEY,
  email TEXT UNIQUE,
  full_name TEXT,
  hashed_password TEXT,
  role TEXT,                -- admin, editor, viewer
  is_active BOOLEAN,
  created_at TEXT,
  last_login TEXT
)

refresh_tokens (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  token TEXT UNIQUE,
  expires_at TEXT,
  created_at TEXT
)
```

### 6.6 usage_history.db — Lịch sử sử dụng
```sql
usage_log (
  id INTEGER PRIMARY KEY,
  endpoint TEXT,
  method TEXT,
  input_data TEXT,
  output_data TEXT,
  status_code INTEGER,
  duration_ms REAL,
  error TEXT,
  created_at TEXT
)
```

---

## 7. API Endpoints (99 endpoints)

### 7.1 Xác thực (Auth) — 9 endpoints
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | `/api/auth/register` | Đăng ký tài khoản mới |
| POST | `/api/auth/login` | Đăng nhập → JWT token |
| POST | `/api/auth/refresh` | Làm mới access token |
| POST | `/api/auth/logout` | Đăng xuất |
| GET | `/api/auth/me` | Thông tin user hiện tại |
| PUT | `/api/auth/me` | Cập nhật profile |
| GET | `/api/auth/users` | Danh sách users (admin) |
| PUT | `/api/auth/users/{id}/role` | Đổi role (admin) |
| DELETE | `/api/auth/users/{id}` | Vô hiệu hóa user (admin) |

### 7.2 SEO Tools — 4 endpoints
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | `/api/seo-tools/core-web-vitals` | Kiểm tra Core Web Vitals |
| POST | `/api/seo-tools/validate-sitemap` | Validate sitemap XML |
| POST | `/api/seo-tools/broken-links` | Tìm link hỏng |
| POST | `/api/seo-tools/validate-schema` | Validate JSON-LD schema |

### 7.3 SEO Analysis — 4 endpoints
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | `/api/audit-seo` | Phân tích SEO on-page |
| POST | `/api/audit-url` | Audit URL nhanh |
| POST | `/api/tech-seo/scan` | Scan kỹ thuật 8 tiêu chí |
| POST | `/api/ai-keywords` | Phân tích từ khóa AI |

### 7.4 Content AI — 6 endpoints
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | `/api/content/write-full` | Viết bài AI (Groq LLaMA) |
| POST | `/api/content/spin` | Spin nội dung |
| POST | `/api/content/spin-multi` | Spin nhiều phiên bản |
| POST | `/api/content/spin-paragraphs` | Spin từng đoạn |
| POST | `/api/content/polish` | Humanize nội dung |
| POST | `/api/plan-content` | Lập kế hoạch nội dung |

### 7.5 GEO Schema — 12 endpoints
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | `/api/geo/generate-faq` | FAQ Schema |
| POST | `/api/geo/generate-schema` | LocalBusiness Schema |
| POST | `/api/geo/generate-product-schema` | Product Schema |
| POST | `/api/geo/generate-article-schema` | Article Schema |
| POST | `/api/geo/generate-review-schema` | Review Schema |
| POST | `/api/geo/generate-event-schema` | Event Schema |
| POST | `/api/geo/generate-howto-schema` | HowTo Schema |
| POST | `/api/geo/generate-video-schema` | Video Schema |
| POST | `/api/geo/generate-breadcrumb-schema` | Breadcrumb Schema |
| POST | `/api/geo/generate-organization-schema` | Organization Schema |
| POST | `/api/geo/generate-jobposting-schema` | JobPosting Schema |
| POST | `/api/geo/generate-website-schema` | WebSite Schema |

### 7.6 Rank Tracker — 10 endpoints
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/api/rank-tracker/keywords` | Danh sách keywords |
| GET | `/api/rank-tracker/history` | Lịch sử thứ hạng |
| POST | `/api/rank-tracker/add` | Thêm keyword |
| DELETE | `/api/rank-tracker/remove` | Xóa keyword |
| POST | `/api/rank-tracker/sync` | Đồng bộ GSC |
| GET | `/api/rank-tracker/alerts` | Cảnh báo biến động |
| GET | `/api/rank-tracker/tags` | Danh sách tags |
| PUT | `/api/rank-tracker/update-tag` | Cập nhật tag |
| GET | `/api/rank-tracker/export-csv` | Xuất CSV |
| GET | `/api/rank-tracker/export-excel` | Xuất Excel |

### 7.7 Calendar — 5 endpoints
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/api/calendar/items` | Danh sách content items |
| POST | `/api/calendar/add` | Thêm content item |
| PUT | `/api/calendar/update` | Cập nhật content item |
| DELETE | `/api/calendar/delete` | Xóa content item |
| GET | `/api/calendar/stats` | Thống kê calendar |

### 7.8 Các endpoint khác
- **SERP Analysis**: 3 endpoints — live search, single analyze, deep analyze
- **Backlink Analysis**: 1 endpoint
- **Competitor Gap**: 1 endpoint
- **A/B Testing**: 4 endpoints — create, list, evaluate, delete
- **Report**: 2 endpoints — generate, export PDF
- **Convert**: 4 endpoints — file, URL, SEO, formats
- **Satellite Sites**: 6 endpoints — CRUD + spin & post
- **Data Sync**: 4 endpoints — GSC, SERP, bulk, status
- **Google OAuth**: 3 endpoints — setup, callback, status
- **Config**: 2 endpoints — GET/POST server config

---

## 8. Giao diện người dùng (22+ Routes)

| # | Đường dẫn | Component | Mô tả |
|---|----------|-----------|--------|
| 1 | `/` | DashboardOverview | Trang tổng quan GSC + GA4 |
| 2 | `/seo-audit` | SEO Audit | Kiểm tra SEO on-page |
| 3 | `/technical-seo` | TechnicalSeo | Scan kỹ thuật 8 tiêu chí |
| 4 | `/cro` | CroDashboard | CRO & Trust signals |
| 5 | `/serp` | SerpResultsPanel | Live SERP analysis |
| 6 | `/backlinks` | BacklinkAnalyzer | Phân tích backlink |
| 7 | `/rank-tracker` | RankTracker | Theo dõi thứ hạng |
| 8 | `/keywords` | AI Keywords | Phân tích từ khóa AI |
| 9 | `/competitor` | CompetitorRadar | Phân tích đối thủ |
| 10 | `/content-planner` | ContentPlanner | Lập kế hoạch nội dung |
| 11 | `/spin-editor` | SpinEditor | Viết lại nội dung |
| 12 | `/geo-optimizer` | GeoOptimizer | Schema.org (12 types) |
| 13 | `/content-calendar` | ContentCalendar | Lịch nội dung |
| 14 | `/ab-testing` | AbTesting | A/B Testing SEO |
| 15 | `/report` | ReportGenerator | Báo cáo PDF |
| 16 | `/campaign` | CampaignTracker | Theo dõi chiến dịch |
| 17 | `/file-converter` | FileConverter | Chuyển đổi file |
| 18 | `/sites` | SiteManager | Quản lý multi-site |
| 19 | `/google-setup` | GoogleSetup | Cấu hình API keys |
| 20 | `/core-web-vitals` | CoreWebVitals | PageSpeed Insights |
| 21 | `/broken-links` | BrokenLinkChecker | Tìm link hỏng |
| 22 | `/schema-validator` | SchemaValidator | Validate JSON-LD |
| 23 | `/login` | AuthPage | Đăng nhập/Đăng ký |
| 24 | `/admin/users` | UserManagement | Quản lý người dùng |

---

## 9. Tính năng chi tiết

### 9.1 AI Engine (Groq LLaMA 3.3 70B)
- **Viết bài SEO tự động** — nhập keyword, AI tạo bài hoàn chỉnh với heading, meta description
- **Spin nội dung** — viết lại bài giữ nguyên ý nghĩa, tránh duplicate content
- **Humanize** — biến nội dung AI thành văn phong tự nhiên
- **Phân tích từ khóa** — gợi ý long-tail keywords, search intent
- **Phân tích đối thủ** — so sánh content gap với competitor

### 9.2 SEO Audit Engine
- **On-page SEO**: Title, Meta, H1-H6, Images alt, Internal links
- **Technical SEO**: 8 tiêu chí scan (robots.txt, sitemap, HTTPS, speed...)
- **Core Web Vitals**: LCP, FID, CLS qua Google PageSpeed API
- **Schema Validation**: Kiểm tra JSON-LD markup
- **Broken Link Checker**: Tìm và báo cáo link hỏng

### 9.3 Content Management
- **Content Calendar**: Lập lịch xuất bản, theo dõi trạng thái
- **Content Planner**: AI gợi ý topic dựa trên keyword cluster
- **Spin Editor**: Nhiều phiên bản nội dung từ 1 bài gốc
- **File Converter**: Chuyển đổi PDF, Word, Excel, PPT → Markdown

### 9.4 Rank Tracking
- **Theo dõi keyword**: Thêm/xóa keywords, gắn tag
- **Lịch sử thứ hạng**: Biểu đồ recharts theo thời gian
- **Đồng bộ GSC**: Lấy data từ Google Search Console
- **Export**: CSV và Excel
- **Cảnh báo**: Alert khi thứ hạng thay đổi đáng kể

### 9.5 CRO & Trust Analysis
- **Conversion Rate Optimization**: Đánh giá yếu tố chuyển đổi
- **Trust Signals**: SSL, testimonials, contact info, privacy policy
- **Above-the-fold Analysis**: Đánh giá nội dung hiển thị đầu tiên
- **CTA Analysis**: Phân tích call-to-action effectiveness

### 9.6 Multi-site Management
- Quản lý nhiều website từ 1 dashboard
- Chuyển đổi site nhanh
- Scan SEO riêng cho từng site

---

## 10. Bảo mật

| Tính năng | Chi tiết |
|-----------|---------|
| **Authentication** | JWT (JSON Web Token) |
| **Password** | bcrypt hash |
| **Role-based Access** | admin, editor, viewer |
| **Token Refresh** | Refresh token với expiry |
| **API Key Protection** | Masked display, .env storage |
| **CORS** | Configurable origins |
| **Input Validation** | Pydantic models |

---

## 11. Deployment

### 11.1 Docker Architecture

```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports: ["80:80"]
    # Nginx serves static React build
    
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./backend/.env:/app/.env
      - db-data:/app/data
    environment:
      - GROQ_API_KEY
      - JWT_SECRET_KEY
```

### 11.2 Production Setup
- **VPS**: Ubuntu Linux
- **Reverse Proxy**: Nginx (SSL via Let's Encrypt)
- **Domain**: trannhuy.online
- **Container Runtime**: Docker + docker-compose

---

## 12. Thống kê mã nguồn

### 12.1 Lines of Code

| Module | Files | Lines | Ghi chú |
|--------|-------|-------|---------|
| **Backend — core/** | 50 | 15,938 | Core business logic |
| **Backend — routers/** | 15 | 3,454 | API endpoints |
| **Backend — main.py** | 1 | 254 | App initialization |
| **Backend — init_database.py** | 1 | 370 | DB setup |
| **Frontend — components/** | 38 | ~12,000 | React components |
| **Frontend — App.tsx** | 1 | ~2,500 | Main routing |
| **Frontend — index.css** | 1 | ~3,000 | Design system |
| **Frontend — hooks/lib/types** | 19 | ~2,100 | Utilities |
| **Tổng cộng** | **~125** | **~37,600+** | |

### 12.2 Component Count

| Loại | Số lượng |
|------|---------|
| React Components | 38 |
| Custom Hooks | 6 |
| API Routers | 15 |
| Core Modules | 50 |
| API Endpoints | 99 |
| Database Tables | 8 |
| UI Routes | 22+ |

---

## 13. Tiến độ phát triển

| Module | Hoàn thành | Ghi chú |
|--------|-----------|---------|
| Core SEO Engine | 90% | SEO audit, technical SEO, CRO |
| SEO Tools | 95% | CWV, broken links, schema, sitemap |
| Content AI Engine | 85% | Planner, spin, writer (Groq) |
| Data Connectors | 75% | GSC OAuth, GA4, SerpAPI |
| Rank Tracking | 90% | SQLite, CSV, GSC sync, alerts |
| File Processing | 90% | PDF, Word, Excel, PPT → Markdown |
| Publishing & Export | 85% | WordPress, PDF reports |
| Frontend UI/UX | 95% | 38 components, redesigned UI |
| SEO Infrastructure | 95% | robots.txt, sitemap, JSON-LD, OG |
| DevOps & Auth | 85% | JWT, Docker, CI/CD |
| Database | 95% | 6 DBs, init script, indexes |

---

## 14. Kết quả kiểm thử API

Đã kiểm tra **26 endpoints** chính trên production server:

| Nhóm | Kết quả |
|------|---------|
| Health & Config | ✅ 4/4 |
| Sites | ✅ 2/2 |
| Rank Tracker | ✅ 3/3 |
| Calendar | ✅ 2/2 |
| A/B Test & Convert | ✅ 2/2 |
| Satellite | ✅ 2/2 |
| Google Auth | ✅ 1/1 |
| SEO Tools (POST) | ✅ 4/4 |
| Auth (cần token) | ✅ Đúng thiết kế |

**Kết quả: 100% endpoints hoạt động ổn định.**

---

## 15. Environment Variables

```env
# AI Engine
GROQ_API_KEY=gsk_xxx

# Google APIs
GOOGLE_SEARCH_CONSOLE_CLIENT_ID=xxx
GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET=xxx
GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN=xxx
GSC_SITE_URL=https://binhphuocmitsubishi.com
GA4_PROPERTY_ID=properties/xxx
GA4_CREDENTIALS_PATH=path/to/service-account.json

# SERP Data
DATAFORSEO_LOGIN=xxx
DATAFORSEO_PASSWORD=xxx

# Core Web Vitals
PAGESPEED_API_KEY=AIzaSy...

# Authentication
JWT_SECRET_KEY=your-secret-key
```

---

## 16. Hướng phát triển tương lai

- [ ] PostgreSQL migration cho production scale
- [ ] Unit tests coverage > 80%
- [ ] API rate limiting
- [ ] Email notifications
- [ ] PWA (Progressive Web App)
- [ ] Mobile app (React Native)
- [ ] AI model selector (chọn LLaMA / Gemini / GPT)
- [ ] Real-time collaboration
- [ ] Webhook integrations

---

## 17. Cách chạy dự án

### Development
```bash
# 1. Backend
cd backend
pip install -r requirements.txt
python init_database.py
python -m uvicorn main:app --reload --port 8000

# 2. Frontend
cd frontend
npm install
npm run dev  # → http://localhost:5173
```

### Production (Docker)
```bash
docker-compose up --build
# Frontend: http://localhost
# Backend: http://localhost:8000
```

### Build
```bash
cd frontend
npm run build  # → dist/
```

---

*Báo cáo được tạo tự động bởi AI Marketing Hub Project Manager.*  
*Phiên bản: v3.2.0 — Cập nhật: 25/05/2026*
