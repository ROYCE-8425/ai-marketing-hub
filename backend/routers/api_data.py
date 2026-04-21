"""
API Data Router — Phase 6

Provides live data connectors:
- GET  /api/data/status    — Check connection status per data source
- POST /api/data/gsc-sync  — Fetch real GSC + GA4 metrics for a URL/keyword
- POST /api/data/serp-sync — Fetch SERP data (DataForSEO or mock)
- POST /api/data/bulk-sync — Run all connectors in parallel → unified payload
"""

from __future__ import annotations

import asyncio
import os
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────────────────────────
# Lazy-load SDK classes so the server starts without optional dependencies
# ─────────────────────────────────────────────────────────────────────────────

def _ga4():
    from core.google_analytics import GoogleAnalytics as _cls
    return _cls

def _gsc():
    from core.google_search_console import GoogleSearchConsole as _cls
    return _cls

def _dfs():
    from core.dataforseo import DataForSEO as _cls
    return _cls


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class GscSyncRequest(BaseModel):
    url: str = Field(..., description="Full URL of the page to analyze")
    keyword: str = Field(..., description="Target keyword to track")
    gsc_site_url: Optional[str] = None
    gsc_credentials_path: Optional[str] = None
    ga4_property_id: Optional[str] = None
    ga4_credentials_path: Optional[str] = None


class SerpSyncRequest(BaseModel):
    keyword: str = Field(..., description="Keyword to analyze")
    location_code: int = Field(2840, description="DataForSEO location code (2840=US)")
    language_code: str = Field("en", description="Language code")
    dataforseo_login: Optional[str] = None
    dataforseo_password: Optional[str] = None


class DataConnectorStatus(BaseModel):
    gsc: Literal["connected", "disconnected"] = "disconnected"
    ga4: Literal["connected", "disconnected"] = "disconnected"
    dataforseo: Literal["connected", "disconnected", "pending"] = "pending"
    last_checked: Optional[str] = None


router = APIRouter(prefix="/api", tags=["Phase 6 — Live Data Connectors"])

# ─────────────────────────────────────────────────────────────────────────────
# Mock data generators (fallback when credentials are missing)
# ─────────────────────────────────────────────────────────────────────────────

def _mock_gsc_data(keyword: str, _url: str) -> Dict[str, Any]:
    """Realistic GSC mock data based on keyword commercial intent."""
    kw = keyword.lower()
    is_commercial = any(t in kw for t in [
        "best", "top", "review", "vs", "compare", "alternative", "pricing", "hosting"
    ])
    base_imp = 2400 if is_commercial else 1200
    base_clk = int(base_imp * (0.04 if is_commercial else 0.05))
    base_pos = 14.3 if is_commercial else 18.7
    return {
        "keyword": keyword,
        "clicks": base_clk,
        "impressions": base_imp,
        "ctr": round(base_clk / base_imp, 4),
        "position": round(base_pos + (hash(keyword) % 10) - 5, 1),
        "source": "mock_gsc",
        "note": "Configure GSC credentials for live data"
    }


def _mock_ga4_data(url: str) -> Dict[str, Any]:
    return {
        "url": url,
        "total_pageviews": 4820,
        "sessions": 3640,
        "avg_engagement_rate": 0.61,
        "bounce_rate": 0.38,
        "trend_direction": "rising",
        "trend_percent": 12.4,
        "source": "mock_ga4",
        "note": "Configure GA4 credentials for live analytics"
    }


def _mock_serp_data(keyword: str) -> Dict[str, Any]:
    """Realistic SERP mock data based on keyword intent."""
    kw = keyword.lower()
    is_tx = any(t in kw for t in ["buy", "pricing", "cost", "plan"])
    is_cm = any(t in kw for t in ["best", "top", "review", "vs", "compare", "alternative", "pricing", "hosting", "software", "tool"])
    is_if = any(t in kw for t in ["how to", "what is", "guide", "tutorial"])

    if is_tx:   vol, diff, cpc = 3200, 68, 4.80
    elif is_cm: vol, diff, cpc = 5800, 55, 3.20
    elif is_if: vol, diff, cpc = 9100, 42, 1.10
    else:       vol, diff, cpc = 2400, 35, 0.80

    features = []
    if vol > 5000:  features.extend(["featured_snippet", "people_also_ask", "top_stories"])
    if is_cm:      features.extend(["local_pack", "shopping_results"])
    if is_if:      features.append("video_carousel")

    seed = hash(keyword) % 100
    vol  = max(100, vol  + (seed - 50) * 20)
    diff = max(5, min(95, diff + (seed % 30) - 15))

    return {
        "keyword": keyword,
        "search_volume": vol,
        "difficulty": diff,
        "cpc": cpc,
        "competition": round(diff / 100, 2),
        "serp_features": features[:5],
        "estimated_ctr_position_1": 0.28,
        "estimated_ctr_position_3": 0.12,
        "estimated_ctr_position_10": 0.025,
        "source": "mock_dataforseo",
        "note": "DataForSEO API key required for live SERP data"
    }


# ─────────────────────────────────────────────────────────────────────────────
# HTTP scraping helper
# ─────────────────────────────────────────────────────────────────────────────

def _scrape_page(url: str) -> Dict[str, str]:
    """Return {title, content} from a URL, or empty dict on failure."""
    try:
        resp = httpx.get(
            url, timeout=8.0, follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AI-Marketing-Hub/1.0)"}
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        title = soup.title.string.strip() if soup.title else ""
        paragraphs = soup.find_all("p")
        content = " ".join(p.get_text(separator=" ").strip() for p in paragraphs)
        return {"title": title, "content": content}
    except Exception:
        return {"title": "", "content": ""}


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/data/status
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/data/status", response_model=DataConnectorStatus)
async def get_data_status(
    gsc_site_url: Optional[str] = None,
    gsc_creds_path: Optional[str] = None,
    ga4_property_id: Optional[str] = None,
    ga4_creds_path: Optional[str] = None,
    dfs_login: Optional[str] = None,
    dfs_password: Optional[str] = None,
):
    """Check live connection status for each data source."""
    gsc_s: Literal["connected", "disconnected"] = "disconnected"
    ga4_s: Literal["connected", "disconnected"] = "disconnected"
    dfs_s: Literal["connected", "disconnected"] = "pending"

    if gsc_site_url and gsc_creds_path:
        try:
            client = _gsc()(site_url=gsc_site_url, credentials_path=gsc_creds_path)
            client.get_keyword_positions(days=7, limit=1)
            gsc_s = "connected"
        except Exception:
            pass

    if ga4_property_id and ga4_creds_path:
        try:
            client = _ga4()(property_id=ga4_property_id, credentials_path=ga4_creds_path)
            client.get_top_pages(days=7, limit=1)
            ga4_s = "connected"
        except Exception:
            pass

    if dfs_login and dfs_password:
        try:
            client = _dfs()(login=dfs_login, password=dfs_password)
            client.get_serp_data("test keyword")
            dfs_s = "connected"
        except Exception:
            dfs_s = "disconnected"

    return DataConnectorStatus(
        gsc=gsc_s, ga4=ga4_s, dataforseo=dfs_s,
        last_checked=datetime.now().isoformat()
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/data/gsc-sync
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/data/gsc-sync")
async def sync_gsc_data(
    body: GscSyncRequest,
    days: int = Query(30, description="Days to look back in GSC")
):
    """
    Fetch GSC + GA4 data for a URL/keyword.
    Falls back to intelligent mock data when credentials are absent.
    """
    result: Dict[str, Any] = {
        "url": body.url, "keyword": body.keyword,
        "analyzed_at": datetime.now().isoformat(),
        "period_days": days, "source": "mock",
        "gsc": None, "ga4": None, "page_content": None,
    }

    # ── GSC ────────────────────────────────────────────────────────────────────
    if body.gsc_site_url and body.gsc_credentials_path:
        try:
            client = _gsc()(site_url=body.gsc_site_url, credentials_path=body.gsc_credentials_path)
            gsc_data = client.get_keyword_positions(days=days, limit=500)
            kw_lower = body.keyword.lower()
            matched = [
                r for r in gsc_data
                if kw_lower in r["keyword"].lower() or r["keyword"].lower() in kw_lower
            ]
            result["gsc"] = (matched[0] if matched else (gsc_data[0] if gsc_data else None))
            if result["gsc"]:
                result["gsc"]["source"] = "live_gsc"
                result["source"] = "live"
        except Exception as exc:
            result["gsc"] = {"error": str(exc), "source": "live_gsc"}
    else:
        result["gsc"] = _mock_gsc_data(body.keyword, body.url)

    # ── GA4 ──────────────────────────────────────────────────────────────────
    if body.ga4_property_id and body.ga4_credentials_path:
        try:
            client = _ga4()(property_id=body.ga4_property_id, credentials_path=body.ga4_credentials_path)
            result["ga4"] = client.get_page_performance(body.url, days=days)
            result["ga4"]["source"] = "live_ga4"
        except Exception:
            result["ga4"] = _mock_ga4_data(body.url)
    else:
        result["ga4"] = _mock_ga4_data(body.url)

    # ── Page content ─────────────────────────────────────────────────────────
    if result["gsc"] and result["gsc"].get("position"):
        result["page_content"] = await asyncio.to_thread(_scrape_page, body.url)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/data/serp-sync
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/data/serp-sync")
async def sync_serp_data(body: SerpSyncRequest):
    """
    Fetch SERP metrics for a keyword.
    Live DataForSEO when credentials provided; intent-based mock otherwise.
    """
    result: Dict[str, Any] = {
        "keyword": body.keyword,
        "location_code": body.location_code,
        "analyzed_at": datetime.now().isoformat(),
        "source": "mock",
    }

    login = body.dataforseo_login or os.getenv("DATAFORSEO_LOGIN")
    password = body.dataforseo_password or os.getenv("DATAFORSEO_PASSWORD")

    if login and password:
        try:
            client = _dfs()(login=login, password=password)
            serp = client.get_serp_data(body.keyword, location_code=body.location_code)
            kw_info = serp.get("keyword_data", {}).get("keyword_info", {})
            if kw_info:
                result["search_volume"] = kw_info.get("search_volume")
                result["difficulty"] = round((kw_info.get("competition") or 0) * 100)
                result["cpc"] = kw_info.get("cpc")
                result["competition"] = kw_info.get("competition")
                result["source"] = "live_dataforseo"
            if "features" in serp:
                result["serp_features"] = serp["features"]
        except Exception as exc:
            result["error"] = str(exc)
            result["note"] = "DataForSEO request failed — falling back to mock data"

    if result.get("source") == "mock" or result.get("search_volume") is None:
        mock = _mock_serp_data(body.keyword)
        for key in ["search_volume", "difficulty", "cpc", "competition",
                    "serp_features", "estimated_ctr_position_1",
                    "estimated_ctr_position_3", "estimated_ctr_position_10",
                    "source", "note"]:
            result.setdefault(key, mock.get(key))

    # Cross-reference search intent
    try:
        from core.search_intent_analyzer import SearchIntentAnalyzer
        analyzer = SearchIntentAnalyzer()
        serp_list: Optional[list] = result.get("serp_features")
        ir = analyzer.analyze(body.keyword, serp_list)
        result["search_intent"] = {
            "primary": ir["primary_intent"],
            "secondary": ir.get("secondary_intent", ""),
            "confidence": ir.get("confidence", {}),
            "content_recommendations": ir.get("content_recommendations", []),
        }
    except Exception:
        pass

    return result


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/data/bulk-sync
# ─────────────────────────────────────────────────────────────────────────────

class BulkDataRequest(BaseModel):
    url: str = Field(..., description="Target page URL")
    keyword: str = Field(..., description="Target keyword")
    gsc_site_url: Optional[str] = None
    gsc_credentials_path: Optional[str] = None
    ga4_property_id: Optional[str] = None
    ga4_credentials_path: Optional[str] = None
    dfs_login: Optional[str] = None
    dfs_password: Optional[str] = None
    days: int = Field(30, description="GSC lookback days")


@router.post("/data/bulk-sync")
async def bulk_data_sync(body: BulkDataRequest):
    """
    Run gsc-sync and serp-sync concurrently, merge into one unified payload.
    This is what the Auto-Fill button calls to pre-populate the Tracker form.
    """
    # Build partial request dicts so we can pass them as kwargs
    gsc_kwargs = dict(
        url=body.url, keyword=body.keyword,
        gsc_site_url=body.gsc_site_url,
        gsc_credentials_path=body.gsc_credentials_path,
        ga4_property_id=body.ga4_property_id,
        ga4_credentials_path=body.ga4_credentials_path,
    )
    serp_kwargs = dict(
        keyword=body.keyword,
        location_code=2840,
        dataforseo_login=body.dfs_login,
        dataforseo_password=body.dfs_password,
    )

    # Run both in parallel via asyncio.gather
    gsc_result, serp_result = await asyncio.gather(
        sync_gsc_data(GscSyncRequest(**gsc_kwargs), days=body.days),
        sync_serp_data(SerpSyncRequest(**serp_kwargs)),
    )

    unified: Dict[str, Any] = {
        "url": body.url,
        "keyword": body.keyword,
        "analyzed_at": datetime.now().isoformat(),
        "data_sources": {
            "gsc": gsc_result.get("source", "unknown"),
            "serp": serp_result.get("source", "unknown"),
        },
        "_raw_gsc": gsc_result,
        "_raw_serp": serp_result,
    }

    # Extract scalar metrics
    gsc = gsc_result.get("gsc") or {}
    if not gsc.get("error"):
        unified["current_position"]    = gsc.get("position")
        unified["monthly_clicks"]      = gsc.get("clicks")
        unified["monthly_impressions"] = gsc.get("impressions")
        unified["ctr"]                 = gsc.get("ctr")

    if serp_result.get("search_volume") is not None:
        unified["search_volume"] = serp_result["search_volume"]
    if serp_result.get("difficulty") is not None:
        unified["difficulty"] = serp_result["difficulty"]
    if serp_result.get("serp_features"):
        unified["serp_features"] = ",".join(serp_result["serp_features"])
    if serp_result.get("search_intent"):
        unified["search_intent"] = serp_result["search_intent"]["primary"]

    return unified
