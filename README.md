# AI Marketing Hub

AI-powered SEO & Marketing automation platform.

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
- SEO Audit & Analysis
- CRO & Trust Signal Detection
- Competitor Radar
- AI Content Writer
- Campaign Tracker
- **SERP Live** — Real-time search rankings via DuckDuckGo

## Tech Stack
- **Backend**: FastAPI + Python 3.12
- **Frontend**: React + Vite + TypeScript
- **SERP Data**: DuckDuckGo Search (free) / DataForSEO (premium)
