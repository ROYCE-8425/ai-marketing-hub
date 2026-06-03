"""
AI Advisor Report Export Generator — Phase 9

Provides sanitization and renderer functions to format AI Advisor diagnostics
into Markdown, HTML, and JSON formats for user download.
"""

from __future__ import annotations
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

def build_exportable_advisor_report(data: dict) -> dict:
    """
    Sanitizes raw input data and retains only safe, recognized advisor report fields.
    Prevents client-side manipulation of data structure or dumping of raw model schemas.
    """
    if not isinstance(data, dict):
        data = {}

    def clean_str(v: Any) -> str:
        return str(v).strip() if v is not None else ""

    def clean_int(v: Any, default: int = 0) -> int:
        try:
            return int(v) if v is not None else default
        except (ValueError, TypeError):
            return default

    # 1. Main metrics
    site_url = clean_str(data.get("site_url"))
    analyzed_at = clean_str(data.get("analyzed_at"))
    confidence = clean_str(data.get("confidence"))
    if not confidence:
        confidence = "medium"
    confidence_score = clean_int(data.get("confidence_score"), 0)
    summary = clean_str(data.get("summary"))

    # 2. Core diagnostic lists
    top_issues = []
    for issue in (data.get("top_issues") or []):
        if isinstance(issue, dict):
            top_issues.append({
                "severity": clean_str(issue.get("severity")),
                "category": clean_str(issue.get("category")),
                "message": clean_str(issue.get("message")),
                "fix": clean_str(issue.get("fix")),
            })

    quick_wins = []
    for qw in (data.get("quick_wins") or []):
        if isinstance(qw, dict):
            quick_wins.append({
                "keyword": clean_str(qw.get("keyword")),
                "current_position": clean_int(qw.get("current_position"), 0),
                "impressions": clean_int(qw.get("impressions"), 0),
                "action": clean_str(qw.get("action")),
            })

    tech_blockers = []
    for tb in (data.get("technical_blockers") or []):
        if isinstance(tb, dict):
            tech_blockers.append({
                "category": clean_str(tb.get("category")),
                "message": clean_str(tb.get("message")),
                "fix": clean_str(tb.get("fix")),
            })

    content_opps = []
    for co in (data.get("content_opportunities") or []):
        if isinstance(co, dict):
            content_opps.append({
                "keyword": clean_str(co.get("keyword")),
                "search_intent": clean_str(co.get("search_intent")),
                "reason": clean_str(co.get("reason")),
            })

    # 3. Actions 7d & 30d
    action_7d = []
    for plan in (data.get("action_plan_7d") or []):
        if isinstance(plan, dict):
            action_7d.append({
                "day": clean_str(plan.get("day")),
                "task": clean_str(plan.get("task")),
                "priority": clean_str(plan.get("priority")),
                "impact": clean_str(plan.get("impact")),
                "history_note": clean_str(plan.get("history_note")),
                "pattern_note": clean_str(plan.get("pattern_note")),
            })

    action_30d = []
    for plan in (data.get("action_plan_30d") or []):
        if isinstance(plan, dict):
            action_30d.append({
                "week": clean_str(plan.get("week")),
                "task": clean_str(plan.get("task")),
                "priority": clean_str(plan.get("priority")),
                "impact": clean_str(plan.get("impact")),
                "history_note": clean_str(plan.get("history_note")),
                "pattern_note": clean_str(plan.get("pattern_note")),
            })

    # 4. Memory history context
    memory_context = {}
    raw_mem = data.get("memory_context") or {}
    if isinstance(raw_mem, dict):
        memory_context = {
            "keyword_memory_records": clean_int(raw_mem.get("keyword_memory_records"), 0),
            "recommendation_outcomes": clean_int(raw_mem.get("recommendation_outcomes"), 0),
            "pending_recommendations_count": clean_int(raw_mem.get("pending_recommendations_count"), 0)
        }

    recurring_opportunities = []
    for ro in (data.get("recurring_opportunities") or []):
        if isinstance(ro, dict):
            recurring_opportunities.append({
                "keyword": clean_str(ro.get("keyword")),
                "opportunity_type": clean_str(ro.get("opportunity_type")),
                "occurrences": clean_int(ro.get("occurrences"), 0),
                "clicks": clean_int(ro.get("clicks"), 0),
                "impressions": clean_int(ro.get("impressions"), 0),
                "ctr": ro.get("ctr"),
            })

    repeated_recommendations = []
    for rr in (data.get("repeated_recommendations") or []):
        if isinstance(rr, dict):
            repeated_recommendations.append({
                "recommendation_text": clean_str(rr.get("recommendation_text")),
                "recommendation_type": clean_str(rr.get("recommendation_type")),
                "priority": clean_str(rr.get("priority")),
                "occurrences": clean_int(rr.get("occurrences"), 0),
                "last_seen": clean_str(rr.get("last_seen")),
            })

    pending_recommendations = []
    for pr in (data.get("pending_recommendations") or []):
        if isinstance(pr, dict):
            pending_recommendations.append({
                "id": clean_int(pr.get("id")),
                "recommendation_type": clean_str(pr.get("recommendation_type")),
                "recommendation_text": clean_str(pr.get("recommendation_text")),
                "priority": clean_str(pr.get("priority")),
                "impact": clean_str(pr.get("impact")),
                "status": clean_str(pr.get("status")),
                "page_url": clean_str(pr.get("page_url")),
                "keyword": clean_str(pr.get("keyword")),
                "created_at": clean_str(pr.get("created_at")),
            })

    # 5. Pattern memory context
    pattern_memory_context = {}
    raw_pattern = data.get("pattern_memory_context") or {}
    if isinstance(raw_pattern, dict):
        pattern_memory_context = {
            "total_patterns": clean_int(raw_pattern.get("total_patterns"), 0),
            "by_pattern_type": raw_pattern.get("by_pattern_type") or {},
            "top_pattern_labels": raw_pattern.get("top_pattern_labels") or [],
            "recurring_patterns": raw_pattern.get("recurring_patterns") or []
        }

    # 6. Outcome tracking context
    outcome_tracking_context = {}
    raw_outcome = data.get("outcome_tracking_context") or {}
    if isinstance(raw_outcome, dict):
        outcome_tracking_context = {
            "total_outcomes": clean_int(raw_outcome.get("total_outcomes"), 0),
            "pending_count": clean_int(raw_outcome.get("pending_count"), 0),
            "in_progress_count": clean_int(raw_outcome.get("in_progress_count"), 0),
            "completed_count": clean_int(raw_outcome.get("completed_count"), 0),
            "failed_count": clean_int(raw_outcome.get("failed_count"), 0),
            "completed_with_delta_count": clean_int(raw_outcome.get("completed_with_delta_count"), 0),
            "recent_completed_recommendations": raw_outcome.get("recent_completed_recommendations") or [],
            "recent_failed_recommendations": raw_outcome.get("recent_failed_recommendations") or []
        }

    # 7. Summaries
    completed_recommendations_summary = clean_str(data.get("completed_recommendations_summary"))
    failed_recommendations_summary = clean_str(data.get("failed_recommendations_summary"))
    effective_recommendation_summary = clean_str(data.get("effective_recommendation_summary"))
    new_vs_recurring_summary = clean_str(data.get("new_vs_recurring_summary"))
    structural_pattern_summary = clean_str(data.get("structural_pattern_summary"))

    return {
        "site_url": site_url,
        "analyzed_at": analyzed_at,
        "confidence": confidence,
        "confidence_score": confidence_score,
        "summary": summary,
        "top_issues": top_issues,
        "quick_wins": quick_wins,
        "technical_blockers": tech_blockers,
        "content_opportunities": content_opps,
        "action_plan_7d": action_7d,
        "action_plan_30d": action_30d,
        "memory_context": memory_context,
        "recurring_opportunities": recurring_opportunities,
        "repeated_recommendations": repeated_recommendations,
        "pending_recommendations": pending_recommendations,
        "new_vs_recurring_summary": new_vs_recurring_summary,
        "pattern_memory_context": pattern_memory_context,
        "structural_pattern_summary": structural_pattern_summary,
        "outcome_tracking_context": outcome_tracking_context,
        "completed_recommendations_summary": completed_recommendations_summary,
        "failed_recommendations_summary": failed_recommendations_summary,
        "effective_recommendation_summary": effective_recommendation_summary
    }

def export_report_as_json(data: dict) -> str:
    """Export clean report data as formatted JSON."""
    return json.dumps(data, indent=2, ensure_ascii=False)

def export_report_as_markdown(data: dict) -> str:
    """Format and render diagnostic report as structured Markdown."""
    lines = [
        f"# BÁO CÁO CỐ VẤN SEO & MARKETING AUTOMATION",
        f"- **Trang web phân tích**: {data['site_url']}",
        f"- **Thời điểm chẩn đoán**: {data['analyzed_at'] or datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- **Mức độ tin cậy**: {data['confidence_score']}% ({data['confidence'].upper()})",
        "",
        "---",
        "",
        "## 1. Tóm tắt điều hành (Executive Summary)",
        f"> {data['summary'] or 'Chưa có thông tin tóm tắt điều hành.'}",
        "",
        "---",
        "",
        "## 2. Kế hoạch hành động 7 ngày tới (7-Day Action Plan)",
    ]

    if not data["action_plan_7d"]:
        lines.append("Chưa có kế hoạch hành động 7 ngày được đề xuất.")
    else:
        for plan in data["action_plan_7d"]:
            prio = plan["priority"].upper()
            lines.append(f"- **{plan['day'] or 'Giai đoạn'}**: {plan['task']} (Mức ưu tiên: `{prio}`, Tác động: `{plan['impact']}`)")
            if plan.get("history_note"):
                lines.append(f"  * ⚠️ *Lịch sử:* {plan['history_note']}")
            if plan.get("pattern_note"):
                lines.append(f"  * 💡 *Mẫu lập:* {plan['pattern_note']}")

    lines.append("")
    lines.append("## 3. Chiến lược tăng trưởng 30 ngày (30-Day Strategy)")
    if not data["action_plan_30d"]:
        lines.append("Chưa có chiến lược tăng trưởng 30 ngày được đề xuất.")
    else:
        for plan in data["action_plan_30d"]:
            prio = plan["priority"].upper()
            lines.append(f"- **{plan['week'] or 'Tuần'}**: {plan['task']} (Mức ưu tiên: `{prio}`, Tác động: `{plan['impact']}`)")
            if plan.get("history_note"):
                lines.append(f"  * ⚠️ *Lịch sử:* {plan['history_note']}")
            if plan.get("pattern_note"):
                lines.append(f"  * 💡 *Mẫu lập:* {plan['pattern_note']}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Các vấn đề cần ưu tiên xử lý hàng đầu (Top Issues)")
    if not data["top_issues"]:
        lines.append("Không phát hiện vấn đề khẩn cấp nào cần xử lý.")
    else:
        for issue in data["top_issues"]:
            lines.append(f"- **[{issue['category']}]** {issue['message']}")
            lines.append(f"  * 👉 *Khắc phục:* {issue['fix']} (Mức độ: `{issue['severity'].upper()}`)")

    lines.append("")
    lines.append("## 5. Cơ hội thăng hạng nhanh (Quick Wins)")
    if not data["quick_wins"]:
        lines.append("Chưa tìm thấy cơ hội thăng hạng nhanh nào.")
    else:
        lines.append("| Từ khóa cơ hội | Vị trí hiện tại | Lượt hiển thị | Khuyến nghị hành động |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for qw in data["quick_wins"]:
            lines.append(f"| {qw['keyword']} | #{qw['current_position']} | {qw['impressions']:,} | {qw['action']} |")

    lines.append("")
    lines.append("## 6. Rào cản kỹ thuật & Core Web Vitals")
    if not data["technical_blockers"]:
        lines.append("Không phát hiện rào cản kỹ thuật đáng kể.")
    else:
        for tb in data["technical_blockers"]:
            lines.append(f"- **[{tb['category']}]** {tb['message']}")
            lines.append(f"  * 👉 *Giải pháp:* {tb['fix']}")

    lines.append("")
    lines.append("## 7. Cơ hội mở rộng nội dung (Content Gaps)")
    if not data["content_opportunities"]:
        lines.append("Chưa ghi nhận cơ hội mở rộng nội dung mới.")
    else:
        for co in data["content_opportunities"]:
            kw_part = f"Từ khóa '{co['keyword']}' - " if co.get("keyword") else ""
            lines.append(f"- **[{co['search_intent'].upper()}]** {kw_part}{co['reason']}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 8. Bộ nhớ lịch sử SEO & Trí tuệ tích lũy")
    lines.append(f"- **Số lượng cơ hội từ khóa lưu trữ**: {data['memory_context'].get('keyword_memory_records', 0)}")
    lines.append(f"- **Tổng số đề xuất chẩn đoán lịch sử**: {data['memory_context'].get('recommendation_outcomes', 0)}")
    lines.append(f"- **Khuyến nghị đang tồn đọng chờ thực hiện**: {data['memory_context'].get('pending_recommendations_count', 0)}")
    if data["new_vs_recurring_summary"]:
        lines.append(f"- *Tóm tắt lịch sử:* {data['new_vs_recurring_summary']}")

    lines.append("")
    lines.append("### Cơ hội từ khóa lặp lại nhiều lần")
    if not data["recurring_opportunities"]:
        lines.append("Chưa ghi nhận từ khóa lặp lại đủ điều kiện phát hiện cơ hội.")
    else:
        for ro in data["recurring_opportunities"]:
            ctr_str = f", CTR: {ro['ctr']}%" if ro.get("ctr") else ""
            lines.append(f"- **{ro['keyword']}** ({ro['opportunity_type']}): Lặp lại **{ro['occurrences']} lần** (Hiển thị: {ro['impressions']:,}, Clicks: {ro['clicks']}{ctr_str})")

    lines.append("")
    lines.append("### Khuyến nghị trùng lặp ghi nhận")
    if not data["repeated_recommendations"]:
        lines.append("Không ghi nhận khuyến nghị trùng lặp nhiều lần.")
    else:
        for rr in data["repeated_recommendations"]:
            lines.append(f"- **{rr['recommendation_text']}** (Loại: {rr['recommendation_type']}): Xuất hiện **{rr['occurrences']} lần** (Ưu tiên: `{rr['priority'] or 'THẤP'}`, Lần cuối: {rr['last_seen'][:10] if rr['last_seen'] else 'Không rõ'})")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 9. Tiến độ thực thi khuyến nghị & Outcome Tracking")
    ot = data["outcome_tracking_context"]
    lines.append(f"- **Tổng số khuyến nghị đã tạo**: {ot.get('total_outcomes', 0)}")
    lines.append(f"- **Đang chờ xử lý (Pending)**: {ot.get('pending_count', 0)}")
    lines.append(f"- **Đang thực hiện (In Progress)**: {ot.get('in_progress_count', 0)}")
    lines.append(f"- **Đã hoàn thành (Completed)**: {ot.get('completed_count', 0)} (có {ot.get('completed_with_delta_count', 0)} ghi nhận số liệu KPI)")
    lines.append(f"- **Thất bại (Failed)**: {ot.get('failed_count', 0)}")

    if data["effective_recommendation_summary"]:
        lines.append(f"\n> 📈 **Đánh giá hiệu quả:** {data['effective_recommendation_summary']}")
    if data["completed_recommendations_summary"]:
        lines.append(f"\n> ✅ **Thực thi hoàn thành:** {data['completed_recommendations_summary']}")
    if data["failed_recommendations_summary"]:
        lines.append(f"\n> ⚠️ **Khuyến nghị thất bại:** {data['failed_recommendations_summary']}")

    lines.append("")
    lines.append("### Chi tiết kết quả hoàn thành gần đây")
    if not ot.get("recent_completed_recommendations"):
        lines.append("Chưa có khuyến nghị nào hoàn thành đo lường.")
    else:
        for rec in ot["recent_completed_recommendations"]:
            lines.append(f"- **{rec.get('recommendation_text')}** (Loại: {rec.get('recommendation_type')})")
            if rec.get("updated_at"):
                lines.append(f"  * *Hoàn thành ngày:* {rec['updated_at'][:10]}")
            delta = rec.get("measured_delta") or {}
            if delta:
                delta_parts = []
                if "ctr_before" in delta: delta_parts.append(f"CTR: {delta['ctr_before']}% → {delta.get('ctr_after')}%")
                if "position_before" in delta: delta_parts.append(f"Vị trí: #{delta['position_before']} → #{delta.get('position_after')}")
                if "clicks_diff" in delta: delta_parts.append(f"Clicks: {delta['clicks_diff'] > 0 and '+' or ''}{delta['clicks_diff']}")
                if "impressions_diff" in delta: delta_parts.append(f"Hiển thị: {delta['impressions_diff'] > 0 and '+' or ''}{delta['impressions_diff']}")
                lines.append(f"  * *KPI thay đổi:* {', '.join(delta_parts)}")

    lines.append("")
    lines.append("### Khuyến nghị thực hiện không thành công")
    if not ot.get("recent_failed_recommendations"):
        lines.append("Không ghi nhận khuyến nghị thất bại.")
    else:
        for rec in ot["recent_failed_recommendations"]:
            lines.append(f"- **{rec.get('recommendation_text')}** (Loại: {rec.get('recommendation_type')})")
            if rec.get("execution_note"):
                lines.append(f"  * *Lý do/Ghi chú thất bại:* {rec['execution_note']}")

    lines.append("")
    lines.append("═══════════════════════════════════════════")
    lines.append("    Báo cáo xuất từ AI Marketing Hub")
    lines.append("═══════════════════════════════════════════")

    return "\n".join(lines)

def export_report_as_html(data: dict) -> str:
    """Format and render diagnostic report as a standalone HTML page with dark glassmorphism styling."""
    
    # Render Action Plans
    plan_7d_html = ""
    if not data["action_plan_7d"]:
        plan_7d_html = "<p class='empty-text'>Chưa có kế hoạch hành động 7 ngày được đề xuất.</p>"
    else:
        for plan in data["action_plan_7d"]:
            hist = f"<div class='history-note'>⚠️ Lịch sử: {plan['history_note']}</div>" if plan.get("history_note") else ""
            pat = f"<div class='pattern-note'>💡 Mẫu lập: {plan['pattern_note']}</div>" if plan.get("pattern_note") else ""
            plan_7d_html += f"""
            <div class='action-item'>
                <strong>{plan['day'] or 'Giai đoạn'}</strong>: {plan['task']}
                <div class='meta-line'>Uu tiên: <span class='badge'>{plan['priority'].upper()}</span> | Tác động: <em>{plan['impact']}</em></div>
                {hist}
                {pat}
            </div>
            """

    plan_30d_html = ""
    if not data["action_plan_30d"]:
        plan_30d_html = "<p class='empty-text'>Chưa có chiến lược tăng trưởng 30 ngày được đề xuất.</p>"
    else:
        for plan in data["action_plan_30d"]:
            hist = f"<div class='history-note'>⚠️ Lịch sử: {plan['history_note']}</div>" if plan.get("history_note") else ""
            pat = f"<div class='pattern-note'>💡 Mẫu lập: {plan['pattern_note']}</div>" if plan.get("pattern_note") else ""
            plan_30d_html += f"""
            <div class='action-item' style='border-left-color: var(--cyan);'>
                <strong>{plan['week'] or 'Tuần'}</strong>: {plan['task']}
                <div class='meta-line'>Ưu tiên: <span class='badge'>{plan['priority'].upper()}</span> | Tác động: <em>{plan['impact']}</em></div>
                {hist}
                {pat}
            </div>
            """

    # Render Issues
    issues_html = ""
    if not data["top_issues"]:
        issues_html = "<p class='empty-text'>Không phát hiện vấn đề khẩn cấp nào cần xử lý.</p>"
    else:
        for issue in data["top_issues"]:
            sev_class = "badge-failed" if issue["severity"].lower() == "critical" else "badge-pending"
            issues_html += f"""
            <div class='issue-item'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <strong>[{issue['category']}]</strong>
                    <span class='badge {sev_class}'>{issue['severity'].upper()}</span>
                </div>
                <p style='margin: 8px 0;'>{issue['message']}</p>
                <div class='solution-box'>👉 <strong>Khắc phục:</strong> {issue['fix']}</div>
            </div>
            """

    # Render Quick Wins Table
    quick_wins_html = ""
    if not data["quick_wins"]:
        quick_wins_html = "<p class='empty-text'>Chưa tìm thấy cơ hội thăng hạng nhanh nào.</p>"
    else:
        rows = ""
        for qw in data["quick_wins"]:
            rows += f"""
            <tr>
                <td style='font-weight:700;'>{qw['keyword']}</td>
                <td style='color:var(--cyan); font-weight:bold;'>#{qw['current_position']}</td>
                <td>{qw['impressions']:,}</td>
                <td style='font-size:12px; color:var(--text-dim);'>{qw['action']}</td>
            </tr>
            """
        quick_wins_html = f"""
        <table>
            <thead>
                <tr>
                    <th>Từ khóa cơ hội</th>
                    <th>Vị trí hiện tại</th>
                    <th>Lượt hiển thị</th>
                    <th>Hành động đề xuất</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """

    # Render Technical Blockers
    blockers_html = ""
    if not data["technical_blockers"]:
        blockers_html = "<p class='empty-text'>Không phát hiện rào cản kỹ thuật đáng kể.</p>"
    else:
        for tb in data["technical_blockers"]:
            blockers_html += f"""
            <div class='issue-item' style='border-left-color: var(--yellow);'>
                <strong>[{tb['category']}]</strong>
                <p style='margin: 6px 0;'>{tb['message']}</p>
                <div class='solution-box' style='border-color: rgba(245,158,11,0.2); background:rgba(245,158,11,0.03); color:#fde68a;'>👉 {tb['fix']}</div>
            </div>
            """

    # Render Content Opportunities
    content_html = ""
    if not data["content_opportunities"]:
        content_html = "<p class='empty-text'>Chưa ghi nhận cơ hội mở rộng nội dung mới.</p>"
    else:
        for co in data["content_opportunities"]:
            kw_part = f"Từ khóa '{co['keyword']}' - " if co.get("keyword") else ""
            content_html += f"""
            <div class='issue-item' style='border-left-color: #ec4899;'>
                <span class='badge' style='background:rgba(236,72,153,0.15); color:#ec4899; border: 1px solid rgba(236,72,153,0.3);'>{co['search_intent'].upper()}</span>
                <p style='margin: 6px 0 0 0;'>{kw_part}{co['reason']}</p>
            </div>
            """

    # Render Keyword memory lists
    rec_opp_html = ""
    if not data["recurring_opportunities"]:
        rec_opp_html = "<p class='empty-text'>Chưa ghi nhận cơ hội từ khóa lặp lại.</p>"
    else:
        for ro in data["recurring_opportunities"]:
            ctr_str = f", CTR: {ro['ctr']}%" if ro.get("ctr") else ""
            rec_opp_html += f"""
            <div class='memory-subitem'>
                <strong>{ro['keyword']}</strong> <span style='font-size:11px; opacity:0.7;'>({ro['opportunity_type']})</span>
                <div class='meta-line'>Lặp lại: <strong>{ro['occurrences']} lần</strong> (Hiển thị: {ro['impressions']:,}, Clicks: {ro['clicks']}{ctr_str})</div>
            </div>
            """

    # Render Repeated recommendations
    repeated_rec_html = ""
    if not data["repeated_recommendations"]:
        repeated_rec_html = "<p class='empty-text'>Không ghi nhận khuyến nghị trùng lặp nhiều lần.</p>"
    else:
        for rr in data["repeated_recommendations"]:
            repeated_rec_html += f"""
            <div class='memory-subitem'>
                <strong>{rr['recommendation_text']}</strong> <span style='font-size:11px; opacity:0.7;'>({rr['recommendation_type']})</span>
                <div class='meta-line'>Số lần: <strong>{rr['occurrences']} lần</strong> | Mức độ: <span class='badge'>{rr['priority'] or 'THẤP'}</span> | Lần cuối: {rr['last_seen'][:10] if rr['last_seen'] else 'Không rõ'}</div>
            </div>
            """

    # Render Outcome tracking Completed
    ot = data["outcome_tracking_context"]
    completed_details_html = ""
    if not ot.get("recent_completed_recommendations"):
        completed_details_html = "<p class='empty-text'>Chưa có đề xuất nào hoàn thành.</p>"
    else:
        for rec in ot["recent_completed_recommendations"]:
            delta = rec.get("measured_delta") or {}
            delta_html = ""
            if delta:
                delta_parts = []
                if "ctr_before" in delta: delta_parts.append(f"<li>CTR: {delta['ctr_before']}% &rarr; {delta.get('ctr_after')}%</li>")
                if "position_before" in delta: delta_parts.append(f"<li>Vị trí: #{delta['position_before']} &rarr; #{delta.get('position_after')}</li>")
                if "clicks_diff" in delta: delta_parts.append(f"<li>Clicks: {delta['clicks_diff'] > 0 and '+' or ''}{delta['clicks_diff']}</li>")
                if "impressions_diff" in delta: delta_parts.append(f"<li>Hiển thị: {delta['impressions_diff'] > 0 and '+' or ''}{delta['impressions_diff']}</li>")
                delta_html = f"<ul style='margin:4px 0 0 0; padding-left:16px; font-size:11px; color:var(--green);'>{''.join(delta_parts)}</ul>"
            
            completed_details_html += f"""
            <div class='memory-subitem' style='border-left: 2px solid var(--green); padding-left: 10px;'>
                <strong>{rec.get('recommendation_text')}</strong>
                <div class='meta-line'>Loại: {rec.get('recommendation_type')}{rec.get('updated_at') and f' | Ngày duyệt: {rec["updated_at"][:10]}' or ''}</div>
                {delta_html}
            </div>
            """

    # Render Outcome tracking Failed
    failed_details_html = ""
    if not ot.get("recent_failed_recommendations"):
        failed_details_html = "<p class='empty-text'>Không ghi nhận đề xuất thực thi thất bại.</p>"
    else:
        for rec in ot["recent_failed_recommendations"]:
            failed_details_html += f"""
            <div class='memory-subitem' style='border-left: 2px solid var(--red); padding-left: 10px;'>
                <strong>{rec.get('recommendation_text')}</strong>
                <div class='meta-line'>Loại: {rec.get('recommendation_type')}</div>
                <div class='history-note' style='margin-top:4px;'>Lý do thất bại: {rec.get('execution_note') or 'Không ghi nhận ghi chú.'}</div>
            </div>
            """

    # Summaries banners
    summary_banners_html = ""
    if data["effective_recommendation_summary"]:
        summary_banners_html += f"<div class='banner banner-green'><strong>📈 Đánh giá hiệu quả:</strong> {data['effective_recommendation_summary']}</div>"
    if data["completed_recommendations_summary"]:
        summary_banners_html += f"<div class='banner banner-cyan'><strong>✅ Thực thi hoàn thành:</strong> {data['completed_recommendations_summary']}</div>"
    if data["failed_recommendations_summary"]:
        summary_banners_html += f"<div class='banner banner-red'><strong>⚠️ Khuyến nghị thất bại:</strong> {data['failed_recommendations_summary']}</div>"

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo Cố vấn SEO AI - {data['site_url']}</title>
    <style>
        :root {{
            --bg: #090514;
            --surface: rgba(255, 255, 255, 0.02);
            --border: rgba(255, 255, 255, 0.08);
            --text: #e2e8f0;
            --text-dim: #94a3b8;
            --primary: #8b5cf6;
            --cyan: #06b6d4;
            --green: #10b981;
            --yellow: #f59e0b;
            --red: #ef4444;
        }}
        body {{
            background-color: var(--bg);
            color: var(--text);
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            max-width: 960px;
            margin: 0 auto;
            padding: 2.5rem 1.5rem;
        }}
        h1, h2, h3, h4 {{
            color: #ffffff;
            margin-top: 0;
        }}
        h1 {{
            font-size: 26px;
            font-weight: 800;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1rem;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        h2 {{
            font-size: 18px;
            color: var(--primary);
            border-left: 4px solid var(--cyan);
            padding-left: 10px;
            margin: 2.5rem 0 1.2rem 0;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
            margin-bottom: 2rem;
        }}
        .meta-card {{
            background: rgba(139, 92, 246, 0.03);
            border: 1px solid rgba(139, 92, 246, 0.15);
            border-radius: 10px;
            padding: 14px 18px;
        }}
        .meta-label {{
            font-size: 11px;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .meta-value {{
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
        }}
        .badge {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.08);
            color: var(--text);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}
        .badge-pending {{ background: rgba(245, 158, 11, 0.15); color: var(--yellow); border-color: rgba(245, 158, 11, 0.3); }}
        .badge-progress {{ background: rgba(6, 182, 212, 0.15); color: var(--cyan); border-color: rgba(6, 182, 212, 0.3); }}
        .badge-completed {{ background: rgba(16, 185, 129, 0.15); color: var(--green); border-color: rgba(16, 185, 129, 0.3); }}
        .badge-failed {{ background: rgba(239, 68, 68, 0.15); color: var(--red); border-color: rgba(239, 68, 68, 0.3); }}
        
        blockquote {{
            margin: 0;
            padding: 14px 20px;
            background: rgba(255, 255, 255, 0.01);
            border-left: 3px solid var(--primary);
            border-radius: 0 8px 8px 0;
            font-size: 14px;
            color: #f1f5f9;
            line-height: 1.7;
        }}
        
        .action-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }}
        .action-item {{
            background: rgba(255,255,255,0.01);
            border: 1px solid var(--border);
            border-left: 3px solid var(--primary);
            border-radius: 6px;
            padding: 12px 16px;
            margin-bottom: 10px;
        }}
        .meta-line {{
            font-size: 11px;
            color: var(--text-dim);
            margin-top: 6px;
        }}
        .history-note {{
            font-size: 11px;
            color: var(--yellow);
            margin-top: 4px;
            font-style: italic;
        }}
        .pattern-note {{
            font-size: 11px;
            color: #c084fc;
            margin-top: 4px;
            font-style: italic;
        }}
        .issue-item {{
            background: rgba(255,255,255,0.01);
            border: 1px solid var(--border);
            border-left: 3px solid var(--red);
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 12px;
        }}
        .solution-box {{
            font-size: 12px;
            color: var(--green);
            background: rgba(16, 185, 129, 0.03);
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid rgba(16, 185, 129, 0.15);
            margin-top: 8px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }}
        th, td {{
            padding: 10px 12px;
            border: 1px solid var(--border);
            text-align: left;
        }}
        th {{
            background: rgba(255, 255, 255, 0.02);
            color: #ffffff;
            font-weight: 700;
        }}
        
        .memory-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 12px;
        }}
        .memory-subitem {{
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 8px;
            font-size: 13px;
        }}
        
        .banner {{
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 12px;
            font-size: 13px;
        }}
        .banner-green {{ border-color: rgba(16,185,129,0.3); background: rgba(16,185,129,0.03); color: #a7f3d0; }}
        .banner-cyan {{ border-color: rgba(6,182,212,0.3); background: rgba(6,182,212,0.03); color: #93c5fd; }}
        .banner-red {{ border-color: rgba(239,68,68,0.3); background: rgba(239,68,68,0.03); color: #fca5a5; }}
        
        .empty-text {{
            font-size: 13px;
            color: var(--text-dim);
            font-style: italic;
            margin: 0;
        }}
        footer {{
            text-align: center;
            margin-top: 3rem;
            font-size: 12px;
            color: var(--text-dim);
            border-top: 1px solid var(--border);
            padding-top: 1.5rem;
        }}
    </style>
</head>
<body>
    <h1>🎯 Báo cáo Cố vấn SEO AI</h1>
    
    <div class="meta-grid">
        <div class="meta-card">
            <div class="meta-label">Trang web phân tích</div>
            <div class="meta-value" style="font-size:14px; word-break:break-all;">{data['site_url']}</div>
        </div>
        <div class="meta-card" style="border-color: rgba(6, 182, 212, 0.15); background: rgba(6, 182, 212, 0.03);">
            <div class="meta-label">Thời điểm phân tích</div>
            <div class="meta-value" style="font-size:14px;">{data['analyzed_at'] or datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        <div class="meta-card" style="border-color: rgba(16, 185, 129, 0.15); background: rgba(16, 185, 129, 0.03);">
            <div class="meta-label">Độ tin cậy chẩn đoán</div>
            <div class="meta-value">{data['confidence_score']}% ({data['confidence'].upper()})</div>
        </div>
    </div>

    <div class="card">
        <h2>1. Tóm tắt điều hành (Executive Summary)</h2>
        <blockquote>{data['summary'] or 'Chưa có thông tin tóm tắt điều hành.'}</blockquote>
    </div>

    <div class="card">
        <h2>2. Kế hoạch hành động 7 ngày tới</h2>
        <div style="margin-top: 10px;">{plan_7d_html}</div>
    </div>

    <div class="card">
        <h2>3. Chiến lược tăng trưởng 30 ngày</h2>
        <div style="margin-top: 10px;">{plan_30d_html}</div>
    </div>

    <div class="card">
        <h2>4. Các vấn đề cần ưu tiên xử lý hàng đầu</h2>
        <div style="margin-top: 10px;">{issues_html}</div>
    </div>

    <div class="card">
        <h2>5. Cơ hội thăng hạng nhanh (Quick Wins)</h2>
        <div style="margin-top: 10px;">{quick_wins_html}</div>
    </div>

    <div class="card">
        <h2>6. Rào cản kỹ thuật & Core Web Vitals</h2>
        <div style="margin-top: 10px;">{blockers_html}</div>
    </div>

    <div class="card">
        <h2>7. Cơ hội mở rộng nội dung (Content Gaps)</h2>
        <div style="margin-top: 10px;">{content_html}</div>
    </div>

    <div class="card">
        <h2>8. Bộ nhớ lịch sử SEO & Trí tuệ tích lũy</h2>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:12px; margin-bottom:1.5rem;">
            <div class="meta-card" style="border-color:rgba(255,255,255,0.08); background:rgba(255,255,255,0.01);">
                <div class="meta-label">Cơ hội từ khóa lưu trữ</div>
                <div class="meta-value">{data['memory_context'].get('keyword_memory_records', 0)} bản ghi</div>
            </div>
            <div class="meta-card" style="border-color:rgba(255,255,255,0.08); background:rgba(255,255,255,0.01);">
                <div class="meta-label">Tổng đề xuất lịch sử</div>
                <div class="meta-value">{data['memory_context'].get('recommendation_outcomes', 0)} đề xuất</div>
            </div>
            <div class="meta-card" style="border-color:rgba(255,255,255,0.08); background:rgba(255,255,255,0.01);">
                <div class="meta-label">Khuyến nghị tồn đọng</div>
                <div class="meta-value">{data['memory_context'].get('pending_recommendations_count', 0)} chờ xử lý</div>
            </div>
        </div>
        
        {data['new_vs_recurring_summary'] and f"<p style='font-size:13px; color:var(--text-dim); margin-bottom:1.5rem;'><strong>Phân tích bộ nhớ:</strong> {data['new_vs_recurring_summary']}</p>" or ''}
        
        <div class="memory-grid">
            <div>
                <h4 style="color:var(--cyan); border-bottom:1px solid var(--border); padding-bottom:4px; font-size:13px;">🔄 Từ khóa cơ hội lặp lại</h4>
                {rec_opp_html}
            </div>
            <div>
                <h4 style="color:var(--yellow); border-bottom:1px solid var(--border); padding-bottom:4px; font-size:13px;">⚙️ Đề xuất chẩn đoán trùng lặp</h4>
                {repeated_rec_html}
            </div>
        </div>
    </div>

    <div class="card">
        <h2>9. Tiến độ thực thi khuyến nghị (Outcome Tracking)</h2>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:10px; margin-bottom:1.5rem;">
            <div class="meta-card" style="border-color: rgba(245,158,11,0.15); background:rgba(245,158,11,0.03);">
                <div class="meta-label">Đang chờ (Pending)</div>
                <div class="meta-value">{ot.get('pending_count', 0)}</div>
            </div>
            <div class="meta-card" style="border-color: rgba(6,182,212,0.15); background:rgba(6,182,212,0.03);">
                <div class="meta-label">Đang làm (In Progress)</div>
                <div class="meta-value">{ot.get('in_progress_count', 0)}</div>
            </div>
            <div class="meta-card" style="border-color: rgba(16,185,129,0.15); background:rgba(16,185,129,0.03);">
                <div class="meta-label">Đã xong (Completed)</div>
                <div class="meta-value">{ot.get('completed_count', 0)}</div>
            </div>
            <div class="meta-card" style="border-color: rgba(239,68,68,0.15); background:rgba(239,68,68,0.03);">
                <div class="meta-label">Thất bại (Failed)</div>
                <div class="meta-value">{ot.get('failed_count', 0)}</div>
            </div>
        </div>

        {summary_banners_html}

        <div class="memory-grid" style="margin-top:1.5rem;">
            <div>
                <h4 style="color:var(--green); border-bottom:1px solid var(--border); padding-bottom:4px; font-size:13px;">✅ Đề xuất hoàn thành gần đây</h4>
                {completed_details_html}
            </div>
            <div>
                <h4 style="color:var(--red); border-bottom:1px solid var(--border); padding-bottom:4px; font-size:13px;">❌ Đề xuất thực thi thất bại</h4>
                {failed_details_html}
            </div>
        </div>
    </div>

    <footer>
        Báo cáo tự động chẩn đoán tích hợp Trí nhớ SEO & Outcome Tracking - AI Marketing Hub
    </footer>
</body>
</html>
"""
    return html
