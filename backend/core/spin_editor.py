"""
Spin Editor — Phase 11

AI-powered content rewriting using Groq LLaMA.
Preserves SEO keywords while changing sentence structure.
"""

import os
import re
from typing import Any, Dict, List, Optional
from difflib import SequenceMatcher

import httpx


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def _similarity(a: str, b: str) -> float:
    """Calculate similarity ratio between two texts."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _diff_segments(original: str, rewritten: str) -> List[Dict[str, str]]:
    """Compute inline diff between original and rewritten text."""
    sm = SequenceMatcher(None, original.split(), rewritten.split())
    segments = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            segments.append({"type": "same", "text": " ".join(original.split()[i1:i2])})
        elif tag == "replace":
            segments.append({"type": "removed", "text": " ".join(original.split()[i1:i2])})
            segments.append({"type": "added", "text": " ".join(rewritten.split()[j1:j2])})
        elif tag == "delete":
            segments.append({"type": "removed", "text": " ".join(original.split()[i1:i2])})
        elif tag == "insert":
            segments.append({"type": "added", "text": " ".join(rewritten.split()[j1:j2])})
    return segments


async def spin_content(
    content: str,
    level: str = "medium",
    preserve_keywords: Optional[List[str]] = None,
    language: str = "vi",
) -> Dict[str, Any]:
    """
    Rewrite content using AI.

    Args:
        content: Original text to rewrite
        level: 'light' (30%), 'medium' (60%), or 'heavy' (90%)
        preserve_keywords: SEO keywords to keep unchanged
        language: Target language

    Returns:
        Dict with rewritten content, diff, and uniqueness score
    """
    if not content or len(content.strip()) < 20:
        return {"error": "Nội dung quá ngắn (cần ít nhất 20 ký tự)"}

    if not GROQ_API_KEY:
        return {"error": "Chưa cấu hình GROQ_API_KEY"}

    level_map = {
        "light": "Viết lại khoảng 30% câu chữ. Giữ nguyên phần lớn cấu trúc và ý chính, chỉ đổi một số từ/cụm từ đồng nghĩa.",
        "medium": "Viết lại khoảng 60% câu chữ. Đổi cấu trúc câu, thay thế nhiều cụm từ nhưng giữ nguyên ý nghĩa.",
        "heavy": "Viết lại gần như hoàn toàn (90%). Đổi cấu trúc câu, thứ tự trình bày, cách diễn đạt — nhưng giữ nguyên thông tin và ý chính.",
    }

    level_instruction = level_map.get(level, level_map["medium"])
    keywords_text = ""
    if preserve_keywords:
        kw_list = ", ".join(f'"{k}"' for k in preserve_keywords)
        keywords_text = f"\n\nQUAN TRỌNG: Giữ nguyên các từ khóa SEO sau (KHÔNG thay đổi): {kw_list}"

    lang_map = {"vi": "tiếng Việt", "en": "tiếng Anh"}
    lang_name = lang_map.get(language, "tiếng Việt")

    prompt = f"""Bạn là chuyên gia viết lại nội dung SEO. Hãy viết lại đoạn văn sau bằng {lang_name}.

HƯỚNG DẪN: {level_instruction}

YÊU CẦU:
- Giữ nguyên ý nghĩa và thông tin
- Đảm bảo văn phong tự nhiên, đọc trôi chảy
- KHÔNG thêm thông tin mới
- KHÔNG dùng markdown hoặc tiêu đề
- Chỉ trả về nội dung đã viết lại, không giải thích{keywords_text}

NỘI DUNG GỐC:
{content}"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7 if level == "light" else 0.85 if level == "medium" else 0.95,
                    "max_tokens": 4096,
                },
            )

            if resp.status_code != 200:
                return {"error": f"Groq API lỗi: {resp.status_code}"}

            data = resp.json()
            rewritten = data["choices"][0]["message"]["content"].strip()

            # Remove any AI artifacts
            rewritten = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', rewritten)

            # Calculate uniqueness
            similarity = _similarity(content, rewritten)
            uniqueness = round((1 - similarity) * 100, 1)

            # Generate diff
            diff = _diff_segments(content, rewritten)

            # Word counts
            original_words = len(content.split())
            rewritten_words = len(rewritten.split())

            return {
                "original": content,
                "rewritten": rewritten,
                "diff": diff,
                "uniqueness_percent": uniqueness,
                "similarity_percent": round(similarity * 100, 1),
                "original_words": original_words,
                "rewritten_words": rewritten_words,
                "level": level,
                "preserved_keywords": preserve_keywords or [],
                "language": language,
            }

    except httpx.TimeoutException:
        return {"error": "Groq API timeout — thử lại sau"}
    except Exception as e:
        return {"error": f"Lỗi: {str(e)}"}
