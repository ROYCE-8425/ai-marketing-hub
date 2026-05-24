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

## 9. Mô tả nghiệp vụ chi tiết từng chức năng

### 9.1 Trang tổng quan — Dashboard (`/`)

**Mục đích:** Cung cấp cái nhìn tổng quan về hiệu suất SEO và marketing của website đang quản lý.

**Luồng nghiệp vụ:**
1. Khi người dùng truy cập, hệ thống tự động lấy dữ liệu từ Google Search Console (GSC) và Google Analytics 4 (GA4)
2. Hiển thị các chỉ số chính: tổng clicks, impressions, CTR trung bình, vị trí trung bình
3. Biểu đồ xu hướng 28 ngày gần nhất (recharts line chart)
4. Top 10 keywords có hiệu suất cao nhất
5. Top pages được truy cập nhiều nhất
6. Quick actions: chuyển nhanh đến các công cụ SEO

**Dữ liệu đầu vào:** GSC API, GA4 API (real-time)  
**Dữ liệu đầu ra:** Dashboard cards, biểu đồ, bảng rankings  
**Giá trị nghiệp vụ:** Giúp chủ website nắm nhanh tình hình SEO mà không cần truy cập từng công cụ Google riêng lẻ

---

### 9.2 Kiểm tra SEO On-page — SEO Audit (`/seo-audit`)

**Mục đích:** Phân tích toàn diện chất lượng SEO on-page của một URL cụ thể.

**Luồng nghiệp vụ:**
1. Người dùng nhập URL cần kiểm tra và từ khóa mục tiêu
2. Backend crawl URL, parse HTML bằng BeautifulSoup
3. AI (Groq LLaMA) phân tích nội dung và chấm điểm theo 10+ tiêu chí:
   - **Title tag**: Độ dài (50-60 ký tự), có chứa keyword không
   - **Meta description**: Độ dài (150-160 ký tự), tính hấp dẫn
   - **Heading structure**: H1 duy nhất, hierarchy H2-H6
   - **Keyword density**: Mật độ từ khóa trong content (1-3%)
   - **Image optimization**: Alt text, kích thước file
   - **Internal/External links**: Số lượng và chất lượng
   - **Content length**: So sánh với top 10 SERP
   - **Readability**: Đánh giá độ dễ đọc
4. Trả về điểm tổng (0-100), danh sách lỗi critical/warning/suggestion
5. Gợi ý cải thiện cụ thể bằng AI

**Dữ liệu đầu vào:** URL + keyword  
**Dữ liệu đầu ra:** SEO score (0-100), chi tiết từng tiêu chí, gợi ý cải thiện  
**Giá trị nghiệp vụ:** Thay thế việc kiểm tra thủ công, tiết kiệm 2-3 giờ/trang so với làm tay

---

### 9.3 Technical SEO Scanner (`/technical-seo`)

**Mục đích:** Scan toàn bộ các yếu tố kỹ thuật ảnh hưởng đến SEO của website.

**Luồng nghiệp vụ:**
1. Nhập domain cần scan
2. Hệ thống kiểm tra 8 tiêu chí kỹ thuật:
   - **robots.txt**: Tồn tại, cấu hình đúng, không block Googlebot
   - **sitemap.xml**: Tồn tại, valid XML, số lượng URLs
   - **HTTPS**: Certificate hợp lệ, redirect HTTP → HTTPS
   - **Page Speed**: Thời gian tải trang
   - **Mobile-friendly**: Viewport meta, responsive design
   - **Canonical tags**: Tránh duplicate content
   - **Structured Data**: JSON-LD markup
   - **Hreflang**: Đa ngôn ngữ (nếu có)
3. Mỗi tiêu chí có trạng thái: Pass ✅ / Fail ❌ / Warning ⚠️
4. Tổng hợp điểm kỹ thuật và danh sách khuyến nghị sửa

**Dữ liệu đầu vào:** Domain URL  
**Dữ liệu đầu ra:** 8 tiêu chí với trạng thái, điểm tổng, khuyến nghị  
**Giá trị nghiệp vụ:** Phát hiện lỗi kỹ thuật trước khi Google phạt, cải thiện crawlability

---

### 9.4 Core Web Vitals (`/core-web-vitals`)

**Mục đích:** Đo lường trải nghiệm người dùng theo 3 chỉ số chính của Google.

**Luồng nghiệp vụ:**
1. Nhập URL cần đo
2. Backend gọi Google PageSpeed Insights API
3. Hiển thị 3 chỉ số Core Web Vitals:
   - **LCP (Largest Contentful Paint)**: Thời gian load phần tử lớn nhất (tốt < 2.5s)
   - **FID (First Input Delay)**: Thời gian phản hồi tương tác đầu tiên (tốt < 100ms)
   - **CLS (Cumulative Layout Shift)**: Mức độ dịch chuyển layout (tốt < 0.1)
4. Đánh giá mỗi chỉ số: Good 🟢 / Needs Improvement 🟡 / Poor 🔴
5. Performance score tổng (0-100)
6. Danh sách cơ hội tối ưu (opportunities) với estimated savings

**Dữ liệu đầu vào:** URL  
**Dữ liệu đầu ra:** LCP, FID, CLS scores + performance score + opportunities  
**Giá trị nghiệp vụ:** CWV là ranking signal của Google từ 2021, ảnh hưởng trực tiếp đến thứ hạng

---

### 9.5 Broken Link Checker (`/broken-links`)

**Mục đích:** Phát hiện link hỏng (404, 500) trên website để sửa kịp thời.

**Luồng nghiệp vụ:**
1. Nhập URL trang cần kiểm tra
2. Backend crawl trang, trích xuất tất cả links (internal + external)
3. Kiểm tra từng link bằng HTTP HEAD request
4. Phân loại: Working ✅ / Broken ❌ / Redirect ↗️ / Timeout ⏱
5. Hiển thị bảng kết quả: URL, HTTP status, anchor text, vị trí trên trang
6. Tổng kết: số link OK, broken, redirect

**Dữ liệu đầu vào:** URL cần scan  
**Dữ liệu đầu ra:** Danh sách links với status code, phân loại  
**Giá trị nghiệp vụ:** Broken links ảnh hưởng đến UX và SEO, Google giảm ranking nếu có nhiều 404

---

### 9.6 Schema Validator (`/schema-validator`)

**Mục đích:** Kiểm tra và tạo JSON-LD structured data cho website.

**Luồng nghiệp vụ:**
1. Nhập URL hoặc paste JSON-LD code
2. Hệ thống parse và validate theo schema.org specification
3. Kiểm tra: cú pháp JSON, required fields, data types, nested objects
4. Hiển thị lỗi cụ thể: missing field, invalid value, deprecated property
5. Preview kết quả structured data như Google sẽ hiểu

**Dữ liệu đầu vào:** URL hoặc JSON-LD code  
**Dữ liệu đầu ra:** Validation results, lỗi chi tiết, preview  
**Giá trị nghiệp vụ:** Structured data giúp xuất hiện rich snippets trên Google (FAQ, rating stars, price...)

---

### 9.7 SERP Analysis (`/serp`)

**Mục đích:** Phân tích kết quả tìm kiếm Google real-time cho từ khóa.

**Luồng nghiệp vụ:**
1. Nhập từ khóa cần tra cứu, chọn quốc gia/ngôn ngữ
2. Backend gọi DataForSEO API hoặc scrape Google SERP
3. Hiển thị top 10-20 kết quả với:
   - Thứ hạng, title, URL, meta description
   - Domain authority (nếu có)
   - Features: featured snippet, people also ask, images, videos
4. AI phân tích:
   - Search intent (thông tin / giao dịch / điều hướng)
   - Content type pattern (blog / product / landing page)
   - Khó khăn cạnh tranh (competition level)

**Dữ liệu đầu vào:** Keyword + location  
**Dữ liệu đầu ra:** SERP results, search intent, competition analysis  
**Giá trị nghiệp vụ:** Hiểu đối thủ đang rank cho keyword, xác định content strategy phù hợp

---

### 9.8 Backlink Analyzer (`/backlinks`)

**Mục đích:** Phân tích hồ sơ backlink của website hoặc đối thủ.

**Luồng nghiệp vụ:**
1. Nhập domain cần phân tích
2. Backend truy vấn DataForSEO Backlinks API
3. Hiển thị:
   - Tổng số backlinks, referring domains
   - Top referring domains theo authority
   - Anchor text distribution
   - Dofollow vs Nofollow ratio
   - New vs Lost backlinks trend
4. So sánh với đối thủ (nếu nhập thêm domain)

**Dữ liệu đầu vào:** Domain URL  
**Dữ liệu đầu ra:** Backlink profile, referring domains, anchor text analysis  
**Giá trị nghiệp vụ:** Backlinks là top 3 ranking factors, cần theo dõi để xây dựng link building strategy

---

### 9.9 Rank Tracker (`/rank-tracker`)

**Mục đích:** Theo dõi thứ hạng từ khóa trên Google theo thời gian.

**Luồng nghiệp vụ:**
1. **Thêm keyword**: Nhập keyword + URL + tag phân nhóm → lưu vào `rank_tracker.db`
2. **Đồng bộ**: Sync dữ liệu từ Google Search Console API
3. **Biểu đồ**: Recharts line chart hiển thị biến động thứ hạng theo ngày/tuần/tháng
4. **Cảnh báo**: Tự động phát hiện keyword tụt > 5 vị trí → alert
5. **Phân nhóm**: Gắn tag (brand, product, long-tail...) để quản lý
6. **Export**: Xuất báo cáo CSV/Excel cho stakeholders

**Dữ liệu đầu vào:** Keywords, site URL, GSC API data  
**Dữ liệu đầu ra:** Biểu đồ ranking history, alerts, CSV/Excel reports  
**Database:** `rank_tracker.db` (tracked_keywords + ranking_history)  
**Giá trị nghiệp vụ:** Đo lường hiệu quả SEO campaign, phát hiện sớm vấn đề ranking

---

### 9.10 AI Keywords (`/keywords`)

**Mục đích:** Phân tích và gợi ý từ khóa SEO bằng AI.

**Luồng nghiệp vụ:**
1. Nhập seed keyword (ví dụ: "Mitsubishi Xpander")
2. AI (Groq LLaMA) phân tích và trả về:
   - **Related keywords**: Từ khóa liên quan
   - **Long-tail keywords**: Từ khóa đuôi dài (ít cạnh tranh)
   - **Question keywords**: Câu hỏi người dùng hay tìm
   - **Search intent**: Informational / Transactional / Navigational
   - **Keyword difficulty**: Ước lượng độ khó (Easy / Medium / Hard)
   - **Content suggestions**: Gợi ý loại nội dung phù hợp
3. Cho phép copy keyword list để dùng trong content planning

**Dữ liệu đầu vào:** Seed keyword  
**Dữ liệu đầu ra:** Keyword clusters, search intent, difficulty, suggestions  
**Giá trị nghiệp vụ:** Thay thế công cụ keyword research trả phí (Ahrefs, SEMrush), tiết kiệm $99-249/tháng

---

### 9.11 Competitor Radar (`/competitor`)

**Mục đích:** Phân tích và so sánh SEO giữa website mình và đối thủ.

**Luồng nghiệp vụ:**
1. Nhập URL mình + URL đối thủ + keyword chung
2. Hệ thống crawl cả 2 trang, AI so sánh:
   - Content length & quality
   - Keyword usage & density
   - Heading structure
   - Internal linking
   - Page speed
   - Backlink profile
3. Hiển thị bảng so sánh side-by-side
4. AI đưa ra action items: "Đối thủ hơn bạn ở X, cần cải thiện Y"

**Dữ liệu đầu vào:** URL mình + URL đối thủ + keyword  
**Dữ liệu đầu ra:** So sánh chi tiết, gap analysis, action items  
**Giá trị nghiệp vụ:** Biết đối thủ mạnh/yếu ở đâu để tập trung nguồn lực cạnh tranh

---

### 9.12 CRO Dashboard (`/cro`)

**Mục đích:** Đánh giá khả năng chuyển đổi (Conversion Rate Optimization) của trang web.

**Luồng nghiệp vụ:**
1. Nhập URL landing page cần đánh giá
2. Hệ thống phân tích 4 nhóm yếu tố:
   - **CTA (Call-to-Action)**: Số lượng, vị trí, màu sắc, text
   - **Trust Signals**: SSL, reviews, testimonials, contact info, chính sách
   - **Above-the-fold**: Headline, sub-headline, hero image, value proposition
   - **Engagement**: Form fields, navigation, loading speed
3. Chấm điểm từng nhóm (0-100)
4. Checklist CRO: Pass/Fail cho ~20 tiêu chí
5. Sales risk alerts: Cảnh báo yếu tố gây mất khách

**Dữ liệu đầu vào:** URL landing page  
**Dữ liệu đầu ra:** CRO score, checklist, trust signals, recommendations  
**Giá trị nghiệp vụ:** Tăng tỷ lệ chuyển đổi từ visitor → lead/customer

---

### 9.13 Content Planner (`/content-planner`)

**Mục đích:** AI lập kế hoạch nội dung SEO dựa trên keyword cluster.

**Luồng nghiệp vụ:**
1. Nhập chủ đề/keyword chính + niche
2. AI tạo content plan gồm:
   - **Pillar content**: Bài trụ cột (3,000+ từ)
   - **Cluster content**: Bài hỗ trợ (1,000-2,000 từ)
   - **Topic map**: Sơ đồ liên kết nội dung
   - **Publishing schedule**: Lịch xuất bản gợi ý
   - **Keyword mapping**: Mỗi bài target keyword nào
3. Cho phép chỉnh sửa plan và thêm vào Content Calendar
4. Tạo outline chi tiết cho từng bài (heading + bullet points)

**Dữ liệu đầu vào:** Topic + niche  
**Dữ liệu đầu ra:** Content plan, topic map, outlines, schedule  
**Giá trị nghiệp vụ:** Xây dựng topical authority, strategy nội dung 3-6 tháng

---

### 9.14 AI Content Writer (tích hợp trong Content Planner)

**Mục đích:** Viết bài SEO hoàn chỉnh bằng AI Groq LLaMA 3.3 70B.

**Luồng nghiệp vụ:**
1. Nhập keyword chính, từ khóa phụ, tone of voice, độ dài mong muốn
2. AI generate bài viết với:
   - Title tag tối ưu SEO
   - Meta description hấp dẫn
   - Heading structure (H1, H2, H3...)
   - Nội dung body chia đoạn rõ ràng
   - Internal link suggestions
   - FAQ section
3. Điểm SEO preview (0-100) trước khi publish
4. Cho phép chỉnh sửa, regenerate từng section
5. Export: Copy HTML, Markdown, hoặc đẩy thẳng lên WordPress

**Dữ liệu đầu vào:** Keyword, LSI keywords, tone, length  
**Dữ liệu đầu ra:** Full article (HTML/Markdown), SEO score, meta tags  
**Giá trị nghiệp vụ:** Viết 1 bài 2,000 từ trong 30 giây thay vì 3-4 giờ viết tay

---

### 9.15 Spin Editor (`/spin-editor`)

**Mục đích:** Viết lại nội dung giữ nguyên ý nghĩa, tránh duplicate content.

**Luồng nghiệp vụ:**
1. Paste nội dung gốc hoặc nhập URL nguồn
2. Chọn chế độ spin:
   - **Spin đơn**: 1 phiên bản mới
   - **Spin đa phiên bản**: 3-5 phiên bản khác nhau
   - **Spin từng đoạn**: Chọn đoạn cụ thể để viết lại
3. AI viết lại với:
   - Thay đổi cấu trúc câu
   - Sử dụng từ đồng nghĩa
   - Giữ nguyên thông tin và ý nghĩa chính
   - Đảm bảo tính tự nhiên (không giống máy)
4. So sánh bản gốc vs bản spin (diff view)
5. Kiểm tra % uniqueness

**Dữ liệu đầu vào:** Nội dung gốc hoặc URL  
**Dữ liệu đầu ra:** Nội dung đã spin, uniqueness score  
**Giá trị nghiệp vụ:** Tạo nội dung unique cho satellite sites, tránh Google penalty duplicate

---

### 9.16 Content Humanizer (Polish)

**Mục đích:** Biến nội dung AI thành văn phong tự nhiên, bypass AI detection tools.

**Luồng nghiệp vụ:**
1. Paste nội dung do AI viết
2. Hệ thống phân tích patterns AI: lặp cấu trúc, quá formal, thiếu variation
3. AI viết lại với:
   - Thêm conversational tone
   - Đa dạng cấu trúc câu (ngắn/dài xen kẽ)
   - Thêm ví dụ thực tế
   - Giảm formal language
4. So sánh before/after

**Dữ liệu đầu vào:** AI-generated content  
**Dữ liệu đầu ra:** Humanized content  
**Giá trị nghiệp vụ:** Google ngày càng phát hiện AI content, humanize giúp tránh penalize

---

### 9.17 GEO Optimizer — Schema Generator (`/geo-optimizer`)

**Mục đích:** Tạo structured data (JSON-LD) cho 12 loại schema.org phổ biến.

**Luồng nghiệp vụ:**
1. Chọn loại schema cần tạo (1 trong 12):
   - LocalBusiness, Product, Article, FAQ
   - Review, Event, HowTo, Video
   - Breadcrumb, Organization, JobPosting, WebSite
2. Điền form thông tin (tên, địa chỉ, giá, mô tả...)
3. Hệ thống generate JSON-LD code hợp lệ
4. Preview: Hiển thị như Google sẽ hiểu
5. Copy code → Paste vào `<head>` của website
6. Validate: Kiểm tra tự động trước khi copy

**Dữ liệu đầu vào:** Form fields tùy loại schema  
**Dữ liệu đầu ra:** JSON-LD code, preview, validation  
**Giá trị nghiệp vụ:** Rich snippets tăng CTR lên 20-30% trên SERP

---

### 9.18 Content Calendar (`/content-calendar`)

**Mục đích:** Quản lý lịch xuất bản nội dung cho team content.

**Luồng nghiệp vụ:**
1. **Tạo item**: Nhập tiêu đề, keyword, loại content, ngày dự kiến, tác giả
2. **Quản lý trạng thái**: Draft → Scheduled → Published
3. **Calendar view**: Hiển thị dạng lịch tháng
4. **Thống kê**: Số bài draft/scheduled/published, phân bố theo tuần
5. **AI suggest**: Gợi ý topic mới dựa trên keyword gaps
6. **CRUD**: Thêm, sửa, xóa, lọc theo trạng thái/tác giả

**Dữ liệu đầu vào:** Content item metadata  
**Dữ liệu đầu ra:** Calendar view, statistics, AI suggestions  
**Database:** `content_calendar.db`  
**Giá trị nghiệp vụ:** Đảm bảo content team publish đều đặn, tránh gaps trong content strategy

---

### 9.19 A/B Testing SEO (`/ab-testing`)

**Mục đích:** So sánh hiệu quả SEO giữa 2 phiên bản trang.

**Luồng nghiệp vụ:**
1. **Tạo test**: Nhập tên test, URL A, URL B, keyword target
2. **Thu thập**: Hệ thống phân tích cả 2 URL — SEO score, content quality, speed
3. **Đánh giá**: AI so sánh và chọn winner dựa trên:
   - SEO score comparison
   - Content relevance
   - Technical performance
   - User experience signals
4. **AI Analysis**: Giải thích tại sao version này tốt hơn
5. **Lịch sử**: Lưu kết quả tests đã chạy

**Dữ liệu đầu vào:** 2 URLs + keyword  
**Dữ liệu đầu ra:** Winner, comparison scores, AI analysis  
**Database:** `ab_tests.db`  
**Giá trị nghiệp vụ:** Data-driven SEO decisions thay vì đoán mò

---

### 9.20 Report Generator (`/report`)

**Mục đích:** Tạo báo cáo SEO chuyên nghiệp dạng PDF.

**Luồng nghiệp vụ:**
1. Chọn website và khoảng thời gian
2. Hệ thống tổng hợp dữ liệu từ:
   - GSC: traffic, impressions, clicks
   - Rank tracker: thay đổi thứ hạng
   - SEO audit: điểm hiện tại
   - Content calendar: bài đã publish
3. Generate PDF với:
   - Executive summary
   - Traffic overview (biểu đồ)
   - Keyword rankings (bảng)
   - SEO improvements made
   - Action items for next period
4. Export PDF để gửi cho khách hàng/quản lý

**Dữ liệu đầu vào:** Site + date range  
**Dữ liệu đầu ra:** PDF report  
**Giá trị nghiệp vụ:** Báo cáo chuyên nghiệp cho agency gửi khách hàng, tiết kiệm 2-3 giờ/report

---

### 9.21 Campaign Tracker (`/campaign`)

**Mục đích:** Theo dõi hiệu quả chiến dịch marketing tổng hợp.

**Luồng nghiệp vụ:**
1. Tạo campaign: tên, mục tiêu, kênh (SEO, Ads, Social...)
2. Liên kết với keywords đang theo dõi
3. Dashboard campaign:
   - Tiến độ so với mục tiêu
   - ROI ước tính
   - Keyword performance trong campaign
   - Content đã xuất bản cho campaign
4. So sánh hiệu quả giữa các campaign

**Dữ liệu đầu vào:** Campaign metadata, linked keywords  
**Dữ liệu đầu ra:** Campaign dashboard, ROI metrics  
**Giá trị nghiệp vụ:** Đo lường ROI của SEO investment theo từng campaign

---

### 9.22 File Converter (`/file-converter`)

**Mục đích:** Chuyển đổi file office sang Markdown cho content team.

**Luồng nghiệp vụ:**
1. Upload file: PDF, Word (.docx), Excel (.xlsx), PowerPoint (.pptx)
2. Backend parse file bằng python-docx, openpyxl, python-pptx
3. Convert sang Markdown với formatting giữ nguyên:
   - Headings, bold, italic
   - Tables (Excel → Markdown table)
   - Lists, images (base64 embed)
4. SEO mode: Convert + AI tối ưu SEO (thêm headings, meta...)
5. URL mode: Nhập URL → scrape → convert to Markdown

**Dữ liệu đầu vào:** File upload hoặc URL  
**Dữ liệu đầu ra:** Markdown content  
**Giá trị nghiệp vụ:** Content team viết trên Word/Google Docs, cần convert để publish lên CMS

---

### 9.23 Site Manager (`/sites`)

**Mục đích:** Quản lý nhiều website trong 1 hệ thống.

**Luồng nghiệp vụ:**
1. **Thêm site**: Nhập URL, tên, mô tả, niche
2. **Chọn site active**: Tất cả tools sẽ sử dụng site đang active
3. **Dashboard site**: Last scan score, scan date
4. **CRUD**: Thêm, sửa, xóa, bật/tắt site

**Dữ liệu đầu vào:** Site metadata  
**Dữ liệu đầu ra:** Sites list, active site  
**Database:** `sites.db`  
**Giá trị nghiệp vụ:** Agency quản lý nhiều khách hàng, mỗi khách 1 site

---

### 9.24 Google Setup (`/google-setup`)

**Mục đích:** Cấu hình API keys và kết nối dịch vụ bên ngoài.

**Luồng nghiệp vụ:**
1. Hiển thị trạng thái từng API key: "Đã cấu hình" ✅ / "Chưa cấu hình" ⚠️
2. 4 nhóm cấu hình:
   - **AI Engine**: Groq API Key
   - **Google APIs**: GSC Client ID/Secret, GA4 credentials, PageSpeed API Key
   - **SERP & Backlinks**: DataForSEO Login/Password
   - **Bảo mật**: JWT Secret Key
3. Cho phép thêm/sửa key trực tiếp → Lưu vào `.env` trên backend
4. Thanh tiến trình: "8/10 API keys đã cấu hình"
5. Keys hiển thị dạng masked (gsk_dH...o3Qj)

**Dữ liệu đầu vào:** API keys  
**Dữ liệu đầu ra:** Config status, masked keys  
**Giá trị nghiệp vụ:** Admin dễ dàng cấu hình mà không cần SSH vào server

---

### 9.25 Đăng nhập / Đăng ký (`/login`)

**Mục đích:** Xác thực người dùng và phân quyền truy cập.

**Luồng nghiệp vụ:**
1. **Đăng ký**: Email + họ tên + mật khẩu → hash bcrypt → lưu `auth.db`
2. **Đăng nhập**: Email + password → verify → JWT access token + refresh token
3. **Token management**: Access token (15 phút) + Refresh token (7 ngày)
4. **Auto refresh**: Frontend tự động refresh token khi gần hết hạn
5. **Roles**: admin (full access), editor (CRUD content), viewer (read-only)

**Dữ liệu đầu vào:** Email + password  
**Dữ liệu đầu ra:** JWT tokens, user profile  
**Database:** `auth.db`  
**Giá trị nghiệp vụ:** Bảo vệ hệ thống, phân quyền team

---

### 9.26 Quản lý người dùng (`/admin/users`)

**Mục đích:** Admin quản lý tài khoản người dùng trong hệ thống.

**Luồng nghiệp vụ:**
1. Danh sách tất cả users: email, tên, role, trạng thái, lần login cuối
2. **Đổi role**: Nâng/hạ quyền (admin ↔ editor ↔ viewer)
3. **Vô hiệu hóa**: Tạm khóa tài khoản (soft delete)
4. Chỉ admin mới truy cập được trang này

**Dữ liệu đầu vào:** User actions (role change, deactivate)  
**Dữ liệu đầu ra:** User list, status updates  
**Giá trị nghiệp vụ:** Quản lý team access, revoke quyền khi nhân sự nghỉ việc

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
