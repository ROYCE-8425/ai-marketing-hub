"""
GEO Analyzer — Phase 13

Generative Engine Optimization: Score and optimize content
for AI search engines (Google AI Overviews, ChatGPT, Gemini, Perplexity).
"""

import re
import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


def _check_schema(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check Schema.org JSON-LD quality for AI understanding."""
    schemas = []
    score = 0
    recommendations = []

    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                schemas.append(data.get("@type", "Unknown"))
            elif isinstance(data, list):
                for item in data:
                    schemas.append(item.get("@type", "Unknown"))
        except (json.JSONDecodeError, AttributeError):
            pass

    # Score schema types
    important_schemas = {
        "LocalBusiness": 4, "AutoDealer": 4, "Organization": 3,
        "FAQPage": 5, "WebSite": 2, "BreadcrumbList": 2,
        "Product": 3, "Offer": 2, "Article": 3, "HowTo": 4,
        "Review": 3, "AggregateRating": 3,
    }

    for schema_type in schemas:
        score += important_schemas.get(schema_type, 1)

    score = min(20, score)

    if "FAQPage" not in schemas:
        recommendations.append("Thêm FAQ Schema — giúp AI trích dẫn câu hỏi/trả lời trực tiếp")
    if not any(t in schemas for t in ["LocalBusiness", "AutoDealer", "Organization"]):
        recommendations.append("Thêm Schema LocalBusiness/Organization — AI cần hiểu loại hình doanh nghiệp")
    if "HowTo" not in schemas:
        recommendations.append("Thêm HowTo Schema — giúp AI hiểu quy trình (VD: quy trình mua xe trả góp)")
    if "AggregateRating" not in schemas and "Review" not in schemas:
        recommendations.append("Thêm Review/Rating Schema — AI ưu tiên nguồn có đánh giá")

    return {"score": score, "schemas_found": schemas, "recommendations": recommendations}


def _check_content_structure(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check content structure for AI readability."""
    score = 0
    recommendations = []

    # Check headings hierarchy
    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")
    h3_tags = soup.find_all("h3")

    if h1_tags:
        score += 4
    else:
        recommendations.append("Thêm thẻ H1 — AI cần hiểu chủ đề chính của trang")

    if h2_tags:
        score += min(4, len(h2_tags))
    else:
        recommendations.append("Thêm thẻ H2 — chia nội dung thành các phần rõ ràng")

    if h3_tags:
        score += min(3, len(h3_tags))

    # Check bullet points / lists
    ul_tags = soup.find_all("ul")
    ol_tags = soup.find_all("ol")
    if ul_tags or ol_tags:
        score += 3
    else:
        recommendations.append("Thêm danh sách (bullet points) — AI dễ trích xuất thông tin từ danh sách")

    # Check tables
    if soup.find_all("table"):
        score += 3
    else:
        recommendations.append("Thêm bảng so sánh — AI ưu tiên dữ liệu có cấu trúc (VD: bảng giá xe)")

    # Check Q&A format
    text = soup.get_text().lower()
    qa_patterns = ["hỏi:", "đáp:", "câu hỏi", "trả lời", "faq", "?"]
    qa_count = sum(1 for p in qa_patterns if p in text)
    if qa_count >= 2:
        score += 3
    else:
        recommendations.append("Thêm nội dung dạng Hỏi-Đáp (Q&A) — AI trích dẫn trực tiếp dạng này")

    return {"score": min(20, score), "headings": {"h1": len(h1_tags), "h2": len(h2_tags), "h3": len(h3_tags)},
            "lists": len(ul_tags) + len(ol_tags), "tables": len(soup.find_all("table")),
            "recommendations": recommendations}


def _check_eeat(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check E-E-A-T signals (Experience, Expertise, Authority, Trust)."""
    score = 0
    recommendations = []
    text = soup.get_text().lower()

    # Author info
    author_meta = soup.find("meta", {"name": "author"})
    if author_meta:
        score += 4
    else:
        recommendations.append("Thêm meta author — AI cần biết ai viết nội dung")

    # Date/update info
    time_tags = soup.find_all("time")
    date_meta = soup.find("meta", {"property": "article:modified_time"}) or \
                soup.find("meta", {"property": "article:published_time"})
    if time_tags or date_meta:
        score += 3
    else:
        recommendations.append("Thêm ngày cập nhật — AI ưu tiên nội dung mới")

    # Trust signals
    trust_words = ["chính hãng", "ủy quyền", "đại lý", "chứng nhận", "bảo hành",
                   "hotline", "giấy phép", "đăng ký", "verified", "official"]
    trust_count = sum(1 for w in trust_words if w in text)
    score += min(5, trust_count)

    if trust_count < 3:
        recommendations.append("Thêm tín hiệu uy tín (chính hãng, ủy quyền, bảo hành, chứng nhận)")

    # Contact info
    phone_pattern = r'\d{4}[\s.-]?\d{3}[\s.-]?\d{3}'
    if re.search(phone_pattern, text):
        score += 3
    else:
        recommendations.append("Hiển thị số điện thoại rõ ràng trên trang")

    # Social proof
    social_words = ["đánh giá", "review", "khách hàng", "feedback", "testimonial"]
    if any(w in text for w in social_words):
        score += 3
    else:
        recommendations.append("Thêm đánh giá/review từ khách hàng — AI trích dẫn nguồn có social proof")

    # Address/location
    if soup.find("meta", {"name": "geo.placename"}) or "địa chỉ" in text:
        score += 2

    return {"score": min(20, score), "recommendations": recommendations}


def _check_multimodal(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check multimodal content (images, video, structured data)."""
    score = 0
    recommendations = []

    # Images with alt text
    images = soup.find_all("img")
    images_with_alt = [img for img in images if img.get("alt", "").strip()]

    if images:
        alt_ratio = len(images_with_alt) / len(images) if images else 0
        score += min(6, int(alt_ratio * 6))
        if alt_ratio < 0.8:
            missing = len(images) - len(images_with_alt)
            recommendations.append(f"Thêm alt text cho {missing} hình ảnh — AI dùng alt text để hiểu hình")
    else:
        recommendations.append("Thêm hình ảnh với alt text mô tả chi tiết")

    # Video content
    videos = soup.find_all(["video", "iframe"])
    youtube_embeds = [v for v in videos if "youtube" in str(v.get("src", ""))]
    if videos or youtube_embeds:
        score += 5
    else:
        recommendations.append("Nhúng video (YouTube) — AI ưu tiên nội dung đa phương tiện")

    # Tables/comparison data
    tables = soup.find_all("table")
    if tables:
        score += 4
    else:
        recommendations.append("Thêm bảng so sánh sản phẩm — AI dễ trích xuất dữ liệu bảng")

    # Infographic indicators
    figure_tags = soup.find_all("figure")
    if figure_tags:
        score += 3

    # Structured pricing
    if re.search(r'\d+[.,]?\d*\s*(triệu|đ|VND|vnđ)', soup.get_text()):
        score += 2

    return {"score": min(20, score), "images_total": len(images),
            "images_with_alt": len(images_with_alt), "videos": len(videos),
            "recommendations": recommendations}


def _check_ai_visibility(keyword: str, url: str) -> Dict[str, Any]:
    """Estimate AI visibility based on content quality signals."""
    # Note: Actually querying ChatGPT/Gemini would require their APIs
    # This provides a heuristic score based on known ranking factors
    score = 0
    recommendations = []

    # Domain authority signals (heuristic)
    domain = urlparse(url).netloc
    if domain:
        score += 5  # Has a real domain

    # Check if keyword is in domain
    keyword_parts = keyword.lower().split()
    domain_lower = domain.lower()
    if any(part in domain_lower for part in keyword_parts if len(part) > 3):
        score += 5
        recommendations.append("✅ Keyword có trong tên miền — AI nhận diện liên quan cao")
    else:
        recommendations.append("Cân nhắc EMD (Exact Match Domain) cho từ khóa chính")

    # HTTPS
    if url.startswith("https"):
        score += 3
    else:
        recommendations.append("Chuyển sang HTTPS — AI ưu tiên nguồn bảo mật")

    # Estimate based on other scores (will be filled by caller)
    score += 7  # Base score for having a website

    recommendations.append("Đăng ký Google Business Profile — giúp AI nhận diện doanh nghiệp địa phương")
    recommendations.append("Tạo nội dung dạng Q&A trên website — AI trích dẫn trực tiếp")

    return {"score": min(20, score), "recommendations": recommendations}


async def analyze_geo(url: str, keyword: str = "") -> Dict[str, Any]:
    """
    Full GEO analysis for a URL.

    Returns GEO score (0-100) with breakdown and recommendations.
    """
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; AI-Marketing-Hub/1.0)"
            })
            html = resp.text
    except Exception as e:
        return {"error": f"Không thể truy cập {url}: {str(e)}"}

    soup = BeautifulSoup(html, "html.parser")

    schema_result = _check_schema(soup)
    structure_result = _check_content_structure(soup)
    eeat_result = _check_eeat(soup)
    multimodal_result = _check_multimodal(soup)
    visibility_result = _check_ai_visibility(keyword, url)

    total_score = (
        schema_result["score"] +
        structure_result["score"] +
        eeat_result["score"] +
        multimodal_result["score"] +
        visibility_result["score"]
    )

    # Collect all recommendations sorted by impact
    all_recommendations = []
    for category, result in [
        ("Schema & Dữ liệu có cấu trúc", schema_result),
        ("Cấu trúc nội dung", structure_result),
        ("E-E-A-T (Uy tín)", eeat_result),
        ("Đa phương tiện", multimodal_result),
        ("AI Visibility", visibility_result),
    ]:
        for rec in result["recommendations"]:
            all_recommendations.append({"category": category, "recommendation": rec})

    # Grade
    if total_score >= 80:
        grade = "A"
        grade_label = "Xuất sắc"
    elif total_score >= 60:
        grade = "B"
        grade_label = "Tốt"
    elif total_score >= 40:
        grade = "C"
        grade_label = "Trung bình"
    elif total_score >= 20:
        grade = "D"
        grade_label = "Cần cải thiện"
    else:
        grade = "F"
        grade_label = "Yếu"

    return {
        "url": url,
        "keyword": keyword,
        "geo_score": total_score,
        "grade": grade,
        "grade_label": grade_label,
        "breakdown": {
            "schema": {"score": schema_result["score"], "max": 20, "details": schema_result},
            "structure": {"score": structure_result["score"], "max": 20, "details": structure_result},
            "eeat": {"score": eeat_result["score"], "max": 20, "details": eeat_result},
            "multimodal": {"score": multimodal_result["score"], "max": 20, "details": multimodal_result},
            "ai_visibility": {"score": visibility_result["score"], "max": 20, "details": visibility_result},
        },
        "recommendations": all_recommendations,
        "total_recommendations": len(all_recommendations),
    }


def generate_faq_schema(questions: List[Dict[str, str]]) -> str:
    """
    Generate FAQ Schema JSON-LD from Q&A pairs.

    Args:
        questions: List of {"question": "...", "answer": "..."} dicts
    Returns:
        JSON-LD string ready to paste into <script> tag
    """
    faq_items = []
    for qa in questions:
        faq_items.append({
            "@type": "Question",
            "name": qa.get("question", ""),
            "acceptedAnswer": {
                "@type": "Answer",
                "text": qa.get("answer", ""),
            },
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_items,
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def generate_local_business_schema(
    name: str,
    address: str,
    phone: str,
    url: str,
    business_type: str = "AutoDealer",
    description: str = "",
    opening_hours: str = "Mo-Sa 08:00-17:30",
    latitude: float = 0,
    longitude: float = 0,
    image: str = "",
    price_range: str = "",
) -> str:
    """
    Generate LocalBusiness Schema JSON-LD.

    Returns:
        JSON-LD string ready to paste into <script> tag
    """
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": business_type,
        "name": name,
        "url": url,
        "telephone": phone,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": address,
            "addressCountry": "VN",
        },
    }

    if description:
        schema["description"] = description
    if image:
        schema["image"] = image
    if price_range:
        schema["priceRange"] = price_range
    if opening_hours:
        schema["openingHours"] = opening_hours
    if latitude and longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": latitude,
            "longitude": longitude,
        }

    return json.dumps(schema, ensure_ascii=False, indent=2)


async def generate_faq_from_content(url: str) -> Dict[str, Any]:
    """Extract potential FAQ pairs from a webpage using AI."""
    import os

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; AI-Marketing-Hub/1.0)"
            })
            html = resp.text
    except Exception as e:
        return {"error": f"Không thể truy cập: {str(e)}"}

    soup = BeautifulSoup(html, "html.parser")

    # Extract text content
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)[:3000]

    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        return {"error": "Chưa cấu hình GROQ_API_KEY"}

    prompt = f"""Dựa trên nội dung website sau, tạo 5-8 câu hỏi FAQ phổ biến mà khách hàng thường hỏi.
Trả lời bằng tiếng Việt. Format JSON array:
[{{"question": "...", "answer": "..."}}]

Chỉ trả về JSON, không giải thích.

NỘI DUNG:
{text}"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": 2048,
                },
            )
            if resp.status_code != 200:
                return {"error": f"AI lỗi: {resp.status_code}"}

            ai_text = resp.json()["choices"][0]["message"]["content"].strip()
            # Extract JSON from response
            match = re.search(r'\[.*\]', ai_text, re.DOTALL)
            if match:
                faqs = json.loads(match.group())
                schema_code = generate_faq_schema(faqs)
                return {
                    "faqs": faqs,
                    "schema_code": schema_code,
                    "total_faqs": len(faqs),
                }
            return {"error": "AI không trả về format JSON hợp lệ"}
    except Exception as e:
        return {"error": f"Lỗi: {str(e)}"}
