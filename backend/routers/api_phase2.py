"""
API Router — Phase 14, 16-17: Backlink Analyzer, Technical SEO, Report Generator
"""

from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse

router = APIRouter()


# ─── Phase 16: Technical SEO Scanner ────────────────────────────────────

@router.post("/api/tech-seo/scan")
async def scan_tech_seo(
    url: str = Body(..., embed=True),
):
    from core.technical_seo import scan_technical_seo
    return await scan_technical_seo(url)


# ─── Phase 17: AI Report Generator ─────────────────────────────────────

@router.post("/api/report/generate")
async def generate_seo_report(
    url: str = Body(..., embed=True),
    keyword: str = Body("", embed=True),
):
    from core.report_generator import generate_report
    return await generate_report(url, keyword)


@router.post("/api/report/export")
async def export_seo_report(
    url: str = Body(..., embed=True),
    keyword: str = Body("", embed=True),
):
    from core.report_generator import generate_report, format_report_text
    report = await generate_report(url, keyword)
    text = format_report_text(report)
    return PlainTextResponse(
        content=text,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=seo_report_{url.split('//')[1].split('/')[0]}.txt"},
    )


# ─── Phase 14: Backlink Analyzer ───────────────────────────────────────

@router.post("/api/backlinks/analyze")
async def analyze_backlinks_api(
    url: str = Body(..., embed=True),
):
    from core.backlink_analyzer import analyze_backlinks
    return await analyze_backlinks(url)


# ─── Keyword Suggest (like SpinEditor) ──────────────────────────────────

@router.post("/api/keyword-suggest")
async def keyword_suggest_api(
    keyword: str = Body(..., embed=True),
    check_metrics: bool = Body(True, embed=True),
    max_keywords: int = Body(30, embed=True),
):
    """Gợi ý từ khóa (Google Suggest + Allintitle + KEI) — giống SpinEditor."""
    from core.keyword_suggest import keyword_suggest
    return await keyword_suggest(keyword, check_metrics=check_metrics, max_keywords=max_keywords)


# ─── SpinEditor Auto Scraper ───────────────────────────────────────────

@router.post("/api/spineditor/scrape")
async def scrape_spineditor_api(
    keyword: str = Body(..., embed=True),
):
    """Cào dữ liệu THẬT từ SpinEditor tự động (cần cookies đã lưu)."""
    from core.spineditor_scraper import scrape_spineditor
    return await scrape_spineditor(keyword)


@router.post("/api/spineditor/save-cookies")
async def save_spineditor_cookies_api(
    cookies: str = Body(..., embed=True),
):
    """Lưu cookies SpinEditor để cào tự động."""
    from core.spineditor_scraper import save_spineditor_cookies
    return await save_spineditor_cookies(cookies)


@router.get("/api/spineditor/session-status")
async def spineditor_session_status():
    """Kiểm tra trạng thái session SpinEditor."""
    from core.spineditor_scraper import load_spin_session
    session = load_spin_session()
    return {
        "has_session": bool(session.get("cookies")),
        "updated_at": session.get("updated_at"),
    }
