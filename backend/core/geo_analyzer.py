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


def _check_ai_citation_readiness(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Estimate answer extraction readiness (heuristic).

    Checks if content is structured in ways that AI systems
    can easily extract answers from.
    """
    score = 0
    recommendations = []
    text = soup.get_text().lower()

    # Direct Q&A format — highly extractable by AI
    qa_patterns = ["hỏi:", "đáp:", "câu hỏi", "trả lời", "faq", "q:", "a:"]
    qa_count = sum(1 for p in qa_patterns if p in text)
    if qa_count >= 3:
        score += 8
    elif qa_count >= 1:
        score += 4
    else:
        recommendations.append("Thêm nội dung dạng Hỏi-Đáp (Q&A) — AI trích dẫn trực tiếp dạng này")

    # Definition patterns — AI loves clear definitions
    definition_patterns = [" là ", " được định nghĩa ", " có nghĩa là ", " bao gồm "]
    def_count = sum(1 for p in definition_patterns if p in text)
    if def_count >= 2:
        score += 4
    elif def_count >= 1:
        score += 2

    # Step-by-step / numbered content
    ol_tags = soup.find_all("ol")
    if ol_tags:
        score += 4
    else:
        recommendations.append("Thêm nội dung dạng bước-bước (ordered list) — AI dễ trích xuất quy trình")

    # Concise paragraphs (AI prefers 2-3 sentence answers)
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 20]
    short_paragraphs = [p for p in paragraphs if 20 < len(p.split()) < 60]
    if len(short_paragraphs) >= 3:
        score += 4

    return {"score": min(20, score), "type": "heuristic", "recommendations": recommendations}


async def analyze_geo(url: str, keyword: str = "") -> Dict[str, Any]:
    """
    AI Search Readiness analysis for a URL.

    Returns readiness_score (0-100) with breakdown.
    Each category is labeled as deterministic, heuristic, or mixed.
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

    # ── Deterministic checks ──────────────────────────────────────────────
    schema_result = _check_schema(soup)          # max 20 → scale to 25
    structure_result = _check_content_structure(soup)  # max 20
    multimodal_result = _check_multimodal(soup)  # max 20 → scale to 15

    # ── Mixed checks ──────────────────────────────────────────────────────
    eeat_result = _check_eeat(soup)              # max 20

    # ── Heuristic checks ──────────────────────────────────────────────────
    citation_result = _check_ai_citation_readiness(soup)  # max 20

    # ── Scale scores to new weights ───────────────────────────────────────
    # Structured Data Quality: 25 pts
    structured_data_score = min(25, round(schema_result["score"] * 25 / 20))
    # Content Structure for AI: 20 pts
    content_structure_score = min(20, structure_result["score"])
    # E-E-A-T Clarity: 20 pts
    eeat_score = min(20, eeat_result["score"])
    # Answer Extraction Readiness: 20 pts
    citation_score = min(20, citation_result["score"])
    # Media & Corroboration: 15 pts
    media_score = min(15, round(multimodal_result["score"] * 15 / 20))

    total_score = structured_data_score + content_structure_score + eeat_score + citation_score + media_score

    # ── Context signals (NOT scored, just noted) ──────────────────────────
    domain = urlparse(url).netloc
    keyword_parts = keyword.lower().split() if keyword else []
    context_signals = {
        "is_https": url.startswith("https"),
        "has_real_domain": bool(domain),
        "keyword_in_domain": any(
            part in domain.lower() for part in keyword_parts if len(part) > 3
        ) if keyword_parts else False,
    }

    # Collect all recommendations
    all_recommendations = []
    for category, result in [
        ("Dữ liệu có cấu trúc", schema_result),
        ("Cấu trúc nội dung cho AI", structure_result),
        ("E-E-A-T (Uy tín)", eeat_result),
        ("Khả năng AI trích dẫn", citation_result),
        ("Đa phương tiện", multimodal_result),
    ]:
        for rec in result.get("recommendations", []):
            all_recommendations.append({"category": category, "recommendation": rec})

    # Grade
    if total_score >= 80: grade, grade_label = "A", "Xuất sắc"
    elif total_score >= 60: grade, grade_label = "B", "Tốt"
    elif total_score >= 40: grade, grade_label = "C", "Trung bình"
    elif total_score >= 20: grade, grade_label = "D", "Cần cải thiện"
    else: grade, grade_label = "F", "Yếu"

    return {
        "url": url,
        "keyword": keyword,
        "readiness_score": total_score,
        "score_type": "heuristic_readiness",
        "grade": grade,
        "grade_label": grade_label,
        # Backward compat — frontend may still read geo_score
        "geo_score": total_score,
        "breakdown": {
            "structured_data_quality": {
                "score": structured_data_score, "max": 25,
                "type": "deterministic",
                "details": schema_result,
            },
            "content_structure_for_ai": {
                "score": content_structure_score, "max": 20,
                "type": "deterministic",
                "details": structure_result,
            },
            "eeat_clarity": {
                "score": eeat_score, "max": 20,
                "type": "mixed",
                "details": eeat_result,
            },
            "answer_extraction_readiness": {
                "score": citation_score, "max": 20,
                "type": "heuristic",
                "details": citation_result,
            },
            "media_corroboration": {
                "score": media_score, "max": 15,
                "type": "deterministic",
                "details": multimodal_result,
            },
        },
        "context_signals": context_signals,
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


# ── New Schema Generators (Phase 20) ──────────────────────────────────────────


def generate_product_schema(
    name: str,
    description: str = "",
    image: str = "",
    brand: str = "",
    price: float = 0,
    currency: str = "VND",
    availability: str = "InStock",
    url: str = "",
    sku: str = "",
    rating_value: float = 0,
    rating_count: int = 0,
) -> str:
    """
    Generate Product Schema JSON-LD.

    Returns:
        JSON-LD string ready to paste into <script> tag
    """
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
    }
    if description:
        schema["description"] = description
    if image:
        schema["image"] = image
    if brand:
        schema["brand"] = {"@type": "Brand", "name": brand}
    if sku:
        schema["sku"] = sku
    if url:
        schema["url"] = url
    if price > 0:
        schema["offers"] = {
            "@type": "Offer",
            "price": price,
            "priceCurrency": currency,
            "availability": f"https://schema.org/{availability}",
        }
    if rating_value > 0:
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": rating_value,
            "reviewCount": max(1, rating_count),
        }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def generate_article_schema(
    headline: str,
    author: str = "",
    date_published: str = "",
    date_modified: str = "",
    description: str = "",
    image: str = "",
    publisher_name: str = "",
    publisher_logo: str = "",
    url: str = "",
    article_type: str = "Article",
) -> str:
    """
    Generate Article Schema JSON-LD.

    Args:
        article_type: "Article", "NewsArticle", "BlogPosting"

    Returns:
        JSON-LD string ready to paste into <script> tag
    """
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": article_type,
        "headline": headline,
    }
    if description:
        schema["description"] = description
    if author:
        schema["author"] = {"@type": "Person", "name": author}
    if date_published:
        schema["datePublished"] = date_published
    if date_modified:
        schema["dateModified"] = date_modified
    if image:
        schema["image"] = image
    if url:
        schema["url"] = url
        schema["mainEntityOfPage"] = {"@type": "WebPage", "@id": url}
    if publisher_name:
        publisher: Dict[str, Any] = {"@type": "Organization", "name": publisher_name}
        if publisher_logo:
            publisher["logo"] = {"@type": "ImageObject", "url": publisher_logo}
        schema["publisher"] = publisher

    return json.dumps(schema, ensure_ascii=False, indent=2)


def generate_breadcrumb_schema(
    items: List[Dict[str, str]],
) -> str:
    """
    Generate BreadcrumbList Schema JSON-LD.

    Args:
        items: List of {"name": "Trang chủ", "url": "https://..."} ordered from root to current
    Returns:
        JSON-LD string ready to paste into <script> tag
    """
    elements = []
    for i, item in enumerate(items, 1):
        elements.append({
            "@type": "ListItem",
            "position": i,
            "name": item.get("name", ""),
            "item": item.get("url", ""),
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


async def validate_schema_on_page(url: str) -> Dict[str, Any]:
    """
    Fetch a page and validate all Schema.org JSON-LD found.

    Returns detailed analysis of each schema block.
    """
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; AI-Marketing-Hub/1.0)"
            })
            html = resp.text
    except Exception as e:
        return {"error": f"Không thể truy cập: {str(e)}"}

    soup = BeautifulSoup(html, "html.parser")
    schemas_found = []
    errors = []
    missing_schemas = []

    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            raw = script.string or ""
            data = json.loads(raw)
            items = data if isinstance(data, list) else [data]
            for item in items:
                schema_type = item.get("@type", "Unknown")
                required_fields = _SCHEMA_REQUIRED_FIELDS.get(schema_type, [])
                present = [f for f in required_fields if f in item or any(f in str(v) for v in item.values())]
                missing = [f for f in required_fields if f not in present]
                schemas_found.append({
                    "type": schema_type,
                    "valid": len(missing) == 0,
                    "fields_present": list(item.keys()),
                    "required_missing": missing,
                    "char_count": len(raw),
                })
        except json.JSONDecodeError as e:
            errors.append({"raw_preview": (script.string or "")[:100], "error": str(e)})

    # Check for commonly expected schemas
    found_types = {s["type"] for s in schemas_found}
    for expected, label in [
        ("FAQPage", "FAQ Schema — giúp hiển thị FAQ snippet trên Google"),
        ("BreadcrumbList", "Breadcrumb Schema — cải thiện navigation trên SERP"),
        ("Article", "Article Schema — giúp Google hiểu bài viết"),
    ]:
        if expected not in found_types:
            missing_schemas.append({"type": expected, "reason": label})

    return {
        "url": url,
        "schemas_found": schemas_found,
        "total_schemas": len(schemas_found),
        "json_errors": errors,
        "missing_recommended": missing_schemas,
        "score": min(100, len(schemas_found) * 15 + sum(10 for s in schemas_found if s["valid"])),
    }


def _wrap_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Return dict with 'schema' (JSON-LD dict) and 'html' (script tag string)."""
    html = '<script type="application/ld+json">\n' + json.dumps(schema, ensure_ascii=False, indent=2) + '\n</script>'
    return {"schema": schema, "html": html}


def generate_organization_schema(
    name: str,
    url: str = "",
    logo_url: str = "",
    description: str = "",
    founder_name: str = "",
    email: str = "",
    phone: str = "",
    street: str = "",
    city: str = "",
    region: str = "",
    country: str = "VN",
    postal_code: str = "",
    social_profiles: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate Organization Schema JSON-LD.

    Returns:
        Dict with 'schema' (JSON-LD dict) and 'html' (script tag string)
    """
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": name,
    }
    if url:
        schema["url"] = url
    if logo_url:
        schema["logo"] = logo_url
    if description:
        schema["description"] = description
    if founder_name:
        schema["founder"] = {"@type": "Person", "name": founder_name}
    if email or phone:
        contact: Dict[str, Any] = {"@type": "ContactPoint"}
        if phone:
            contact["telephone"] = phone
            contact["contactType"] = "customer service"
        if email:
            contact["email"] = email
        schema["contactPoint"] = contact
    if street or city:
        address: Dict[str, Any] = {"@type": "PostalAddress"}
        if street:
            address["streetAddress"] = street
        if city:
            address["addressLocality"] = city
        if region:
            address["addressRegion"] = region
        if country:
            address["addressCountry"] = country
        if postal_code:
            address["postalCode"] = postal_code
        schema["address"] = address
    if social_profiles:
        schema["sameAs"] = social_profiles

    return _wrap_schema(schema)


def generate_website_schema(
    name: str,
    url: str = "",
    description: str = "",
    search_url_template: str = "",
) -> Dict[str, Any]:
    """
    Generate WebSite Schema JSON-LD with optional SearchAction.

    Returns:
        Dict with 'schema' (JSON-LD dict) and 'html' (script tag string)
    """
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": name,
    }
    if url:
        schema["url"] = url
    if description:
        schema["description"] = description
    if search_url_template:
        schema["potentialAction"] = {
            "@type": "SearchAction",
            "target": search_url_template,
            "query-input": "required name=search_term_string",
        }

    return _wrap_schema(schema)


def generate_jobposting_schema(
    title: str,
    description: str = "",
    company_name: str = "",
    company_url: str = "",
    city: str = "",
    region: str = "",
    country: str = "VN",
    salary_min: float = 0,
    salary_max: float = 0,
    salary_currency: str = "VND",
    employment_type: str = "FULL_TIME",
    date_posted: str = "",
    valid_through: str = "",
    remote: bool = False,
) -> Dict[str, Any]:
    """
    Generate JobPosting Schema JSON-LD.

    Returns:
        Dict with 'schema' (JSON-LD dict) and 'html' (script tag string)
    """
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": title,
    }
    if description:
        schema["description"] = description
    if employment_type:
        schema["employmentType"] = employment_type
    if date_posted:
        schema["datePosted"] = date_posted
    if valid_through:
        schema["validThrough"] = valid_through

    if company_name:
        hiring_org: Dict[str, Any] = {"@type": "Organization", "name": company_name}
        if company_url:
            hiring_org["sameAs"] = company_url
        schema["hiringOrganization"] = hiring_org

    if remote:
        schema["jobLocationType"] = "TELECOMMUTE"
    if city or region or country:
        loc_address: Dict[str, Any] = {"@type": "PostalAddress"}
        if city:
            loc_address["addressLocality"] = city
        if region:
            loc_address["addressRegion"] = region
        if country:
            loc_address["addressCountry"] = country
        schema["jobLocation"] = {"@type": "Place", "address": loc_address}

    if salary_min > 0 or salary_max > 0:
        salary: Dict[str, Any] = {
            "@type": "MonetaryAmount",
            "currency": salary_currency,
            "value": {
                "@type": "QuantitativeValue",
                "unitText": "MONTH",
            },
        }
        if salary_min > 0 and salary_max > 0:
            salary["value"]["minValue"] = salary_min
            salary["value"]["maxValue"] = salary_max
        elif salary_min > 0:
            salary["value"]["value"] = salary_min
        else:
            salary["value"]["value"] = salary_max
        schema["baseSalary"] = salary

    return _wrap_schema(schema)


def generate_event_schema(
    name: str,
    description: str = "",
    start_date: str = "",
    end_date: str = "",
    location_name: str = "",
    location_address: str = "",
    url: str = "",
    image_url: str = "",
    performer_name: str = "",
    offers_price: float = 0,
    offers_currency: str = "VND",
    offers_url: str = "",
) -> Dict[str, Any]:
    """
    Generate Event Schema JSON-LD.

    Returns:
        Dict with 'schema' (JSON-LD dict) and 'html' (script tag string)
    """
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": name,
    }
    if description:
        schema["description"] = description
    if start_date:
        schema["startDate"] = start_date
    if end_date:
        schema["endDate"] = end_date
    if url:
        schema["url"] = url
    if image_url:
        schema["image"] = image_url

    if location_name or location_address:
        location: Dict[str, Any] = {"@type": "Place"}
        if location_name:
            location["name"] = location_name
        if location_address:
            location["address"] = {
                "@type": "PostalAddress",
                "streetAddress": location_address,
            }
        schema["location"] = location

    if performer_name:
        schema["performer"] = {"@type": "Person", "name": performer_name}

    if offers_price > 0 or offers_url:
        offers: Dict[str, Any] = {"@type": "Offer"}
        if offers_price > 0:
            offers["price"] = offers_price
            offers["priceCurrency"] = offers_currency
        if offers_url:
            offers["url"] = offers_url
        offers["availability"] = "https://schema.org/InStock"
        schema["offers"] = offers

    return _wrap_schema(schema)


def generate_howto_schema(
    name: str,
    description: str = "",
    total_time: str = "",
    steps: Optional[List[Dict[str, str]]] = None,
    tools: Optional[List[str]] = None,
    supplies: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate HowTo Schema JSON-LD.

    Args:
        steps: List of {"name": "...", "text": "...", "image_url": "..."(optional)}
        tools: List of tool name strings
        supplies: List of supply name strings
        total_time: ISO 8601 duration (e.g. "PT30M")

    Returns:
        Dict with 'schema' (JSON-LD dict) and 'html' (script tag string)
    """
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": name,
    }
    if description:
        schema["description"] = description
    if total_time:
        schema["totalTime"] = total_time

    if tools:
        schema["tool"] = [{"@type": "HowToTool", "name": t} for t in tools]
    if supplies:
        schema["supply"] = [{"@type": "HowToSupply", "name": s} for s in supplies]

    if steps:
        step_list = []
        for i, step in enumerate(steps, 1):
            s: Dict[str, Any] = {
                "@type": "HowToStep",
                "position": i,
                "name": step.get("name", f"Bước {i}"),
                "text": step.get("text", ""),
            }
            if step.get("image_url"):
                s["image"] = step["image_url"]
            step_list.append(s)
        schema["step"] = step_list

    return _wrap_schema(schema)


def generate_video_schema(
    name: str,
    description: str = "",
    thumbnail_url: str = "",
    upload_date: str = "",
    duration: str = "",
    content_url: str = "",
    embed_url: str = "",
) -> Dict[str, Any]:
    """
    Generate VideoObject Schema JSON-LD.

    Args:
        duration: ISO 8601 duration (e.g. "PT5M30S")

    Returns:
        Dict with 'schema' (JSON-LD dict) and 'html' (script tag string)
    """
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": name,
    }
    if description:
        schema["description"] = description
    if thumbnail_url:
        schema["thumbnailUrl"] = thumbnail_url
    if upload_date:
        schema["uploadDate"] = upload_date
    if duration:
        schema["duration"] = duration
    if content_url:
        schema["contentUrl"] = content_url
    if embed_url:
        schema["embedUrl"] = embed_url

    return _wrap_schema(schema)


def generate_review_schema(
    item_name: str,
    item_type: str = "Product",
    author_name: str = "",
    rating_value: float = 0,
    best_rating: float = 5,
    review_body: str = "",
    date_published: str = "",
) -> Dict[str, Any]:
    """
    Generate Review Schema JSON-LD.

    Args:
        item_type: 'Product', 'LocalBusiness', or 'Organization'

    Returns:
        Dict with 'schema' (JSON-LD dict) and 'html' (script tag string)
    """
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Review",
        "itemReviewed": {
            "@type": item_type,
            "name": item_name,
        },
    }
    if author_name:
        schema["author"] = {"@type": "Person", "name": author_name}
    if review_body:
        schema["reviewBody"] = review_body
    if date_published:
        schema["datePublished"] = date_published
    if rating_value > 0:
        schema["reviewRating"] = {
            "@type": "Rating",
            "ratingValue": rating_value,
            "bestRating": best_rating,
        }

    return _wrap_schema(schema)


_SCHEMA_REQUIRED_FIELDS: Dict[str, List[str]] = {
    "Product": ["name", "offers"],
    "Article": ["headline", "author", "datePublished"],
    "NewsArticle": ["headline", "author", "datePublished"],
    "BlogPosting": ["headline", "author", "datePublished"],
    "FAQPage": ["mainEntity"],
    "LocalBusiness": ["name", "address"],
    "AutoDealer": ["name", "address"],
    "Organization": ["name", "url"],
    "BreadcrumbList": ["itemListElement"],
    "WebSite": ["name", "url"],
    "HowTo": ["name", "step"],
    "JobPosting": ["title", "hiringOrganization", "datePosted"],
    "Event": ["name", "startDate", "location"],
    "VideoObject": ["name", "description", "thumbnailUrl", "uploadDate"],
    "Review": ["itemReviewed", "author"],
}

