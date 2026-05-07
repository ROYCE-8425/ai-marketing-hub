"""
SERP Scraper — Google-first via DataForSEO

Strategy:
1. DataForSEO API (if configured) — returns real Google SERP data
2. Error state with clear message when credentials are missing (no fallback)

All searches are async-safe and never hang.
Google-only architecture — no third-party search engine fallback.
"""

import asyncio
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


LOCATION_MAP = {
    "vn": {"location_code": 2704, "language_code": "vi", "label": "Việt Nam"},
    "us": {"location_code": 2840, "language_code": "en", "label": "Hoa Kỳ"},
    "uk": {"location_code": 2826, "language_code": "en", "label": "Anh"},
    "au": {"location_code": 2036, "language_code": "en", "label": "Úc"},
    "in": {"location_code": 2356, "language_code": "en", "label": "Ấn Độ"},
    "sg": {"location_code": 2702, "language_code": "en", "label": "Singapore"},
    "jp": {"location_code": 2392, "language_code": "ja", "label": "Nhật Bản"},
}


def _try_dataforseo(keyword: str, location_code: int, language_code: str, limit: int) -> Optional[Dict[str, Any]]:
    """
    Attempt to use DataForSEO to get real Google SERP data.
    Returns None if credentials are missing.
    Raises on API errors.
    """
    login = os.getenv("DATAFORSEO_LOGIN")
    password = os.getenv("DATAFORSEO_PASSWORD")
    if not login or not password:
        return None

    from core.dataforseo import DataForSEO
    client = DataForSEO(login=login, password=password)
    serp = client.get_serp_data(keyword, location_code=location_code, limit=limit)

    if "error" in serp:
        raise RuntimeError(serp["error"])

    return serp


class GoogleSerpScraper:
    """Google SERP scraper via DataForSEO API (real Google data)."""

    async def search(self, keyword: str, location: str = "vn", num_results: int = 10) -> Dict[str, Any]:
        loc = LOCATION_MAP.get(location.lower(), LOCATION_MAP["vn"])
        location_code = loc["location_code"]
        language_code = loc["language_code"]
        num = max(5, min(20, num_results))

        # Try DataForSEO (real Google SERP)
        try:
            raw = await asyncio.wait_for(
                asyncio.to_thread(_try_dataforseo, keyword, location_code, language_code, num),
                timeout=20.0,
            )
            if raw is None:
                # No credentials configured
                return {
                    "keyword": keyword,
                    "location": loc.get("label", ""),
                    "organic_results": [],
                    "serp_features": [],
                    "total_results": 0,
                    "results_count": 0,
                    "source": "missing_credentials",
                    "error": "Cần cấu hình DataForSEO API để lấy Google SERP. "
                             "Set DATAFORSEO_LOGIN và DATAFORSEO_PASSWORD trong backend/.env. "
                             "Đăng ký tại https://dataforseo.com",
                }

            # Format DataForSEO response to standard format
            return self._format_dataforseo(raw, keyword, loc)

        except RuntimeError as exc:
            return {
                "keyword": keyword,
                "location": loc.get("label", ""),
                "organic_results": [],
                "serp_features": [],
                "total_results": 0,
                "results_count": 0,
                "source": "api_error",
                "error": f"DataForSEO API lỗi: {str(exc)[:200]}",
            }
        except Exception as exc:
            return {
                "keyword": keyword,
                "location": loc.get("label", ""),
                "organic_results": [],
                "serp_features": [],
                "total_results": 0,
                "results_count": 0,
                "source": "error",
                "error": f"Không thể kết nối DataForSEO. Kiểm tra credentials và kết nối mạng. ({str(exc)[:100]})",
            }

    def _format_dataforseo(self, raw: Dict[str, Any], keyword: str, loc: Dict) -> Dict[str, Any]:
        """Format DataForSEO response to our standard SERP format."""
        organic = []
        for item in raw.get("organic_results", []):
            url = item.get("url", "")
            title = item.get("title", "")
            if not url or not title:
                continue
            try:
                domain = urlparse(url).netloc.replace("www.", "")
            except Exception:
                domain = ""
            organic.append({
                "position": item.get("position") or item.get("rank_absolute", len(organic) + 1),
                "title": title,
                "url": url,
                "domain": domain,
                "snippet": item.get("description", "") or item.get("snippet", ""),
                "breadcrumb": item.get("breadcrumb", ""),
            })

        return {
            "keyword": keyword,
            "location": loc.get("label", ""),
            "organic_results": organic,
            "serp_features": raw.get("features", []),
            "total_results": raw.get("total_results", len(organic)),
            "results_count": len(organic),
            "source": "google_live",
            "search_volume": raw.get("search_volume"),
            "cpc": raw.get("cpc"),
            "competition": raw.get("competition"),
        }


async def scrape_google_serp(keyword: str, location: str = "vn", num_results: int = 10) -> Dict[str, Any]:
    return await GoogleSerpScraper().search(keyword, location, num_results)
