"""
GA4 Data Fetcher — REST API + OAuth2 (no SDK required)

Fetches real Google Analytics 4 data:
- Site overview: sessions, users, pageviews, bounce rate, engagement
- Traffic sources breakdown
- Top pages by pageviews
- Daily sessions timeline

Uses the same OAuth2 credentials (Client ID/Secret/Refresh Token) as GSC.
"""

import os
import httpx
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

GA4_API_URL = "https://analyticsdata.googleapis.com/v1beta"


async def _get_access_token_async() -> Optional[str]:
    """Get OAuth2 access token using the same credentials as GSC."""
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), override=True)
    client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")
    refresh = os.getenv("GA4_REFRESH_TOKEN", "") or os.getenv("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN", "")

    if not all([client_id, secret, refresh]):
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post("https://oauth2.googleapis.com/token", data={
                "client_id": client_id,
                "client_secret": secret,
                "refresh_token": refresh,
                "grant_type": "refresh_token",
            })
            return resp.json().get("access_token")
    except Exception:
        return None


async def _run_report_async(property_id: str, access_token: str, body: Dict) -> Dict:
    """Execute a GA4 Data API runReport request (async)."""
    url = f"{GA4_API_URL}/properties/{property_id}:runReport"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }, json=body)
            if resp.status_code != 200:
                raise ValueError(f"GA4 API error {resp.status_code}: {resp.text[:300]}")
            return resp.json()
    except httpx.TimeoutException:
        raise ValueError("GA4 API timeout")


async def get_ga4_overview(days: int = 30) -> Dict[str, Any]:
    """
    Fetch GA4 site overview: sessions, users, pageviews, engagement.
    Returns mock data if GA4 is not configured.
    """
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), override=True)
    property_id = os.getenv("GA4_PROPERTY_ID", "")
    result: Dict[str, Any] = {
        "fetched_at": datetime.now().isoformat(),
        "period_days": days,
        "data_source": "mock",
        "property_id": property_id,
        "overview": {},
        "traffic_sources": [],
        "top_pages": [],
        "daily_sessions": [],
    }

    if not property_id:
        result["error"] = "GA4_PROPERTY_ID chưa được cấu hình. Vào Google Analytics → Admin → Property Details để lấy Property ID."
        result["overview"] = _mock_overview()
        result["traffic_sources"] = _mock_traffic_sources()
        result["top_pages"] = _mock_top_pages()
        result["daily_sessions"] = _mock_daily_sessions(days)
        return result

    access_token = await _get_access_token_async()
    if not access_token:
        result["error"] = "Không lấy được access token. Kiểm tra OAuth2 credentials."
        result["overview"] = _mock_overview()
        result["traffic_sources"] = _mock_traffic_sources()
        result["top_pages"] = _mock_top_pages()
        result["daily_sessions"] = _mock_daily_sessions(days)
        return result

    errors = []

    # 1. Overview metrics
    try:
        resp = await _run_report_async(property_id, access_token, {
            "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
            "metrics": [
                {"name": "sessions"},
                {"name": "activeUsers"},
                {"name": "screenPageViews"},
                {"name": "bounceRate"},
                {"name": "engagementRate"},
                {"name": "averageSessionDuration"},
                {"name": "newUsers"},
            ],
        })
        rows = resp.get("rows", [])
        if rows:
            mv = rows[0].get("metricValues", [])
            result["overview"] = {
                "sessions": int(mv[0]["value"]) if len(mv) > 0 else 0,
                "active_users": int(mv[1]["value"]) if len(mv) > 1 else 0,
                "pageviews": int(mv[2]["value"]) if len(mv) > 2 else 0,
                "bounce_rate": round(float(mv[3]["value"]) * 100, 1) if len(mv) > 3 else 0,
                "engagement_rate": round(float(mv[4]["value"]) * 100, 1) if len(mv) > 4 else 0,
                "avg_session_duration": round(float(mv[5]["value"]), 1) if len(mv) > 5 else 0,
                "new_users": int(mv[6]["value"]) if len(mv) > 6 else 0,
            }
        else:
            # New property with no data yet
            result["overview"] = {
                "sessions": 0, "active_users": 0, "pageviews": 0,
                "bounce_rate": 0, "engagement_rate": 0,
                "avg_session_duration": 0, "new_users": 0,
            }
            result["note"] = "Property mới, chưa có dữ liệu. Cài Google Tag G-DFEE14V0T8 vào website để bắt đầu thu thập."
        result["data_source"] = "live_ga4"
    except Exception as e:
        errors.append(f"Overview: {e}")
        result["overview"] = _mock_overview()

    # 2. Traffic sources
    try:
        resp = await _run_report_async(property_id, access_token, {
            "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "sessionDefaultChannelGroup"}],
            "metrics": [
                {"name": "sessions"},
                {"name": "activeUsers"},
                {"name": "engagementRate"},
            ],
            "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
            "limit": 10,
        })
        sources = []
        for row in resp.get("rows", []):
            dv = row.get("dimensionValues", [])
            mv = row.get("metricValues", [])
            sources.append({
                "source": dv[0]["value"] if dv else "Unknown",
                "sessions": int(mv[0]["value"]) if len(mv) > 0 else 0,
                "users": int(mv[1]["value"]) if len(mv) > 1 else 0,
                "engagement_rate": round(float(mv[2]["value"]) * 100, 1) if len(mv) > 2 else 0,
            })
        result["traffic_sources"] = sources
    except Exception as e:
        errors.append(f"Traffic: {e}")
        result["traffic_sources"] = _mock_traffic_sources()

    # 3. Top pages
    try:
        resp = await _run_report_async(property_id, access_token, {
            "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "pagePath"}, {"name": "pageTitle"}],
            "metrics": [
                {"name": "screenPageViews"},
                {"name": "sessions"},
                {"name": "bounceRate"},
                {"name": "averageSessionDuration"},
            ],
            "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
            "limit": 15,
        })
        pages = []
        for row in resp.get("rows", []):
            dv = row.get("dimensionValues", [])
            mv = row.get("metricValues", [])
            pages.append({
                "path": dv[0]["value"] if len(dv) > 0 else "/",
                "title": dv[1]["value"] if len(dv) > 1 else "",
                "pageviews": int(mv[0]["value"]) if len(mv) > 0 else 0,
                "sessions": int(mv[1]["value"]) if len(mv) > 1 else 0,
                "bounce_rate": round(float(mv[2]["value"]) * 100, 1) if len(mv) > 2 else 0,
                "avg_duration": round(float(mv[3]["value"]), 1) if len(mv) > 3 else 0,
            })
        result["top_pages"] = pages
    except Exception as e:
        errors.append(f"Pages: {e}")
        result["top_pages"] = _mock_top_pages()

    # 4. Daily sessions timeline
    try:
        resp = await _run_report_async(property_id, access_token, {
            "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "date"}],
            "metrics": [
                {"name": "sessions"},
                {"name": "screenPageViews"},
                {"name": "activeUsers"},
            ],
            "orderBys": [{"dimension": {"dimensionName": "date"}, "desc": False}],
        })
        timeline = []
        for row in resp.get("rows", []):
            dv = row.get("dimensionValues", [])
            mv = row.get("metricValues", [])
            date_str = dv[0]["value"] if dv else ""
            # Format: 20260423 → 23/04
            formatted = f"{date_str[6:8]}/{date_str[4:6]}" if len(date_str) == 8 else date_str
            timeline.append({
                "date": formatted,
                "sessions": int(mv[0]["value"]) if len(mv) > 0 else 0,
                "pageviews": int(mv[1]["value"]) if len(mv) > 1 else 0,
                "users": int(mv[2]["value"]) if len(mv) > 2 else 0,
            })
        result["daily_sessions"] = timeline
    except Exception as e:
        errors.append(f"Timeline: {e}")
        result["daily_sessions"] = _mock_daily_sessions(days)

    if errors:
        result["errors"] = errors

    return result


# ── Mock data (when GA4 is not configured) ───────────────────────────────────

def _mock_overview() -> Dict[str, Any]:
    return {
        "sessions": 1247,
        "active_users": 892,
        "pageviews": 3421,
        "bounce_rate": 42.3,
        "engagement_rate": 57.7,
        "avg_session_duration": 124.5,
        "new_users": 645,
    }

def _mock_traffic_sources() -> List[Dict[str, Any]]:
    return [
        {"source": "Organic Search", "sessions": 523, "users": 412, "engagement_rate": 62.1},
        {"source": "Direct", "sessions": 312, "users": 245, "engagement_rate": 55.3},
        {"source": "Social", "sessions": 198, "users": 167, "engagement_rate": 48.2},
        {"source": "Referral", "sessions": 134, "users": 98, "engagement_rate": 71.5},
        {"source": "Email", "sessions": 80, "users": 65, "engagement_rate": 68.9},
    ]

def _mock_top_pages() -> List[Dict[str, Any]]:
    return [
        {"path": "/", "title": "Trang chủ", "pageviews": 1245, "sessions": 980, "bounce_rate": 35.2, "avg_duration": 95.3},
        {"path": "/xe-mitsubishi/", "title": "Xe Mitsubishi", "pageviews": 567, "sessions": 423, "bounce_rate": 38.7, "avg_duration": 142.1},
        {"path": "/bang-gia/", "title": "Bảng giá", "pageviews": 432, "sessions": 345, "bounce_rate": 28.4, "avg_duration": 186.5},
        {"path": "/lien-he/", "title": "Liên hệ", "pageviews": 298, "sessions": 234, "bounce_rate": 45.1, "avg_duration": 67.8},
        {"path": "/xpander/", "title": "Mitsubishi Xpander", "pageviews": 245, "sessions": 198, "bounce_rate": 32.6, "avg_duration": 210.4},
    ]

def _mock_daily_sessions(days: int) -> List[Dict[str, Any]]:
    import random
    random.seed(42)
    result = []
    base = datetime.now().date() - timedelta(days=days)
    for i in range(days):
        d = base + timedelta(days=i)
        weekday_boost = 1.3 if d.weekday() < 5 else 0.7
        sessions = int(random.gauss(40, 12) * weekday_boost)
        result.append({
            "date": d.strftime("%d/%m"),
            "sessions": max(5, sessions),
            "pageviews": max(8, int(sessions * random.uniform(2.2, 3.5))),
            "users": max(3, int(sessions * random.uniform(0.65, 0.85))),
        })
    return result
