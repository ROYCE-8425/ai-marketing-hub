"""
AI Website Advisor (AI Cố vấn website) Core — Phase 21

Consolidates all SEO & marketing metrics in the system, performs deterministic
insights analysis first, and synthesizes executive action plans using Groq AI.
Falls back gracefully to rich template-based deterministic summaries if no key is present.
"""

from __future__ import annotations

import asyncio
import os
import re
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

import httpx
from dotenv import load_dotenv

# Load env variables from backend root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Import existing modules
from core.technical_seo import scan_technical_seo
from core.core_web_vitals import check_core_web_vitals
from core.schema_validator import validate_schema
from core.broken_link_checker import check_broken_links
from core.usage_history import get_usage_stats
from core.rank_tracker import get_tracked_keywords, check_ranking_alerts
from core.google_search_console import GoogleSearchConsole
from core.ga4_fetcher import get_ga4_overview
from core.site_manager import get_active_site

# ─────────────────────────────────────────────────────────────────────────────
# Parallel Fetchers with Graceful Error/Missing Credentials Handling
# ─────────────────────────────────────────────────────────────────────────────

async def fetch_gsc(site_url: str, days: int) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Fetch search performance, keywords and quick wins from GSC."""
    client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")
    refresh = os.getenv("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN", "")
    site = os.getenv("GSC_SITE_URL", site_url)

    if not all([client_id, secret, refresh, site]):
        return "missing_credentials", None

    try:
        gsc = GoogleSearchConsole(site_url=site)
        keywords = await gsc.get_keyword_positions(days=days, limit=100)
        quick_wins = await gsc.get_quick_wins(days=days)
        trending = await gsc.get_trending_queries(days_recent=7, days_total=days)
        return "ok", {
            "keywords": keywords,
            "quick_wins": quick_wins,
            "trending": trending
        }
    except Exception as e:
        return "error", {"error": str(e)}


async def fetch_ga4(days: int) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Fetch traffic stats, channels, top pages from GA4."""
    property_id = os.getenv("GA4_PROPERTY_ID", "")
    if not property_id:
        return "missing_credentials", None

    try:
        overview = await get_ga4_overview(days=days)
        if overview.get("data_source") in ("live_ga4", "partial_live_ga4"):
            return "ok", overview
        else:
            return "error", {"error": overview.get("error") or "Không lấy được dữ liệu GA4"}
    except Exception as e:
        return "error", {"error": str(e)}


async def fetch_serp(keyword: Optional[str]) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Fetch live SERP if target keyword is explicitly provided."""
    if not keyword:
        return "disabled", None

    login = os.getenv("DATAFORSEO_LOGIN")
    password = os.getenv("DATAFORSEO_PASSWORD")
    if not login or not password:
        # Fallback to SerpAPI if configured
        if os.getenv("SERPAPI_API_KEY"):
            try:
                from core.serpapi_search import search_serpapi
                res = await asyncio.to_thread(search_serpapi, keyword, "vn", 10)
                if res and res.get("organic_results"):
                    return "ok", res
            except Exception:
                pass
        return "missing_credentials", None

    try:
        from routers.api_serp import _try_dataforseo
        # 2704 is Vietnam location code
        res = await asyncio.to_thread(_try_dataforseo, keyword, 2704, 10)
        if res and res.get("organic_results"):
            return "ok", res
        return "error", {"error": "Không có kết quả hữu cơ từ DataForSEO"}
    except Exception as e:
        return "error", {"error": str(e)}


async def fetch_technical(site_url: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Run full technical SEO scanner."""
    try:
        res = await scan_technical_seo(site_url)
        if "error" in res:
            return "error", res
        return "ok", res
    except Exception as e:
        return "error", {"error": str(e)}


async def fetch_cwv(site_url: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Measure PageSpeed Core Web Vitals."""
    psi_key = os.getenv("PAGESPEED_API_KEY")
    try:
        res = await check_core_web_vitals(site_url, strategy="mobile", api_key=psi_key)
        if "error" in res:
            return "error", res
        return "ok", res
    except Exception as e:
        return "error", {"error": str(e)}


async def fetch_schema(site_url: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Validate JSON-LD Structured Data Schema."""
    try:
        res = await validate_schema(site_url)
        if "error" in res:
            return "error", res
        return "ok", res
    except Exception as e:
        return "error", {"error": str(e)}


async def fetch_broken_links(site_url: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Scan for broken links (cap at 25 links for quick response)."""
    try:
        res = await check_broken_links(site_url, max_links=25)
        if "error" in res:
            return "error", res
        return "ok", res
    except Exception as e:
        return "error", {"error": str(e)}


async def fetch_rank_tracking(site_url: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Fetch tracked keywords and ranking alerts from local database."""
    try:
        keywords = await asyncio.to_thread(get_tracked_keywords, site_url)
        alerts = await asyncio.to_thread(check_ranking_alerts, site_url)
        return "ok", {
            "keywords": keywords,
            "alerts": alerts
        }
    except Exception as e:
        return "error", {"error": str(e)}


async def fetch_usage_history() -> Tuple[str, Optional[Dict[str, Any]]]:
    """Fetch usage log stats from local database."""
    try:
        stats = await asyncio.to_thread(get_usage_stats)
        return "ok", stats
    except Exception as e:
        return "error", {"error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# Deterministic Normalization and Rules Logic
# ─────────────────────────────────────────────────────────────────────────────

def normalize_site_url(site_url: Optional[str]) -> str:
    """Resolve site URL based on request, active site context, or env fallback."""
    url = ""
    if site_url:
        url = site_url.strip()
    else:
        try:
            active = get_active_site()
            if active and active.get("url"):
                url = active["url"].strip()
        except Exception:
            pass

    if not url:
        url = os.getenv("GSC_SITE_URL", "https://binhphuocmitsubishi.com")

    # Clean and prefix
    url = url.rstrip("/")
    if not url.startswith("http"):
        url = f"https://{url}"
    return url


def build_normalized_snapshot(
    url: str,
    gsc: Tuple[str, Any],
    ga4: Tuple[str, Any],
    serp: Tuple[str, Any],
    tech: Tuple[str, Any],
    cwv: Tuple[str, Any],
    schema: Tuple[str, Any],
    broken: Tuple[str, Any],
    rank_tracking: Tuple[str, Any],
    usage: Tuple[str, Any]
) -> Dict[str, Any]:
    """Normalize varying shapes into a clean, solid internal DTO contract."""
    
    # 1. GSC Snapshot
    gsc_dto = {
        "clicks": 0, "impressions": 0, "ctr": 0.0, "avg_position": 0.0,
        "top_queries": [], "quick_wins": []
    }
    if gsc[0] == "ok" and gsc[1]:
        kws = gsc[1].get("keywords", [])
        gsc_dto["clicks"] = sum(k["clicks"] for k in kws)
        gsc_dto["impressions"] = sum(k["impressions"] for k in kws)
        if gsc_dto["impressions"] > 0:
            gsc_dto["ctr"] = round((gsc_dto["clicks"] / gsc_dto["impressions"]) * 100, 2)
        if kws:
            gsc_dto["avg_position"] = round(sum(k["position"] for k in kws) / len(kws), 1)
        gsc_dto["top_queries"] = sorted(kws, key=lambda x: x["impressions"], reverse=True)[:10]
        gsc_dto["quick_wins"] = gsc[1].get("quick_wins", [])[:10]

    # 2. GA4 Snapshot
    ga4_dto = {
        "total_sessions": 0, "total_pageviews": 0, "engagement_rate": 0.0, "bounce_rate": 0.0,
        "top_pages": [], "top_channels": []
    }
    if ga4[0] == "ok" and ga4[1]:
        overview = ga4[1].get("overview", {})
        ga4_dto["total_sessions"] = overview.get("sessions", 0)
        ga4_dto["total_pageviews"] = overview.get("pageviews", 0)
        ga4_dto["engagement_rate"] = overview.get("engagement_rate", 0.0)
        ga4_dto["bounce_rate"] = overview.get("bounce_rate", 0.0)
        ga4_dto["top_pages"] = ga4[1].get("top_pages", [])[:10]
        ga4_dto["top_channels"] = ga4[1].get("traffic_sources", [])

    # 3. Technical SEO & Speed & Schema Snapshot
    tech_dto = {
        "seo_score": 0, "grade": "F", "load_time": 0.0, "broken_links_count": 0,
        "critical_issues": [], "warnings": [], "cwv": {}, "schema": {}
    }
    if tech[0] == "ok" and tech[1]:
        t = tech[1]
        tech_dto["seo_score"] = t.get("score", 0)
        tech_dto["grade"] = t.get("grade", "F")
        tech_dto["load_time"] = t.get("load_time", 0.0)
        
        # Parse issues by category
        for issue in t.get("issues", []):
            mapped = {"category": issue.get("category", "SEO"), "message": issue.get("message", ""), "fix": issue.get("fix", "")}
            if issue.get("severity") == "critical":
                tech_dto["critical_issues"].append(mapped)
            elif issue.get("severity") == "warning":
                tech_dto["warnings"].append(mapped)

    # Core Web Vitals
    if cwv[0] == "ok" and cwv[1]:
        c = cwv[1]
        tech_dto["cwv"] = {
            "overall_status": c.get("overall_status", "poor"),
            "lighthouse_scores": c.get("lighthouse_scores", {}),
            "metrics": c.get("metrics", {}),
            "opportunities": c.get("opportunities", [])[:5]
        }
    elif cwv[0] == "error":
        tech_dto["cwv"] = {"overall_status": "error", "error": cwv[1].get("error")}

    # Schema Validation
    if schema[0] == "ok" and schema[1]:
        s = schema[1]
        tech_dto["schema"] = {
            "schemas_found": s.get("schemas_found", 0),
            "valid": s.get("valid", False),
            "types_found": s.get("types_found", []),
            "errors": s.get("errors", []),
            "warnings": s.get("warnings", [])
        }
    elif schema[0] == "error":
        tech_dto["schema"] = {"valid": False, "errors": [schema[1].get("error")]}

    # Broken links
    if broken[0] == "ok" and broken[1]:
        b = broken[1]
        tech_dto["broken_links_count"] = b.get("summary", {}).get("broken_count", 0)
        for bl in b.get("broken_links", []):
            tech_dto["critical_issues"].append({
                "category": "Links",
                "message": f"Link hỏng ({bl.get('source_tag')}): {bl.get('url')} trả về mã lỗi {bl.get('status')}",
                "fix": "Cập nhật hoặc xóa liên kết hỏng này."
            })

    # 4. Local Rank Tracking
    rank_dto = {"tracked_keywords": [], "alerts": []}
    if rank_tracking[0] == "ok" and rank_tracking[1]:
        rank_dto["tracked_keywords"] = rank_tracking[1].get("keywords", [])
        rank_dto["alerts"] = rank_tracking[1].get("alerts", [])

    # 5. Usage Snapshot
    usage_dto = {"total_calls": 0, "success_rate": 100.0, "error_count": 0, "anomalies": []}
    if usage[0] == "ok" and usage[1]:
        u = usage[1]
        usage_dto["total_calls"] = u.get("total_calls", 0)
        usage_dto["success_rate"] = u.get("success_rate", 100.0)
        usage_dto["error_count"] = u.get("errors", 0)
        
        # Check for anomalies
        if usage_dto["success_rate"] < 90.0:
            usage_dto["anomalies"].append(f"Tần suất lỗi hệ thống cao ({100.0 - usage_dto['success_rate']:.1f}%).")
        for endpoint, details in u.get("endpoints", {}).items():
            if details.get("errors", 0) > 3:
                usage_dto["anomalies"].append(f"Endpoint '{endpoint}' có nhiều cuộc gọi thất bại ({details['errors']} lỗi).")
            if details.get("avg_ms", 0) > 2000.0:
                usage_dto["anomalies"].append(f"Endpoint '{endpoint}' phản hồi rất chậm (trung bình {details['avg_ms']:.0f}ms).")

    return {
        "gsc": gsc_dto,
        "ga4": ga4_dto,
        "technical": tech_dto,
        "rank_tracking": rank_dto,
        "usage_history": usage_dto,
        "serp": serp[1] if serp[0] == "ok" else None
    }


def compute_deterministic_insights(snapshot: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], float]:
    """Calculate precise, rule-based diagnostic metrics before passing to AI."""
    top_issues = []
    quick_wins = []
    technical_blockers = []
    content_opportunities = []
    confidence_score = 100.0

    # ─────────────────────────────────────────────────────────────────────────
    # 1. GSC Rules
    # ─────────────────────────────────────────────────────────────────────────
    gsc = snapshot["gsc"]
    if gsc["impressions"] > 0:
        # A. High Impression / Low CTR (Opportunity for titles/snippets)
        for q in gsc["top_queries"]:
            if q["position"] <= 10 and q["impressions"] >= 150 and q["ctr"] < 2.0:
                top_issues.append({
                    "severity": "warning",
                    "category": "Search Console",
                    "message": f"Từ khóa '{q['keyword']}' xếp thứ {q['position']} có hiển thị cao ({q['impressions']}) nhưng CTR thấp ({q['ctr']}%).",
                    "fix": "Viết lại thẻ Title hấp dẫn hơn hoặc tối ưu Meta Description để tăng tỷ lệ nhấp chuột."
                })

        # B. GSC Quick Wins (Close to page 1 top ranking)
        for qw in gsc["quick_wins"]:
            quick_wins.append({
                "keyword": qw["keyword"],
                "current_position": qw["position"],
                "impressions": qw["impressions"],
                "action": f"Từ khóa '{qw['keyword']}' đang ở vị trí {qw['position']}. Cần bổ sung LSI, hình ảnh, hoặc chèn thêm internal link để đẩy nhanh lên Top 3."
            })
    else:
        confidence_score -= 25.0

    # ─────────────────────────────────────────────────────────────────────────
    # 2. GA4 Rules
    # ─────────────────────────────────────────────────────────────────────────
    ga4 = snapshot["ga4"]
    if ga4["total_sessions"] > 0:
        # High views / Low engagement
        for page in ga4["top_pages"]:
            if page.get("pageviews", 0) >= 50 and (page.get("engagement_rate", 100.0) < 45.0 or page.get("bounce_rate", 0.0) > 55.0):
                top_issues.append({
                    "severity": "critical",
                    "category": "Analytics",
                    "message": f"Trang '{page['path']}' có lượt xem lớn ({page['pageviews']}) nhưng tỷ lệ tương tác thấp ({page.get('engagement_rate', 0.0)}%) hoặc tỷ lệ thoát cao.",
                    "fix": "Tối ưu hóa dàn bài, thêm nút CTA hoặc cải thiện tốc độ tải trang cụ thể của trang này."
                })
    else:
        confidence_score -= 25.0

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Technical SEO Rules
    # ─────────────────────────────────────────────────────────────────────────
    tech = snapshot["technical"]
    if tech["seo_score"] > 0:
        # Technical blockers (Critical issues from scan_technical_seo)
        for issue in tech["critical_issues"]:
            technical_blockers.append(issue)
        for issue in tech["warnings"]:
            if issue["category"] in ("Performance", "Bảo mật", "Sitemap/Robots"):
                technical_blockers.append(issue)

        # Core Web Vitals blockers
        cwv_data = tech.get("cwv", {})
        if cwv_data and cwv_data.get("overall_status") in ("poor", "needs_improvement"):
            metrics = cwv_data.get("metrics", {})
            for m_key, m_val in metrics.items():
                if m_val.get("rating") == "poor":
                    technical_blockers.append({
                        "category": "Tốc độ (CWV)",
                        "message": f"Chỉ số {m_key.upper()} ({m_val.get('value')} {m_val.get('unit')}) ở trạng thái báo động đỏ (poor).",
                        "fix": "Nén hình ảnh dung lượng lớn, hoãn thực thi JS không quan trọng hoặc sử dụng cơ chế đệm (browser cache)."
                    })
    else:
        confidence_score -= 25.0

    # Schema Gaps
    schema_data = tech.get("schema", {})
    if schema_data and not schema_data.get("valid", True):
        for err in schema_data.get("errors", []):
            technical_blockers.append({
                "category": "Schema.org",
                "message": f"Lỗi structured data: {err}",
                "fix": "Sửa lại mã cú pháp JSON-LD của schema này."
            })
    for warn in schema_data.get("warnings", []):
        if "thiếu" in warn.lower() or "should be" in warn.lower():
            technical_blockers.append({
                "category": "Schema.org",
                "message": f"Khuyến nghị Schema: {warn}",
                "fix": "Bổ sung thuộc tính bị thiếu để tăng cơ hội hiển thị Rich Snippets."
            })

    # ─────────────────────────────────────────────────────────────────────────
    # 4. SERP & Keyword opportunities
    # ─────────────────────────────────────────────────────────────────────────
    serp = snapshot.get("serp")
    if serp and serp.get("organic_results"):
        intent = serp.get("search_intent", {})
        content_opportunities.append({
            "keyword": serp["keyword"],
            "search_intent": intent.get("primary", "commercial"),
            "reason": f"Phân tích SERP đối thủ cạnh tranh cho từ khóa mục tiêu '{serp['keyword']}'."
        })
        for rec in intent.get("content_recommendations", []):
            content_opportunities.append({
                "keyword": serp["keyword"],
                "search_intent": intent.get("primary", "commercial"),
                "reason": rec
            })

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Local Rank Tracker drops
    # ─────────────────────────────────────────────────────────────────────────
    rank_tracking = snapshot["rank_tracking"]
    for alert in rank_tracking.get("alerts", []):
        top_issues.append({
            "severity": "critical" if alert["severity"] == "critical" else "warning",
            "category": "Thứ hạng",
            "message": f"Từ khóa theo dõi '{alert['keyword']}' bị tụt {alert['drop']} hạng (Vị trí hiện tại: {alert['current_position']}).",
            "fix": "Kiểm tra thay đổi nội dung gần đây của bạn hoặc kiểm tra đối thủ cạnh tranh vượt lên."
        })

    # Deduplicate issues
    seen_issues = set()
    unique_issues = []
    for issue in top_issues:
        key = (issue["category"], issue["message"])
        if key not in seen_issues:
            seen_issues.add(key)
            unique_issues.append(issue)

    # Sort technical blockers: critical first
    # (By default, our lists are collected in logical categories)

    return unique_issues, quick_wins, technical_blockers, content_opportunities, max(10.0, confidence_score)

# ─────────────────────────────────────────────────────────────────────────────
# AI Synthesis & Falling back to Templates
# ─────────────────────────────────────────────────────────────────────────────

def _call_groq_advisor(prompt: str) -> Optional[str]:
    """Call Groq LLaMA 3.3 to synthesize the executive advice."""
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return None

    try:
        resp = httpx.post("https://api.groq.com/openai/v1/chat/completions", headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }, json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Bạn là chuyên gia cố vấn SEO và tối ưu hóa website cấp cao. "
                        "Hãy sử dụng số liệu đo đạc thực tế của hệ thống để đưa ra phân tích chính xác, "
                        "lập luận logic, đề xuất cụ thể, tập trung hành động và viết hoàn toàn bằng Tiếng Việt. "
                        "Trả về kết quả định dạng JSON chuẩn (chỉ trả về JSON, không chứa markdown code block hay text ngoài):\n"
                        "{\n"
                        "  \"summary\": \"Tóm tắt điều hành ngắn gọn, súc tích\",\n"
                        "  \"action_plan_7d\": [\n"
                        "     {\"day\": \"Ngày 1-2\", \"task\": \"Công việc cụ thể\", \"priority\": \"high|medium|low\", \"impact\": \"Tác động dự kiến\"}\n"
                        "  ],\n"
                        "  \"action_plan_30d\": [\n"
                        "     {\"week\": \"Tuần 1\", \"task\": \"Công việc cụ thể\", \"priority\": \"high|medium|low\", \"impact\": \"Tác động dự kiến\"}\n"
                        "  ]\n"
                        "}"
                    )
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 3000,
        }, timeout=30.0)

        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        pass
    return None


def build_outcome_summaries(outcome_tracking_ctx: Optional[Dict[str, Any]]) -> Tuple[str, str, str]:
    """
    Builds clean deterministic Vietnamese summaries for completed, failed, and effective recommendations.
    Returns: (completed_summary, failed_summary, effective_summary)
    """
    if not outcome_tracking_ctx or outcome_tracking_ctx.get("total_outcomes", 0) == 0:
        return (
            "Chưa ghi nhận khuyến nghị hoàn thành trong lịch sử thực thi.",
            "Chưa ghi nhận khuyến nghị thất bại trong lịch sử thực thi.",
            "Chưa có số liệu đo lường hiệu quả (KPI Delta) cho các khuyến nghị lịch sử."
        )

    completed_count = outcome_tracking_ctx.get("completed_count", 0)
    failed_count = outcome_tracking_ctx.get("failed_count", 0)
    delta_count = outcome_tracking_ctx.get("completed_with_delta_count", 0)

    # 1. Completed recommendations summary
    if completed_count > 0:
        completed_summary = f"Đã hoàn thành thành công {completed_count} khuyến nghị tối ưu trước đó."
    else:
        completed_summary = "Chưa ghi nhận khuyến nghị nào hoàn thành trong lịch sử thực thi."

    # 2. Failed recommendations summary
    failed_types = outcome_tracking_ctx.get("failed_recommendation_types", {})
    if failed_count > 0:
        types_str = ", ".join([f"nhóm '{t}' ({c} lần)" for t, c in failed_types.items()])
        failed_summary = f"Ghi nhận {failed_count} khuyến nghị đã thất bại hoặc không thể triển khai: {types_str}."
    else:
        failed_summary = "Không ghi nhận khuyến nghị thất bại trong lịch sử tối ưu."

    # 3. Effective recommendations summary (completed with delta)
    success_types = outcome_tracking_ctx.get("successful_recommendation_types", {})
    if delta_count > 0:
        types_str = ", ".join([f"nhóm '{t}' ({c} lần)" for t, c in success_types.items()])
        effective_summary = (
            f"Tích lũy {delta_count} lần tối ưu có dữ liệu đo lường hiệu quả tích cực thuộc: {types_str}. "
            f"Các nhóm này đã chứng minh hiệu quả thực tế và nên tiếp tục được nhân rộng."
        )
    else:
        effective_summary = "Chưa có số liệu đo lường hiệu quả (KPI Delta) cụ thể được ghi nhận thành công từ lịch sử."

    return completed_summary, failed_summary, effective_summary


def match_task_to_outcomes(
    task_text: str,
    all_outcomes: List[Any]
) -> Tuple[bool, int, int, bool, Optional[str]]:
    """
    Matches a task text against past outcomes using Jaccard word overlap similarity.
    Returns: (was_completed_before, completed_before_count, failed_before_count, has_measured_delta_before, outcome_note)
    """
    if not all_outcomes:
        return False, 0, 0, False, None

    norm_task = normalize_text_for_matching(task_text)
    if not norm_task:
        return False, 0, 0, False, None

    completed_before_count = 0
    failed_before_count = 0
    has_measured_delta_before = False

    for o in all_outcomes:
        norm_o = normalize_text_for_matching(o.recommendation_text)
        is_match = False
        if norm_task == norm_o:
            is_match = True
        else:
            words_task = set(norm_task.split())
            words_o = set(norm_o.split())
            if words_task and words_o:
                intersection = words_task.intersection(words_o)
                overlap_ratio = len(intersection) / max(len(words_task), len(words_o))
                if overlap_ratio >= 0.7:
                    is_match = True

        if is_match:
            if o.status == "completed":
                completed_before_count += 1
                if o.measured_delta_json and o.measured_delta_json.strip() not in ("", "{}"):
                    has_measured_delta_before = True
            elif o.status == "failed":
                failed_before_count += 1

    was_completed_before = completed_before_count > 0
    
    notes = []
    if was_completed_before:
        notes.append("Khuyến nghị tương tự đã từng hoàn thành trước đó")
    if failed_before_count > 0:
        notes.append("Loại khuyến nghị này từng thất bại trong lịch sử thực thi, cần xem lại cách triển khai")
    if has_measured_delta_before:
        notes.append("Đã có dữ liệu đo lường hiệu quả (KPI Delta) từ lần thực hiện trước")

    outcome_note = " + ".join(notes) if notes else None
    return was_completed_before, completed_before_count, failed_before_count, has_measured_delta_before, outcome_note


def generate_fallback_summary(
    url: str,
    top_issues: List[Dict],
    quick_wins: List[Dict],
    blockers: List[Dict],
    opportunities: List[Dict],
    keyword_memory_ctx: Optional[Dict[str, Any]] = None,
    recommendation_memory_ctx: Optional[Dict[str, Any]] = None,
    pattern_memory_ctx: Optional[Dict[str, Any]] = None,
    completed_recs: Optional[List[Any]] = None,
    failed_recs: Optional[List[Any]] = None,
    outcome_tracking_ctx: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Template-based diagnostic synthesis when GROQ_API_KEY is not configured, enhanced with SEO memory context."""
    
    # 1. Exec Summary
    summary = (
        f"Báo cáo cố vấn website tự động cho {url}. "
        f"Phân tích phát hiện thấy {len(top_issues)} vấn đề về hiệu suất, "
        f"{len(blockers)} rào cản kỹ thuật/Core Web Vitals nguy hiểm, và "
        f"{len(quick_wins)} từ khóa cơ hội đang cận kề Top 3/Trang 1. "
    )
    
    memory_notes = []
    if keyword_memory_ctx and recommendation_memory_ctx:
        total_kw = keyword_memory_ctx.get("total_keyword_records", 0)
        total_rec = recommendation_memory_ctx.get("total_recommendations", 0)
        pending_count = recommendation_memory_ctx.get("pending_recommendations_count", 0)
        repeated_list = recommendation_memory_ctx.get("repeated_recommendations", [])
        
        if total_kw == 0 and total_rec == 0:
            memory_notes.append("Đây là lần chạy đầu tiên, hệ thống chưa ghi nhận lịch sử SEO cho website này.")
        else:
            memory_notes.append(
                f"Dữ liệu lịch sử lưu trữ {total_kw} cơ hội từ khóa và {total_rec} khuyến nghị."
            )
            if pending_count > 0:
                memory_notes.append(
                    f"Hiện tại có {pending_count} khuyến nghị đang trong trạng thái chờ xử lý (pending). "
                    f"Nên ưu tiên giải quyết các khuyến nghị pending trước khi mở thêm hướng mới."
                )
            if len(repeated_list) > 0:
                memory_notes.append(
                    f"Một số khuyến nghị đang lặp lại nhưng chưa được xử lý (phát hiện {len(repeated_list)} khuyến nghị lặp lại)."
                )
                
    if pattern_memory_ctx and pattern_memory_ctx.get("total_patterns", 0) > 0:
        total_pat = pattern_memory_ctx.get("total_patterns", 0)
        crit_pat = pattern_memory_ctx.get("critical_structural_patterns", [])
        rec_pat = pattern_memory_ctx.get("recurring_patterns", [])
        
        pat_str = f"Hệ thống cũng ghi nhận {total_pat} mẫu tối ưu lịch sử (pattern memory)."
        if crit_pat:
            labels_str = ", ".join([p["label"] for p in crit_pat[:3]])
            pat_str += f" Đặc biệt, các lỗi cấu trúc kỹ thuật lặp lại cần ưu tiên sửa đổi: {labels_str}."
        elif rec_pat:
            labels_str = ", ".join([p["label"] for p in rec_pat[:3]])
            pat_str += f" Có các mẫu kỹ thuật lặp lại như: {labels_str}."
        memory_notes.append(pat_str)

    if outcome_tracking_ctx and outcome_tracking_ctx.get("total_outcomes", 0) > 0:
        completed_c = outcome_tracking_ctx.get("completed_count", 0)
        failed_c = outcome_tracking_ctx.get("failed_count", 0)
        delta_c = outcome_tracking_ctx.get("completed_with_delta_count", 0)
        pending_c = outcome_tracking_ctx.get("pending_count", 0)
        repeated_list_pending = outcome_tracking_ctx.get("repeated_pending_recommendations", [])

        if completed_c > 0:
            memory_notes.append(f"Đã hoàn thành {completed_c} khuyến nghị tối ưu (có {delta_c} khuyến nghị ghi nhận cải thiện chỉ số).")
        if failed_c > 0:
            memory_notes.append(f"Ghi nhận {failed_c} đề xuất tối ưu thất bại hoặc không hiệu quả trong lịch sử thực thi.")
        if pending_c > 0:
            memory_notes.append(f"Hiện còn {pending_c} khuyến nghị đang tồn đọng (chờ xử lý).")
        if len(repeated_list_pending) > 0:
            memory_notes.append(f"Có {len(repeated_list_pending)} khuyến nghị đang bị lặp lại liên tục nhưng chưa được giải quyết.")
    else:
        if completed_recs:
            memory_notes.append(f"Đã hoàn thành {len(completed_recs)} khuyến nghị trước đó (chỉ số được cải thiện).")
        if failed_recs:
            memory_notes.append(f"Ghi nhận {len(failed_recs)} khuyến nghị đã thất bại trong lịch sử thực thi, cần thay đổi giải pháp.")
                
    if memory_notes:
        summary += "Về lịch sử tối ưu: " + " ".join(memory_notes)
    else:
        if blockers:
            summary += "Hệ thống khuyến nghị tập trung giải quyết triệt để các rào cản kỹ thuật để giải phóng dòng chảy SEO."
        else:
            summary += "Website có cấu trúc kỹ thuật tương đối ổn định. Khuyến nghị tập trung sản xuất content gap và tối ưu CTR để bứt phá lượt nhấp."

    # 2. 7 Days Plan
    plan_7d = []
    day_idx = 1
    
    # Blockers first
    if blockers:
        for b in blockers[:3]:
            plan_7d.append({
                "day": f"Ngày {day_idx}-{day_idx+1}",
                "task": f"[{b['category']}] Khắc phục: {b['message']}. Giải pháp: {b['fix']}",
                "priority": "high",
                "impact": "Giúp công cụ tìm kiếm thu thập thông tin trơn tru hơn"
            })
            day_idx += 2

    # Quick Wins
    if quick_wins:
        for qw in quick_wins[:2]:
            if day_idx <= 6:
                plan_7d.append({
                    "day": f"Ngày {day_idx}-{day_idx+1}",
                    "task": f"Tối ưu hóa bài viết chứa từ khóa '{qw['keyword']}': Chèn thêm từ khóa LSI, cải thiện heading và bổ sung liên kết nội bộ.",
                    "priority": "medium",
                    "impact": "Đẩy từ khóa hiện tại đang ở hạng tốt lên Top cao hơn"
                })
                day_idx += 2

    # Rest of week
    if len(plan_7d) < 3:
        plan_7d.append({
            "day": "Ngày 5-7",
            "task": "Tối ưu hóa các thẻ tiêu đề (Title) có CTR thấp để thu hút lượt click chuột từ SERP.",
            "priority": "medium",
            "impact": "Tăng traffic tự nhiên mà không cần viết bài mới"
        })

    # 3. 30 Days Plan
    plan_30d = []
    
    # Week 1
    plan_30d.append({
        "week": "Tuần 1",
        "task": "Giải quyết dứt điểm các lỗi 404, schema metadata bị thiếu và cải thiện điểm Core Web Vitals trên Mobile.",
        "priority": "high",
        "impact": "Củng cố nền móng Technical SEO, tăng điểm chất lượng website."
    })
    # Week 2
    plan_30d.append({
        "week": "Tuần 2",
        "task": (
            "Triển khai tối ưu lại toàn bộ danh sách từ khóa Quick Wins. "
            "Bổ sung FAQ Schema bằng GEO Optimizer cho các trang đích quan trọng."
        ),
        "priority": "high",
        "impact": "Bứt phá thứ hạng từ khóa mục tiêu đang ở trang 2 lên trang 1 Google."
    })
    # Week 3
    if opportunities:
        opp_str = ", ".join([f"'{o['keyword']}'" for o in opportunities[:2]])
        task_str = f"Sản xuất bài viết mới cho các cụm chủ đề tiềm năng: {opp_str}."
    else:
        task_str = "Nghiên cứu khoảng trống nội dung (content gaps) so với 3 đối thủ đứng đầu ngành."

    plan_30d.append({
        "week": "Tuần 3",
        "task": task_str,
        "priority": "medium",
        "impact": "Mở rộng độ phủ từ khóa và thu hút tệp khách hàng tiềm năng mới."
    })
    # Week 4
    plan_30d.append({
        "week": "Tuần 4",
        "task": "Kiểm tra dữ liệu Google Analytics 4 để đo lường hiệu quả tương tác sau tối ưu. Chạy thử nghiệm A/B Testing SEO cho tiêu đề.",
        "priority": "medium",
        "impact": "Đảm bảo tỷ lệ chuyển đổi tăng trưởng bền vững."
    })

    return {
        "summary": summary,
        "action_plan_7d": plan_7d,
        "action_plan_30d": plan_30d
    }


def normalize_text_for_matching(text: str) -> str:
    if not text:
        return ""
    # Lowercase, strip tags/brackets like [Technical], strip non-alphanumeric, and extra spaces
    text = text.lower().strip()
    # Remove brackets content e.g. [Technical]
    text = re.sub(r"^\[.*?\]", "", text)
    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)
    # Collapse multiple spaces
    text = " ".join(text.split())
    return text


def match_task_to_history(
    task_text: str,
    db: Session,
    site_id: int
) -> Tuple[bool, int, int, Optional[str]]:
    """
    Checks if a recommendation task text matches any historical outcomes in the database.
    Returns: (is_recurring, seen_before_count, pending_before_count, history_note)
    """
    if not db or not site_id:
        return False, 0, 0, None
        
    norm_task = normalize_text_for_matching(task_text)
    if not norm_task:
        return False, 0, 0, None
        
    from core.models import SEORecommendationOutcome
    
    # Fetch all past recommendation outcomes for this site
    all_recs = db.query(
        SEORecommendationOutcome.recommendation_text,
        SEORecommendationOutcome.status
    ).filter(
        SEORecommendationOutcome.site_id == site_id
    ).all()
    
    seen_count = 0
    pending_count = 0
    
    for r in all_recs:
        norm_r = normalize_text_for_matching(r.recommendation_text)
        
        is_match = False
        if norm_task == norm_r:
            is_match = True
        else:
            # Word overlap ratio (simple Jaccard distance/overlap)
            words_task = set(norm_task.split())
            words_r = set(norm_r.split())
            if words_task and words_r:
                intersection = words_task.intersection(words_r)
                overlap_ratio = len(intersection) / max(len(words_task), len(words_r))
                if overlap_ratio >= 0.7:  # 70% word overlap threshold
                    is_match = True
                    
        if is_match:
            seen_count += 1
            if r.status == "pending":
                pending_count += 1
                
    if seen_count > 0:
        is_recurring = True
        if pending_count > 0:
            history_note = f"Khuyến nghị tương tự đang pending {pending_count} lần từ trước"
        else:
            history_note = f"Khuyến nghị này đã từng xuất hiện {seen_count} lần trong lịch sử"
    else:
        is_recurring = False
        history_note = "Đây là khuyến nghị mới, chưa thấy trong history"
        
    return is_recurring, seen_count, pending_count, history_note


def is_task_completed(task_text: str, completed_texts: List[str]) -> bool:
    """Helper to check if a task is already completed based on Jaccard word overlap."""
    norm_task = normalize_text_for_matching(task_text)
    if not norm_task:
        return False
    for completed in completed_texts:
        norm_comp = normalize_text_for_matching(completed)
        if norm_task == norm_comp:
            return True
        words_task = set(norm_task.split())
        words_comp = set(norm_comp.split())
        if words_task and words_comp:
            intersection = words_task.intersection(words_comp)
            overlap_ratio = len(intersection) / max(len(words_task), len(words_comp))
            if overlap_ratio >= 0.7:
                return True
    return False


def match_task_to_patterns(
    task_text: str,
    pattern_memory_ctx: Optional[Dict[str, Any]]
) -> Tuple[bool, Optional[str], int, Optional[str]]:
    """
    Checks if a recommendation task matches any pattern in pattern_memory_ctx.
    Returns: (pattern_related, pattern_label, pattern_occurrences, pattern_note)
    """
    if not pattern_memory_ctx or not pattern_memory_ctx.get("total_patterns", 0):
        return False, None, 0, None
        
    norm_task = task_text.lower()
    
    # Match keywords inside task text to guess pattern types
    matched_type = None
    if any(w in norm_task for w in ["speed", "performance", "tốc độ", "tải trang", "cwv", "core web vitals", "lcp", "cls", "inp"]):
        matched_type = "cwv_pattern"
    elif any(w in norm_task for w in ["schema", "json-ld", "structured data", "dữ liệu cấu trúc", "faq page", "breadcrumb"]):
        matched_type = "schema_pattern"
    elif any(w in norm_task for w in ["ctr", "click", "nhấp", "tiêu đề", "title", "description", "meta", "snippet"]):
        matched_type = "ctr_pattern"
    elif any(w in norm_task for w in ["khuyến nghị", "lặp lại", "tồn đọng", "re-optimize"]):
        matched_type = "recommendation_pattern"
        
    if not matched_type:
        return False, None, 0, None
        
    # Check if there is a pattern of this type in our list
    # Prefer recurring patterns
    recurring_patterns = pattern_memory_ctx.get("recurring_patterns", [])
    for p in recurring_patterns:
        if p["type"] == matched_type:
            return (
                True,
                p["label"],
                p["occurrences"],
                f"Lỗi cấu trúc lặp lại: '{p['label']}' phát hiện {p['occurrences']} lần"
            )
            
    # Check other recent patterns if no recurring matched
    recent_patterns = pattern_memory_ctx.get("recent_patterns", [])
    from collections import Counter
    recent_counts = Counter(p["pattern_label"] for p in recent_patterns)
    for p in recent_patterns:
        if p["pattern_type"] == matched_type:
            lbl = p["pattern_label"]
            cnt = recent_counts[lbl]
            return (
                True,
                lbl,
                cnt,
                f"Lỗi cấu trúc: '{lbl}' phát hiện {cnt} lần"
            )
            
    return False, None, 0, None


def build_structural_pattern_summary(pattern_memory_ctx: Optional[Dict[str, Any]]) -> str:
    """
    Builds a clean deterministic Vietnamese summary of the site's repeating structural patterns.
    """
    if not pattern_memory_ctx or pattern_memory_ctx.get("total_patterns", 0) == 0:
        return "Website chưa ghi nhận mẫu tối ưu hoặc lỗi cấu trúc lặp lại trong lịch sử."
        
    total_pat = pattern_memory_ctx.get("total_patterns", 0)
    crit_pat = pattern_memory_ctx.get("critical_structural_patterns", [])
    rec_pat = pattern_memory_ctx.get("recurring_patterns", [])
    unresolved_rec = pattern_memory_ctx.get("unresolved_recommendation_patterns", [])
    
    parts = [f"Phát hiện tổng cộng {total_pat} mẫu kỹ thuật lịch sử."]
    
    if crit_pat:
        labels = [p["label"] for p in crit_pat]
        crit_list = []
        if "mobile_cwv_needs_improvement" in labels:
            crit_list.append("hiệu suất tốc độ di động (Core Web Vitals) chưa đạt chuẩn")
        if "schema_validation_failed_or_missing" in labels:
            crit_list.append("cấu trúc Schema JSON-LD bị thiếu hoặc lỗi cấu pháp")
        if "low_ctr_high_impression_query" in labels:
            crit_list.append("nhóm từ khóa thứ hạng tốt nhưng CTR thấp")
            
        if crit_list:
            parts.append(f"Ghi nhận các lỗi cấu trúc lặp lại nhiều lần bao gồm: {', '.join(crit_list)}.")
        else:
            labels_str = ", ".join([p["label"] for p in crit_pat[:3]])
            parts.append(f"Ghi nhận lỗi kỹ thuật lặp lại: {labels_str}.")
            
    if unresolved_rec:
        parts.append(f"Có {len(unresolved_rec)} nhóm khuyến nghị đang bị tồn đọng và lặp lại qua các lần phân tích.")
        
    if not crit_pat and not unresolved_rec:
        if rec_pat:
            labels_str = ", ".join([p["label"] for p in rec_pat[:3]])
            parts.append(f"Có các mẫu kỹ thuật lặp lại nhẹ như: {labels_str}.")
        else:
            parts.append("Các mẫu kỹ thuật đã ghi nhận tương đối ổn định và không phát hiện lỗi cấu trúc lặp lại nghiêm trọng.")
            
    return " ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Main Async Orchestration
# ─────────────────────────────────────────────────────────────────────────────

async def analyze_site(
    site_url: Optional[str] = None,
    target_keyword: Optional[str] = None,
    days: int = 30,
    include_gsc: bool = True,
    include_ga4: bool = True,
    include_serp: bool = True,
    include_rank_tracking: bool = True,
    include_technical: bool = True,
    include_cwv: bool = True,
    include_schema: bool = True,
    include_usage_history: bool = True,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Consolidates data sources concurrently, builds clean DTO, computes
    deterministic insights, and returns complete advisor response.
    """
    
    # 1. Resolve active or default site URL
    url = normalize_site_url(site_url)
    analyzed_at = datetime.now().isoformat()

    # Define tasks to gather concurrently
    tasks = []
    
    # Task mapping so we can unpack easily
    task_keys = []

    # A. GSC
    if include_gsc:
        tasks.append(fetch_gsc(url, days))
        task_keys.append("gsc")
    else:
        tasks.append(asyncio.sleep(0, result=("disabled", None)))
        task_keys.append("gsc")

    # B. GA4
    if include_ga4:
        tasks.append(fetch_ga4(days))
        task_keys.append("ga4")
    else:
        tasks.append(asyncio.sleep(0, result=("disabled", None)))
        task_keys.append("ga4")

    # C. SERP (Requires target_keyword constraint)
    if include_serp and target_keyword and target_keyword.strip():
        tasks.append(fetch_serp(target_keyword.strip()))
        task_keys.append("serp")
    else:
        tasks.append(asyncio.sleep(0, result=("disabled", None)))
        task_keys.append("serp")

    # D. Technical SEO
    if include_technical:
        tasks.append(fetch_technical(url))
        task_keys.append("technical")
    else:
        tasks.append(asyncio.sleep(0, result=("disabled", None)))
        task_keys.append("technical")

    # E. Core Web Vitals
    if include_cwv:
        tasks.append(fetch_cwv(url))
        task_keys.append("cwv")
    else:
        tasks.append(asyncio.sleep(0, result=("disabled", None)))
        task_keys.append("cwv")

    # F. Schema
    if include_schema:
        tasks.append(fetch_schema(url))
        task_keys.append("schema")
    else:
        tasks.append(asyncio.sleep(0, result=("disabled", None)))
        task_keys.append("schema")

    # G. Broken Links
    if include_technical: # Follows tech flag or can be isolated
        tasks.append(fetch_broken_links(url))
        task_keys.append("broken")
    else:
        tasks.append(asyncio.sleep(0, result=("disabled", None)))
        task_keys.append("broken")

    # H. Rank Tracking
    if include_rank_tracking:
        tasks.append(fetch_rank_tracking(url))
        task_keys.append("rank_tracking")
    else:
        tasks.append(asyncio.sleep(0, result=("disabled", None)))
        task_keys.append("rank_tracking")

    # I. Usage History
    if include_usage_history:
        tasks.append(fetch_usage_history())
        task_keys.append("usage")
    else:
        tasks.append(asyncio.sleep(0, result=("disabled", None)))
        task_keys.append("usage")

    # 2. Gather All Tasks Concurrently
    results = await asyncio.gather(*tasks)
    
    # Unpack into map
    results_map = dict(zip(task_keys, results))

    # 3. Build normalized data contract snapshot
    snapshot = build_normalized_snapshot(
        url=url,
        gsc=results_map["gsc"],
        ga4=results_map["ga4"],
        serp=results_map["serp"],
        tech=results_map["technical"],
        cwv=results_map["cwv"],
        schema=results_map["schema"],
        broken=results_map["broken"],
        rank_tracking=results_map["rank_tracking"],
        usage=results_map["usage"]
    )

    # 4. Compute deterministic insights
    top_issues, quick_wins, tech_blockers, content_opps, confidence = compute_deterministic_insights(snapshot)

    # Build source statuses
    source_status = {}
    for key in ["gsc", "ga4", "technical", "cwv", "schema", "broken", "rank_tracking", "usage"]:
        status_val = results_map.get(key, ("disabled", None))[0]
        source_status[key] = status_val

    # SERP status custom mapping
    if not (include_serp and target_keyword and target_keyword.strip()):
        source_status["serp"] = "disabled"
    else:
        source_status["serp"] = results_map.get("serp", ("disabled", None))[0]

    # Fetch memory context if db is available
    keyword_memory_ctx = None
    recommendation_memory_ctx = None
    pattern_memory_ctx = None
    outcome_tracking_ctx = None
    completed_recs = []
    failed_recs = []
    if db is not None:
        try:
            from core.seo_intelligence import (
                build_keyword_memory_context,
                build_recommendation_memory_context,
                build_pattern_memory_context,
                build_outcome_tracking_context,
                normalize_site_domain
            )
            keyword_memory_ctx = build_keyword_memory_context(db, url)
            recommendation_memory_ctx = build_recommendation_memory_context(db, url)
            pattern_memory_ctx = build_pattern_memory_context(db, url)
            outcome_tracking_ctx = build_outcome_tracking_context(db, url)
            
            # Fetch completed and failed rec outcomes to filter and pass to AI synthesis
            from core.models import ManagedSite, SEORecommendationOutcome
            target_norm = normalize_site_domain(url)
            site = db.query(ManagedSite).filter(ManagedSite.url.like(f"%{target_norm}%")).first()
            if site:
                completed_recs = db.query(SEORecommendationOutcome).filter(
                    SEORecommendationOutcome.site_id == site.id,
                    SEORecommendationOutcome.status == "completed"
                ).order_by(SEORecommendationOutcome.updated_at.desc()).limit(10).all()
                failed_recs = db.query(SEORecommendationOutcome).filter(
                    SEORecommendationOutcome.site_id == site.id,
                    SEORecommendationOutcome.status == "failed"
                ).order_by(SEORecommendationOutcome.updated_at.desc()).limit(10).all()
        except Exception as e:
            print(f"[ADVISOR MEMORY CONTEXT ERROR] Failed to fetch memory context: {e}", flush=True)

    # Filter out completed recommendations from deterministic insights lists
    completed_texts = [r.recommendation_text for r in completed_recs]
    if completed_texts:
        top_issues = [issue for issue in top_issues if not is_task_completed(issue["message"], completed_texts) and not is_task_completed(issue.get("fix", ""), completed_texts)]
        quick_wins = [qw for qw in quick_wins if not is_task_completed(qw["action"], completed_texts) and not is_task_completed(qw["keyword"], completed_texts)]
        tech_blockers = [b for b in tech_blockers if not is_task_completed(b["message"], completed_texts) and not is_task_completed(b.get("fix", ""), completed_texts)]
        content_opps = [opp for opp in content_opps if not is_task_completed(opp["reason"], completed_texts) and not is_task_completed(opp["keyword"], completed_texts)]

    # 5. Executive Synthesis (Groq vs Template Fallback)
    summary = ""
    action_7d = []
    action_30d = []
    ai_provider = "none"

    if os.getenv("GROQ_API_KEY"):
        # Format a tight diagnostic payload for Groq
        payload = {
            "site_url": url,
            "days": days,
            "target_keyword": target_keyword,
            "deterministic_top_issues": top_issues[:5],
            "deterministic_quick_wins": quick_wins[:5],
            "deterministic_technical_blockers": tech_blockers[:5],
            "deterministic_content_opportunities": content_opps[:5],
            "source_status": source_status
        }
        
        prompt = (
            f"Hãy cố vấn chiến lược cho website này dựa trên snapshot chẩn đoán thực tế:\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        )
        
        # If memory context is present, add it to the prompt
        has_keyword_rec_mem = (keyword_memory_ctx and keyword_memory_ctx["total_keyword_records"] > 0) or (recommendation_memory_ctx and recommendation_memory_ctx["total_recommendations"] > 0)
        has_pattern_mem = pattern_memory_ctx and pattern_memory_ctx["total_patterns"] > 0
        has_outcomes_history = len(completed_recs) > 0 or len(failed_recs) > 0
        
        if has_keyword_rec_mem or has_pattern_mem or has_outcomes_history or outcome_tracking_ctx:
            memory_payload = {}
            if keyword_memory_ctx:
                memory_payload.update({
                    "total_past_keywords_recorded": keyword_memory_ctx["total_keyword_records"],
                    "top_recurring_queries": [k["keyword"] for k in keyword_memory_ctx["top_recurring_keywords"][:5]],
                    "recurring_quick_wins": [k["keyword"] for k in keyword_memory_ctx["recurring_quick_wins"][:5]]
                })
            if recommendation_memory_ctx:
                memory_payload.update({
                    "total_past_recommendations": recommendation_memory_ctx["total_recommendations"],
                    "pending_tasks": [r["recommendation_text"] for r in recommendation_memory_ctx["pending_recommendations"][:5]],
                    "already_recommended_multiple_times": [r["recommendation_text"] for r in recommendation_memory_ctx["repeated_recommendations"][:5]]
                })
            if pattern_memory_ctx:
                memory_payload.update({
                    "total_patterns_recorded": pattern_memory_ctx["total_patterns"],
                    "recurring_technical_patterns": [p["label"] for p in pattern_memory_ctx["recurring_patterns"][:5]],
                    "critical_structural_patterns": [p["label"] for p in pattern_memory_ctx["critical_structural_patterns"][:5]]
                })
            if completed_recs:
                completed_payload = []
                for r in completed_recs:
                    delta = {}
                    if r.measured_delta_json:
                        try:
                            delta = json.loads(r.measured_delta_json)
                        except Exception:
                            delta = {"raw": r.measured_delta_json}
                    completed_payload.append({
                        "task": r.recommendation_text,
                        "completed_at": r.reviewed_at.isoformat() if r.reviewed_at else (r.updated_at.isoformat() if r.updated_at else None),
                        "measured_delta": delta
                    })
                memory_payload["completed_recommendation_outcomes"] = completed_payload
            if failed_recs:
                memory_payload["failed_recommendation_outcomes"] = [
                    {
                        "task": r.recommendation_text,
                        "execution_note": r.execution_note,
                        "failed_at": r.reviewed_at.isoformat() if r.reviewed_at else (r.updated_at.isoformat() if r.updated_at else None)
                    } for r in failed_recs
                ]
            if outcome_tracking_ctx:
                memory_payload["outcome_tracking_history"] = {
                    "total_outcomes": outcome_tracking_ctx.get("total_outcomes", 0),
                    "pending_count": outcome_tracking_ctx.get("pending_count", 0),
                    "in_progress_count": outcome_tracking_ctx.get("in_progress_count", 0),
                    "completed_count": outcome_tracking_ctx.get("completed_count", 0),
                    "failed_count": outcome_tracking_ctx.get("failed_count", 0),
                    "completed_with_delta_count": outcome_tracking_ctx.get("completed_with_delta_count", 0),
                    "successful_recommendation_types": outcome_tracking_ctx.get("successful_recommendation_types", {}),
                    "failed_recommendation_types": outcome_tracking_ctx.get("failed_recommendation_types", {}),
                    "repeated_pending_recommendations": outcome_tracking_ctx.get("repeated_pending_recommendations", [])
                }
                
            prompt += (
                f"Dưới đây là DỮ LIỆU LỊCH SỬ/TRÍ NHỚ SEO & LỊCH SỬ THỰC THI (SEO Memory & Outcome History) của website này:\n"
                f"{json.dumps(memory_payload, ensure_ascii=False, indent=2)}\n\n"
                f"HƯỚNG DẪN DÙNG TRÍ NHỚ LỊCH SỬ & LỊCH SỬ THỰC THI:\n"
                f"1. Xác định những vấn đề mới xuất hiện so với những vấn đề lặp lại.\n"
                f"2. Nếu có 'pending_tasks' hoặc 'repeated_pending_recommendations' quan trọng chưa được xử lý, hãy nhắc nhở người dùng ưu tiên xử lý chúng trong phần tóm tắt (summary) thay vì tiếp tục đưa ra đề xuất mới trùng lặp.\n"
                f"3. Thiết lập kế hoạch hành động thực tế, ưu tiên giải quyết các công việc đang dở dang (pending) và tránh lặp lại các khuyến nghị đã đưa ra nhiều lần mà không có cập nhật mới.\n"
                f"4. Nếu phát hiện các lỗi kỹ thuật lặp lại nhiều lần (như 'mobile_cwv_needs_improvement' hoặc 'schema_validation_failed_or_missing' hoặc 'low_ctr_high_impression_query' xuất hiện trong 'critical_structural_patterns' hoặc 'recurring_technical_patterns'), hãy nhấn mạnh chúng trong Summary như một lỗi cấu trúc nghiêm trọng (structural blocker) cần xử lý dứt điểm.\n"
                f"5. Tuyệt đối KHÔNG đề xuất lại các nhiệm vụ trùng lặp hoặc tương đồng với các nhiệm vụ đã hoàn thành ('completed_recommendation_outcomes'). Nếu các nhiệm vụ hoàn thành hoặc loại khuyến nghị hoàn thành ('successful_recommendation_types') có kết quả delta tốt, hãy ghi nhận trong Summary và ưu tiên đề xuất các hành động tương tự để nhân rộng kết quả.\n"
                f"6. Nếu phát hiện nhiệm vụ trong danh sách thất bại ('failed_recommendation_outcomes') hoặc thuộc loại thường thất bại ('failed_recommendation_types'), hãy thay đổi phương pháp tiếp cận hoặc đề xuất phương án khắc phục khác thay vì lặp lại y nguyên đề xuất cũ.\n\n"
            )
            
        prompt += f"Vui lòng trả về cấu trúc JSON tóm tắt điều hành + kế hoạch 7 ngày + kế hoạch 30 ngày cụ thể bằng Tiếng Việt."
        
        ai_resp = await asyncio.to_thread(_call_groq_advisor, prompt)
        if ai_resp:
            try:
                # Cleanup potential markdown ticks
                clean = ai_resp.strip()
                clean = re.sub(r'^```json?\s*', '', clean, flags=re.MULTILINE)
                clean = re.sub(r'```\s*$', '', clean, flags=re.MULTILINE)
                
                json_start = clean.find("{")
                json_end = clean.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    parsed = json.loads(clean[json_start:json_end])
                    summary = parsed.get("summary", "")
                    action_7d = parsed.get("action_plan_7d", [])
                    action_30d = parsed.get("action_plan_30d", [])
                    ai_provider = "groq"
            except Exception:
                pass  # Fallback to template on JSON parsing failures

    if not summary:
        # Fallback template-based synthesis
        ai_provider = "builtin_template"
        fallback = generate_fallback_summary(
            url=url,
            top_issues=top_issues,
            quick_wins=quick_wins,
            blockers=tech_blockers,
            opportunities=content_opps,
            keyword_memory_ctx=keyword_memory_ctx,
            recommendation_memory_ctx=recommendation_memory_ctx,
            pattern_memory_ctx=pattern_memory_ctx,
            completed_recs=completed_recs,
            failed_recs=failed_recs,
            outcome_tracking_ctx=outcome_tracking_ctx
        )
        summary = fallback["summary"]
        action_7d = fallback["action_plan_7d"]
        action_30d = fallback["action_plan_30d"]

    # 5.5 Post-process and enrich both Groq and fallback action plans with history metadata
    site_id = None
    all_outcomes = []
    if db is not None:
        try:
            from core.models import ManagedSite, SEORecommendationOutcome
            from core.seo_intelligence import normalize_site_domain
            target_norm = normalize_site_domain(url)
            site = db.query(ManagedSite).filter(ManagedSite.url.like(f"%{target_norm}%")).first()
            if site:
                site_id = site.id
                all_outcomes = db.query(SEORecommendationOutcome).filter(
                    SEORecommendationOutcome.site_id == site_id
                ).all()
        except Exception:
            pass
            
    enriched_7d = []
    if isinstance(action_7d, list):
        for item in action_7d:
            if isinstance(item, dict) and "task" in item:
                task_text = item["task"]
                is_rec, seen, pending, note = False, 0, 0, None
                is_pat, pat_label, pat_occ, pat_note = False, None, 0, None
                was_comp, comp_cnt, fail_cnt, has_delta, out_note = False, 0, 0, False, None
                if db is not None and site_id is not None:
                    try:
                        is_rec, seen, pending, note = match_task_to_history(task_text, db, site_id)
                        is_pat, pat_label, pat_occ, pat_note = match_task_to_patterns(task_text, pattern_memory_ctx)
                        was_comp, comp_cnt, fail_cnt, has_delta, out_note = match_task_to_outcomes(task_text, all_outcomes)
                    except Exception:
                        pass
                
                enriched_7d.append({
                    "day": item.get("day", ""),
                    "task": task_text,
                    "priority": item.get("priority", "medium"),
                    "impact": item.get("impact", ""),
                    "is_recurring": is_rec,
                    "seen_before_count": seen,
                    "pending_before_count": pending,
                    "history_note": note,
                    "pattern_related": is_pat,
                    "pattern_label": pat_label,
                    "pattern_occurrences": pat_occ,
                    "pattern_note": pat_note,
                    "was_completed_before": was_comp,
                    "completed_before_count": comp_cnt,
                    "failed_before_count": fail_cnt,
                    "has_measured_delta_before": has_delta,
                    "outcome_note": out_note
                })
            else:
                enriched_7d.append(item)
                
    enriched_30d = []
    if isinstance(action_30d, list):
        for item in action_30d:
            if isinstance(item, dict) and "task" in item:
                task_text = item["task"]
                is_rec, seen, pending, note = False, 0, 0, None
                is_pat, pat_label, pat_occ, pat_note = False, None, 0, None
                was_comp, comp_cnt, fail_cnt, has_delta, out_note = False, 0, 0, False, None
                if db is not None and site_id is not None:
                    try:
                        is_rec, seen, pending, note = match_task_to_history(task_text, db, site_id)
                        is_pat, pat_label, pat_occ, pat_note = match_task_to_patterns(task_text, pattern_memory_ctx)
                        was_comp, comp_cnt, fail_cnt, has_delta, out_note = match_task_to_outcomes(task_text, all_outcomes)
                    except Exception:
                        pass
                
                enriched_30d.append({
                    "week": item.get("week", ""),
                    "task": task_text,
                    "priority": item.get("priority", "medium"),
                    "impact": item.get("impact", ""),
                    "is_recurring": is_rec,
                    "seen_before_count": seen,
                    "pending_before_count": pending,
                    "history_note": note,
                    "pattern_related": is_pat,
                    "pattern_label": pat_label,
                    "pattern_occurrences": pat_occ,
                    "pattern_note": pat_note,
                    "was_completed_before": was_comp,
                    "completed_before_count": comp_cnt,
                    "failed_before_count": fail_cnt,
                    "has_measured_delta_before": has_delta,
                    "outcome_note": out_note
                })
            else:
                enriched_30d.append(item)
                
    action_7d = enriched_7d
    action_30d = enriched_30d

    if db is not None:
        try:
            from core.seo_intelligence import (
                ingest_raw_snapshot,
                normalize_site_page,
                ingest_normalized_issue,
                ingest_advisor_run,
                ingest_derived_signal,
                record_recommendation_memory,
                record_keyword_memory,
                record_recommendation_outcome,
                record_pattern_memory
            )
            from urllib.parse import urljoin

            # 1. Save Advisor Run History first to get its ID
            run_result = {
                "confidence_score": confidence,
                "summary": summary,
                "action_plan_7d": action_7d,
                "action_plan_30d": action_30d,
                "ai_provider": ai_provider
            }
            run_record = ingest_advisor_run(db, url, days, target_keyword, run_result)
            advisor_run_id = run_record.id if run_record else None

            # 2. Save Raw Snapshots
            for src_name, src_tuple in results_map.items():
                if src_tuple[0] == "ok" and src_tuple[1]:
                    ingest_raw_snapshot(db, url, src_name, src_tuple[1])

            # 3. Save Normalized Pages (top pages from GA4 + audited target from Technical Scan)
            saved_urls = set()
            
            # A. Audited target page from Technical Scan
            if results_map.get("technical") and results_map["technical"][0] == "ok" and results_map["technical"][1]:
                tech_data = results_map["technical"][1]
                tech_url = tech_data.get("final_url") or tech_data.get("url") or url
                if not tech_url.startswith("http"):
                    tech_url = urljoin(url, tech_url)
                
                meta_details = tech_data.get("breakdown", {}).get("meta_tags", {}).get("details", {})
                tech_title = meta_details.get("title")
                tech_desc = meta_details.get("description")
                
                if tech_url:
                    normalize_site_page(db, url, tech_url, title=tech_title, meta_description=tech_desc)
                    saved_urls.add(tech_url)
                    
            # B. Top Pages from GA4
            for page in snapshot["ga4"].get("top_pages", []):
                path = page.get("path", "")
                if not path:
                    continue
                full_page_url = urljoin(url, path)
                title = page.get("title")
                
                # normalize_site_page accepts title/description and ignores them if None. 
                # Since GA4 doesn't provide meta description, we pass None to avoid overwriting existing ones.
                normalize_site_page(db, url, full_page_url, title=title, meta_description=None)
                saved_urls.add(full_page_url)

            # 4. Save Normalized Issues
            for issue in snapshot["technical"].get("critical_issues", []):
                ingest_normalized_issue(
                    db, url, 
                    page_url=issue.get("page_url") if "page_url" in issue else None, 
                    category=issue.get("category", "Technical"),
                    severity="critical",
                    message=issue.get("message", ""),
                    fix_action=issue.get("fix")
                )
            for issue in snapshot["technical"].get("warnings", []):
                ingest_normalized_issue(
                    db, url, 
                    page_url=issue.get("page_url") if "page_url" in issue else None, 
                    category=issue.get("category", "Technical"),
                    severity="warning",
                    message=issue.get("message", ""),
                    fix_action=issue.get("fix")
                )

            # 5. Save Derived Signals (passing advisor_run_id for historical snapshots)
            for qw in quick_wins:
                ingest_derived_signal(db, url, "quick_wins", qw["keyword"], qw, advisor_run_id=advisor_run_id)
            for issue in top_issues:
                if "CTR" in issue.get("message", ""):
                    ingest_derived_signal(db, url, "ctr_opportunity", issue["message"], issue, advisor_run_id=advisor_run_id)
            for blocker in tech_blockers:
                ingest_derived_signal(db, url, "technical_blockers", blocker["message"], blocker, advisor_run_id=advisor_run_id)

            # 6. Save Recommendation Memory (from action_plan_7d and action_plan_30d)
            def parse_rule_name(task_str: str, default_rule: str) -> str:
                match = re.match(r"^\[(.*?)\]", task_str)
                if match:
                    return f"{default_rule}_{match.group(1).lower().replace(' ', '_')}"
                return default_rule

            # Process 7-day action plan
            if isinstance(action_7d, list):
                for item in action_7d:
                    if isinstance(item, dict) and "task" in item:
                        task_text = item["task"]
                        rule_name = parse_rule_name(task_text, "action_plan_7d")
                        record_recommendation_memory(
                            db, url, 
                            rule_name=rule_name, 
                            recommendation_text=task_text, 
                            outcome="pending"
                        )
                        
            # Process 30-day action plan
            if isinstance(action_30d, list):
                for item in action_30d:
                    if isinstance(item, dict) and "task" in item:
                        task_text = item["task"]
                        rule_name = parse_rule_name(task_text, "action_plan_30d")
                        record_recommendation_memory(
                            db, url, 
                            rule_name=rule_name, 
                            recommendation_text=task_text, 
                            outcome="pending"
                        )

            # 7. Save Keyword Memory (Phase 1)
            gsc_data = snapshot.get("gsc", {})
            if gsc_data:
                # Build trending lookup for trend_direction mapping
                trending_lookup = {}
                if results_map.get("gsc") and results_map["gsc"][0] == "ok" and results_map["gsc"][1]:
                    for t_q in results_map["gsc"][1].get("trending", []):
                        trending_lookup[t_q["keyword"]] = "up" if t_q.get("change_percent", 0) > 0 else "down"

                # A. GSC Quick Wins
                for qw in gsc_data.get("quick_wins", []):
                    record_keyword_memory(
                        db=db,
                        site_url=url,
                        keyword=qw["keyword"],
                        source="gsc",
                        opportunity_type="quick_win",
                        clicks=qw.get("clicks", 0),
                        impressions=qw.get("impressions", 0),
                        ctr=qw.get("ctr", 0.0),
                        avg_position=qw.get("position", 0.0),
                        advisor_run_id=advisor_run_id,
                        trend_direction=trending_lookup.get(qw["keyword"]),
                        confidence_score=90.0,
                        evidence_json={
                            "opportunity_score": qw.get("opportunity_score"),
                            "commercial_intent": qw.get("commercial_intent"),
                            "priority": qw.get("priority")
                        }
                    )

                # B. GSC Top Queries and Low CTR High Impression Opportunities
                for q in gsc_data.get("top_queries", []):
                    is_low_ctr = q.get("position", 0.0) <= 10 and q.get("impressions", 0) >= 150 and q.get("ctr", 0.0) < 2.0
                    
                    if is_low_ctr:
                        record_keyword_memory(
                            db=db,
                            site_url=url,
                            keyword=q["keyword"],
                            source="gsc",
                            opportunity_type="low_ctr_high_impression",
                            clicks=q.get("clicks", 0),
                            impressions=q.get("impressions", 0),
                            ctr=q.get("ctr", 0.0),
                            avg_position=q.get("position", 0.0),
                            advisor_run_id=advisor_run_id,
                            trend_direction=trending_lookup.get(q["keyword"]),
                            confidence_score=85.0,
                            evidence_json={
                                "clicks": q.get("clicks", 0),
                                "impressions": q.get("impressions", 0),
                                "ctr": q.get("ctr", 0.0),
                                "position": q.get("position", 0.0),
                                "threshold_ctr": 2.0,
                                "threshold_impressions": 150
                            }
                        )
                    else:
                        # Save only if it meets noise threshold (clicks >= 10 or impressions >= 100)
                        if q.get("clicks", 0) >= 10 or q.get("impressions", 0) >= 100:
                            record_keyword_memory(
                                db=db,
                                site_url=url,
                                keyword=q["keyword"],
                                source="gsc",
                                opportunity_type="top_query",
                                clicks=q.get("clicks", 0),
                                impressions=q.get("impressions", 0),
                                ctr=q.get("ctr", 0.0),
                                avg_position=q.get("position", 0.0),
                                advisor_run_id=advisor_run_id,
                                trend_direction=trending_lookup.get(q["keyword"]),
                                confidence_score=80.0,
                                evidence_json={
                                    "clicks": q.get("clicks", 0),
                                    "impressions": q.get("impressions", 0),
                                    "ctr": q.get("ctr", 0.0),
                                    "position": q.get("position", 0.0)
                                }
                            )

            # 8. Save Recommendation Outcomes (Phase 1)
            def parse_rec_type(task_str: str, default_type: str) -> str:
                match = re.match(r"^\[(.*?)\]", task_str)
                if match:
                    return match.group(1)
                return default_type

            def extract_context_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
                # Strict URL check
                url_match = re.search(r'https?://[^\s,\)\]]+', text)
                ext_url = url_match.group(0) if url_match else None
                
                # Verify URL domain match strictly if found
                if ext_url:
                    try:
                        target_domain = normalize_site_domain(url)
                        ext_domain = normalize_site_domain(ext_url)
                        if target_domain != ext_domain:
                            ext_url = None
                    except Exception:
                        ext_url = None
                        
                # Keyword check: strictly match quotes, e.g. 'keyword' or "keyword" or «keyword» or “keyword”
                kw_match = re.search(r'[\'"`“«]([^\'"`”»]{3,40})[\'"`”»]', text)
                ext_kw = kw_match.group(1) if kw_match else None
                
                return ext_url, ext_kw

            # Process 7-day action plan for outcomes
            if isinstance(action_7d, list):
                for item in action_7d:
                    if isinstance(item, dict) and "task" in item:
                        task_text = item["task"]
                        priority = item.get("priority")
                        impact = item.get("impact")
                        rec_type = parse_rec_type(task_text, "action_plan_7d")
                        ext_url, ext_kw = extract_context_from_text(task_text)
                        record_recommendation_outcome(
                            db=db,
                            site_url=url,
                            recommendation_type=rec_type,
                            recommendation_text=task_text,
                            advisor_run_id=advisor_run_id,
                            priority=priority,
                            impact=impact,
                            page_url=ext_url,
                            keyword=ext_kw
                        )

            # Process 30-day action plan for outcomes
            if isinstance(action_30d, list):
                for item in action_30d:
                    if isinstance(item, dict) and "task" in item:
                        task_text = item["task"]
                        priority = item.get("priority")
                        impact = item.get("impact")
                        rec_type = parse_rec_type(task_text, "action_plan_30d")
                        ext_url, ext_kw = extract_context_from_text(task_text)
                        record_recommendation_outcome(
                            db=db,
                            site_url=url,
                            recommendation_type=rec_type,
                            recommendation_text=task_text,
                            advisor_run_id=advisor_run_id,
                            priority=priority,
                            impact=impact,
                            page_url=ext_url,
                            keyword=ext_kw
                        )

            # 9. Ingest SEO Pattern Memories (Phase 5) using real evidence
            # A. CTR pattern: Low CTR High Impression Queries
            for q in snapshot["gsc"].get("top_queries", []):
                is_low_ctr = q.get("position", 0.0) <= 10 and q.get("impressions", 0) >= 150 and q.get("ctr", 0.0) < 2.0
                if is_low_ctr:
                    record_pattern_memory(
                        db=db,
                        site_url=url,
                        pattern_type="ctr_pattern",
                        pattern_label="low_ctr_high_impression_query",
                        page_type=None,
                        search_intent=None,
                        source="search_console",
                        confidence_score=90.0,
                        pattern_payload={
                            "keyword": q["keyword"],
                            "clicks": q.get("clicks", 0),
                            "impressions": q.get("impressions", 0),
                            "ctr": q.get("ctr", 0.0),
                            "avg_position": q.get("position", 0.0)
                        },
                        advisor_run_id=advisor_run_id
                    )

            # B. CWV pattern: Mobile CWV needs improvement
            cwv_data = snapshot["technical"].get("cwv", {})
            if cwv_data and cwv_data.get("overall_status") in ("poor", "needs_improvement"):
                record_pattern_memory(
                    db=db,
                    site_url=url,
                    pattern_type="cwv_pattern",
                    pattern_label="mobile_cwv_needs_improvement",
                    page_type=None,
                    search_intent=None,
                    source="crawler",
                    confidence_score=85.0,
                    pattern_payload={
                        "overall_status": cwv_data.get("overall_status"),
                        "lighthouse_scores": cwv_data.get("lighthouse_scores", {}),
                        "metrics": cwv_data.get("metrics", {})
                    },
                    advisor_run_id=advisor_run_id
                )

            # C. Schema pattern: Invalid or missing schema
            schema_data = snapshot["technical"].get("schema", {})
            if schema_data and (not schema_data.get("valid", True) or schema_data.get("schemas_found", 0) == 0):
                record_pattern_memory(
                    db=db,
                    site_url=url,
                    pattern_type="schema_pattern",
                    pattern_label="schema_validation_failed_or_missing",
                    page_type=None,
                    search_intent=None,
                    source="crawler",
                    confidence_score=95.0,
                    pattern_payload={
                        "valid": schema_data.get("valid", False),
                        "schemas_found": schema_data.get("schemas_found", 0),
                        "errors": schema_data.get("errors", []),
                        "warnings": schema_data.get("warnings", [])
                    },
                    advisor_run_id=advisor_run_id
                )

            # D. Recommendation recurrence pattern: Highly recurring unresolved recommendation
            repeated_recs = recommendation_memory_ctx.get("repeated_recommendations", []) if recommendation_memory_ctx else []
            if repeated_recs:
                for rec_item in repeated_recs:
                    record_pattern_memory(
                        db=db,
                        site_url=url,
                        pattern_type="recommendation_pattern",
                        pattern_label="highly_recurring_unresolved_recommendation",
                        page_type=None,
                        search_intent=None,
                        source="advisor",
                        confidence_score=80.0,
                        pattern_payload={
                            "recommendation_text": rec_item.get("recommendation_text"),
                            "recommendation_type": rec_item.get("recommendation_type"),
                            "occurrences": rec_item.get("occurrences"),
                            "priority": rec_item.get("priority")
                        },
                        advisor_run_id=advisor_run_id
                    )

        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger("site_advisor")
            logger.error(f"[ADVISOR PERSISTENCE ERROR] Failed to save site intelligence data for {url}: {e}", exc_info=True)
            print(f"[ADVISOR PERSISTENCE ERROR] Failed to save site intelligence data for {url}: {e}", flush=True)
            traceback.print_exc()

    # Build memory response context
    memory_context = {
        "keyword_memory_records": keyword_memory_ctx.get("total_keyword_records", 0) if keyword_memory_ctx else 0,
        "recommendation_outcomes": recommendation_memory_ctx.get("total_recommendations", 0) if recommendation_memory_ctx else 0,
        "top_recurring_keywords": [k["keyword"] for k in keyword_memory_ctx.get("top_recurring_keywords", [])] if keyword_memory_ctx else [],
        "top_recurring_recommendation_types": list(recommendation_memory_ctx.get("top_recurring_types", {}).keys()) if recommendation_memory_ctx else [],
        "pending_recommendations_count": recommendation_memory_ctx.get("pending_recommendations_count", 0) if recommendation_memory_ctx else 0
    }
    recurring_opportunities = keyword_memory_ctx.get("top_recurring_keywords", []) if keyword_memory_ctx else []
    repeated_recommendations = recommendation_memory_ctx.get("repeated_recommendations", []) if recommendation_memory_ctx else []
    pending_recommendations = recommendation_memory_ctx.get("pending_recommendations", []) if recommendation_memory_ctx else []
    in_progress_recommendations = recommendation_memory_ctx.get("in_progress_recommendations", []) if recommendation_memory_ctx else []
    
    total_kw = memory_context["keyword_memory_records"]
    total_rec = memory_context["recommendation_outcomes"]
    pending_count = memory_context["pending_recommendations_count"]
    
    if total_kw == 0 and total_rec == 0:
        new_vs_recurring_summary = "Website chưa có dữ liệu lịch sử trong hệ thống (lần chạy đầu tiên)."
    else:
        new_vs_recurring_summary = (
            f"Hệ thống ghi nhận {total_kw} cơ hội từ khóa lịch sử và {total_rec} khuyến nghị đã đưa ra. "
            f"Hiện tại có {pending_count} khuyến nghị đang chờ xử lý (pending). "
            f"Phát hiện {len(repeated_recommendations)} khuyến nghị lặp lại nhiều lần."
        )

    pattern_memory_context = pattern_memory_ctx if pattern_memory_ctx else {
        "total_patterns": 0,
        "by_pattern_type": {},
        "top_pattern_labels": [],
        "recurring_patterns": [],
        "recent_patterns": [],
        "critical_structural_patterns": [],
        "unresolved_recommendation_patterns": []
    }
    recurring_patterns = pattern_memory_context.get("recurring_patterns", [])
    structural_pattern_summary = build_structural_pattern_summary(pattern_memory_ctx)
    completed_rec_summary, failed_rec_summary, effective_rec_summary = build_outcome_summaries(outcome_tracking_ctx)

    # Build roadmap tree & summary — Phase 10
    roadmap_tree = build_roadmap_tree(action_7d, action_30d)
    roadmap_summary = generate_roadmap_summary(roadmap_tree)

    return {
        "site_url": url,
        "analyzed_at": analyzed_at,
        "confidence": "high" if confidence >= 80 else ("medium" if confidence >= 50 else "low"),
        "confidence_score": confidence,
        "summary": summary,
        "top_issues": top_issues,
        "quick_wins": quick_wins,
        "technical_blockers": tech_blockers,
        "content_opportunities": content_opps,
        "action_plan_7d": action_7d,
        "action_plan_30d": action_30d,
        "data_snapshot": snapshot,
        "source_status": source_status,
        "ai_provider": ai_provider,
        "memory_context": memory_context,
        "recurring_opportunities": recurring_opportunities,
        "repeated_recommendations": repeated_recommendations,
        "pending_recommendations": pending_recommendations,
        "in_progress_recommendations": in_progress_recommendations,
        "new_vs_recurring_summary": new_vs_recurring_summary,
        "pattern_memory_context": pattern_memory_context,
        "recurring_patterns": recurring_patterns,
        "structural_pattern_summary": structural_pattern_summary,
        "outcome_tracking_context": outcome_tracking_ctx,
        "completed_recommendations_summary": completed_rec_summary,
        "failed_recommendations_summary": failed_rec_summary,
        "effective_recommendation_summary": effective_rec_summary,
        "roadmap_tree": roadmap_tree,
        "roadmap_summary": roadmap_summary
    }


# ─────────────────────────────────────────────────────────────────────────────
# Roadmap Tree & Grouping Helpers — Phase 10
# ─────────────────────────────────────────────────────────────────────────────

def get_stream_for_task(task_dict: dict) -> Tuple[str, str]:
    """
    Determine which roadmap workstream a task belongs to based on keywords and metadata.
    Returns (stream_id, stream_reason).
    """
    task_text = (task_dict.get("task") or "").lower()
    rec_type = (task_dict.get("recommendation_type") or "").lower()
    pattern_label = (task_dict.get("pattern_label") or "").lower()

    # 1. Execution Followup (monitoring, tracking KPI delta, checking completed/in_progress, following up)
    followup_keywords = ["followup", "follow-up", "outcome", "tracking", "monitor", "review", "check", "delta", "kpi", "đo lường", "kiểm tra", "theo dõi"]
    if any(kw in task_text for kw in followup_keywords):
        return "execution_followup", "Khuyến nghị liên quan đến việc theo dõi và đánh giá kết quả triển khai thực tế."

    # 2. Schema & Entity Trust
    schema_keywords = ["schema", "structured data", "json-ld", "json_ld", "faq", "entity", "trust", "author", "publisher", "structured_data"]
    if rec_type in schema_keywords or pattern_label in schema_keywords or any(kw in task_text for kw in schema_keywords):
        return "schema_and_entity_trust", "Tối ưu cấu trúc thực thể và khai báo dữ liệu có cấu trúc để Google định danh thực thể tốt hơn."

    # 3. Technical Foundation
    tech_keywords = ["cwv", "speed", "lcp", "inp", "fid", "cls", "404", "broken", "redirect", "technical", "https", "ssl", "crawl", "robots", "sitemap", "page speed", "load time", "broken_links", "pagespeed"]
    if rec_type in tech_keywords or pattern_label in tech_keywords or any(kw in task_text for kw in tech_keywords):
        return "technical_foundation", "Củng cố hạ tầng kỹ thuật, cải thiện trải nghiệm trang và tốc độ tải trang theo chỉ số PageSpeed."

    # 4. CTR & SERP Optimization
    ctr_keywords = ["ctr", "title", "meta", "description", "snippet", "click", "impression", "serp", "position", "meta_description", "meta_tags"]
    if rec_type in ctr_keywords or pattern_label in ctr_keywords or any(kw in task_text for kw in ctr_keywords):
        return "ctr_and_serp_optimization", "Tập trung tối ưu các yếu tố hiển thị trực quan để kích thích người dùng click chuột trên kết quả tìm kiếm."

    # 5. Content Expansion
    content_keywords = ["content", "article", "writer", "blog", "keyword", "expansion", "gap", "linkbuilding", "anchor", "outline", "seo target", "viết bài", "nội dung", "opportunity", "planner"]
    if rec_type in content_keywords or pattern_label in content_keywords or any(kw in task_text for kw in content_keywords):
        return "content_expansion", "Mở rộng mức độ bao phủ từ khóa và xây dựng nội dung chất lượng cao theo các cụm chủ đề."

    # Default fallback: If it's technical or content, route accordingly. If ambiguous, route to technical_foundation as general fixes.
    if any(kw in task_text for kw in ["sửa", "lỗi", "cấu hình", "fix", "update", "tối ưu"]):
        return "technical_foundation", "Cải thiện kỹ thuật chung nhằm tối ưu hóa tổng thể cấu trúc trang."
    return "content_expansion", "Tối ưu hóa và xây dựng nội dung xoay quanh các cơ hội từ khóa tiềm năng."


def build_roadmap_tree(action_7d: list, action_30d: list) -> dict:
    """Builds a prioritized, grouped roadmap tree structure from action plans."""
    streams_metadata = {
        "technical_foundation": {
            "title": "Nền tảng kỹ thuật & Tốc độ",
            "description": "Tối ưu hiệu suất Core Web Vitals, sửa lỗi thu thập dữ liệu và liên kết hỏng."
        },
        "schema_and_entity_trust": {
            "title": "Schema & Thực thể tin cậy",
            "description": "Cấu hình JSON-LD, FAQ Schema và gia tăng các tín hiệu xác thực thực thể."
        },
        "ctr_and_serp_optimization": {
            "title": "Tối ưu hóa CTR & SERP",
            "description": "Tinh chỉnh thẻ tiêu đề, mô tả và cấu trúc hiển thị trên kết quả tìm kiếm Google."
        },
        "content_expansion": {
            "title": "Mở rộng & Tối ưu nội dung",
            "description": "Xây dựng các cụm chủ đề (content cluster), viết bài mới và lấp đầy các khoảng trống nội dung."
        },
        "execution_followup": {
            "title": "Theo dõi & Thực thi hành động",
            "description": "Đánh giá tiến độ, kiểm tra các khuyến nghị đang thực hiện và đo lường kết quả."
        }
    }

    # Group all tasks from both 7d and 30d plans
    all_raw_tasks = []
    for item in (action_7d or []):
        item_copy = dict(item)
        item_copy["phase"] = "7d"
        all_raw_tasks.append(item_copy)

    for item in (action_30d or []):
        item_copy = dict(item)
        item_copy["phase"] = "30d"
        all_raw_tasks.append(item_copy)

    # Initialize streams mapping
    grouped_streams = {stream_id: [] for stream_id in streams_metadata.keys()}

    counter = 1
    for raw_task in all_raw_tasks:
        stream_id, stream_reason = get_stream_for_task(raw_task)
        
        # Base priority score calculation
        prio = (raw_task.get("priority") or "medium").lower()
        if prio == "high":
            score = 100
        elif prio == "medium":
            score = 50
        elif prio == "low":
            score = 10
        else:
            score = 30

        # Build priority reasons list
        priority_reasons = []

        # 1. Base Priority reason
        priority_reasons.append(f"Mức ưu tiên gốc: {prio.upper()}")

        # Priority modifiers
        pending_before_count = raw_task.get("pending_before_count") or 0
        if pending_before_count > 0:
            score += 20
            priority_reasons.append(f"Tồn đọng trong lịch sử ({pending_before_count} lần)")

        if raw_task.get("is_recurring"):
            score += 15
            priority_reasons.append("Khuyến nghị lặp lại (recurring)")

        if raw_task.get("pattern_related"):
            score += 15
            priority_reasons.append(f"Phát hiện mẫu lặp (pattern: {raw_task.get('pattern_label') or 'không rõ'})")

        was_completed = raw_task.get("was_completed_before") or False
        has_delta = raw_task.get("has_measured_delta_before") or False
        failed_count = raw_task.get("failed_before_count") or 0

        # Refined: only add points if has_measured_delta_before == True
        if has_delta:
            score += 25
            priority_reasons.append("Đã từng triển khai thành công và đo lường có cải thiện KPI (delta)")

        if stream_id == "technical_foundation":
            score += 10
            priority_reasons.append("Ưu tiên nền tảng kỹ thuật trước")
        elif stream_id == "schema_and_entity_trust":
            score += 5
            priority_reasons.append("Khai báo cấu hình Schema thực thể tin cậy")

        if failed_count > 0:
            penalty = 30 if failed_count > 1 else 15
            score -= penalty
            priority_reasons.append(f"Đã từng thất bại {failed_count} lần trong lịch sử")

        if was_completed and not raw_task.get("is_recurring"):
            score -= 25
            priority_reasons.append("Công việc không lặp lại đã được hoàn thành gần đây")

        # Normalize score
        score = max(1, score)

        # Build child object
        child = {
            "id": f"task_{counter:03d}",
            "phase": raw_task["phase"],
            "day": raw_task.get("day") if raw_task["phase"] == "7d" else None,
            "week": raw_task.get("week") if raw_task["phase"] == "30d" else None,
            "task": raw_task.get("task") or "",
            "priority": raw_task.get("priority") or "medium",
            "impact": raw_task.get("impact") or "Trung bình",
            "is_recurring": bool(raw_task.get("is_recurring")),
            "pending_before_count": pending_before_count,
            "history_note": raw_task.get("history_note"),
            "pattern_related": bool(raw_task.get("pattern_related")),
            "pattern_label": raw_task.get("pattern_label"),
            "pattern_occurrences": raw_task.get("pattern_occurrences") or 0,
            "pattern_note": raw_task.get("pattern_note"),
            "was_completed_before": was_completed,
            "completed_before_count": raw_task.get("completed_before_count") or 0,
            "failed_before_count": failed_count,
            "has_measured_delta_before": has_delta,
            "outcome_note": raw_task.get("outcome_note"),
            "roadmap_priority_score": score,
            "priority_reasons": priority_reasons,
            "stream_reason": stream_reason
        }
        
        grouped_streams[stream_id].append(child)
        counter += 1

    # Form streams list
    streams = []
    for stream_id, meta in streams_metadata.items():
        children = grouped_streams[stream_id]
        if not children:
            continue
            
        # Sort children by priority score descending
        children.sort(key=lambda c: c["roadmap_priority_score"], reverse=True)
        
        # Stream-level priority is determined by the max score of its children
        max_score = max(c["roadmap_priority_score"] for c in children)
        if max_score >= 80:
            stream_prio = "high"
        elif max_score >= 40:
            stream_prio = "medium"
        else:
            stream_prio = "low"

        streams.append({
            "id": stream_id,
            "title": meta["title"],
            "description": meta["description"],
            "priority": stream_prio,
            "max_score": max_score,
            "children": children
        })

    # Sort streams by predefined logical sequence
    order_map = {
        "technical_foundation": 1,
        "schema_and_entity_trust": 2,
        "ctr_and_serp_optimization": 3,
        "content_expansion": 4,
        "execution_followup": 5
    }
    streams.sort(key=lambda s: order_map.get(s["id"], 99))

    return {
        "goal": "Tối ưu hóa & tăng trưởng SEO toàn diện cho website",
        "streams": streams
    }


def generate_roadmap_summary(roadmap_tree: dict) -> str:
    """Generate a Vietnamese summary explaining the roadmap execution priority."""
    streams = roadmap_tree.get("streams", [])
    if not streams:
        return "Chưa có đủ kế hoạch hành động để xây dựng cây lộ trình."
        
    high_streams = [s for s in streams if s["priority"] == "high"]
    med_streams = [s for s in streams if s["priority"] == "medium"]
    
    parts = []
    if high_streams:
        titles = [f"'{s['title']}'" for s in high_streams]
        parts.append(f"Cây lộ trình đề xuất tập trung ưu tiên cao nhất vào nhóm {', '.join(titles)} do ghi nhận nhiều vấn đề khẩn cấp hoặc các cơ hội lặp lại cần khắc phục ngay.")
    if med_streams:
        titles = [f"'{s['title']}'" for s in med_streams]
        parts.append(f"Tiếp theo, các nhóm {', '.join(titles)} nên được thực hiện song song để tối ưu hóa traffic và mở rộng khoảng trống nội dung.")
    else:
        parts.append("Các công việc khác có thể thực hiện tuần tự theo kế hoạch trung hạn.")
        
    return " ".join(parts)

