"""
API SERP Router — Phase 8

Provides live SERP data endpoints:
- POST /api/serp/live          — Get real top-ranking pages for a keyword
- POST /api/serp/deep-analyze  — Deep-analyze content of top-ranking pages
"""

from __future__ import annotations

import asyncio
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


# ─── Schemas ────────────────────────────────────────────────────────────────────

class SerpLiveRequest(BaseModel):
    keyword: str = Field(..., min_length=1, description="Search keyword")
    location: str = Field("vn", description="Country code: vn, us, uk, au, in, sg, jp")
    num_results: int = Field(10, ge=5, le=20, description="Number of results (5-20)")


class DeepAnalyzeRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    urls: List[str] = Field(..., min_length=1, max_length=10, description="URLs to deep-analyze")
    your_word_count: Optional[int] = Field(None, description="Your content word count for comparison")


# ─── Router ─────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api", tags=["Phase 8 — Live SERP Results"])


# ─── Helpers ────────────────────────────────────────────────────────────────────

def _try_dataforseo(keyword: str, location_code: int = 2840, limit: int = 10) -> Optional[Dict[str, Any]]:
    """
    Attempt to use DataForSEO if credentials exist.
    Returns None if unavailable.
    """
    login = os.getenv("DATAFORSEO_LOGIN")
    password = os.getenv("DATAFORSEO_PASSWORD")
    if not login or not password:
        return None

    try:
        from core.dataforseo import DataForSEO
        client = DataForSEO(login=login, password=password)
        serp = client.get_serp_data(keyword, location_code=location_code, limit=limit)

        if "error" in serp:
            return None

        # Normalize to our standard format
        return {
            "keyword": keyword,
            "organic_results": serp.get("organic_results", []),
            "serp_features": serp.get("features", []),
            "total_results": serp.get("total_results", 0),
            "results_count": len(serp.get("organic_results", [])),
            "search_volume": serp.get("search_volume"),
            "cpc": serp.get("cpc"),
            "competition": serp.get("competition"),
            "source": "dataforseo_live",
        }
    except Exception:
        return None


async def _scrape_page_content(url: str) -> Dict[str, Any]:
    """Scrape a single page and return content metrics."""
    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            http2=True,
        ) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            })
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # Remove non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        # Try to find main content area
        main = None
        for sel in ["article", "main", '[role="main"]', ".content", "#content", ".post", ".entry-content"]:
            main = soup.select_one(sel)
            if main:
                break
        if not main:
            main = soup.find("body")

        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        if main:
            text = main.get_text(separator=" ", strip=True)
            words = re.findall(r"\b[a-zA-ZÀ-ỹ]{2,}\b", text)
            word_count = len(words)

            # Count headings
            headings = len(main.find_all(re.compile(r"^h[1-6]$")))

            # Count images
            images = len(main.find_all("img"))

            # Count links
            links = len(main.find_all("a", href=True))

            # Count paragraphs
            paragraphs = len(main.find_all("p"))

            # Estimate reading time (avg 200 words/min)
            reading_time_min = round(word_count / 200, 1)
        else:
            word_count = 0
            headings = 0
            images = 0
            links = 0
            paragraphs = 0
            reading_time_min = 0

        return {
            "url": url,
            "title": title,
            "word_count": word_count,
            "headings": headings,
            "images": images,
            "links": links,
            "paragraphs": paragraphs,
            "reading_time_min": reading_time_min,
            "status": "ok",
        }

    except httpx.TimeoutException:
        return {"url": url, "status": "timeout", "word_count": 0}
    except httpx.HTTPStatusError as exc:
        return {"url": url, "status": f"http_{exc.response.status_code}", "word_count": 0}
    except Exception as exc:
        return {"url": url, "status": f"error: {str(exc)[:80]}", "word_count": 0}


# ─── POST /api/serp/live ────────────────────────────────────────────────────────

@router.post("/serp/live")
async def serp_live(body: SerpLiveRequest):
    """
    Get real top-ranking pages for a keyword.

    Strategy:
    1. If DATAFORSEO_LOGIN env is set → use DataForSEO API (premium, most accurate)
    2. Otherwise → scrape Google directly (free, may be rate-limited)
    """
    # Location mapping for DataForSEO
    dfs_location_map = {
        "vn": 2704, "us": 2840, "uk": 2826, "au": 2036,
        "in": 2356, "sg": 2702, "jp": 2392,
    }

    # Strategy 1: Try DataForSEO
    dfs_loc = dfs_location_map.get(body.location.lower(), 2840)
    dfs_result = await asyncio.to_thread(
        _try_dataforseo, body.keyword, dfs_loc, body.num_results
    )
    if dfs_result and dfs_result.get("organic_results"):
        dfs_result["analyzed_at"] = datetime.now().isoformat()
        return dfs_result

    # Strategy 2: Scrape Google directly
    from core.google_serp_scraper import GoogleSerpScraper
    scraper = GoogleSerpScraper()
    result = await scraper.search(
        keyword=body.keyword,
        location=body.location,
        num_results=body.num_results,
    )

    if result.get("error"):
        # Return the error but don't crash — let frontend handle it
        result["analyzed_at"] = datetime.now().isoformat()
        return result

    result["analyzed_at"] = datetime.now().isoformat()
    return result


# ─── POST /api/serp/deep-analyze ────────────────────────────────────────────────

@router.post("/serp/deep-analyze")
async def serp_deep_analyze(body: DeepAnalyzeRequest):
    """
    Deep-analyze content of top-ranking pages.

    Scrapes each URL in parallel, counts words, headings, images,
    and provides statistical comparison.
    """
    # Scrape all URLs in parallel
    tasks = [_scrape_page_content(url) for url in body.urls]
    page_results = await asyncio.gather(*tasks)

    # Filter successful results
    successful = [p for p in page_results if p.get("word_count", 0) > 0]

    # Calculate statistics
    if successful:
        counts = [p["word_count"] for p in successful]
        import statistics as st

        stats = {
            "min": min(counts),
            "max": max(counts),
            "mean": round(st.mean(counts)),
            "median": round(st.median(counts)),
            "std_dev": round(st.stdev(counts)) if len(counts) > 1 else 0,
        }

        if len(counts) > 3:
            quantiles = st.quantiles(counts, n=4)
            stats["percentile_25"] = round(quantiles[0])
            stats["percentile_75"] = round(quantiles[2])
        else:
            stats["percentile_25"] = min(counts)
            stats["percentile_75"] = max(counts)

        # Recommendation
        target_optimal = max(
            stats.get("percentile_75", stats["median"]),
            int(stats["median"] * 1.2)
        )

        recommendation = {
            "recommended_min": stats["median"],
            "recommended_optimal": target_optimal,
            "recommended_max": int(target_optimal * 1.2),
            "reasoning": f"Based on median ({stats['median']}) and 75th percentile ({stats.get('percentile_75', 'N/A')}) of top {len(successful)} results",
        }

        # If user provided their word count, add comparison
        if body.your_word_count:
            wc = body.your_word_count
            shorter = len([c for c in counts if c < wc])
            if wc < stats["median"] * 0.8:
                recommendation["your_status"] = "too_short"
                recommendation["message"] = f"Your content ({wc} words) is significantly shorter than competitors. Add {target_optimal - wc} more words."
            elif wc < stats["median"]:
                recommendation["your_status"] = "short"
                recommendation["message"] = f"Your content is shorter than most competitors. Consider adding {target_optimal - wc} more words."
            elif wc < target_optimal:
                recommendation["your_status"] = "good"
                recommendation["message"] = f"Your content length is competitive. Add {target_optimal - wc} more words to match top performers."
            elif wc <= int(target_optimal * 1.2):
                recommendation["your_status"] = "optimal"
                recommendation["message"] = "Your content length is optimal — matches or exceeds top competitors."
            else:
                recommendation["your_status"] = "long"
                recommendation["message"] = "Your content is longer than competitors. Ensure all content adds value."

            recommendation["your_percentile"] = round(shorter / len(counts) * 100)
    else:
        stats = {}
        recommendation = {"error": "Could not analyze any competitor pages"}

    return {
        "keyword": body.keyword,
        "analyzed_at": datetime.now().isoformat(),
        "pages_requested": len(body.urls),
        "pages_analyzed": len(successful),
        "pages": page_results,
        "statistics": stats,
        "recommendation": recommendation,
    }
