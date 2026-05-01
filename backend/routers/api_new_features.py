"""
API Router — Phase 10-13 (Upgraded): Rank Tracker, Spin Editor, GEO Optimizer
"""

from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse
from typing import List, Optional
import os

router = APIRouter()

_DEFAULT_SITE = lambda: os.getenv("GSC_SITE_URL", "https://binhphuocmitsubishi.com/")


# ─── Phase 10: Rank Tracker ─────────────────────────────────────────────

@router.post("/api/rank-tracker/add")
async def add_tracked_keyword(
    keyword: str = Body(..., embed=True),
    site_url: str = Body(None, embed=True),
    tag: str = Body("", embed=True),
):
    from core.rank_tracker import add_keyword
    return add_keyword(keyword, site_url or _DEFAULT_SITE(), tag)


@router.post("/api/rank-tracker/remove")
async def remove_tracked_keyword(
    keyword: str = Body(..., embed=True),
    site_url: str = Body(None, embed=True),
):
    from core.rank_tracker import remove_keyword
    return remove_keyword(keyword, site_url or _DEFAULT_SITE())


@router.post("/api/rank-tracker/update-tag")
async def update_tag(
    keyword: str = Body(..., embed=True),
    tag: str = Body(..., embed=True),
    site_url: str = Body(None, embed=True),
):
    from core.rank_tracker import update_keyword_tag
    return update_keyword_tag(keyword, site_url or _DEFAULT_SITE(), tag)


@router.get("/api/rank-tracker/keywords")
async def get_tracked_keywords_list(site_url: str = None, tag: str = ""):
    from core.rank_tracker import get_tracked_keywords
    return {"keywords": get_tracked_keywords(site_url or _DEFAULT_SITE(), tag)}


@router.get("/api/rank-tracker/tags")
async def get_all_tags_api(site_url: str = None):
    from core.rank_tracker import get_all_tags
    return {"tags": get_all_tags(site_url or _DEFAULT_SITE())}


@router.get("/api/rank-tracker/history")
async def get_keyword_history_api(keyword: str, days: int = 30, site_url: str = None):
    from core.rank_tracker import get_keyword_history
    return {"keyword": keyword, "history": get_keyword_history(keyword, site_url or _DEFAULT_SITE(), days)}


@router.post("/api/rank-tracker/sync")
async def sync_rankings():
    from core.rank_tracker import sync_rankings_from_gsc
    return await sync_rankings_from_gsc(_DEFAULT_SITE())


@router.post("/api/rank-tracker/import-csv")
async def import_csv(
    csv_text: str = Body(..., embed=True),
    site_url: str = Body(None, embed=True),
):
    from core.rank_tracker import import_keywords_csv
    return import_keywords_csv(csv_text, site_url or _DEFAULT_SITE())


@router.get("/api/rank-tracker/export-csv")
async def export_csv(site_url: str = None):
    from core.rank_tracker import export_keywords_csv
    csv_data = export_keywords_csv(site_url or _DEFAULT_SITE())
    return PlainTextResponse(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rank_tracker_export.csv"},
    )


@router.get("/api/rank-tracker/alerts")
async def get_alerts(threshold: int = 5, site_url: str = None):
    from core.rank_tracker import check_ranking_alerts
    return {"alerts": check_ranking_alerts(site_url or _DEFAULT_SITE(), threshold)}


# ─── Phase 11: Spin Editor ──────────────────────────────────────────────

@router.post("/api/content/spin")
async def spin_content_api(
    content: str = Body(..., embed=True),
    level: str = Body("medium", embed=True),
    preserve_keywords: Optional[List[str]] = Body(None, embed=True),
    language: str = Body("vi", embed=True),
    tone: str = Body("neutral", embed=True),
):
    from core.spin_editor import spin_content
    return await spin_content(content, level, preserve_keywords, language, tone)


@router.post("/api/content/spin-multi")
async def spin_multi_api(
    content: str = Body(..., embed=True),
    level: str = Body("medium", embed=True),
    preserve_keywords: Optional[List[str]] = Body(None, embed=True),
    language: str = Body("vi", embed=True),
    tone: str = Body("neutral", embed=True),
    num_versions: int = Body(3, embed=True),
):
    from core.spin_editor import spin_multi_version
    return await spin_multi_version(content, level, preserve_keywords, language, tone, num_versions)


@router.post("/api/content/spin-paragraphs")
async def spin_paragraphs_api(
    content: str = Body(..., embed=True),
    level: str = Body("medium", embed=True),
    preserve_keywords: Optional[List[str]] = Body(None, embed=True),
    language: str = Body("vi", embed=True),
    tone: str = Body("neutral", embed=True),
):
    from core.spin_editor import spin_paragraphs
    return await spin_paragraphs(content, level, preserve_keywords, language, tone)


# ─── Phase 13: GEO Optimizer ────────────────────────────────────────────

@router.post("/api/geo/analyze")
async def analyze_geo_api(
    url: str = Body(..., embed=True),
    keyword: str = Body("", embed=True),
):
    from core.geo_analyzer import analyze_geo
    return await analyze_geo(url, keyword)


@router.post("/api/geo/generate-faq")
async def generate_faq_api(
    url: str = Body(..., embed=True),
):
    from core.geo_analyzer import generate_faq_from_content
    return await generate_faq_from_content(url)


@router.post("/api/geo/generate-schema")
async def generate_schema_api(
    name: str = Body(..., embed=True),
    address: str = Body(..., embed=True),
    phone: str = Body(..., embed=True),
    url: str = Body(..., embed=True),
    business_type: str = Body("AutoDealer", embed=True),
    description: str = Body("", embed=True),
    opening_hours: str = Body("Mo-Sa 08:00-17:30", embed=True),
):
    from core.geo_analyzer import generate_local_business_schema
    code = generate_local_business_schema(name, address, phone, url, business_type, description, opening_hours)
    return {"schema_code": code, "type": business_type}


@router.post("/api/geo/generate-product-schema")
async def generate_product_schema_api(
    name: str = Body(..., embed=True),
    description: str = Body("", embed=True),
    brand: str = Body("", embed=True),
    price: float = Body(0, embed=True),
    currency: str = Body("VND", embed=True),
    url: str = Body("", embed=True),
    image: str = Body("", embed=True),
    sku: str = Body("", embed=True),
):
    from core.geo_analyzer import generate_product_schema
    code = generate_product_schema(name, description, image, brand, price, currency, url=url, sku=sku)
    return {"schema_code": code, "type": "Product"}


@router.post("/api/geo/generate-article-schema")
async def generate_article_schema_api(
    headline: str = Body(..., embed=True),
    author: str = Body("", embed=True),
    date_published: str = Body("", embed=True),
    description: str = Body("", embed=True),
    url: str = Body("", embed=True),
    publisher_name: str = Body("", embed=True),
    article_type: str = Body("Article", embed=True),
):
    from core.geo_analyzer import generate_article_schema
    code = generate_article_schema(headline, author, date_published, description=description, url=url, publisher_name=publisher_name, article_type=article_type)
    return {"schema_code": code, "type": article_type}


@router.post("/api/geo/generate-breadcrumb-schema")
async def generate_breadcrumb_schema_api(
    items: List[dict] = Body(..., embed=True),
):
    from core.geo_analyzer import generate_breadcrumb_schema
    code = generate_breadcrumb_schema(items)
    return {"schema_code": code, "type": "BreadcrumbList"}


@router.post("/api/geo/validate-schema")
async def validate_schema_api(
    url: str = Body(..., embed=True),
):
    from core.geo_analyzer import validate_schema_on_page
    return await validate_schema_on_page(url)

