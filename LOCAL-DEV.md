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

These are **lazy-loaded**: the server starts without them, but endpoints return mock data unless credentials are set.

#### Google Search Console + GA4

```env
GOOGLE_SEARCH_CONSOLE_CLIENT_ID=...
GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET=...
GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN=...
GSC_SITE_URL=https://search.google.com/search-console/...

GA4_PROPERTY_ID=123456789
GA4_CREDENTIALS_PATH=/path/to/service-account.json
```

#### DataForSEO (SERP data)

```env
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password
```

#### WordPress Publishing

```env
WORDPRESS_URL=https://yoursite.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=xxxx_xxxx_xxxx_xxxx
```

## Mock vs. Live Data

| Feature | No Credentials | Credentials Configured |
|---|---|---|
| SEO Audit (`/api/audit-url`) | Live (scrapes target URL) | Live |
| CRO & Trust Analysis | Live (from scraped content) | Live |
| Competitor Radar | Live (scrapes competitor URLs) | Live |
| Content Planner | Live (rule-based outline) | Live |
| Campaign Tracker Auto-Fill | **Mock data** (estimated metrics) | **Mock data** |
| Live Data Connectors | **Mock data** + warning banner | **Live data** |

> **Important:** When no credentials are configured, the Campaign Tracker shows a
> yellow "Mock data" warning banner. Data is synthetic and for preview only.

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
