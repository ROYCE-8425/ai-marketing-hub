# AI Marketing Hub — Vibe Coding Configuration

## Project Context
This is a full-stack SEO platform:
- **Backend**: FastAPI (Python) — `backend/`
- **Frontend**: React + TypeScript (Vite) — `frontend/`
- **AI Engine**: Groq LLaMA 3.3 70B
- **Database**: SQLite (4 databases)
- **Style**: Dark mode glassmorphism, premium SaaS aesthetic

## Coding Standards
- Use Vietnamese for UI text/labels
- Use English for code comments and variable names  
- Follow existing CSS design system in `frontend/src/index.css`
- All API endpoints go in `backend/routers/`
- All business logic goes in `backend/core/`
- Components use functional React with hooks
- Use `fetch()` for API calls (no axios)

## Key Design Tokens
```css
--bg: #080b14
--surface: rgba(255,255,255,0.03)
--primary: #8b5cf6
--accent: #06b6d4
--text-h: #f1f5f9
```

## Skills & Tools Installed
- `.superpowers/` — obra/superpowers (agentic skills framework)
- `.skills/` — mattpocock/skills (engineering skills)
- Backend uses `markitdown` for file conversion

## Architecture Rules
1. Lazy-import core modules in routers (keeps startup fast)
2. Use `asyncio.to_thread()` for CPU-heavy analysis
3. SQLite databases stored in `backend/` directory
4. Frontend max-width: 1100px, sidebar: 240px
5. All forms use glassmorphism gradient backgrounds
