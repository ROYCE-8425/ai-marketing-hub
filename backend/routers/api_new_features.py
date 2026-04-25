"""
API Router — Phase 10-13: Rank Tracker, Spin Editor, GEO Optimizer
"""

from fastapi import APIRouter, Body
from typing import List, Optional
import os

router = APIRouter()


# ─── Phase 10: Rank Tracker ─────────────────────────────────────────────

@router.post("/api/rank-tracker/add")
async def add_tracked_keyword(
    keyword: str = Body(..., embed=True),
    site_url: str = Body(None, embed=True),
):
    from core.rank_tracker import add_keyword
    url = site_url or os.getenv("GSC_SITE_URL", "https://binhphuocmitsubishi.com/")
    return add_keyword(keyword, url)


@router.post("/api/rank-tracker/remove")
async def remove_tracked_keyword(
    keyword: str = Body(..., embed=True),
    site_url: str = Body(None, embed=True),
):
    from core.rank_tracker import remove_keyword
    url = site_url or os.getenv("GSC_SITE_URL", "https://binhphuocmitsubishi.com/")
    return remove_keyword(keyword, url)


@router.get("/api/rank-tracker/keywords")
async def get_tracked_keywords_list(site_url: str = None):
    from core.rank_tracker import get_tracked_keywords
    url = site_url or os.getenv("GSC_SITE_URL", "https://binhphuocmitsubishi.com/")
    return {"keywords": get_tracked_keywords(url)}


@router.get("/api/rank-tracker/history")
async def get_keyword_history_api(keyword: str, days: int = 30, site_url: str = None):
    from core.rank_tracker import get_keyword_history
    url = site_url or os.getenv("GSC_SITE_URL", "https://binhphuocmitsubishi.com/")
    return {"keyword": keyword, "history": get_keyword_history(keyword, url, days)}


@router.post("/api/rank-tracker/sync")
async def sync_rankings():
    from core.rank_tracker import sync_rankings_from_gsc
    url = os.getenv("GSC_SITE_URL", "https://binhphuocmitsubishi.com/")
    return await sync_rankings_from_gsc(url)


# ─── Phase 11: Spin Editor ──────────────────────────────────────────────

@router.post("/api/content/spin")
async def spin_content_api(
    content: str = Body(..., embed=True),
    level: str = Body("medium", embed=True),
    preserve_keywords: Optional[List[str]] = Body(None, embed=True),
    language: str = Body("vi", embed=True),
):
    from core.spin_editor import spin_content
    return await spin_content(content, level, preserve_keywords, language)


# ─── Phase 13: GEO Optimizer ────────────────────────────────────────────

@router.post("/api/geo/analyze")
async def analyze_geo_api(
    url: str = Body(..., embed=True),
    keyword: str = Body("", embed=True),
):
    from core.geo_analyzer import analyze_geo
    return await analyze_geo(url, keyword)
