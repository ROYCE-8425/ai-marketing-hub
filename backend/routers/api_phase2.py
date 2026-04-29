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
