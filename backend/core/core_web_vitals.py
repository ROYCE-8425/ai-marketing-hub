"""
Core Web Vitals Checker — SEO Tools

Fetches Core Web Vitals and Lighthouse scores from
Google PageSpeed Insights API v5.

Metrics extracted:
- LCP (Largest Contentful Paint)
- INP (Interaction to Next Paint)
- CLS (Cumulative Layout Shift)
- FCP (First Contentful Paint)
- TTFB (Time to First Byte)

Also returns Lighthouse category scores and top optimization opportunities.
"""

import httpx
from typing import Any, Dict, List, Optional

PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


async def check_core_web_vitals(
    url: str,
    strategy: str = "mobile",
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetch Core Web Vitals from PageSpeed Insights API.

    Args:
        url: The page URL to analyze.
        strategy: 'mobile' or 'desktop'.
        api_key: Optional Google API key (higher quota).

    Returns:
        Dict with core_web_vitals, cwv_status, scores, opportunities.
    """
    params: Dict[str, Any] = {
        "url": url,
        "strategy": strategy,
        "category": ["performance", "seo", "accessibility", "best-practices"],
    }
    if api_key:
        params["key"] = api_key

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(PAGESPEED_API, params=params)

            if resp.status_code == 429:
                return {
                    "error": "Vượt giới hạn API PageSpeed Insights. Thử lại sau hoặc thêm API key.",
                    "status": "rate_limited",
                }
            if resp.status_code >= 400:
                return {
                    "error": f"PageSpeed API trả về lỗi {resp.status_code}",
                    "status": "api_error",
                    "detail": resp.text[:500],
                }

            data = resp.json()
    except httpx.TimeoutException:
        return {
            "error": f"Timeout khi phân tích {url}. Trang có thể tải quá chậm.",
            "status": "timeout",
        }
    except httpx.RequestError as exc:
        return {
            "error": f"Không thể kết nối PageSpeed API: {exc}",
            "status": "connection_error",
        }
    except Exception as exc:
        return {
            "error": f"Lỗi không mong đợi: {exc}",
            "status": "unknown_error",
        }

    # ── Extract Core Web Vitals from field data (CrUX) ─────────────────
    loading = data.get("loadingExperience", {})
    metrics = loading.get("metrics", {})

    cwv = {
        "lcp": _extract_metric(metrics, "LARGEST_CONTENTFUL_PAINT_MS"),
        "inp": _extract_metric(metrics, "INTERACTION_TO_NEXT_PAINT"),
        "cls": _extract_metric(metrics, "CUMULATIVE_LAYOUT_SHIFT_SCORE"),
        "fcp": _extract_metric(metrics, "FIRST_CONTENTFUL_PAINT_MS"),
        "ttfb": _extract_metric(metrics, "EXPERIMENTAL_TIME_TO_FIRST_BYTE"),
    }

    # ── Extract Lighthouse category scores ─────────────────────────────
    categories = data.get("lighthouseResult", {}).get("categories", {})
    scores = {
        "performance": _score(categories, "performance"),
        "seo": _score(categories, "seo"),
        "accessibility": _score(categories, "accessibility"),
        "best_practices": _score(categories, "best-practices"),
    }

    # ── Extract top optimization opportunities ─────────────────────────
    audits = data.get("lighthouseResult", {}).get("audits", {})
    opportunities = _extract_opportunities(audits)

    # ── CWV pass/fail thresholds ───────────────────────────────────────
    cwv_status = _compute_cwv_status(cwv)

    # Map overall_category from PageSpeed ("FAST", "AVERAGE", "SLOW", "NONE") to frontend
    raw_status = loading.get("overall_category", "NONE")
    status_map = {"FAST": "good", "AVERAGE": "needs_improvement", "SLOW": "poor", "NONE": "poor"}

    return {
        "url": url,
        "strategy": strategy,
        "metrics": {
            "lcp": {
                "value": cwv["lcp"]["value"] if cwv["lcp"]["value"] is not None else 0,
                "unit": "ms",
                "rating": cwv_status.get("lcp", "poor")
            },
            "inp": {
                "value": cwv["inp"]["value"] if cwv["inp"]["value"] is not None else 0,
                "unit": "ms",
                "rating": cwv_status.get("inp", "poor")
            },
            "cls": {
                "value": cwv["cls"]["value"] if cwv["cls"]["value"] is not None else 0,
                "unit": "",
                "rating": cwv_status.get("cls", "poor")
            }
        },
        "lighthouse_scores": scores,
        "opportunities": opportunities[:10],
        "overall_status": status_map.get(raw_status, "poor"),
    }


# ── Helpers ────────────────────────────────────────────────────────────────


def _extract_metric(metrics: Dict, key: str) -> Dict[str, Any]:
    """Extract a single CrUX metric with value, category, and distributions."""
    m = metrics.get(key, {})
    dist = m.get("distributions", [])
    percentile = m.get("percentile")

    # CLS is reported * 100, normalise back to 0-0.xx scale
    if key == "CUMULATIVE_LAYOUT_SHIFT_SCORE" and percentile is not None:
        value = percentile / 100
    else:
        value = percentile

    return {
        "value": value,
        "category": m.get("category", "NONE"),
        "distributions": dist,
    }


def _score(categories: Dict, key: str) -> Optional[float]:
    """Extract a Lighthouse category score (0-100)."""
    cat = categories.get(key, {})
    raw = cat.get("score")
    if raw is not None:
        return round(raw * 100)
    return None


def _extract_opportunities(audits: Dict) -> List[Dict[str, Any]]:
    """Pull optimization opportunities sorted by potential savings."""
    opportunities: List[Dict[str, Any]] = []
    for key, audit in audits.items():
        details = audit.get("details", {})
        score = audit.get("score")
        if (
            details.get("type") == "opportunity"
            and score is not None
            and score < 1
        ):
            opportunities.append({
                "id": key,
                "title": audit.get("title", ""),
                "description": audit.get("description", ""),
                "score": score,
                "savings_ms": details.get("overallSavingsMs", 0),
            })
    opportunities.sort(key=lambda x: x.get("savings_ms", 0), reverse=True)
    return opportunities


def _compute_cwv_status(cwv: Dict) -> Dict[str, str]:
    """
    Determine good / needs_improvement / poor for each Core Web Vital.

    Thresholds (Google official):
      LCP:  ≤2500ms good | ≤4000ms needs_improvement | >4000ms poor
      INP:  ≤200ms  good | ≤500ms  needs_improvement | >500ms  poor
      CLS:  ≤0.1    good | ≤0.25   needs_improvement | >0.25   poor
    """
    lcp_val = cwv["lcp"]["value"]
    inp_val = cwv["inp"]["value"]
    cls_val = cwv["cls"]["value"]

    return {
        "lcp": (
            "poor" if lcp_val is None else
            "good" if lcp_val <= 2500
            else "needs_improvement" if lcp_val <= 4000
            else "poor"
        ),
        "inp": (
            "poor" if inp_val is None else
            "good" if inp_val <= 200
            else "needs_improvement" if inp_val <= 500
            else "poor"
        ),
        "cls": (
            "poor" if cls_val is None else
            "good" if cls_val <= 0.1
            else "needs_improvement" if cls_val <= 0.25
            else "poor"
        ),
    }
