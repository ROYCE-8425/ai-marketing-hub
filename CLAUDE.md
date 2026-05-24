# CLAUDE.md — Instructions for Claude Code / Codex

## Identity
You are a Senior Full-Stack Developer and Project Manager for AI Marketing Hub — an AI-powered SEO & Marketing automation platform for the Vietnamese market.

## First Steps
1. Read `AGENTS.md` for complete project context (architecture, DB schemas, API endpoints, coding rules)
2. Read `OpenSpec/PROJECT_CONTEXT.md` for current progress and TODO list
3. Check relevant source files BEFORE making any changes

## Quick Reference

### Tech Stack
- **Frontend**: React 19 + TypeScript 6 + Vite 8 + recharts + vanilla CSS (dark glassmorphism)
- **Backend**: FastAPI + Python 3.13 + Groq LLaMA 3.3 70B + SQLite × 6
- **Auth**: JWT (bcrypt + python-jose)
- **Domain**: binhphuocmitsubishi.com

### Critical Rules (MUST FOLLOW)
1. UI text = **Tiếng Việt** (Vietnamese)
2. **NO Tailwind** — vanilla CSS only, follow `frontend/src/index.css`
3. **NO axios** — use `fetch()` or `authFetch()` from `lib/auth.ts`
4. **NO mock data** — real data or error states only
5. **Groq** = primary AI (not Gemini, not OpenAI)
6. Dark glassmorphism UI — purple `#8b5cf6`, cyan `#06b6d4`
7. New feature pattern: `core/` → `routers/` → `components/` → `App.tsx`
8. Lazy imports in backend routers
9. CPU-heavy → `asyncio.to_thread()`

### Commands
```bash
# Frontend
cd frontend && npm run dev          # Dev server :5173
cd frontend && npx tsc -b           # Type check
cd frontend && npm run build        # Production build

# Backend  
cd backend && python init_database.py           # Init DBs
cd backend && python -m uvicorn main:app --reload --port 8000
cd backend && python -c "from main import app"  # Verify imports

# Docker
docker-compose up --build
```

### Database Files (in backend/)
- `sites.db` — managed_sites
- `rank_tracker.db` — tracked_keywords, ranking_history
- `content_calendar.db` — content_items
- `ab_tests.db` — ab_tests
- `auth.db` — users, refresh_tokens
- `data/usage_history.db` — usage_log

### Default Login
- Email: `admin@aimarketing.vn`
- Password: `admin123`

### Key Directories
- `frontend/src/components/` — 31+ React components
- `frontend/src/lib/` — apiConfig.ts, auth.ts, history.ts
- `backend/routers/` — 15 API routers (99 endpoints total)
- `backend/core/` — 47+ business logic modules
- `OpenSpec/` — All project documentation

## When Making Changes
1. Always verify TypeScript compiles: `npx tsc -b`
2. Always verify backend imports: `python -c "from main import app"`
3. Update `OpenSpec/PROJECT_CONTEXT.md` if significant changes
4. Keep comments in English, UI text in Vietnamese
