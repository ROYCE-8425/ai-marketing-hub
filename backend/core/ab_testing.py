"""
SEO A/B Testing — Phase 19 (SQLAlchemy)

Create and evaluate A/B tests for SEO elements:
- Title tag testing
- Meta description testing
- Content heading testing
- AI-powered evaluation of variants
"""

import os
import json
from datetime import datetime, timezone
from typing import Any, Dict, List
import httpx

from core.database import SessionLocal
from core.models import ManagedSite, AbTest

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _get_site_id(db, site_url: str) -> int:
    site = db.query(ManagedSite).filter(ManagedSite.url == site_url).first()
    if not site:
        raise ValueError(f"Site {site_url} không tồn tại")
    return site.id


def create_test(
    name: str,
    test_type: str,
    variant_a: str,
    variant_b: str,
    site_url: str,
    url: str = "",
    keyword: str = "",
) -> Dict[str, Any]:
    """Create a new A/B test."""
    db = SessionLocal()
    try:
        site_id = _get_site_id(db, site_url)
        new_test = AbTest(
            site_id=site_id,
            name=name.strip(),
            test_type=test_type,
            variant_a=variant_a.strip(),
            variant_b=variant_b.strip(),
            url=url,
            primary_keyword=keyword,
            status="pending"
        )
        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        return {"status": "ok", "id": new_test.id, "name": new_test.name}
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def get_tests(site_url: str, status: str = "") -> List[Dict[str, Any]]:
    """Get all A/B tests."""
    db = SessionLocal()
    try:
        site_id = _get_site_id(db, site_url)
        query = db.query(AbTest).filter(AbTest.site_id == site_id)
        if status:
            query = query.filter(AbTest.status == status)
            
        tests = query.order_by(AbTest.created_at.desc()).all()
        return [{
            "id": t.id,
            "name": t.name,
            "test_type": t.test_type,
            "url": t.url,
            "keyword": t.primary_keyword,
            "variant_a": t.variant_a,
            "variant_b": t.variant_b,
            "winner": t.winner,
            "ai_analysis": t.ai_analysis,
            "score_a": t.score_a,
            "score_b": t.score_b,
            "status": t.status,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "evaluated_at": t.evaluated_at.isoformat() if t.evaluated_at else None
        } for t in tests]
    except ValueError:
        return []
    finally:
        db.close()


def delete_test(test_id: int) -> Dict[str, Any]:
    """Delete an A/B test."""
    db = SessionLocal()
    try:
        test = db.query(AbTest).filter(AbTest.id == test_id).first()
        if test:
            db.delete(test)
            db.commit()
            return {"status": "ok", "deleted": test_id}
        return {"status": "error", "message": "Test not found"}
    finally:
        db.close()


async def evaluate_test(test_id: int) -> Dict[str, Any]:
    """AI-evaluate an A/B test and determine winner."""
    db = SessionLocal()
    try:
        test = db.query(AbTest).filter(AbTest.id == test_id).first()
        if not test:
            return {"error": "Test không tồn tại"}

        # Extract info before closing session or just use it
        test_info = {
            "test_type": test.test_type,
            "url": test.url,
            "keyword": test.primary_keyword,
            "variant_a": test.variant_a,
            "variant_b": test.variant_b
        }
    finally:
        db.close()

    if not GROQ_API_KEY:
        return {"error": "Chưa cấu hình GROQ_API_KEY"}

    type_labels = {
        "title": "Title tag (thẻ tiêu đề SEO)",
        "description": "Meta description",
        "heading": "Heading (H1/H2)",
        "content": "Nội dung bài viết",
    }
    type_label = type_labels.get(test_info["test_type"], test_info["test_type"])

    prompt = f"""Bạn là chuyên gia SEO. So sánh 2 phiên bản {type_label} và chọn bản tốt hơn.

URL: {test_info.get('url', 'N/A')}
Từ khóa mục tiêu: {test_info.get('keyword', 'N/A')}

PHIÊN BẢN A:
{test_info['variant_a']}

PHIÊN BẢN B:
{test_info['variant_b']}

Phân tích theo các tiêu chí:
1. SEO (keyword placement, length, relevance)
2. CTR (hấp dẫn, gây tò tự, power words)
3. User Intent (phù hợp search intent)
4. Độ tự nhiên (không spam, đọc tốt)

Trả về JSON format:
{{
  "winner": "A" hoặc "B",
  "score_a": 0-100,
  "score_b": 0-100,
  "analysis": "Phân tích chi tiết...",
  "criteria": {{
    "seo": {{"a": 0-25, "b": 0-25, "note": "..."}},
    "ctr": {{"a": 0-25, "b": 0-25, "note": "..."}},
    "intent": {{"a": 0-25, "b": 0-25, "note": "..."}},
    "natural": {{"a": 0-25, "b": 0-25, "note": "..."}}
  }}
}}

Chỉ trả về JSON."""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 1024,
                },
            )
            if resp.status_code != 200:
                return {"error": f"AI lỗi: {resp.status_code}"}

            import re
            ai_text = resp.json()["choices"][0]["message"]["content"].strip()
            match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if not match:
                return {"error": "AI không trả về JSON hợp lệ"}

            result = json.loads(match.group())

            # Save results
            db2 = SessionLocal()
            try:
                t = db2.query(AbTest).filter(AbTest.id == test_id).first()
                if t:
                    t.winner = result.get("winner", "")
                    t.score_a = result.get("score_a", 0)
                    t.score_b = result.get("score_b", 0)
                    t.ai_analysis = json.dumps(result, ensure_ascii=False)
                    t.status = 'evaluated'
                    t.evaluated_at = datetime.now(timezone.utc)
                    db2.commit()
            finally:
                db2.close()

            return {
                "status": "ok",
                "test_id": test_id,
                "winner": result.get("winner"),
                "score_a": result.get("score_a"),
                "score_b": result.get("score_b"),
                "analysis": result.get("analysis"),
                "criteria": result.get("criteria", {}),
            }

    except Exception as e:
        return {"error": str(e)}
