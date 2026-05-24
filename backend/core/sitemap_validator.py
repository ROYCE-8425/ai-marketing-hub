"""
Sitemap Validator — SEO Tools

Validates sitemap.xml files:
- Fetches and parses XML (regular sitemap & sitemap index)
- Validates <lastmod> date format
- Checks sitemap size limits (50,000 URLs, 50 MB uncompressed)
- Samples up to 20 <loc> URLs and verifies HTTP 200 status
- Returns a structured validation report
"""

import asyncio
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

import httpx


# Sitemap protocol limits
MAX_URLS_PER_SITEMAP = 50_000
MAX_SITEMAP_BYTES = 50 * 1024 * 1024  # 50 MB uncompressed
MAX_SAMPLE_URLS = 20

# Common XML namespace
_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# Acceptable lastmod formats (ISO-8601 variants)
_LASTMOD_PATTERNS = [
    r"^\d{4}-\d{2}-\d{2}$",                              # 2024-01-15
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",             # 2024-01-15T10:30:00...
]

USER_AGENT = "Mozilla/5.0 (compatible; AI-Marketing-Hub/1.0; SitemapValidator)"


async def validate_sitemap(url: str) -> Dict[str, Any]:
    """
    Validate a sitemap.xml URL.

    Args:
        url: Direct URL to the sitemap (e.g. https://example.com/sitemap.xml).

    Returns:
        Dict with: valid, is_index, url_count, errors, warnings, url_samples.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # ── 1. Fetch sitemap ───────────────────────────────────────────────
    try:
        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            resp = await client.get(url)
    except httpx.TimeoutException:
        return _error_result(url, "Timeout khi tải sitemap. Trang phản hồi quá chậm.")
    except httpx.RequestError as exc:
        return _error_result(url, f"Không thể tải sitemap: {exc}")

    if resp.status_code != 200:
        return _error_result(url, f"Sitemap trả về HTTP {resp.status_code} (cần 200).")

    raw = resp.text
    size_bytes = len(raw.encode("utf-8"))

    # ── 2. Size check ──────────────────────────────────────────────────
    if size_bytes > MAX_SITEMAP_BYTES:
        errors.append(
            f"Sitemap vượt giới hạn kích thước: {size_bytes / (1024*1024):.1f} MB "
            f"(tối đa {MAX_SITEMAP_BYTES // (1024*1024)} MB)."
        )

    # ── 3. Parse XML ───────────────────────────────────────────────────
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        return _error_result(url, f"XML không hợp lệ: {exc}")

    tag = _strip_ns(root.tag)
    is_index = tag == "sitemapindex"

    # ── 4. Extract URLs / sub-sitemaps ─────────────────────────────────
    if is_index:
        entries = root.findall("sm:sitemap", _NS) or root.findall("sitemap")
        loc_tag = "sm:loc"
        lastmod_tag = "sm:lastmod"
    else:
        entries = root.findall("sm:url", _NS) or root.findall("url")
        loc_tag = "sm:loc"
        lastmod_tag = "sm:lastmod"

    if not entries:
        # Try without namespace
        if is_index:
            entries = root.findall("sitemap")
        else:
            entries = root.findall("url")
        loc_tag = "loc"
        lastmod_tag = "lastmod"

    url_count = len(entries)

    if url_count == 0:
        errors.append("Sitemap không chứa URL nào.")
    elif not is_index and url_count > MAX_URLS_PER_SITEMAP:
        errors.append(
            f"Sitemap chứa {url_count:,} URLs (giới hạn {MAX_URLS_PER_SITEMAP:,}). "
            "Nên chia thành sitemap index."
        )

    # ── 5. Extract <loc> and validate <lastmod> ────────────────────────
    locs: List[str] = []
    lastmod_issues = 0
    has_lastmod = False

    for entry in entries:
        loc_el = entry.find(loc_tag, _NS) if ":" in loc_tag else entry.find(loc_tag)
        if loc_el is not None and loc_el.text:
            locs.append(loc_el.text.strip())
        else:
            errors.append("Phát hiện entry thiếu <loc>.")

        lm_el = entry.find(lastmod_tag, _NS) if ":" in lastmod_tag else entry.find(lastmod_tag)
        if lm_el is not None and lm_el.text:
            has_lastmod = True
            if not _valid_lastmod(lm_el.text.strip()):
                lastmod_issues += 1

    if not has_lastmod:
        warnings.append(
            "Không có <lastmod> trong sitemap. Nên thêm để Google ưu tiên crawl trang mới."
        )
    if lastmod_issues > 0:
        warnings.append(
            f"{lastmod_issues} entry có <lastmod> sai định dạng (cần ISO-8601, ví dụ 2024-01-15)."
        )

    # ── 6. Sample URL reachability check ───────────────────────────────
    sample_results = await _check_sample_urls(locs)

    unreachable = [s for s in sample_results if s["status"] != 200]
    if unreachable:
        warnings.append(
            f"{len(unreachable)}/{len(sample_results)} URL mẫu không trả về HTTP 200."
        )

    valid = len(errors) == 0

    return {
        "url": url,
        "valid": valid,
        "is_index": is_index,
        "url_count": url_count,
        "size_kb": round(size_bytes / 1024, 1),
        "has_lastmod": has_lastmod,
        "errors": errors,
        "warnings": warnings,
        "sample_urls": sample_results,
        "summary": (
            f"{'Sitemap index' if is_index else 'Sitemap'} — "
            f"{url_count:,} {'sub-sitemaps' if is_index else 'URLs'}, "
            f"{len(errors)} lỗi, {len(warnings)} cảnh báo"
        ),
    }


# ── Helpers ────────────────────────────────────────────────────────────────


def _strip_ns(tag: str) -> str:
    """Remove XML namespace from a tag name."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _valid_lastmod(value: str) -> bool:
    """Check if a lastmod string is a valid ISO-8601 date."""
    return any(re.match(p, value) for p in _LASTMOD_PATTERNS)


async def _check_sample_urls(
    locs: List[str],
    max_sample: int = MAX_SAMPLE_URLS,
) -> List[Dict[str, Any]]:
    """HEAD-check a sample of URLs for reachability."""
    if not locs:
        return []

    # Evenly sample across the list
    step = max(1, len(locs) // max_sample)
    sample = locs[::step][:max_sample]

    results: List[Dict[str, Any]] = []

    async with httpx.AsyncClient(
        timeout=10,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        tasks = [_head_url(client, u) for u in sample]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    for loc, res in zip(sample, responses):
        if isinstance(res, Exception):
            results.append({"url": loc, "status": 0, "error": str(res)[:100]})
        else:
            results.append(res)

    return results


async def _head_url(client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
    """HEAD-request a single URL and return status."""
    try:
        resp = await client.head(url)
        return {"url": url, "status": resp.status_code}
    except Exception as exc:
        return {"url": url, "status": 0, "error": str(exc)[:100]}


def _error_result(url: str, message: str) -> Dict[str, Any]:
    """Return a standardised error response."""
    return {
        "url": url,
        "valid": False,
        "is_index": False,
        "url_count": 0,
        "size_kb": 0,
        "has_lastmod": False,
        "errors": [message],
        "warnings": [],
        "sample_urls": [],
        "summary": f"Lỗi: {message}",
    }
