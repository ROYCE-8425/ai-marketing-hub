"""
AI Report Generator — Phase 17

Generates comprehensive SEO reports by aggregating data from
all modules and using AI to summarize findings.
"""

import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


async def _ai_summary(data_text: str) -> str:
    """Generate AI summary of SEO data."""
    if not GROQ_API_KEY:
        return "⚠️ Chưa cấu hình GROQ_API_KEY — không thể tạo AI summary."

    prompt = f"""Bạn là chuyên gia SEO. Dựa trên dữ liệu SEO sau, viết bản tóm tắt ngắn gọn (5-8 câu) bằng tiếng Việt.
Tập trung vào:
1. Điểm mạnh chính
2. Vấn đề nghiêm trọng nhất cần sửa ngay
3. Ưu tiên hành động (top 3 việc cần làm)

DỮ LIỆU:
{data_text}"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": 1024,
                },
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        pass
    return "Không thể tạo AI summary."


async def generate_report(url: str, keyword: str = "") -> Dict[str, Any]:
    """
    Generate comprehensive SEO report by running all scans.

    Returns structured report with scores, issues, and AI recommendations.
    """
    from core.technical_seo import scan_technical_seo
    from core.geo_analyzer import analyze_geo
    from core.rank_tracker import get_tracked_keywords, export_keywords_csv

    report: Dict[str, Any] = {
        "url": url,
        "keyword": keyword,
        "generated_at": datetime.utcnow().isoformat(),
        "sections": {},
    }

    # 1. Technical SEO scan
    try:
        tech = await scan_technical_seo(url)
        report["sections"]["technical_seo"] = {
            "title": "🔧 Technical SEO",
            "score": tech.get("score", 0),
            "max": tech.get("max_score", 100),
            "grade": tech.get("grade", "?"),
            "load_time": tech.get("load_time"),
            "issues": tech.get("issues", [])[:10],
            "critical_count": tech.get("critical_count", 0),
            "warning_count": tech.get("warning_count", 0),
        }
    except Exception as e:
        report["sections"]["technical_seo"] = {"title": "🔧 Technical SEO", "error": str(e)}

    # 2. GEO analysis
    try:
        geo = await analyze_geo(url, keyword)
        if not geo.get("error"):
            report["sections"]["geo"] = {
                "title": "🤖 GEO Optimization",
                "score": geo.get("geo_score", 0),
                "max": 100,
                "grade": geo.get("grade", "?"),
                "recommendations": geo.get("recommendations", [])[:8],
            }
    except Exception as e:
        report["sections"]["geo"] = {"title": "🤖 GEO Optimization", "error": str(e)}

    # 3. Rank Tracker summary
    try:
        site_url = os.getenv("GSC_SITE_URL", url.rstrip("/") + "/")
        keywords = get_tracked_keywords(site_url)
        if keywords:
            top_kws = sorted([k for k in keywords if k.get("position")], key=lambda x: x["position"])[:10]
            dropping = [k for k in keywords if k.get("change") is not None and k["change"] < -3]
            report["sections"]["rankings"] = {
                "title": "📊 Keyword Rankings",
                "total_tracked": len(keywords),
                "top_keywords": [{"keyword": k["keyword"], "position": k["position"], "change": k["change"]} for k in top_kws],
                "dropping": [{"keyword": k["keyword"], "position": k["position"], "drop": abs(k["change"])} for k in dropping],
            }
    except Exception:
        pass

    # Calculate overall score
    scores = []
    for section in report["sections"].values():
        if "score" in section and "max" in section:
            scores.append((section["score"] / section["max"]) * 100)

    if scores:
        report["overall_score"] = round(sum(scores) / len(scores))
    else:
        report["overall_score"] = 0

    if report["overall_score"] >= 80: report["overall_grade"] = "A"
    elif report["overall_score"] >= 60: report["overall_grade"] = "B"
    elif report["overall_score"] >= 40: report["overall_grade"] = "C"
    else: report["overall_grade"] = "D"

    # AI Summary
    summary_data = json.dumps({
        "url": url,
        "overall_score": report["overall_score"],
        "sections": {k: {kk: vv for kk, vv in v.items() if kk != "issues"} for k, v in report["sections"].items()},
    }, ensure_ascii=False, default=str)[:2000]
    report["ai_summary"] = await _ai_summary(summary_data)

    # All issues combined
    all_issues = []
    for section in report["sections"].values():
        for issue in section.get("issues", []):
            all_issues.append(issue)
    report["all_issues"] = all_issues[:20]
    report["total_issues"] = len(all_issues)

    return report


def format_report_text(report: Dict[str, Any]) -> str:
    """Format report as readable text for export."""
    lines = [
        f"═══════════════════════════════════════════",
        f"   SEO REPORT — {report['url']}",
        f"   Ngày: {report['generated_at'][:10]}",
        f"═══════════════════════════════════════════",
        "",
        f"📊 TỔNG ĐIỂM: {report['overall_score']}/100 ({report.get('overall_grade', '?')})",
        "",
        "━━━ AI TÓM TẮT ━━━",
        report.get("ai_summary", ""),
        "",
    ]

    for key, section in report.get("sections", {}).items():
        title = section.get("title", key)
        score = section.get("score", "—")
        max_score = section.get("max", "—")
        grade = section.get("grade", "")
        lines.append(f"━━━ {title} ━━━")
        if "error" in section:
            lines.append(f"  Lỗi: {section['error']}")
        else:
            lines.append(f"  Điểm: {score}/{max_score} {f'({grade})' if grade else ''}")

            if "critical_count" in section:
                lines.append(f"  Critical: {section['critical_count']}, Warning: {section['warning_count']}")
            if "load_time" in section:
                lines.append(f"  Tốc độ: {section['load_time']}s")
            if "total_tracked" in section:
                lines.append(f"  Keywords theo dõi: {section['total_tracked']}")
            if section.get("top_keywords"):
                lines.append("  Top keywords:")
                for kw in section["top_keywords"][:5]:
                    change = f" ({'+' if kw.get('change', 0) > 0 else ''}{kw.get('change', 0)})" if kw.get("change") else ""
                    lines.append(f"    #{kw['position']} — {kw['keyword']}{change}")
        lines.append("")

    if report.get("all_issues"):
        lines.append("━━━ 🔴 VẤN ĐỀ CẦN SỬA ━━━")
        for issue in report["all_issues"][:15]:
            sev = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(issue.get("severity"), "⚪")
            lines.append(f"  {sev} [{issue.get('category', '')}] {issue['message']}")
            if issue.get("fix"):
                lines.append(f"     → {issue['fix']}")
        lines.append("")

    lines.append("═══════════════════════════════════════════")
    lines.append("   AI Marketing Hub — SEO Report Generator")
    lines.append("═══════════════════════════════════════════")
    return "\n".join(lines)
