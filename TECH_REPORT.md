# 📋 Báo Cáo Kỹ Thuật — AI Marketing Hub

> **Ngày:** 24/04/2026 · **Phiên bản:** 1.0.0 (Phase 9)  
> **Tác giả:** Trần Như Ý  
> **Website mục tiêu:** https://binhphuocmitsubishi.com

---

## 1. Tổng quan

**AI Marketing Hub** là nền tảng phân tích SEO & Marketing tự động tích hợp AI, gồm 9 module chính:

| # | Tính năng | Mô tả |
|---|----------|-------|
| 1 | Kiểm tra SEO | Phân tích on-page: Title, Meta, Heading, Schema, từ khóa |
| 2 | CRO & Uy tín | Đánh giá CTA, trust signals, tối ưu chuyển đổi |
| 3 | Phân tích đối thủ | So sánh nội dung, khoảng cách với top SERP |
| 4 | Viết nội dung AI | Lập dàn ý + viết bài bằng Groq LLaMA 3.3 |
| 5 | Xuất bản WordPress | Đăng bài trực tiếp + chấm điểm cơ hội |
| 6 | Dữ liệu Google | GSC (rankings, clicks) + GA4 (sessions, traffic) |
| 7 | Anti-AI Detection | Tẩy zero-width chars, cải thiện readability |
| 8 | SERP trực tiếp | Kết quả tìm kiếm real-time + deep analyze |
| 9 | Dashboard tổng quan | Biểu đồ, stat cards, lịch sử, export CSV |

---

## 2. Kiến trúc hệ thống

![Kiến trúc hệ thống](docs/architecture_diagram.png)

**Công nghệ chính:**

| Lớp | Công nghệ |
|-----|-----------|
| Frontend | React 18, TypeScript 5, Vite 5, Recharts, CSS3 (Glassmorphism) |
| Backend | FastAPI, Uvicorn, httpx, BeautifulSoup4, scikit-learn, textstat |
| AI | Groq API (LLaMA 3.3 70B), Google Gemini (backup) |
| ML | TF-IDF Vectorizer + KMeans Clustering (phân nhóm từ khóa) |
| Google APIs | Search Console API v3, Analytics Data API v1beta, OAuth 2.0 |

---

## 3. Sơ đồ luồng hoạt động

### 3.1 Luồng tổng quan hệ thống

![Sơ đồ luồng tổng quan hệ thống](docs/system_flowchart.png)

### 3.2 Luồng thu thập & xử lý dữ liệu

![Sơ đồ luồng dữ liệu](docs/data_flow_diagram.png)

### 3.3 Luồng xác thực Google OAuth2

![Sơ đồ OAuth2](docs/oauth2_flowchart.png)

| Nguồn dữ liệu | Phương pháp | Thời gian |
|----------------|-------------|-----------|
| HTML (Title, Meta, Schema...) | httpx + BeautifulSoup | ~2s |
| SERP Top 10 | DuckDuckGo search | ~3s |
| Từ khóa phân cụm | TF-IDF + KMeans | <1s |
| GSC (ranking, clicks, CTR) | Google API + OAuth2 | ~2s |
| GA4 (sessions, traffic) | Google API + OAuth2 | ~3s |
| AI analysis | Groq LLaMA 3.3 70B | ~5s |

---

## 5. OAuth2 — Xác thực Google

| Thông số | Giá trị |
|---------|---------|
| Project | AI Marketing Hub (`ai-marketing-hub-49420`) |
| OAuth Client | `45850011490-irk36bce2stg512hfor3fm5m52ai650a` |
| Scopes | `webmasters.readonly` + `analytics.readonly` |
| GSC Site | `https://binhphuocmitsubishi.com/` |
| GA4 Property | `534300482` · Measurement ID: `G-DFEE14V0T8` |

**Luồng:** OAuth Playground → Authorization Code → Refresh Token (lưu .env) → Auto-refresh Access Token (1 giờ)

---

## 6. API Endpoints (17 endpoints)

| Method | Endpoint | Chức năng |
|--------|---------|-----------|
| `GET` | `/health` | Kiểm tra server |
| `POST` | `/api/seo/audit` | Kiểm tra SEO toàn diện |
| `POST` | `/api/content/plan` | Tạo dàn ý bài viết AI |
| `POST` | `/api/content/competitor-gap` | Phân tích đối thủ |
| `POST` | `/api/content/polish` | Tẩy AI watermark |
| `POST` | `/api/execution/score-opportunity` | Chấm điểm cơ hội |
| `POST` | `/api/execution/publish-wordpress` | Xuất bản WordPress |
| `POST` | `/api/data/gsc-sync` | Đồng bộ dữ liệu GSC |
| `POST` | `/api/ga4-overview` | Lấy dữ liệu GA4 |
| `POST` | `/api/ai-keywords` | Phân tích từ khóa AI |
| `POST` | `/api/serp/live` | SERP real-time |
| `POST` | `/api/serp/deep-analyze` | Phân tích sâu nội dung |
| `POST` | `/api/config/gsc` | Lưu credentials GSC |
| `POST` | `/api/config/ga4` | Lưu GA4 Property ID |
| `GET` | `/api/oauth/authorize` | URL xác thực OAuth2 |
| `GET` | `/api/oauth/callback` | Callback OAuth2 |
| `GET` | `/api/data/status` | Trạng thái kết nối |

---

## 7. Cấu trúc thư mục

```
ai-marketing-hub/
├── backend/                    ⚙️ Python + FastAPI
│   ├── main.py                 Entry point
│   ├── .env                    API Keys & Tokens
│   ├── core/                   27 modules phân tích
│   │   ├── seo_quality_rater.py
│   │   ├── keyword_analyzer.py     (TF-IDF + KMeans)
│   │   ├── ai_keyword_analyzer.py  (Groq LLaMA)
│   │   ├── ga4_fetcher.py          (GA4 REST API)
│   │   ├── google_search_console.py
│   │   └── ... (22 modules nữa)
│   └── routers/                6 API routers
│       ├── api_seo.py, api_data.py, api_content.py
│       ├── api_serp.py, api_execution.py, api_polish.py
│
├── frontend/                   🖥️ React + TypeScript
│   └── src/
│       ├── App.tsx             Main app (~1200 dòng)
│       ├── components/         8 component + CSS
│       ├── hooks/              4 custom hooks
│       └── lib/                Utilities
```

---

## 8. Khởi chạy

```bash
# Backend (Terminal 1)
cd backend && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend && npm install && npm run dev
```

**Truy cập:** http://localhost:5173

---

## 9. Thống kê

| Metric | Giá trị |
|--------|---------|
| Tổng file code | ~50 files |
| Backend | 27 modules (~470KB) |
| Frontend | 15 files (~166KB) |
| API endpoints | 17 |
| External APIs | 5 (GSC, GA4, Groq, Gemini, DuckDuckGo) |
| Phases | 9/9 ✅ |

---

*AI Marketing Hub — Phiên bản 1.0.0*
