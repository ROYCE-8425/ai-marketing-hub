# 🧠 AI MARKETING HUB — CODEX / AI CONTEXT DOCUMENT

> **Mục đích:** File này giúp bất kỳ AI nào (Codex, Claude, Gemini, Cursor...) hiểu ngay lập tức dự án đang ở đâu, đang làm gì, và cần làm gì tiếp.
>
> **Cập nhật lần cuối:** 03/05/2026 | **Version:** 3.1.0 | **Phase:** 20

---

## 1. DỰ ÁN LÀ GÌ?

**AI Marketing Hub** là một nền tảng SEO/Marketing AI all-in-one, được xây dựng cho thị trường Việt Nam. Nó cho phép người dùng:
- Kiểm tra SEO on-page bất kỳ URL nào
- Phân tích keywords, đối thủ cạnh tranh
- Viết và spin content bằng AI (Groq LLaMA 3.3 70B)
- Theo dõi thứ hạng keyword trên Google
- Tối ưu GEO (Generative Engine Optimization) cho AI search
- Quản lý lịch nội dung, A/B testing SEO
- Xuất bản lên WordPress tự động
- Convert file (PDF/Word/Excel) sang Markdown qua MarkItDown
- Kết nối Google Search Console và GA4 cho data thật

**Khách hàng mục tiêu:** Owner website `binhphuocmitsubishi.com` — đại lý Mitsubishi Bình Phước.

---

## 2. KIẾN TRÚC KỸ THUẬT

```
ai_marketing_hub/
├── backend/                    # FastAPI (Python 3.12)
│   ├── main.py                 # Entry point, register 10 routers
│   ├── .env                    # API keys (Groq, GSC, GA4, Gemini, ZAI)
│   ├── core/                   # 37 business logic modules
│   │   ├── keyword_analyzer.py     # TF-IDF + KMeans clustering
│   │   ├── seo_quality_rater.py    # SEO scoring A-F
│   │   ├── technical_seo.py        # Sitemap, robots, meta, speed
│   │   ├── geo_analyzer.py         # GEO + Schema generators
│   │   ├── spin_editor.py          # AI content spinning (Groq)
│   │   ├── rank_tracker.py         # Keyword rank tracking (SQLite)
│   │   ├── google_search_console.py # GSC via httpx+OAuth2 (REAL)
│   │   ├── ga4_fetcher.py          # GA4 (mock — needs service account)
│   │   ├── file_converter.py       # MarkItDown integration
│   │   ├── content_scorer.py       # Multi-algorithm scoring
│   │   ├── cro_checker.py          # CRO analysis
│   │   ├── wordpress_publisher.py  # WP REST API publisher
│   │   └── ... (37 modules total)
│   ├── routers/                # 10 API routers
│   │   ├── api_seo.py              # SEO audit endpoints
│   │   ├── api_data.py             # GSC/GA4/DataForSEO sync
│   │   ├── api_new_features.py     # Rank tracker, Spin, GEO, Schema
│   │   ├── api_convert.py          # File converter + SEO pipeline
│   │   ├── api_serp.py             # Live SERP results
│   │   └── ... (10 routers total)
│   ├── venv/                   # Python virtual environment
│   ├── *.db                    # 4 SQLite databases
│   └── requirements.txt
├── frontend/                   # React + TypeScript (Vite)
│   ├── src/
│   │   ├── App.tsx             # Main app, sidebar nav, 20 tabs
│   │   ├── index.css           # Design system (2419 LOC)
│   │   ├── components/         # 19 page components
│   │   │   ├── DashboardOverview.tsx
│   │   │   ├── RankTracker.tsx
│   │   │   ├── SpinEditor.tsx
│   │   │   ├── FileConverter.tsx
│   │   │   └── ... (19 components)
│   │   ├── hooks/              # useSeoAudit, useOpportunities...
│   │   ├── lib/                # history, apiConfig
│   │   └── types/              # TypeScript types
│   └── package.json
├── .superpowers/               # obra/superpowers (agentic skills)
├── .skills/                    # mattpocock/skills
├── CLAUDE.md                   # AI coding context
├── MOCK_DATA_NOTE.md           # Mock vs real data tracking
├── PHAN_TICH_PHAT_TRIEN.md     # Development breakdown (8 parts, 52 tasks)
└── PHAN_TICH_CHUC_NANG.md      # Feature analysis
```

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | **FastAPI** (Python 3.12, uvicorn) |
| Frontend | **React 18 + TypeScript** (Vite 6) |
| AI Engine | **Groq** (LLaMA 3.3 70B Versatile) |
| Database | **SQLite** × 4 (rank_tracker, content_calendar, ab_tests, sites) |
| Styling | **Vanilla CSS** — dark glassmorphism theme |
| Charts | **Recharts** |
| File Processing | **MarkItDown** (Microsoft) |
| SEO Data | **Google Search Console** (OAuth2, real data) |
| Publishing | **WordPress REST API** |

### Design System
```css
--bg: #080b14         /* Deep dark background */
--surface: rgba(255,255,255,0.03)
--primary: #8b5cf6    /* Purple accent */
--accent: #06b6d4     /* Cyan accent */
--text-h: #f1f5f9     /* Heading text */
--text-m: #94a3b8     /* Muted text */
```
- Dark mode glassmorphism, gradient borders
- Sidebar: 240px, collapsible
- Max-width: 1100px

---

## 3. API KEYS — TRẠNG THÁI

| Key | Status | Ghi chú |
|-----|--------|---------|
| `GROQ_API_KEY` | ✅ **Hoạt động** | AI engine chính, dùng cho Spin/GEO/Report/A-B Test |
| `GSC_*` (3 keys) | ✅ **Real data** | OAuth2 refresh token mới (01/05/2026), site: binhphuocmitsubishi.com |
| `GA4_PROPERTY_ID` | 🟡 **Thiếu credentials** | Có Property ID nhưng thiếu Service Account JSON |
| `GEMINI_API_KEY` | 🟡 **Hết quota (429)** | User chọn dùng Groq thay thế |
| `ZAI_API_KEY` | ⚪ **Chưa dùng** | Có key nhưng chưa tích hợp |

---

## 4. DATA THẬT vs MOCK

### ✅ Real Data (22 modules)
Tất cả SEO analysis, AI features, databases, file converter, WordPress publisher, GSC.

### 🔴 Mock Data (còn lại)
| Module | File | Vấn đề | Cách fix |
|--------|------|--------|----------|
| GA4 | `ga4_fetcher.py` | Random mock numbers | Cần Service Account JSON |
| Data Router (GA4 part) | `api_data.py` | `_mock_ga4_data()` fallback | Khi GA4 credentials có |
| SERP Scraper | `google_serp_scraper.py` | `_mock_serp()` fallback | DuckDuckGo real hoạt động, mock chỉ khi fail |

**GSC đã fix xong — trả real data từ 01/05/2026.**

---

## 5. LỊCH SỬ PHÁT TRIỂN (Git Log)

| Phase | Commit | Nội dung |
|-------|--------|---------|
| 1-4 | a29caf1 | Live SERP, AI keyword analysis |
| 5-9 | afea68a → f33921d | Dashboard charts, GA4 integration, Việt hóa |
| 10-13 | 8dfc97f → 7972564 | Rank Tracker, Spin Editor, GEO Optimizer |
| 14-15 | 71e3a75 | Backlink Analyzer, Content Calendar |
| 16-17 | 84f4e87 | Technical SEO Scanner, AI Report Generator |
| 18-19 | 331ba64 | Multi-site Manager, A/B Testing |
| UI | 0541b28 → 5125ae6 | Premium Glassmorphism sidebar |
| 20 | 7f0fab0 | MarkItDown + Superpowers + Skills |
| 20+ | eff2796 | File Converter UI + Mock Data Inventory |
| 20++ | a8130b4 | Technical SEO enhanced, Schema generators, GSC rewrite |

---

## 6. CHỨC NĂNG HIỆN TẠI (20 modules)

### SEO Analysis
1. **Kiểm tra SEO** — Audit on-page (keyword density, quality A-F, LSI)
2. **Technical SEO** — Meta tags, headings, images, links, sitemap, robots.txt
3. **CRO & Uy tín** — CRO checklist, CTA analysis, trust signals, above-fold
4. **Backlinks** — Internal/external link extraction, anchor text

### Keywords
5. **Theo dõi Keyword** — SQLite, tags, history, CSV import/export, alerts
6. **AI Keyword Analysis** — Groq AI + TF-IDF clustering
7. **Phân tích đối thủ** — Competitor gap analysis, content gap

### Content
8. **Viết nội dung AI** — Auto outline, section planning, meta tags
9. **Spin Editor** — Single/multi spin, 4 tones, preserve keywords
10. **Tối ưu GEO** — GEO score, E-E-A-T, AI visibility, Schema (FAQ/Local/Product/Article/Breadcrumb)
11. **Lịch nội dung** — CRUD, status workflow, AI topic suggestions

### Tools
12. **A/B Testing** — SEO A/B test with Groq AI analysis
13. **Báo cáo AI** — AI-generated SEO reports
14. **Chiến dịch** — Campaign tracking
15. **File Converter** — Drag-drop upload, 20 formats → Markdown, SEO pipeline

### Data
16. **SERP trực tiếp** — DuckDuckGo live search, deep content analysis
17. **Dashboard** — Charts (Recharts), GA4 data, GSC data, history

### Management
18. **Multi-site** — Manage multiple websites
19. **WordPress Publisher** — Publish to WP with Yoast SEO meta

---

## 7. NHỮNG GÌ CHƯA LÀM (TODO)

### Ưu tiên cao — Cần làm sớm
- [ ] **GA4 real data** — Cần tạo Service Account JSON trên Google Cloud
- [x] **Export Excel (Rank Tracker)** — ✅ Đã xong Phase 21 (`/api/rank-tracker/export-excel`, openpyxl)
- [ ] **Export PDF** — Báo cáo xuất file PDF (reportlab)
- [ ] **Ranking chart** — Line graph cho keyword history (đã có sẵn trong `RankTracker.tsx` dùng Recharts)

### Ưu tiên trung bình
- [ ] **AI viết full bài** — Từ outline → full article (đã có một phần qua `PolishPanel`)
- [ ] **Plagiarism check** — Kiểm tra đạo văn
- [ ] **Calendar view** — Month grid cho content calendar
- [ ] **Core Web Vitals** — PageSpeed API integration
- [ ] **Dark/Light mode toggle**

### Ưu tiên thấp / Tương lai
- [ ] Auth (login/signup/JWT) — Hiện tại open access
- [ ] Docker + deploy (Railway/Vercel)
- [ ] PostgreSQL migration
- [ ] Email notifications
- [ ] CI/CD pipeline

---

## 8. CÁCH CHẠY DỰ ÁN

```bash
# Terminal 1 — Backend
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
npm run dev
# → http://localhost:5173
```

### Ports
- Backend: `http://localhost:8000` (FastAPI + Swagger at /docs)
- Frontend: `http://localhost:5173` (Vite dev server)
- Health check: `GET http://localhost:8000/health`

---

## 9. QUY TẮC CODE

1. **Ngôn ngữ:** UI text = Tiếng Việt, Code = English
2. **Backend:** Lazy-import core modules in routers (fast startup)
3. **CPU-heavy tasks:** Dùng `asyncio.to_thread()`
4. **Styling:** Theo design system trong `index.css`, không dùng Tailwind
5. **API calls frontend:** Dùng `fetch()` (không axios)
6. **Databases:** SQLite files trong `backend/` directory
7. **New features:** Tạo file trong `core/`, expose qua `routers/`, tạo component trong `components/`, thêm vào `App.tsx` sidebar

---

## 10. CONTEXT CHO AI TIẾP THEO

Khi tiếp tục làm việc trên dự án này, hãy:

1. **Đọc file này trước** — Hiểu kiến trúc, trạng thái, TODO
2. **Check `.env`** — Biết API keys nào hoạt động
3. **Check `MOCK_DATA_NOTE.md`** — Biết data nào thật/giả
4. **Không tạo mock data mới** — User muốn 100% real data
5. **Ưu tiên Groq** — Không dùng Gemini (hết quota), user chọn Groq
6. **Design:** Dark mode glassmorphism, purple/cyan accent
7. **Commit format:** Emoji prefix (🔧🚀✨🎨) + Vietnamese description

### Tổng LOC hiện tại: ~27,600 lines
### Dependencies chính: fastapi, httpx, beautifulsoup4, groq, markitdown, recharts

---

*File này được tạo để đồng bộ context giữa các phiên AI coding.*
*Cập nhật file này mỗi khi có thay đổi lớn.*
