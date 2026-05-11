"""
AI Marketing Hub — FastAPI Backend (Phase 20)

Phase 5: Publish to WordPress + Opportunity & Performance Scoring
Phase 6: Live Data Connectors — GSC, GA4, DataForSEO
Phase 7: Anti-Detection & Content Polish — Humanize AI text
Phase 8: Live SERP Results — Real Google rankings
Phase 9: Dashboard Overview, History & Export
Phase 10-13: Rank Tracker, Spin Editor, DataForSEO, GEO Optimizer
Phase 14: Backlink Analyzer
Phase 15: Content Calendar
Phase 16: Technical SEO Scanner
Phase 17: AI Report Generator
Phase 18: Multi-site Manager
Phase 19: SEO A/B Testing
Phase 20: MarkItDown File Converter (PDF/Word/Excel/PPT → Markdown)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import api_seo
from routers import api_content
from routers import api_execution
from routers import api_data
from routers import api_polish
from routers import api_serp
from routers import api_new_features
from routers import api_phase2
from routers import api_phase3
from routers import api_convert
from routers import api_auth

app = FastAPI(
    title="AI Marketing Hub — Backend",
    version="3.1.0",
    description=(
        "AI Marketing Hub API — Phase 20: SEO Audit, CRO, Competitor Gap, "
        "Content Planning, Publish, Opportunity Scoring, Live Data Connectors, "
        "Content Polish, Live SERP, Dashboard, Rank Tracker, Spin Editor, "
        "GEO Optimizer, Backlinks, Content Calendar, Technical SEO, "
        "AI Reports, Multi-site, A/B Testing, File Converter (MarkItDown)"
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_seo.router)
app.include_router(api_content.router)
app.include_router(api_execution.router)
app.include_router(api_data.router)
app.include_router(api_polish.router)
app.include_router(api_serp.router)
app.include_router(api_new_features.router)
app.include_router(api_phase2.router)
app.include_router(api_phase3.router)
app.include_router(api_convert.router)
app.include_router(api_auth.router)


@app.get("/health")
async def health():
    return {"status": "ok", "phase": 20, "version": "3.1.0"}
