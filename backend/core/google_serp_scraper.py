"""
SERP Scraper — Multi-source Google SERP

Strategy (waterfall):
1. DataForSEO API (if configured) — real Google organic SERP + SEO metrics
2. SerpAPI (if configured) — real Google SERP, 100 free/month (with 1h cache)
3. Google Custom Search JSON API (if configured) — Programmable Search
4. Error state with clear message when no credentials configured

All searches are async-safe and never hang.
SERP results are cached in-memory for 1 hour to save quota.
"""

import asyncio
import os
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


# ─── In-memory SERP cache (TTL = 1 hour) ──────────────────────────────────────
_serp_cache: Dict[str, Dict[str, Any]] = {}
_CACHE_TTL = 3600  # 1 hour


def _cache_key(keyword: str, location: str, num: int) -> str:
    return f"{keyword.lower().strip()}|{location.lower()}|{num}"


def _get_cached(keyword: str, location: str, num: int) -> Optional[Dict[str, Any]]:
    key = _cache_key(keyword, location, num)
    entry = _serp_cache.get(key)
    if entry and (time.time() - entry["_ts"]) < _CACHE_TTL:
        result = {k: v for k, v in entry.items() if k != "_ts"}
        result["_cached"] = True
        return result
    if entry:
        del _serp_cache[key]
    return None


def _set_cache(keyword: str, location: str, num: int, data: Dict[str, Any]):
    key = _cache_key(keyword, location, num)
    _serp_cache[key] = {**data, "_ts": time.time()}
    # Evict old entries if cache grows too large
    if len(_serp_cache) > 200:
        oldest = min(_serp_cache, key=lambda k: _serp_cache[k]["_ts"])
        del _serp_cache[oldest]


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


def _try_serpapi(keyword: str, location: str, num_results: int) -> Optional[Dict[str, Any]]:
    """
    Attempt to use SerpAPI to get real Google SERP data.
    Returns None if API key is missing.
    """
    from core.serpapi_search import search_serpapi
    return search_serpapi(keyword, location=location, num_results=num_results)


def _try_google_custom_search(keyword: str, location: str, num_results: int) -> Optional[Dict[str, Any]]:
    """
    Attempt to use Google Custom Search JSON API.
    Returns None if credentials are missing.
    """
    from core.google_custom_search import search_google_cse
    return search_google_cse(keyword, location=location, num_results=num_results)


class GoogleSerpScraper:
    """
    Multi-source Google SERP scraper.

    Priority:
    1. DataForSEO (premium, real Google organic SERP + SEO metrics)
    2. SerpAPI (real Google SERP, 100 free searches/month)
    3. Google Custom Search JSON API (Programmable Search)
    4. Error state (no credentials)
    """

    async def search(self, keyword: str, location: str = "vn", num_results: int = 10) -> Dict[str, Any]:
        loc = LOCATION_MAP.get(location.lower(), LOCATION_MAP["vn"])
        location_code = loc["location_code"]
        language_code = loc["language_code"]
        num = max(5, min(20, num_results))

        # ── Check cache first (saves SerpAPI quota) ──
        cached = _get_cached(keyword, location, num)
        if cached:
            return cached

        # ── Strategy 1: DataForSEO (premium, real Google SERP) ──
        try:
            raw = await asyncio.wait_for(
                asyncio.to_thread(_try_dataforseo, keyword, location_code, language_code, num),
                timeout=20.0,
            )
            if raw is not None:
                result = self._format_dataforseo(raw, keyword, loc)
                _set_cache(keyword, location, num, result)
                return result
        except RuntimeError:
            pass
        except Exception:
            pass

        # ── Strategy 2: SerpAPI (real Google SERP, free 100/month) ──
        try:
            serpapi_result = await asyncio.wait_for(
                asyncio.to_thread(_try_serpapi, keyword, location.lower(), num),
                timeout=20.0,
            )
            if serpapi_result is not None:
                if serpapi_result.get("source") != "api_error":
                    serpapi_result["location"] = loc.get("label", "")
                    _set_cache(keyword, location, num, serpapi_result)
                    return serpapi_result
        except Exception:
            pass

        # ── Strategy 3: Google Custom Search JSON API ──
        try:
            cse_result = await asyncio.wait_for(
                asyncio.to_thread(_try_google_custom_search, keyword, location.lower(), num),
                timeout=15.0,
            )
            if cse_result is not None:
                if cse_result.get("source") != "api_error":
                    cse_result["location"] = loc.get("label", "")
                    _set_cache(keyword, location, num, cse_result)
                    return cse_result
        except Exception:
            pass

        # ── Strategy 4: No credentials configured ──
        return {
            "keyword": keyword,
            "location": loc.get("label", ""),
            "organic_results": [],
            "serp_features": [],
            "total_results": 0,
            "results_count": 0,
            "source": "missing_credentials",
            "error": "Cần cấu hình ít nhất một SERP provider:\n"
                     "• SerpAPI: set SERPAPI_KEY (miễn phí 100 searches/tháng tại https://serpapi.com)\n"
                     "• DataForSEO: set DATAFORSEO_LOGIN + DATAFORSEO_PASSWORD\n"
                     "Xem LOCAL-DEV.md để biết chi tiết.",
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
            "source": "dataforseo_live",
            "search_volume": raw.get("search_volume"),
            "cpc": raw.get("cpc"),
            "competition": raw.get("competition"),
        }


async def scrape_google_serp(keyword: str, location: str = "vn", num_results: int = 10) -> Dict[str, Any]:
    return await GoogleSerpScraper().search(keyword, location, num_results)
