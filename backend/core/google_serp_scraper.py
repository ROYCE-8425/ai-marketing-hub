"""
<<<<<<< HEAD
SERP Scraper — Google Custom Search API ONLY
=============================================

Strategy:
1. Google Custom Search JSON API — official Google results
2. Mock data — when API not configured or failed

NO DuckDuckGo. NO other search engines.
"""

import os
from typing import Any, Dict, List
from urllib.parse import urlparse

import httpx


LOCATION_MAP = {
    "vn": {"gl": "vn", "hl": "vi", "label": "Việt Nam"},
    "us": {"gl": "us", "hl": "en", "label": "Hoa Kỳ"},
    "uk": {"gl": "uk", "hl": "en", "label": "Anh"},
    "au": {"gl": "au", "hl": "en", "label": "Úc"},
    "in": {"gl": "in", "hl": "en", "label": "Ấn Độ"},
    "sg": {"gl": "sg", "hl": "en", "label": "Singapore"},
    "jp": {"gl": "jp", "hl": "ja", "label": "Nhật Bản"},
}


def _mock_serp(keyword: str, loc_label: str, reason: str = "") -> Dict[str, Any]:
    """Return mock SERP data with clear notice."""
    kw = keyword.lower()
    slug = kw.replace(" ", "-")
    mock_results = [
        {"position": i + 1, "title": t, "url": u, "domain": d, "snippet": s, "breadcrumb": ""}
        for i, (t, u, d, s) in enumerate([
            (f"Top 10 {keyword} - Hướng dẫn đầy đủ 2025", f"https://www.techradar.com/best/{slug}", "techradar.com", f"Chuyên gia đánh giá {kw} tốt nhất."),
            (f"{keyword} - Đánh giá chuyên sâu", f"https://www.pcmag.com/picks/{slug}", "pcmag.com", f"PCMag đánh giá và xếp hạng {kw}."),
            (f"{keyword} tốt nhất (Xếp hạng)", f"https://www.forbes.com/advisor/{slug}", "forbes.com", f"Forbes Advisor xếp hạng {kw}."),
            (f"{keyword}: Hướng dẫn mua hàng", f"https://www.g2.com/categories/{slug}", "g2.com", f"So sánh {kw} dựa trên đánh giá ngườI dùng."),
            (f"Cách chọn {keyword} phù hợp", "https://www.youtube.com/watch?v=example", "youtube.com", f"Video hướng dẫn chọn {kw}."),
            (f"{keyword} - Wikipedia", f"https://vi.wikipedia.org/wiki/{slug}", "wikipedia.org", f"{keyword} là thuật ngữ dùng để chỉ..."),
            (f"Reddit - {keyword} tốt nhất?", f"https://www.reddit.com/r/best_{slug}", "reddit.com", f"Cộng đồng đề xuất {kw} tốt nhất."),
            (f"So sánh {keyword} 2025", f"https://www.capterra.com/compare/{slug}", "capterra.com", f"So sánh chi tiết các giải pháp {kw}."),
            (f"{keyword} giá rẻ cho doanh nghiệp", f"https://www.hostinger.com/{slug}", "hostinger.com", f"Bắt đầu với {kw} chỉ từ 59.000đ/tháng."),
            (f"{keyword} - Đánh giá Trustpilot", f"https://www.trustpilot.com/categories/{slug}", "trustpilot.com", f"Đọc đánh giá thực từ khách hàng về {kw}."),
        ])
    ]
    return {
        "keyword": keyword,
        "location": loc_label,
        "organic_results": mock_results[:10],
        "serp_features": ["video_carousel", "knowledge_panel", "people_also_ask"],
        "total_results": 10,
        "results_count": 10,
        "source": "mock_serp",
        "error": reason or "Chưa cấu hình Google Custom Search API. Vào tab 'Cấu hình Google' để thêm GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_CX.",
    }
=======
SERP Scraper — Google-first via DataForSEO

Strategy:
1. DataForSEO API (if configured) — returns real Google SERP data
2. Error state with clear message when credentials are missing (no fallback)

All searches are async-safe and never hang.
No DuckDuckGo fallback — Google-only architecture.
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
>>>>>>> f70f382 (🔧 Chuyển SERP Live sang Google-first, loại bỏ DuckDuckGo)

    from core.dataforseo import DataForSEO
    client = DataForSEO(login=login, password=password)
    serp = client.get_serp_data(keyword, location_code=location_code, limit=limit)

<<<<<<< HEAD
async def _google_custom_search(keyword: str, location: str, num_results: int) -> List[Dict]:
    """
    Use Google Custom Search JSON API.
    Free: 100 queries/day. Paid: $5 per 1000 queries.
    Requires: GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_CX env vars.
    """
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")
    if not api_key or not cx:
        return []

    loc = LOCATION_MAP.get(location.lower(), LOCATION_MAP["vn"])
    num = min(num_results, 10)

    params = {
        "key": api_key,
        "cx": cx,
        "q": keyword,
        "num": num,
        "gl": loc["gl"],
        "hl": loc["hl"],
    }

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        items = data.get("items", [])
        results = []
        for i, item in enumerate(items, 1):
            link = item.get("link", "")
            try:
                domain = urlparse(link).netloc.replace("www.", "")
            except Exception:
                domain = ""
            results.append({
                "position": i,
                "title": item.get("title", ""),
                "url": link,
                "domain": domain,
                "snippet": item.get("snippet", ""),
                "breadcrumb": item.get("formattedUrl", ""),
            })
        return results
    except Exception:
        return []


class GoogleSerpScraper:
    """SERP scraper: Google Custom Search API ONLY."""

    async def search(self, keyword: str, location: str = "vn", num_results: int = 10) -> Dict[str, Any]:
        loc = LOCATION_MAP.get(location.lower(), LOCATION_MAP["vn"])
        num = max(5, min(20, num_results))

        # Check if Google API is configured
        has_google_api = bool(os.getenv("GOOGLE_SEARCH_API_KEY") and os.getenv("GOOGLE_SEARCH_CX"))

        if not has_google_api:
            return _mock_serp(
                keyword,
                loc.get("label", ""),
                "Chưa cấu hình Google Custom Search API. Vào tab 'Cấu hình Google' để thêm GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_CX."
            )

        # Call Google Custom Search API
        google_results = await _google_custom_search(keyword, location, num)

        if google_results:
            features = self._detect_features(google_results)
            return {
                "keyword": keyword,
                "location": loc.get("label", ""),
                "organic_results": google_results,
                "serp_features": features,
                "total_results": len(google_results),
                "results_count": len(google_results),
                "source": "google_custom_search",
                "note": "Kết quả từ Google Custom Search API (chính xác)",
            }

        # API configured but failed (quota exceeded, invalid key, etc.)
        return _mock_serp(
            keyword,
            loc.get("label", ""),
            "Google Search API trả lỗi hoặc hết quota (100 query/ngày). Vui lòng kiểm tra API key, CX, hoặc đợi ngày mai."
        )

    def _detect_features(self, results: List[Dict]) -> List[str]:
        """Detect SERP features from result domains."""
        features = []
        domains = [r.get("domain", "") for r in results]
        if any("youtube.com" in d for d in domains):
            features.append("video_carousel")
        if any("wikipedia.org" in d for d in domains):
            features.append("knowledge_panel")
        return features
=======
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
>>>>>>> f70f382 (🔧 Chuyển SERP Live sang Google-first, loại bỏ DuckDuckGo)


async def scrape_google_serp(keyword: str, location: str = "vn", num_results: int = 10) -> Dict[str, Any]:
    return await GoogleSerpScraper().search(keyword, location, num_results)
