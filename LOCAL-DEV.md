# AI Marketing Hub — Local Development

## Prerequisites

- **Node.js** ≥ 18 (frontend build)
- **Python** ≥ 3.10 + `venv` (backend)

## Quick Start

### 1. Backend

```bash
cd backend

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at **http://localhost:8000**. API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment config
cp .env.example .env.local   # Already configured for localhost:8000

# Start dev server
npm run dev
```

Frontend runs at **http://localhost:5173** (Vite default).

## Environment Variables

### Frontend (`frontend/.env.local`)

```env
# Backend API URL (no trailing slash)
VITE_API_BASE_URL=http://localhost:8000
```

### Backend — Optional Live Data Connectors

These are **lazy-loaded**: the server starts without them, but endpoints return error states unless credentials are set.

#### Google Search Console + GA4

```env
GOOGLE_SEARCH_CONSOLE_CLIENT_ID=...
GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET=...
GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN=...
GSC_SITE_URL=https://search.google.com/search-console/...

GA4_PROPERTY_ID=123456789
GA4_CREDENTIALS_PATH=/path/to/service-account.json
```

#### DataForSEO (SERP data — ưu tiên #1)

```env
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password
```

#### Google Custom Search JSON API (SERP data — fallback #2, free 100/day)

```env
GOOGLE_CUSTOM_SEARCH_API_KEY=AIza...
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=017...
```

> **Lưu ý:** Google Custom Search trả kết quả từ Programmable Search Engine, không có SEO metrics (volume, CPC). DataForSEO trả Google organic SERP thật + metrics.
#### WordPress Publishing

```env
WORDPRESS_URL=https://yoursite.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=xxxx_xxxx_xxxx_xxxx
```

## Data Availability (No Mock)

| Feature | No Credentials | Credentials Configured |
|---|---|---|
| SEO Audit (`/api/audit-url`) | Live (scrapes target URL) | Live |
| CRO & Trust Analysis | Live (from scraped content) | Live |
| Competitor Radar | Live (scrapes competitor URLs) | Live |
| Content Planner | Live (rule-based outline) | Live |
| SERP Live (Google) | **Error state** + cần cấu hình | **Live data** (DataForSEO hoặc Custom Search API) |
| Google Search Console | **Error state** + red banner | **Live data** (OAuth2) |
| Google Analytics 4 | **Error state** + red banner | **Live data** (needs OAuth scope) |
| Campaign Tracker Auto-Fill | **Error state** + warning | **Live data** |
| DataForSEO SERP Metrics | **Error state** + warning | **Live data** |

> **Zero-mock policy:** Khi không có credentials, UI hiển thị trạng thái lỗi rõ ràng
> (🔴 Chưa kết nối + error message). KHÔNG có dữ liệu giả.

## Verification Commands

```bash
# Backend import check
cd backend && source venv/bin/activate && python -c "import main; print(main.app.title, main.app.version)"

# Frontend build
cd frontend && npm run build

# SEO machine tests (repo root)
python3 -m unittest discover -s seomachine/tests -p 'test_*.py'
```

## Deployment Notes

This is a **local development** setup. Before production deployment:

- [ ] Set `VITE_API_BASE_URL` to your production backend URL
- [ ] Configure all credential env vars above via your deployment platform
- [ ] Enable CORS restrictions in `backend/main.py` for production domains
- [ ] This codebase is **not yet production-ready** — further hardening required
