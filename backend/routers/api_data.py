"""
API Data Router — Phase 6

Provides live data connectors:
- GET  /api/data/status    — Check connection status per data source
- POST /api/data/gsc-sync  — Fetch real GSC + GA4 metrics for a URL/keyword
- POST /api/data/serp-sync — Fetch SERP data (DataForSEO or error)
- POST /api/data/bulk-sync — Run all connectors in parallel → unified payload
"""

from __future__ import annotations

import asyncio
import os
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Any, Dict, Literal, Optional
from dotenv import load_dotenv

# Load .env from backend root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

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
    url: str = Field("https://binhphuocmitsubishi.com", description="Full URL of the page to analyze")
    keyword: str = Field("mitsubishi bình phước", description="Target keyword to track")
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
# POST /api/config/gsc — Save GSC credentials to .env from UI
# ─────────────────────────────────────────────────────────────────────────────

class GscConfigRequest(BaseModel):
    client_id: str
    client_secret: str
    refresh_token: str
    site_url: str

@router.post("/config/gsc")
async def save_gsc_config(body: GscConfigRequest):
    """Save GSC credentials to backend .env file (preserving other vars) and reload."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

    # Keys we will upsert
    updates = {
        "GOOGLE_SEARCH_CONSOLE_CLIENT_ID": body.client_id,
        "GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET": body.client_secret,
        "GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN": body.refresh_token,
        "GSC_SITE_URL": body.site_url,
    }

    # Read existing lines (preserving order and non-GSC vars)
    existing_lines: list[str] = []
    seen_keys: set[str] = set()
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                stripped = line.strip()
                if "=" in stripped and not stripped.startswith("#"):
                    key = stripped.split("=", 1)[0]
                    if key in updates:
                        existing_lines.append(f"{key}={updates[key]}\n")
                        seen_keys.add(key)
                    else:
                        existing_lines.append(line if line.endswith("\n") else line + "\n")
                else:
                    existing_lines.append(line if line.endswith("\n") else line + "\n")

    # Append any keys that were not already in the file
    for key, val in updates.items():
        if key not in seen_keys:
            existing_lines.append(f"{key}={val}\n")

    with open(env_path, "w") as f:
        f.writelines(existing_lines)

    # Reload env vars in current process
    load_dotenv(env_path, override=True)
    return {"status": "ok", "message": "GSC credentials saved"}


# ─────────────────────────────────────────────────────────────────────────────
# OAuth2 flow — Get a refresh token with GSC + GA4 scopes unified
# ─────────────────────────────────────────────────────────────────────────────

OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/analytics.readonly",
]

@router.get("/oauth/authorize")
async def oauth_authorize():
    """Generate OAuth2 authorization URL to get GSC+GA4 scopes."""
    client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    if not client_id:
        return {"error": "GOOGLE_SEARCH_CONSOLE_CLIENT_ID not set in .env"}
    
    import urllib.parse
    params = {
        "client_id": client_id,
        "redirect_uri": "http://localhost:8000/api/oauth/callback",
        "response_type": "code",
        "scope": " ".join(OAUTH_SCOPES),
        "access_type": "offline",
        "prompt": "consent",  # Force consent to get new refresh token
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return {"authorize_url": url, "scopes": OAUTH_SCOPES}


@router.get("/oauth/callback")
async def oauth_callback(code: str = Query(None), error: str = Query(None)):
    """Exchange OAuth2 code for refresh token, save to .env, return HTML."""
    if error:
        return {"error": error}
    if not code:
        return {"error": "No authorization code received"}
    
    client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")
    
    # Exchange code for tokens
    token_resp = httpx.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "http://localhost:8000/api/oauth/callback",
        "grant_type": "authorization_code",
    }, timeout=10.0)
    token_data = token_resp.json()
    
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        return {"error": "No refresh_token in response", "details": token_data}
    
    # Save to .env — update or append REFRESH_TOKEN
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    env_lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN="):
                    env_lines.append(f"GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN={refresh_token}\n")
                    found = True
                else:
                    env_lines.append(line)
    if not found:
        env_lines.append(f"GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN={refresh_token}\n")
    with open(env_path, "w") as f:
        f.writelines(env_lines)
    load_dotenv(env_path, override=True)
    
    # Return a simple HTML page
    from fastapi.responses import HTMLResponse
    return HTMLResponse(f"""
    <html><head><title>OAuth Success</title></head>
    <body style="font-family:system-ui;background:#0f172a;color:#e2e8f0;display:flex;justify-content:center;align-items:center;height:100vh">
    <div style="text-align:center;max-width:500px">
        <h1 style="color:#6ee7b7">✅ Đã kết nối thành công!</h1>
        <p>Refresh token đã được lưu vào .env với cả GSC + GA4 scope.</p>
        <p style="color:#a5b4fc">Token: {refresh_token[:20]}...{refresh_token[-10:]}</p>
        <p>Quay lại Dashboard để xem dữ liệu GA4 thật.</p>
        <a href="http://localhost:5173/" style="color:#c4b5fd;text-decoration:underline">← Quay về Dashboard</a>
    </div>
    </body></html>
    """)

# ─────────────────────────────────────────────────────────────────────────────
# POST /api/ai-keywords — AI-powered keyword analysis using GSC data + Z.AI
# ─────────────────────────────────────────────────────────────────────────────

class AiKeywordsRequest(BaseModel):
    target_keyword: Optional[str] = None

@router.post("/ai-keywords")
async def ai_keyword_analysis(body: AiKeywordsRequest):
    """Fetch GSC keywords and analyze with AI to recommend new keyword opportunities."""
    import asyncio
    from core.ai_keyword_analyzer import analyze_keywords_with_ai
    result = await asyncio.to_thread(analyze_keywords_with_ai, body.target_keyword)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/ga4-overview — GA4 analytics overview (sessions, traffic, pages)
# ─────────────────────────────────────────────────────────────────────────────

class Ga4OverviewRequest(BaseModel):
    days: int = Field(30, description="Number of days to look back")

@router.post("/ga4-overview")
async def ga4_overview(body: Ga4OverviewRequest = None):
    """Fetch GA4 site overview: sessions, users, traffic sources, top pages, daily timeline."""
    from core.ga4_fetcher import get_ga4_overview
    days = body.days if body else 30
    result = await get_ga4_overview(days)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/config/ga4 — Save GA4 Property ID to .env
# ─────────────────────────────────────────────────────────────────────────────

class Ga4ConfigRequest(BaseModel):
    property_id: str

@router.post("/config/ga4")
async def save_ga4_config(body: Ga4ConfigRequest):
    """Save GA4 Property ID to .env."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    # Read existing .env, update or add GA4_PROPERTY_ID
    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GA4_PROPERTY_ID="):
                    lines.append(f"GA4_PROPERTY_ID={body.property_id}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"GA4_PROPERTY_ID={body.property_id}\n")
    with open(env_path, "w") as f:
        f.writelines(lines)
    load_dotenv(env_path, override=True)
    return {"status": "ok", "message": f"GA4 Property ID saved: {body.property_id}"}


# Error response helpers (no synthetic data)
# ─────────────────────────────────────────────────────────────────────────────


def _error_gsc(keyword: str, note: str) -> Dict[str, Any]:
    """Return an error result for GSC (no synthetic metrics)."""
    return {
        "keyword": keyword,
        "source": "error",
        "error": note,
    }


def _error_ga4(url: str, note: str) -> Dict[str, Any]:
    return {
        "url": url,
        "source": "error",
        "error": note,
    }


def _error_serp(keyword: str, note: str) -> Dict[str, Any]:
    return {
        "keyword": keyword,
        "source": "missing_credentials",
        "error": note,
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
    Returns error state when credentials are absent (no synthetic data).
    """
    result: Dict[str, Any] = {
        "url": body.url, "keyword": body.keyword,
        "analyzed_at": datetime.now().isoformat(),
        "period_days": days, "source": "pending",
        "gsc": None, "ga4": None, "page_content": None,
    }

    # ── GSC — try .env credentials first, then request body ────────────────
    gsc_client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    gsc_secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")
    gsc_refresh = os.getenv("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN", "")
    gsc_site = body.gsc_site_url or os.getenv("GSC_SITE_URL", "")

    gsc_connected = bool(gsc_client_id and gsc_secret and gsc_refresh and gsc_site)

    if gsc_connected:
        try:
            # Get a fresh access token using the refresh token
            token_resp = httpx.post("https://oauth2.googleapis.com/token", data={
                "client_id": gsc_client_id,
                "client_secret": gsc_secret,
                "refresh_token": gsc_refresh,
                "grant_type": "refresh_token",
            }, timeout=10.0)
            token_data = token_resp.json()
            access_token = token_data.get("access_token", "")

            if access_token:
                # Query GSC API directly
                api_url = "https://www.googleapis.com/webmasters/v3/sites/{}/searchAnalytics/query".format(
                    httpx.URL(gsc_site).raw_path.decode() if hasattr(httpx.URL(gsc_site).raw_path, 'decode') else gsc_site.rstrip('/')
                )
                # Use encoded site URL
                import urllib.parse
                encoded_site = urllib.parse.quote(gsc_site, safe="")
                api_url = f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site}/searchAnalytics/query"

                from datetime import timedelta
                end_date = datetime.now().date() - timedelta(days=3)
                start_date = end_date - timedelta(days=days)

                gsc_resp = httpx.post(api_url, headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }, json={
                    "startDate": start_date.isoformat(),
                    "endDate": end_date.isoformat(),
                    "dimensions": ["query"],
                    "rowLimit": 500,
                }, timeout=15.0)

                if gsc_resp.status_code == 200:
                    rows = gsc_resp.json().get("rows", [])
                    kw_lower = body.keyword.lower()

                    # Find matching keyword
                    matched = [
                        r for r in rows
                        if kw_lower in r["keys"][0].lower() or r["keys"][0].lower() in kw_lower
                    ]
                    row = matched[0] if matched else (rows[0] if rows else None)

                    if row:
                        result["gsc"] = {
                            "keyword": row["keys"][0],
                            "clicks": int(row["clicks"]),
                            "impressions": int(row["impressions"]),
                            "ctr": round(row["ctr"], 4),
                            "position": round(row["position"], 1),
                            "source": "live_gsc",
                        }
                        result["source"] = "live"
                    else:
                        result["gsc"] = _error_gsc(body.keyword, f"Không tìm thấy từ khóa '{body.keyword}' trong GSC.")
                else:
                    result["gsc"] = _error_gsc(body.keyword, f"GSC API lỗi {gsc_resp.status_code}.")
            else:
                result["gsc"] = _error_gsc(body.keyword, "Không lấy được access token. Refresh token có thể hết hạn.")
        except Exception as exc:
            result["gsc"] = _error_gsc(body.keyword, f"GSC error: {str(exc)[:100]}")
    elif body.gsc_site_url and body.gsc_credentials_path:
        # Legacy path: credentials file
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
            result["gsc"] = _error_gsc(body.keyword, f"GSC legacy error: {str(exc)[:100]}")
    else:
        result["gsc"] = _error_gsc(body.keyword, "GSC chưa được cấu hình. Cần OAuth2 credentials.")

    # ── GA4 — try .env config first, then request body credentials ────────
    env_ga4_property = os.getenv("GA4_PROPERTY_ID", "")
    ga4_prop = body.ga4_property_id or env_ga4_property

    if ga4_prop and body.ga4_credentials_path:
        # Legacy path: credential file from client
        try:
            client = _ga4()(property_id=ga4_prop, credentials_path=body.ga4_credentials_path)
            result["ga4"] = client.get_page_performance(body.url, days=days)
            result["ga4"]["source"] = "live_ga4"
        except Exception as exc:
            result["ga4"] = _error_ga4(body.url, f"GA4 error: {str(exc)[:100]}")
    elif ga4_prop:
        # .env OAuth path — use same refresh token as GSC
        try:
            from core.ga4_fetcher import get_ga4_overview
            overview = await get_ga4_overview(days)
            if overview.get("data_source") in ("live_ga4", "partial_live_ga4"):
                result["ga4"] = {"url": body.url, "source": "live_ga4", **{k: v for k, v in overview.items() if k != "property_id"}}
            else:
                result["ga4"] = _error_ga4(body.url, overview.get("error") or "GA4 không lấy được dữ liệu.")
        except Exception as exc:
            result["ga4"] = _error_ga4(body.url, f"GA4 error: {str(exc)[:100]}")
    else:
        result["ga4"] = _error_ga4(body.url, "GA4_PROPERTY_ID chưa được cấu hình.")

    # ── Page content ─────────────────────────────────────────────────────────
    if result["gsc"] and result["gsc"].get("position"):
        result["page_content"] = await asyncio.to_thread(_scrape_page, body.url)

    # Ensure source is never returned as sentinel value
    if result.get("source") == "pending":
        result["source"] = "error"

    return result


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/data/serp-sync
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/data/serp-sync")
async def sync_serp_data(body: SerpSyncRequest):
    """
    Fetch SERP metrics for a keyword.
    Live DataForSEO when credentials provided; error state otherwise.
    """
    result: Dict[str, Any] = {
        "keyword": body.keyword,
        "location_code": body.location_code,
        "analyzed_at": datetime.now().isoformat(),
        "source": "pending",
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
            result["source"] = "api_error"
            result["note"] = "DataForSEO request failed. Check credentials and try again."

    if result.get("source") == "pending":
        result["source"] = "missing_credentials"
        result["error"] = result.get("error") or "DataForSEO API key chưa được cấu hình. Set DATAFORSEO_LOGIN và DATAFORSEO_PASSWORD trong .env."

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
