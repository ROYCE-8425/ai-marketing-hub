"""
File Converter — MarkItDown Integration

Convert uploaded files (PDF, Word, Excel, PowerPoint, HTML, images)
to Markdown for SEO content analysis.

Uses Microsoft's MarkItDown library (119K+ stars).
"""

from markitdown import MarkItDown
from typing import Optional
import tempfile
import os


_md = MarkItDown(enable_plugins=False)


def convert_file_to_markdown(
    file_bytes: bytes,
    filename: str,
    mime_type: Optional[str] = None,
) -> dict:
    """
    Convert a file to Markdown text.

    Args:
        file_bytes: Raw file content
        filename: Original filename (used for extension detection)
        mime_type: Optional MIME type hint

    Returns:
        dict with keys: markdown, filename, word_count, char_count
    """
    ext = os.path.splitext(filename)[1].lower()

    # Write to temp file (MarkItDown needs a file path)
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        result = _md.convert(tmp_path)
        text = result.text_content or ""

        # Clean up excessive whitespace
        import re
        text = re.sub(r"\n{4,}", "\n\n\n", text)

        words = len(text.split())
        chars = len(text)

        return {
            "markdown": text,
            "filename": filename,
            "word_count": words,
            "char_count": chars,
            "extension": ext,
            "success": True,
        }
    except Exception as e:
        return {
            "markdown": "",
            "filename": filename,
            "word_count": 0,
            "char_count": 0,
            "extension": ext,
            "success": False,
            "error": str(e),
        }
    finally:
        os.unlink(tmp_path)


def convert_url_to_markdown(url: str) -> dict:
    """
    Convert a URL's content to Markdown.

    Args:
        url: Web page URL

    Returns:
        dict with keys: markdown, url, word_count, char_count
    """
    try:
        result = _md.convert_url(url)
        text = result.text_content or ""

        import re
        text = re.sub(r"\n{4,}", "\n\n\n", text)

        words = len(text.split())
        chars = len(text)

        return {
            "markdown": text,
            "url": url,
            "word_count": words,
            "char_count": chars,
            "success": True,
        }
    except Exception as e:
        return {
            "markdown": "",
            "url": url,
            "word_count": 0,
            "char_count": 0,
            "success": False,
            "error": str(e),
        }


SUPPORTED_EXTENSIONS = {
    ".pdf": "PDF Document",
    ".docx": "Microsoft Word",
    ".doc": "Microsoft Word (Legacy)",
    ".pptx": "Microsoft PowerPoint",
    ".xlsx": "Microsoft Excel",
    ".xls": "Microsoft Excel (Legacy)",
    ".csv": "CSV Spreadsheet",
    ".html": "HTML Page",
    ".htm": "HTML Page",
    ".json": "JSON Data",
    ".xml": "XML Data",
    ".txt": "Plain Text",
    ".md": "Markdown",
    ".epub": "E-Book (EPUB)",
    ".zip": "ZIP Archive",
    ".jpg": "JPEG Image",
    ".jpeg": "JPEG Image",
    ".png": "PNG Image",
    ".mp3": "Audio (MP3)",
    ".wav": "Audio (WAV)",
}


def get_supported_formats() -> dict:
    """Return list of supported file formats."""
    return {
        "formats": SUPPORTED_EXTENSIONS,
        "total": len(SUPPORTED_EXTENSIONS),
    }
