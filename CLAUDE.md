# AI Marketing Hub — Project Rules

> **Full context:** Đọc `CODEX_CONTEXT.md` để hiểu toàn bộ dự án.

## Quick Facts
- **Stack:** FastAPI (Python) + React/TypeScript (Vite) + Groq AI + SQLite
- **Phase:** 20 | **Version:** 3.1.0 | **LOC:** ~27,600
- **Site:** binhphuocmitsubishi.com (đại lý Mitsubishi Bình Phước)
- **AI Engine:** Groq LLaMA 3.3 70B (NOT Gemini — quota exceeded)
- **Design:** Dark glassmorphism, `#8b5cf6` purple, `#06b6d4` cyan

## Critical Rules
1. UI text → **Tiếng Việt**. Code comments → English
2. **No mock data** — User wants 100% real. See `MOCK_DATA_NOTE.md`
3. **No Tailwind** — Use vanilla CSS, follow `frontend/src/index.css`
4. **No axios** — Use `fetch()` for API calls
5. Lazy-import in routers: `from core.xxx import yyy` inside endpoint functions
6. CPU-heavy → `asyncio.to_thread()`
7. New features: `core/` → `routers/` → `components/` → `App.tsx` sidebar

## API Keys Status
- ✅ `GROQ_API_KEY` — Working (main AI)
- ✅ `GSC_*` — Real data (OAuth2 token refreshed 01/05/2026)
- 🟡 `GA4_PROPERTY_ID` — Needs Service Account JSON file
- 🟡 `GEMINI_API_KEY` — Quota exceeded, skip
- ⚪ `ZAI_API_KEY` — Not integrated yet

## Architecture
```
backend/core/    → 37 business logic modules
backend/routers/ → 10 API routers
frontend/src/components/ → 19 page components
backend/*.db     → 4 SQLite databases
```

## Key Files
- `CODEX_CONTEXT.md` — Full project context (READ THIS FIRST)
- `MOCK_DATA_NOTE.md` — What's mock vs real
- `PHAN_TICH_PHAT_TRIEN.md` — Development breakdown (8 parts, 52 tasks)
- `backend/.env` — API keys
- `frontend/src/App.tsx` — Main app (sidebar, tabs, routing)
- `frontend/src/index.css` — Design system (2419 LOC)
