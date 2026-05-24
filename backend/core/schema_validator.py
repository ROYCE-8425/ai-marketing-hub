"""
Schema.org JSON-LD Validator — SEO Tools

Validates structured data (JSON-LD) on a web page:
- Fetches page HTML
- Extracts all <script type="application/ld+json"> blocks
- Parses JSON and validates structure
- Checks @type against known Schema.org types
- Validates required properties for common types:
  Article, Product, LocalBusiness, Organization, FAQ,
  BreadcrumbList, WebPage, WebSite, Person, Event,
  Recipe, VideoObject, HowTo, Review
- Returns validation results with errors and warnings
"""

import json
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (compatible; AI-Marketing-Hub/1.0; SchemaValidator)"


# ── Required / recommended properties per @type ───────────────────────────

SCHEMA_RULES: Dict[str, Dict[str, List[str]]] = {
    "Article": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["image", "dateModified", "publisher", "description", "mainEntityOfPage"],
    },
    "NewsArticle": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["image", "dateModified", "publisher", "description"],
    },
    "BlogPosting": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["image", "dateModified", "publisher", "description"],
    },
    "Product": {
        "required": ["name"],
        "recommended": ["image", "description", "offers", "brand", "sku", "review", "aggregateRating"],
    },
    "LocalBusiness": {
        "required": ["name", "address"],
        "recommended": ["telephone", "openingHours", "image", "url", "geo", "priceRange"],
    },
    "Organization": {
        "required": ["name"],
        "recommended": ["url", "logo", "sameAs", "contactPoint", "description"],
    },
    "FAQPage": {
        "required": ["mainEntity"],
        "recommended": [],
    },
    "BreadcrumbList": {
        "required": ["itemListElement"],
        "recommended": [],
    },
    "WebPage": {
        "required": ["name"],
        "recommended": ["url", "description"],
    },
    "WebSite": {
        "required": ["name", "url"],
        "recommended": ["potentialAction", "description"],
    },
    "Person": {
        "required": ["name"],
        "recommended": ["url", "image", "jobTitle", "sameAs"],
    },
    "Event": {
        "required": ["name", "startDate", "location"],
        "recommended": ["endDate", "description", "image", "offers", "performer", "organizer"],
    },
    "Recipe": {
        "required": ["name", "recipeIngredient", "recipeInstructions"],
        "recommended": ["image", "author", "datePublished", "prepTime", "cookTime", "nutrition"],
    },
    "VideoObject": {
        "required": ["name", "uploadDate", "thumbnailUrl"],
        "recommended": ["description", "contentUrl", "duration", "embedUrl"],
    },
    "HowTo": {
        "required": ["name", "step"],
        "recommended": ["image", "totalTime", "estimatedCost", "supply", "tool"],
    },
    "Review": {
        "required": ["itemReviewed", "author"],
        "recommended": ["reviewRating", "datePublished", "reviewBody"],
    },
    "AggregateRating": {
        "required": ["ratingValue", "reviewCount"],
        "recommended": ["bestRating", "worstRating"],
    },
    "Offer": {
        "required": ["price", "priceCurrency"],
        "recommended": ["availability", "url", "validFrom", "seller"],
    },
    "ItemList": {
        "required": ["itemListElement"],
        "recommended": ["numberOfItems"],
    },
}

# Types we recognise but have no strict rules for
KNOWN_TYPES = set(SCHEMA_RULES.keys()) | {
    "SearchAction", "ReadAction", "EntryPoint", "ImageObject",
    "PostalAddress", "GeoCoordinates", "ContactPoint", "MonetaryAmount",
    "ListItem", "Question", "Answer", "Thing", "CreativeWork",
    "MedicalWebPage", "CollectionPage", "AboutPage", "ContactPage",
    "Service", "SoftwareApplication", "MobileApplication",
    "Course", "JobPosting", "Dataset",
}


async def validate_schema(url: str) -> Dict[str, Any]:
    """
    Fetch a page and validate all JSON-LD structured data blocks.

    Returns:
        Dict with schemas_found, valid, errors, warnings, details per block.
    """
    # ── 1. Fetch page HTML ─────────────────────────────────────────────
    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            resp = await client.get(url)
    except httpx.TimeoutException:
        return _error_result(url, "Timeout khi tải trang.")
    except httpx.RequestError as exc:
        return _error_result(url, f"Không thể truy cập trang: {exc}")

    if resp.status_code >= 400:
        return _error_result(url, f"Trang trả về HTTP {resp.status_code}.")

    # ── 2. Extract JSON-LD blocks ──────────────────────────────────────
    soup = BeautifulSoup(resp.text, "lxml")
    ld_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})

    if not ld_scripts:
        return {
            "url": url,
            "schemas_found": 0,
            "valid": False,
            "blocks": [],
            "errors": ["Không tìm thấy structured data (JSON-LD) trên trang."],
            "warnings": ["Nên thêm JSON-LD để Google hiểu nội dung trang tốt hơn."],
            "summary": "Không có structured data",
        }

    # ── 3. Parse and validate each block ───────────────────────────────
    all_errors: List[str] = []
    all_warnings: List[str] = []
    blocks: List[Dict[str, Any]] = []

    for idx, script in enumerate(ld_scripts, 1):
        block_result = _validate_block(script.string or "", idx)
        blocks.append(block_result)
        all_errors.extend(block_result.get("errors", []))
        all_warnings.extend(block_result.get("warnings", []))

    valid = len(all_errors) == 0

    return {
        "url": url,
        "schemas_found": len(ld_scripts),
        "valid": valid,
        "blocks": blocks,
        "errors": all_errors,
        "warnings": all_warnings,
        "types_found": list({b["type"] for b in blocks if b.get("type")}),
        "summary": (
            f"{len(ld_scripts)} JSON-LD block(s) — "
            f"{len(all_errors)} lỗi, {len(all_warnings)} cảnh báo"
        ),
    }


# ── Block-level validation ─────────────────────────────────────────────────


def _validate_block(raw_json: str, index: int) -> Dict[str, Any]:
    """Validate a single JSON-LD block."""
    errors: List[str] = []
    warnings: List[str] = []

    # Parse JSON
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return {
            "index": index,
            "type": None,
            "valid": False,
            "errors": [f"Block #{index}: JSON không hợp lệ — {exc}"],
            "warnings": [],
            "properties": [],
        }

    # Handle @graph arrays
    if isinstance(data, dict) and "@graph" in data:
        items = data["@graph"]
        if isinstance(items, list):
            # Validate each item in the graph
            sub_results = []
            for i, item in enumerate(items):
                sr = _validate_single_item(item, f"#{index}/@graph[{i}]")
                sub_results.append(sr)
                errors.extend(sr.get("errors", []))
                warnings.extend(sr.get("warnings", []))
            return {
                "index": index,
                "type": "@graph",
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "graph_items": sub_results,
                "properties": list(data.keys()),
            }

    # Single item or list
    items = data if isinstance(data, list) else [data]
    for item in items:
        result = _validate_single_item(item, f"#{index}")
        errors.extend(result.get("errors", []))
        warnings.extend(result.get("warnings", []))

    schema_type = _get_type(items[0]) if items else None

    return {
        "index": index,
        "type": schema_type,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "properties": list(items[0].keys()) if items and isinstance(items[0], dict) else [],
    }


def _validate_single_item(item: Any, label: str) -> Dict[str, Any]:
    """Validate a single schema item."""
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(item, dict):
        errors.append(f"Block {label}: Schema item phải là JSON object.")
        return {"errors": errors, "warnings": warnings}

    # Check @context
    context = item.get("@context", "")
    if not context:
        warnings.append(f"Block {label}: Thiếu @context (nên có 'https://schema.org').")
    elif isinstance(context, str) and "schema.org" not in context.lower():
        warnings.append(f"Block {label}: @context không phải schema.org — '{context}'")

    # Check @type
    schema_type = _get_type(item)
    if not schema_type:
        errors.append(f"Block {label}: Thiếu @type — Google không thể nhận diện schema.")
        return {"type": None, "errors": errors, "warnings": warnings}

    # Check if type is known
    if schema_type not in KNOWN_TYPES:
        warnings.append(
            f"Block {label}: @type '{schema_type}' không phổ biến. "
            "Kiểm tra xem Google có hỗ trợ rich results cho type này không."
        )

    # Validate required/recommended properties
    rules = SCHEMA_RULES.get(schema_type)
    if rules:
        for prop in rules.get("required", []):
            if prop not in item or _is_empty(item[prop]):
                errors.append(
                    f"Block {label} ({schema_type}): Thiếu thuộc tính bắt buộc '{prop}'."
                )

        for prop in rules.get("recommended", []):
            if prop not in item or _is_empty(item[prop]):
                warnings.append(
                    f"Block {label} ({schema_type}): Nên thêm thuộc tính '{prop}' "
                    "để rich results đầy đủ hơn."
                )

    # Specific validations
    if schema_type == "FAQPage":
        _validate_faq(item, label, errors, warnings)
    elif schema_type == "BreadcrumbList":
        _validate_breadcrumb(item, label, errors, warnings)

    return {"type": schema_type, "errors": errors, "warnings": warnings}


# ── Type-specific validators ──────────────────────────────────────────────


def _validate_faq(item: Dict, label: str, errors: List[str], warnings: List[str]):
    """Validate FAQ structured data."""
    main_entity = item.get("mainEntity", [])
    if not isinstance(main_entity, list):
        main_entity = [main_entity]

    if not main_entity:
        errors.append(f"Block {label} (FAQPage): mainEntity rỗng — cần ít nhất 1 câu hỏi.")
        return

    for i, q in enumerate(main_entity):
        if not isinstance(q, dict):
            continue
        q_type = _get_type(q)
        if q_type and q_type != "Question":
            errors.append(f"Block {label}: FAQ item [{i}] có @type '{q_type}' thay vì 'Question'.")
        if "name" not in q and "text" not in q:
            errors.append(f"Block {label}: FAQ item [{i}] thiếu 'name' (câu hỏi).")
        accepted = q.get("acceptedAnswer", {})
        if isinstance(accepted, dict) and not accepted.get("text"):
            warnings.append(f"Block {label}: FAQ item [{i}] acceptedAnswer thiếu 'text'.")


def _validate_breadcrumb(item: Dict, label: str, errors: List[str], warnings: List[str]):
    """Validate BreadcrumbList structured data."""
    elements = item.get("itemListElement", [])
    if not isinstance(elements, list):
        errors.append(f"Block {label} (BreadcrumbList): itemListElement phải là mảng.")
        return

    for i, el in enumerate(elements):
        if not isinstance(el, dict):
            continue
        if "position" not in el:
            warnings.append(f"Block {label}: Breadcrumb [{i}] thiếu 'position'.")
        if "name" not in el and "item" not in el:
            warnings.append(f"Block {label}: Breadcrumb [{i}] thiếu 'name' hoặc 'item'.")


# ── Helpers ────────────────────────────────────────────────────────────────


def _get_type(item: Any) -> Optional[str]:
    """Extract @type from a schema item, handling arrays."""
    if not isinstance(item, dict):
        return None
    t = item.get("@type")
    if isinstance(t, list):
        return t[0] if t else None
    return t


def _is_empty(value: Any) -> bool:
    """Check if a value is effectively empty."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    return False


def _error_result(url: str, message: str) -> Dict[str, Any]:
    """Standardised error response."""
    return {
        "url": url,
        "schemas_found": 0,
        "valid": False,
        "blocks": [],
        "errors": [message],
        "warnings": [],
        "types_found": [],
        "summary": f"Lỗi: {message}",
    }
