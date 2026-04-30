# 📊 PHÂN TÍCH CHỨC NĂNG — AI Marketing Hub v3.0.0

> **Ngày tạo:** 30/04/2026  
> **Phiên bản:** 3.0.0 (Phase 19)  
> **Kiến trúc:** FastAPI (Backend) + React/TypeScript (Frontend)  
> **Tổng số tính năng:** 17 modules | 36 core engines | 40+ API endpoints

---

## 📁 KIẾN TRÚC TỔNG QUAN

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TypeScript)         │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │ Sidebar │ │ Dashboard│ │ SEO Tabs │ │ Content Tabs│ │
│  │ Nav (6  │ │ Overview │ │ (5 tools)│ │ (4 tools)   │ │
│  │ groups) │ │ GSC+GA4  │ │          │ │             │ │
│  └─────────┘ └──────────┘ └──────────┘ └─────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    BACKEND (FastAPI v3.0.0)              │
│  9 API Routers → 36 Core Engines → 3 SQLite DBs        │
│  AI: Groq LLaMA 3.3 70B | Data: GSC, GA4, DuckDuckGo  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 NHÓM 1: PHÂN TÍCH SEO (5 công cụ)

### 1.1 Kiểm tra SEO (SEO Audit)
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Phân tích SEO toàn diện từ URL — keyword density, chất lượng nội dung, on-page SEO |
| **API** | `POST /api/audit-url`, `POST /api/audit-seo` |
| **Core Engines** | `seo_quality_rater.py` (23KB), `keyword_analyzer.py` (23KB) |
| **Input** | URL + từ khóa chính |
| **Output** | Overall score (0-100), grade (A-F), category scores, keyword analysis, distribution heatmap, LSI keywords, critical issues, warnings, suggestions |
| **Đặc biệt** | Phân tích word count, keyword stuffing risk, density status, 5+ category scores |

### 1.2 Technical SEO Scanner
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Quét 8 tiêu chí kỹ thuật SEO: meta tags, headings, images, mobile, links, sitemap, performance, security |
| **API** | `POST /api/tech-seo/scan` |
| **Core Engine** | `technical_seo.py` (17KB) |
| **Input** | URL trang web |
| **Output** | Điểm cho từng tiêu chí, grade tổng, danh sách issues + recommendations |
| **Đặc biệt** | Hỗ trợ Grade A detection, async scanning |

### 1.3 CRO & Uy tín (Conversion Rate Optimization)
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Đánh giá khả năng chuyển đổi: CRO checklist, CTA analysis, trust signals, above-fold |
| **API** | Tích hợp trong `/api/audit-url` |
| **Core Engines** | `cro_checker.py` (23KB), `cta_analyzer.py` (19KB), `trust_signal_analyzer.py` (21KB), `above_fold_analyzer.py` (16KB) |
| **Output** | CRO score (weighted: CRO 60% + CTA 20% + ATF 20%), trust score, sales risk alerts |
| **Đặc biệt** | 5-second test, testimonial detection, risk reversal signals, authority analysis |

### 1.4 SERP trực tiếp (Live SERP)
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Lấy kết quả tìm kiếm thực từ Google — phân tích đối thủ trên SERP |
| **API** | `POST /api/serp/live`, `POST /api/serp/deep-analyze` |
| **Core Engine** | `google_serp_scraper.py` (7KB), DuckDuckGo Search API |
| **Input** | Keyword, location (vn/us/uk...), số kết quả (5-20) |
| **Output** | Top ranking URLs, titles, snippets, deep content analysis |
| **Đặc biệt** | Hỗ trợ 7+ quốc gia, so sánh word count với bạn |

### 1.5 Backlink Analyzer
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Phân tích liên kết nội bộ và liên kết ngoài, đánh giá chất lượng anchor text |
| **API** | `POST /api/backlinks/analyze` |
| **Core Engine** | `backlink_analyzer.py` (7KB) |
| **Input** | URL trang web |
| **Output** | Internal/external links, quality score, domain analysis, anchor text breakdown |

---

## 🎯 NHÓM 2: TỪ KHÓA (3 công cụ)

### 2.1 Theo dõi Keyword (Rank Tracker)
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Theo dõi vị trí từ khóa theo thời gian, import/export CSV, cảnh báo tụt hạng |
| **API** | `POST /api/rank-tracker/add`, `/remove`, `/update-tag`, `/sync`, `/import-csv` |
|  | `GET /api/rank-tracker/keywords`, `/tags`, `/history`, `/export-csv`, `/alerts` |
| **Core Engine** | `rank_tracker.py` (13KB) — SQLite storage |
| **Tính năng** | ✅ Thêm/xóa keyword ✅ Tag phân nhóm ✅ Import CSV ✅ Export CSV ✅ Sync từ GSC ✅ Lịch sử ranking ✅ Cảnh báo tụt hạng (threshold) |
| **Database** | SQLite — bảng keywords + history |

### 2.2 AI Keyword Analysis
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Phân tích từ khóa bằng AI — clustering, search volume, difficulty, content strategy |
| **API** | `POST /api/ai-keywords` |
| **Core Engine** | `ai_keyword_analyzer.py` (15KB) |
| **Input** | Từ khóa mục tiêu |
| **Output** | Keyword clusters, search intent, volume estimates, difficulty, content strategy suggestions |
| **AI** | Groq LLaMA 3.3 70B |

### 2.3 Phân tích đối thủ (Competitor Gap)
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | So sánh nội dung với đối thủ, tìm gap và cơ hội |
| **API** | `POST /api/competitor-gap` |
| **Core Engine** | `competitor_gap_analyzer.py` (15KB) |
| **Input** | URL bạn + danh sách URLs đối thủ + keyword |
| **Output** | Gap blueprint, must-fill gaps, differentiation opportunities, structure analysis |
| **Đặc biệt** | Fetch song song tất cả URLs, phân tích content depth |

---

## ✍️ NHÓM 3: NỘI DUNG (4 công cụ)

### 3.1 Viết nội dung AI (Content Planner)
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Tạo kế hoạch bài viết chi tiết: outline, meta tags, section plans, engagement map |
| **API** | `POST /api/plan-content` |
| **Core Engine** | `article_planner.py` (15KB), `section_writer.py` (18KB) |
| **Input** | Keyword + target audience + competitor gaps |
| **Output** | Article plan (meta, sections, word targets, CTAs, featured snippets) |
| **Đặc biệt** | Auto-generate outline, engagement distribution, gap mapping |

### 3.2 Spin Editor
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Viết lại nội dung với nhiều phiên bản, nhiều giọng văn, spin theo đoạn |
| **API** | `POST /api/content/spin`, `/spin-multi`, `/spin-paragraphs` |
| **Core Engine** | `spin_editor.py` (10KB) |
| **Tính năng** | ✅ 3 modes: Single / Multi-version (3 bản) / Paragraph ✅ 3 levels: light/medium/heavy ✅ 4 tones: neutral/formal/casual/persuasive ✅ Preserve keywords |
| **AI** | Groq LLaMA 3.3 70B |

### 3.3 Tối ưu GEO (Generative Engine Optimization)
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Tối ưu cho AI search engines (SGE, Bing Chat, Perplexity) |
| **API** | `POST /api/geo/analyze`, `/generate-faq`, `/generate-schema` |
| **Core Engine** | `geo_analyzer.py` (16KB) |
| **Tính năng** | ✅ GEO score (0-100) ✅ Breakdown theo categories ✅ Auto-generate FAQ Schema (JSON-LD) ✅ Auto-generate LocalBusiness Schema ✅ Recommendations |
| **AI** | Groq LLaMA 3.3 70B (cho FAQ generation) |

### 3.4 Lịch nội dung (Content Calendar)
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Lập lịch xuất bản nội dung, theo dõi trạng thái, AI đề xuất chủ đề |
| **API** | `POST /api/calendar/add`, `/update`, `/delete`, `/suggest-topics` |
|  | `GET /api/calendar/items`, `/stats` |
| **Core Engine** | `content_calendar.py` (7KB) — SQLite storage |
| **Tính năng** | ✅ CRUD bài viết ✅ Status: Nháp → Đang duyệt → Đã đăng ✅ Filter theo status/type/month ✅ Stats dashboard ✅ AI topic suggestions ✅ Priority levels |
| **Database** | `content_calendar.db` |

---

## ⚡ NHÓM 4: CÔNG CỤ (3 công cụ)

### 4.1 SEO A/B Testing
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | So sánh 2 phiên bản title/description/content — AI đánh giá winner |
| **API** | `POST /api/ab-test/create`, `/evaluate`, `/delete` |
|  | `GET /api/ab-test/list` |
| **Core Engine** | `ab_testing.py` (6KB) — SQLite storage |
| **Tính năng** | ✅ 4 test types: title/description/heading/content ✅ AI evaluation: SEO, CTR, Intent Match, Naturalness ✅ Winner scoring ✅ Criteria breakdown |
| **Database** | `ab_tests.db` |
| **AI** | Groq LLaMA 3.3 70B |

### 4.2 Báo cáo AI (Report Generator)
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Tổng hợp tất cả scan results + AI summary → export file |
| **API** | `POST /api/report/generate`, `/export` |
| **Core Engine** | `report_generator.py` (8KB) |
| **Output** | SEO score + Tech SEO + Backlinks + AI summary → export .txt |
| **AI** | Groq LLaMA 3.3 70B (summary generation) |

### 4.3 Chiến dịch (Campaign Tracker)
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Theo dõi chiến dịch SEO: opportunity scoring, search intent, traffic projection |
| **API** | `POST /api/opportunities` |
| **Core Engines** | `opportunity_scorer.py` (17KB), `search_intent_analyzer.py` (13KB), `landing_page_scorer.py` (27KB) |
| **Tính năng** | ✅ 8-factor opportunity score ✅ Search intent detection ✅ Landing page scoring ✅ Traffic projection ✅ Low-hanging fruit classification ✅ Action items |

---

## ⚙️ NHÓM 5: QUẢN LÝ (1 công cụ)

### 5.1 Multi-site Manager
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Quản lý nhiều website, chuyển đổi context giữa các site |
| **API** | `POST /api/sites/add`, `/remove`, `/set-active` |
|  | `GET /api/sites/list`, `/active` |
| **Core Engine** | `site_manager.py` (3KB) — SQLite storage |
| **Tính năng** | ✅ Add/remove websites ✅ Set active site ✅ Site description + niche |
| **Database** | `sites.db` |

---

## 📊 NHÓM 6: TỔNG QUAN (Dashboard)

### 6.1 Dashboard Overview
| Thuộc tính | Chi tiết |
|------------|----------|
| **Mô tả** | Tổng quan dữ liệu thực từ GSC + GA4: sessions, users, pageviews, CTR, bounce rate |
| **Core Engines** | `google_search_console.py` (18KB), `ga4_fetcher.py` (11KB), `google_analytics.py` (13KB), `data_aggregator.py` (12KB) |
| **Tính năng** | ✅ GSC metrics (keywords, clicks, impressions) ✅ GA4 metrics (sessions, users, pageviews) ✅ Top keywords chart ✅ Position distribution donut ✅ Page views trend ✅ Traffic source breakdown |
| **Data Sources** | Google Search Console API, Google Analytics 4 API |

---

## 🔌 TÍCH HỢP BÊN NGOÀI

| Service | Mục đích | Cấu hình |
|---------|----------|----------|
| **Google Search Console** | Keywords, clicks, impressions, positions | `GOOGLE_SEARCH_CONSOLE_*` env vars |
| **Google Analytics 4** | Sessions, users, pageviews, bounce rate | `GA4_PROPERTY_ID` env var |
| **Groq LLaMA 3.3 70B** | AI content generation, spin, evaluate | `GROQ_API_KEY` env var |
| **DuckDuckGo Search** | Live SERP results (miễn phí, không cần API key) | Không cần cấu hình |
| **WordPress REST API** | Xuất bản bài viết trực tiếp | URL + username + app password |

---

## 🗄️ CƠ SỞ DỮ LIỆU

| Database | File | Dùng cho |
|----------|------|----------|
| Rank Tracker | `rank_tracker.db` | Keywords tracking, history |
| Content Calendar | `content_calendar.db` | Bài viết, lịch xuất bản |
| Sites | `sites.db` | Multi-site management |
| A/B Tests | `ab_tests.db` | SEO A/B testing data |

---

## 📈 THỐNG KÊ DỰ ÁN

| Metric | Giá trị |
|--------|---------|
| **Backend files** | 9 routers + 36 core engines |
| **Frontend components** | 24 files (TSX + CSS) |
| **API endpoints** | 40+ endpoints |
| **Core engines total size** | ~500KB Python code |
| **Frontend total size** | ~280KB TSX/CSS code |
| **Dependencies** | FastAPI, httpx, BeautifulSoup, scikit-learn, textstat, duckduckgo-search |
| **AI Provider** | Groq (LLaMA 3.3 70B Versatile) |
| **Databases** | 4 SQLite databases |

---

## 🚀 CHỨC NĂNG BỔ SUNG

| Chức năng | Mô tả |
|-----------|-------|
| **WordPress Publisher** | Xuất bản trực tiếp lên WordPress với Yoast SEO meta |
| **Content Polish** | Humanize AI text, readability scoring (`readability_scorer.py`, `content_scrubber.py`) |
| **Content Length Comparator** | So sánh độ dài nội dung với đối thủ (`content_length_comparator.py`) |
| **Social Research** | Tổng hợp dữ liệu social signals (`social_research_aggregator.py`) |
| **Engagement Analyzer** | Phân tích mức độ tương tác nội dung (`engagement_analyzer.py`) |
| **DataForSEO Integration** | Hỗ trợ SERP data từ DataForSEO API (`dataforseo.py`) |
| **CSV Import/Export** | Rank Tracker hỗ trợ import/export CSV |
| **Sidebar Navigation** | 6 nhóm, collapsible, responsive |
| **Glassmorphism UI** | Premium dark mode với gradient cards |

---

## 🔧 HƯỚNG DẪN CHẠY

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend  
cd frontend
npm run dev
```

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

*Tài liệu được tạo tự động bởi AI Marketing Hub Analysis System*
