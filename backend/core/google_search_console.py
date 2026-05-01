"""
Google Search Console Data Integration — Phase 20 (Rewritten)

Uses httpx + OAuth2 refresh tokens directly (no googleapiclient dependency).
Fetches search performance, keyword rankings, and SERP data.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import quote

import httpx


GSC_API = "https://www.googleapis.com/webmasters/v3"


class GoogleSearchConsole:
    """Google Search Console data fetcher using httpx + OAuth2."""

    def __init__(self, site_url: Optional[str] = None):
        self.site_url = site_url or os.getenv("GSC_SITE_URL", "")
        self._client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
        self._client_secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")
        self._refresh_token = os.getenv("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN", "")
        self._access_token: Optional[str] = None

        if not self.site_url:
            raise ValueError("GSC_SITE_URL must be set in environment")
        if not all([self._client_id, self._client_secret, self._refresh_token]):
            raise ValueError("GSC OAuth credentials not configured")

    async def _get_access_token(self) -> str:
        """Refresh the OAuth2 access token."""
        if self._access_token:
            return self._access_token

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "refresh_token": self._refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            data = resp.json()
            if "access_token" not in data:
                raise ValueError(f"GSC token refresh failed: {data.get('error_description', data)}")
            self._access_token = data["access_token"]
            return self._access_token

    async def _query(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Search Analytics query."""
        token = await self._get_access_token()
        encoded = quote(self.site_url, safe="")
        url = f"{GSC_API}/sites/{encoded}/searchAnalytics/query"

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=body,
            )
            if resp.status_code == 401:
                self._access_token = None
                token = await self._get_access_token()
                resp = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json=body,
                )
            if resp.status_code != 200:
                return {"error": f"GSC API error {resp.status_code}: {resp.text[:200]}"}
            return resp.json()

    async def get_keyword_positions(self, days: int = 28, limit: int = 100) -> List[Dict[str, Any]]:
        """Get keyword rankings and performance."""
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        end = datetime.now().strftime("%Y-%m-%d")

        response = await self._query({
            "startDate": start,
            "endDate": end,
            "dimensions": ["query"],
            "rowLimit": limit,
        })

        if "error" in response:
            return []

        results = []
        for row in response.get("rows", []):
            results.append({
                "keyword": row["keys"][0],
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
            })

        results.sort(key=lambda x: x["impressions"], reverse=True)
        return results

    async def get_quick_wins(
        self,
        days: int = 28,
        position_min: int = 11,
        position_max: int = 20,
        min_impressions: int = 5,
    ) -> List[Dict[str, Any]]:
        """Find keywords ranking 11-20 (close to page 1)."""
        all_kw = await self.get_keyword_positions(days=days, limit=500)

        quick_wins = []
        for kw in all_kw:
            if position_min <= kw["position"] <= position_max and kw["impressions"] >= min_impressions:
                distance = kw["position"] - 10
                score = kw["impressions"] / max(distance, 0.5)
                intent = self._commercial_intent(kw["keyword"])
                quick_wins.append({
                    **kw,
                    "commercial_intent": intent,
                    "opportunity_score": round(score * intent, 2),
                    "priority": "high" if kw["position"] <= 15 else "medium",
                })

        quick_wins.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return quick_wins

    async def get_page_performance(self, page_url: str, days: int = 28) -> Dict[str, Any]:
        """Get search performance for a specific page."""
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        end = datetime.now().strftime("%Y-%m-%d")

        response = await self._query({
            "startDate": start,
            "endDate": end,
            "dimensions": ["page"],
            "dimensionFilterGroups": [{
                "filters": [{"dimension": "page", "operator": "contains", "expression": page_url}]
            }],
        })

        if "error" in response or not response.get("rows"):
            return {"url": page_url, "error": "No data found"}

        row = response["rows"][0]
        return {
            "url": row["keys"][0],
            "clicks": row["clicks"],
            "impressions": row["impressions"],
            "ctr": round(row["ctr"] * 100, 2),
            "avg_position": round(row["position"], 1),
        }

    async def get_trending_queries(self, days_recent: int = 7, days_total: int = 28) -> List[Dict[str, Any]]:
        """Find queries gaining traction."""
        recent = await self.get_keyword_positions(days=days_recent, limit=500)
        previous = await self.get_keyword_positions(days=days_total, limit=500)

        prev_lookup = {kw["keyword"]: kw["impressions"] for kw in previous}
        trending = []

        for kw in recent:
            prev_impr = prev_lookup.get(kw["keyword"], 0)
            if prev_impr > 0:
                change = ((kw["impressions"] - prev_impr) / prev_impr) * 100
            else:
                change = 100.0

            if change > 20:
                trending.append({
                    **kw,
                    "previous_impressions": prev_impr,
                    "change_percent": round(change, 1),
                })

        trending.sort(key=lambda x: x["change_percent"], reverse=True)
        return trending

    @staticmethod
    def _commercial_intent(keyword: str) -> float:
        """Score commercial intent (0.1–3.0)."""
        kw = keyword.lower()
        high = ["giá", "mua", "bán", "trả góp", "đại lý", "pricing", "buy", "price", "cost", "review"]
        mid = ["so sánh", "tốt nhất", "đánh giá", "compare", "best", "vs", "alternative"]
        for t in high:
            if t in kw:
                return 3.0
        for t in mid:
            if t in kw:
                return 2.0
        return 0.5


# ── Standalone helper for quick access without class ──────────────────────────


async def fetch_gsc_keywords(days: int = 28, limit: int = 50) -> Dict[str, Any]:
    """Quick helper — fetch GSC keyword data. Returns real data or error."""
    try:
        gsc = GoogleSearchConsole()
        keywords = await gsc.get_keyword_positions(days=days, limit=limit)
        return {
            "source": "gsc_real",
            "site_url": gsc.site_url,
            "keywords": keywords,
            "total": len(keywords),
            "period_days": days,
        }
    except Exception as e:
        return {"source": "gsc_error", "error": str(e), "keywords": []}
