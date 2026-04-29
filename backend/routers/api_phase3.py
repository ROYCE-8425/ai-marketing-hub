"""
API Router — Phase 15, 18-19: Content Calendar, Multi-site Manager, SEO A/B Testing
"""

from fastapi import APIRouter, Body
from typing import Optional
import os

router = APIRouter()

_DEFAULT_SITE = lambda: os.getenv("GSC_SITE_URL", "https://binhphuocmitsubishi.com/")


# ─── Phase 15: Content Calendar ────────────────────────────────────────

@router.post("/api/calendar/add")
async def add_calendar_item(
    title: str = Body(..., embed=True),
    site_url: str = Body(None, embed=True),
    description: str = Body("", embed=True),
    content_type: str = Body("blog", embed=True),
    scheduled_date: str = Body("", embed=True),
    author: str = Body("", embed=True),
    keywords: str = Body("", embed=True),
    priority: str = Body("medium", embed=True),
):
    from core.content_calendar import add_item
    return add_item(title, site_url or _DEFAULT_SITE(), description, content_type,
                    scheduled_date, author, keywords, priority)


@router.post("/api/calendar/update")
async def update_calendar_item(
    id: int = Body(..., embed=True),
    title: Optional[str] = Body(None, embed=True),
    description: Optional[str] = Body(None, embed=True),
    content_type: Optional[str] = Body(None, embed=True),
    status: Optional[str] = Body(None, embed=True),
    scheduled_date: Optional[str] = Body(None, embed=True),
    author: Optional[str] = Body(None, embed=True),
    keywords: Optional[str] = Body(None, embed=True),
    notes: Optional[str] = Body(None, embed=True),
    priority: Optional[str] = Body(None, embed=True),
):
    from core.content_calendar import update_item
    return update_item(id, title=title, description=description, content_type=content_type,
                       status=status, scheduled_date=scheduled_date, author=author,
                       keywords=keywords, notes=notes, priority=priority)


@router.post("/api/calendar/delete")
async def delete_calendar_item(id: int = Body(..., embed=True)):
    from core.content_calendar import delete_item
    return delete_item(id)


@router.get("/api/calendar/items")
async def get_calendar_items(
    site_url: str = None, month: str = "", status: str = "", content_type: str = "",
):
    from core.content_calendar import get_items
    return {"items": get_items(site_url or _DEFAULT_SITE(), month, status, content_type)}


@router.get("/api/calendar/stats")
async def get_calendar_stats(site_url: str = None):
    from core.content_calendar import get_stats
    return get_stats(site_url or _DEFAULT_SITE())


@router.post("/api/calendar/suggest-topics")
async def suggest_topics_api(
    site_url: str = Body(None, embed=True),
    niche: str = Body("ô tô", embed=True),
    count: int = Body(5, embed=True),
):
    from core.content_calendar import suggest_topics
    return await suggest_topics(site_url or _DEFAULT_SITE(), niche, count)


# ─── Phase 18: Multi-site Manager ──────────────────────────────────────

@router.post("/api/sites/add")
async def add_site_api(
    name: str = Body(..., embed=True),
    url: str = Body(..., embed=True),
    description: str = Body("", embed=True),
    niche: str = Body("", embed=True),
):
    from core.site_manager import add_site
    return add_site(name, url, description, niche)


@router.post("/api/sites/remove")
async def remove_site_api(id: int = Body(..., embed=True)):
    from core.site_manager import remove_site
    return remove_site(id)


@router.get("/api/sites/list")
async def list_sites():
    from core.site_manager import get_sites
    return {"sites": get_sites()}


@router.post("/api/sites/set-active")
async def set_active_api(id: int = Body(..., embed=True)):
    from core.site_manager import set_active_site
    return set_active_site(id)


@router.get("/api/sites/active")
async def get_active():
    from core.site_manager import get_active_site
    return get_active_site()


# ─── Phase 19: SEO A/B Testing ─────────────────────────────────────────

@router.post("/api/ab-test/create")
async def create_ab_test(
    name: str = Body(..., embed=True),
    test_type: str = Body("title", embed=True),
    variant_a: str = Body(..., embed=True),
    variant_b: str = Body(..., embed=True),
    site_url: str = Body(None, embed=True),
    url: str = Body("", embed=True),
    keyword: str = Body("", embed=True),
):
    from core.ab_testing import create_test
    return create_test(name, test_type, variant_a, variant_b, site_url or _DEFAULT_SITE(), url, keyword)


@router.get("/api/ab-test/list")
async def list_ab_tests(site_url: str = None, status: str = ""):
    from core.ab_testing import get_tests
    return {"tests": get_tests(site_url or _DEFAULT_SITE(), status)}


@router.post("/api/ab-test/evaluate")
async def evaluate_ab_test(id: int = Body(..., embed=True)):
    from core.ab_testing import evaluate_test
    return await evaluate_test(id)


@router.post("/api/ab-test/delete")
async def delete_ab_test(id: int = Body(..., embed=True)):
    from core.ab_testing import delete_test
    return delete_test(id)
