"""
API Router — File Converter (MarkItDown)

Provides:
- POST /api/convert/file      — Upload file → Markdown
- POST /api/convert/url       — URL → Markdown  
- GET  /api/convert/formats   — List supported formats
"""

from fastapi import APIRouter, UploadFile, File, Body

router = APIRouter()


@router.post("/api/convert/file")
async def convert_file(file: UploadFile = File(...)):
    """Upload a file and convert it to Markdown for SEO analysis."""
    from core.file_converter import convert_file_to_markdown

    contents = await file.read()
    result = convert_file_to_markdown(contents, file.filename or "unknown")
    return result


@router.post("/api/convert/url")
async def convert_url(url: str = Body(..., embed=True)):
    """Convert a URL's content to Markdown."""
    from core.file_converter import convert_url_to_markdown
    return convert_url_to_markdown(url)


@router.get("/api/convert/formats")
async def list_formats():
    """List all supported file formats for conversion."""
    from core.file_converter import get_supported_formats
    return get_supported_formats()


@router.post("/api/convert/file-seo")
async def convert_and_analyze(
    file: UploadFile = File(...),
    keyword: str = "",
):
    """Upload file → convert to Markdown → run SEO content analysis."""
    from core.file_converter import convert_file_to_markdown
    import asyncio

    contents = await file.read()
    converted = convert_file_to_markdown(contents, file.filename or "unknown")

    if not converted.get("success"):
        return converted

    markdown = converted["markdown"]

    # Run SEO analysis on the converted content
    analysis = {}
    try:
        from core.readability_scorer import score_readability
        analysis["readability"] = await asyncio.to_thread(score_readability, markdown)
    except Exception:
        pass

    try:
        from core.keyword_analyzer import KeywordAnalyzer
        analyzer = KeywordAnalyzer()
        kw = keyword or file.filename.replace(".", " ").split()[0]
        analysis["keywords"] = await asyncio.to_thread(analyzer.analyze, markdown, kw)
    except Exception:
        pass

    try:
        from core.content_scorer import ContentScorer
        scorer = ContentScorer()
        analysis["content_score"] = await asyncio.to_thread(scorer.score, markdown)
    except Exception:
        pass

    return {
        **converted,
        "seo_analysis": analysis,
        "pipeline": "file → markdown → seo",
    }

