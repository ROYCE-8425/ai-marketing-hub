# AI Marketing Hub

AI-powered SEO & Marketing automation platform for the Vietnamese market.

## Quick Start

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Features

### SEO Analysis
- **SEO Audit** — On-page keyword density, quality scoring (A-F), LSI keywords
- **Technical SEO** — Meta tags, headings, images, links, sitemap, robots.txt
- **CRO & Trust** — Conversion optimization checklist, CTA analysis, trust signals
- **SERP Live** — Real-time Google search rankings via DataForSEO
- **Backlinks** — Internal/external link extraction, anchor text analysis

### Keywords
- **Rank Tracker** — SQLite-backed keyword tracking with CSV import/export
- **AI Keyword Analysis** — Groq AI + TF-IDF clustering
- **Competitor Gap** — Content gap analysis against competitor URLs

### Content
- **AI Content Writer** — Auto outline, section planning, meta tags
- **Spin Editor** — Multi-version content spinning with Groq AI
- **GEO Optimizer** — Generative Engine Optimization with Schema.org generators
- **Content Calendar** — CRUD with status workflow and AI topic suggestions

### Tools
- **A/B Testing** — SEO A/B test with AI evaluation
- **AI Reports** — Comprehensive SEO report generation
- **Campaign Tracker** — Opportunity scoring with auto-fill from GSC/DataForSEO
- **File Converter** — PDF/Word/Excel/PPT → Markdown via MarkItDown

### Data Connectors
- **Google Search Console** — Real data via OAuth2 + httpx
- **Google Analytics 4** — Real data via REST API (needs OAuth scope)
- **DataForSEO** — SERP metrics (needs API key)

### Management
- **Multi-site Manager** — Manage multiple websites
- **WordPress Publisher** — Publish to WP with Yoast SEO meta

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12) |
| Frontend | React 18 + TypeScript (Vite 6) |
| AI Engine | Groq (LLaMA 3.3 70B) |
| Database | SQLite × 4 |
| Styling | Vanilla CSS — dark glassmorphism |
| Charts | Recharts |
| File Processing | MarkItDown (Microsoft) |
| SERP Data | DataForSEO (ưu tiên) / Google Custom Search API (free 100/day) |

## Documentation

- `CODEX_CONTEXT.md` — Full project context for AI assistants
- `MOCK_DATA_NOTE.md` — Mock vs real data tracking
- `PHAN_TICH_PHAT_TRIEN.md` — Development breakdown
- `PHAN_TICH_CHUC_NANG.md` — Feature analysis
- `LOCAL-DEV.md` — Local development setup
- `CLAUDE.md` — AI coding rules

## Version

**v3.1.0** · Phase 20 · ~27,600 LOC
