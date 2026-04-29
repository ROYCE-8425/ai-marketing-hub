"""
Spin Editor — Phase 11 (Upgraded)

AI-powered content rewriting using Groq LLaMA.
Features:
- 3 rewrite levels (light/medium/heavy)
- Multi-version: generate 3 versions at once
- Tone selector: professional, friendly, sales
- Paragraph-level spin
- Preserves SEO keywords
"""

import os
import re
import asyncio
from typing import Any, Dict, List, Optional
from difflib import SequenceMatcher

import httpx


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

TONE_MAP = {
    "professional": "Giọng văn chuyên nghiệp, trang trọng, sử dụng thuật ngữ chuyên ngành. Phù hợp báo cáo, tài liệu công ty.",
    "friendly": "Giọng văn thân thiện, gần gũi, dễ hiểu. Phù hợp blog, mạng xã hội.",
    "sales": "Giọng văn bán hàng, thuyết phục, có CTA mạnh. Nhấn mạnh lợi ích, ưu đãi. Phù hợp landing page, quảng cáo.",
    "neutral": "Giọng văn trung lập, khách quan, mang tính thông tin. Phù hợp bài viết tổng hợp.",
}


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


def _build_prompt(content: str, level: str, tone: str, preserve_keywords: Optional[List[str]], language: str) -> str:
    """Build the spin prompt."""
    level_map = {
        "light": "Viết lại khoảng 30% câu chữ. Giữ nguyên phần lớn cấu trúc và ý chính, chỉ đổi một số từ/cụm từ đồng nghĩa.",
        "medium": "Viết lại khoảng 60% câu chữ. Đổi cấu trúc câu, thay thế nhiều cụm từ nhưng giữ nguyên ý nghĩa.",
        "heavy": "Viết lại gần như hoàn toàn (90%). Đổi cấu trúc câu, thứ tự trình bày, cách diễn đạt — nhưng giữ nguyên thông tin và ý chính.",
    }

    level_instruction = level_map.get(level, level_map["medium"])
    tone_instruction = TONE_MAP.get(tone, TONE_MAP["neutral"])

    keywords_text = ""
    if preserve_keywords:
        kw_list = ", ".join(f'"{k}"' for k in preserve_keywords)
        keywords_text = f"\n\nQUAN TRỌNG: Giữ nguyên các từ khóa SEO sau (KHÔNG thay đổi): {kw_list}"

    lang_map = {"vi": "tiếng Việt", "en": "tiếng Anh"}
    lang_name = lang_map.get(language, "tiếng Việt")

    return f"""Bạn là chuyên gia viết lại nội dung SEO. Hãy viết lại đoạn văn sau bằng {lang_name}.

HƯỚNG DẪN: {level_instruction}

GIỌNG VĂN: {tone_instruction}

YÊU CẦU:
- Giữ nguyên ý nghĩa và thông tin
- Đảm bảo văn phong tự nhiên, đọc trôi chảy
- KHÔNG thêm thông tin mới
- KHÔNG dùng markdown hoặc tiêu đề
- Chỉ trả về nội dung đã viết lại, không giải thích{keywords_text}

NỘI DUNG GỐC:
{content}"""


async def _call_groq(prompt: str, temperature: float) -> Optional[str]:
    """Single Groq API call."""
    if not GROQ_API_KEY:
        return None
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
                    "temperature": temperature,
                    "max_tokens": 4096,
                },
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()
            return re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    except Exception:
        return None


def _format_result(original: str, rewritten: str, level: str, tone: str,
                   preserve_keywords: Optional[List[str]], language: str) -> Dict[str, Any]:
    """Format a single spin result."""
    similarity = _similarity(original, rewritten)
    return {
        "original": original,
        "rewritten": rewritten,
        "diff": _diff_segments(original, rewritten),
        "uniqueness_percent": round((1 - similarity) * 100, 1),
        "similarity_percent": round(similarity * 100, 1),
        "original_words": len(original.split()),
        "rewritten_words": len(rewritten.split()),
        "level": level,
        "tone": tone,
        "preserved_keywords": preserve_keywords or [],
        "language": language,
    }


async def spin_content(
    content: str,
    level: str = "medium",
    preserve_keywords: Optional[List[str]] = None,
    language: str = "vi",
    tone: str = "neutral",
) -> Dict[str, Any]:
    """Rewrite content using AI (single version)."""
    if not content or len(content.strip()) < 20:
        return {"error": "Nội dung quá ngắn (cần ít nhất 20 ký tự)"}
    if not GROQ_API_KEY:
        return {"error": "Chưa cấu hình GROQ_API_KEY"}

    prompt = _build_prompt(content.strip(), level, tone, preserve_keywords, language)
    temp = 0.7 if level == "light" else 0.85 if level == "medium" else 0.95

    rewritten = await _call_groq(prompt, temp)
    if not rewritten:
        return {"error": "Groq API không phản hồi — thử lại sau"}

    return _format_result(content.strip(), rewritten, level, tone, preserve_keywords, language)


async def spin_multi_version(
    content: str,
    level: str = "medium",
    preserve_keywords: Optional[List[str]] = None,
    language: str = "vi",
    tone: str = "neutral",
    num_versions: int = 3,
) -> Dict[str, Any]:
    """Generate multiple spin versions concurrently."""
    if not content or len(content.strip()) < 20:
        return {"error": "Nội dung quá ngắn (cần ít nhất 20 ký tự)"}
    if not GROQ_API_KEY:
        return {"error": "Chưa cấu hình GROQ_API_KEY"}

    num_versions = min(5, max(1, num_versions))
    prompt = _build_prompt(content.strip(), level, tone, preserve_keywords, language)

    # Use different temperatures for variety
    temps = [0.7 + (i * 0.08) for i in range(num_versions)]

    tasks = [_call_groq(prompt, t) for t in temps]
    results_raw = await asyncio.gather(*tasks)

    versions = []
    for i, rewritten in enumerate(results_raw):
        if rewritten:
            result = _format_result(content.strip(), rewritten, level, tone, preserve_keywords, language)
            result["version"] = i + 1
            versions.append(result)

    if not versions:
        return {"error": "Không thể tạo bản spin — thử lại sau"}

    # Sort by uniqueness (highest first)
    versions.sort(key=lambda v: v["uniqueness_percent"], reverse=True)

    return {
        "versions": versions,
        "total_versions": len(versions),
        "best_uniqueness": versions[0]["uniqueness_percent"] if versions else 0,
    }


async def spin_paragraphs(
    content: str,
    level: str = "medium",
    preserve_keywords: Optional[List[str]] = None,
    language: str = "vi",
    tone: str = "neutral",
) -> Dict[str, Any]:
    """Spin each paragraph independently."""
    if not content or len(content.strip()) < 20:
        return {"error": "Nội dung quá ngắn (cần ít nhất 20 ký tự)"}
    if not GROQ_API_KEY:
        return {"error": "Chưa cấu hình GROQ_API_KEY"}

    paragraphs = [p.strip() for p in content.strip().split("\n\n") if p.strip()]
    if len(paragraphs) < 2:
        # Fall back to single spin if only one paragraph
        return await spin_content(content, level, preserve_keywords, language, tone)

    temp = 0.7 if level == "light" else 0.85 if level == "medium" else 0.95
    tasks = []
    for para in paragraphs:
        prompt = _build_prompt(para, level, tone, preserve_keywords, language)
        tasks.append(_call_groq(prompt, temp))

    results_raw = await asyncio.gather(*tasks)

    spun_paragraphs = []
    for i, (original, rewritten) in enumerate(zip(paragraphs, results_raw)):
        if rewritten:
            sim = _similarity(original, rewritten)
            spun_paragraphs.append({
                "index": i,
                "original": original,
                "rewritten": rewritten,
                "uniqueness_percent": round((1 - sim) * 100, 1),
                "diff": _diff_segments(original, rewritten),
            })
        else:
            spun_paragraphs.append({
                "index": i,
                "original": original,
                "rewritten": original,
                "uniqueness_percent": 0,
                "diff": [{"type": "same", "text": original}],
                "error": "Không thể spin đoạn này",
            })

    # Combine all rewritten paragraphs
    full_rewritten = "\n\n".join(p["rewritten"] for p in spun_paragraphs)
    overall_sim = _similarity(content.strip(), full_rewritten)

    return {
        "paragraphs": spun_paragraphs,
        "full_rewritten": full_rewritten,
        "overall_uniqueness": round((1 - overall_sim) * 100, 1),
        "total_paragraphs": len(spun_paragraphs),
        "level": level,
        "tone": tone,
    }

