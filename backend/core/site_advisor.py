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
            if q["position"] <= 10 and q["impressions"] >= 100 and q["ctr"] < 2.5:
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


def generate_fallback_summary(
    url: str,
    top_issues: List[Dict],
    quick_wins: List[Dict],
    blockers: List[Dict],
    opportunities: List[Dict]
) -> Dict[str, Any]:
    """Template-based diagnostic synthesis when GROQ_API_KEY is not configured."""
    
    # 1. Exec Summary
    summary = (
        f"Báo cáo cố vấn website tự động cho {url}. "
        f"Phân tích phát hiện thấy {len(top_issues)} vấn đề về hiệu suất, "
        f"{len(blockers)} rào cản kỹ thuật/Core Web Vitals nguy hiểm, và "
        f"{len(quick_wins)} từ khóa cơ hội đang cận kề Top 3/Trang 1. "
    )
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
            f"Vui lòng trả về cấu trúc JSON tóm tắt điều hành + kế hoạch 7 ngày + kế hoạch 30 ngày cụ thể bằng Tiếng Việt."
        )
        
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
            opportunities=content_opps
        )
        summary = fallback["summary"]
        action_7d = fallback["action_plan_7d"]
        action_30d = fallback["action_plan_30d"]

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
        "ai_provider": ai_provider
    }
