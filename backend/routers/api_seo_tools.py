"""
API Router — SEO Tools

Provides:
- POST /api/seo-tools/core-web-vitals   — Google PageSpeed Insights + CWV
- POST /api/seo-tools/validate-sitemap  — Sitemap.xml validation
- POST /api/seo-tools/broken-links      — Broken link scanner
- POST /api/seo-tools/validate-schema   — JSON-LD structured data validation
"""

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

router = APIRouter(prefix="/api/seo-tools", tags=["SEO Tools"])


# ── Pydantic request models ───────────────────────────────────────────────


class CoreWebVitalsRequest(BaseModel):
    """Request schema for Core Web Vitals check."""
    url: HttpUrl = Field(..., description="URL trang cần phân tích")
    strategy: str = Field(
        "mobile",
        description="Chiến lược: 'mobile' hoặc 'desktop'",
        pattern="^(mobile|desktop)$",
    )
    api_key: Optional[str] = Field(
        None,
        description="Google API key (tuỳ chọn, giúp tăng quota)",
    )


class ValidateSitemapRequest(BaseModel):
    """Request schema for sitemap validation."""
    url: HttpUrl = Field(..., description="URL của sitemap.xml cần validate")


class BrokenLinksRequest(BaseModel):
    """Request schema for broken link check."""
    url: HttpUrl = Field(..., description="URL trang cần scan link")
    max_links: int = Field(
        100,
        description="Số link tối đa cần kiểm tra (mặc định 100)",
        ge=1,
        le=500,
    )


class ValidateSchemaRequest(BaseModel):
    """Request schema for JSON-LD validation."""
    url: HttpUrl = Field(..., description="URL trang cần kiểm tra structured data")


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post("/core-web-vitals")
async def core_web_vitals(body: CoreWebVitalsRequest):
    """
    Phân tích Core Web Vitals qua Google PageSpeed Insights API.

    Trả về: LCP, INP, CLS, FCP, TTFB + Lighthouse scores + opportunities.
    """
    from core.core_web_vitals import check_core_web_vitals

    import os
    result = await check_core_web_vitals(
        url=str(body.url),
        strategy=body.strategy,
        api_key=body.api_key or os.getenv("PAGESPEED_API_KEY"),
    )
    return result


@router.post("/validate-sitemap")
async def validate_sitemap(body: ValidateSitemapRequest):
    """
    Validate sitemap.xml — kiểm tra XML, lastmod, size limits, URL reachability.

    Trả về: valid, url_count, errors, warnings, sample URL checks.
    """
    from core.sitemap_validator import validate_sitemap as _validate

    result = await _validate(url=str(body.url))
    return result


@router.post("/broken-links")
async def check_broken_links(body: BrokenLinksRequest):
    """
    Scan trang web tìm link hỏng — <a>, <img>, <link>, <script>.

    Trả về: broken_links, health_score, recommendations.
    """
    from core.broken_link_checker import check_broken_links as _check

    result = await _check(url=str(body.url), max_links=body.max_links)
    return result


@router.post("/validate-schema")
async def validate_schema(body: ValidateSchemaRequest):
    """
    Validate JSON-LD structured data trên trang.

    Kiểm tra @type, required properties (Article, Product, FAQ, etc.).
    Trả về: schemas_found, valid, errors, warnings.
    """
    from core.schema_validator import validate_schema as _validate

    result = await _validate(url=str(body.url))
    return result
