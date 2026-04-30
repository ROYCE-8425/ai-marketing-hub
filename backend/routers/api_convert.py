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
