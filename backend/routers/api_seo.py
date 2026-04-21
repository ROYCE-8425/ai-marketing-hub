"""
SEO Audit API Router

Provides:
- POST /api/audit-seo   — analyze raw article text (Phase 1)
- POST /api/audit-url   — scrape URL → SEO + CRO + Trust analysis (Phase 2/3)
"""

import asyncio
import re
from typing import Any, Dict

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException

from core.schemas import AuditSeoRequest, AuditUrlRequest
from core.seo_quality_rater import SEOQualityRater
from core.keyword_analyzer import KeywordAnalyzer
from core.cro_checker import CROChecker
from core.cta_analyzer import CTAAnalyzer
from core.trust_signal_analyzer import TrustSignalAnalyzer
from core.above_fold_analyzer import AboveFoldAnalyzer

router = APIRouter(prefix="/api", tags=["seo"])


# ─── Sync analysis engine (runs in threadpool) ──────────────────────────────────

def _run_seo_analysis(
    content: str,
    meta_title: str,
    primary_keyword: str,
) -> Dict[str, Any]:
    """Phase 1 sync engine — keyword + SEO quality (CPU-bound, no I/O)."""
    analyzer = KeywordAnalyzer()
    keyword_result = analyzer.analyze(
        content=content,
        primary_keyword=primary_keyword,
        target_density=1.5,
    )

    rater = SEOQualityRater()
    quality_result = rater.rate(
        content=content,
        meta_title=meta_title,
        primary_keyword=primary_keyword,
        keyword_density=keyword_result["primary_keyword"]["density"],
    )

    return {
        "primary_keyword": primary_keyword,
        "keyword_analysis": {
            "word_count": keyword_result["word_count"],
            "primary_keyword": keyword_result["primary_keyword"],
            "keyword_stuffing": keyword_result["keyword_stuffing"],
            "distribution_heatmap": keyword_result["distribution_heatmap"],
            "lsi_keywords": keyword_result["lsi_keywords"],
            "recommendations": keyword_result["recommendations"],
        },
        "seo_quality": {
            "overall_score": quality_result["overall_score"],
            "grade": quality_result["grade"],
            "publishing_ready": quality_result["publishing_ready"],
            "category_scores": quality_result["category_scores"],
            "critical_issues": quality_result["critical_issues"],
            "warnings": quality_result["warnings"],
            "suggestions": quality_result["suggestions"],
            "details": quality_result["details"],
        },
    }


def _run_cro_analysis(content: str) -> Dict[str, Any]:
    """
    Phase 3 sync engine — CRO + Trust + Above-the-Fold analysis.

    All four analyzers are pure-CPU with no I/O, so running them
    sequentially in a thread is safe and doesn't block the async loop.
    """
    # 1. CRO checklist (8 categories)
    cro = CROChecker(page_type="seo", conversion_goal="trial")
    cro_result = cro.check(content)

    # 2. CTA effectiveness
    cta = CTAAnalyzer(conversion_goal="trial")
    cta_result = cta.analyze(content)

    # 3. Trust signals
    trust = TrustSignalAnalyzer()
    trust_result = trust.analyze(content)

    # 4. Above-the-fold first impression
    above_fold = AboveFoldAnalyzer()
    above_fold_result = above_fold.analyze(content)

    # Weighted CRO score (CRO checklist 60% + CTA 20% + above-fold 20%)
    cro_score = cro_result["score"]
    cta_score = cta_result["summary"]["overall_effectiveness"]
    atf_score = above_fold_result["overall_score"]
    trust_score = trust_result["overall_score"]

    combined_cro = round(cro_score * 0.6 + cta_score * 0.2 + atf_score * 0.2, 1)

    return {
        "overall_cro_score": combined_cro,
        "cro_grade": _cro_grade(combined_cro),
        "cro_checklist": {
            "score": cro_result["score"],
            "grade": cro_result["grade"],
            "passes_audit": cro_result["passes_audit"],
            "summary": cro_result["summary"],
            "critical_failures": cro_result["critical_failures"],
            "warnings": cro_result["warnings"],
            "category_scores": {k: v["score"] for k, v in cro_result["categories"].items()},
            "recommendations": cro_result["recommendations"],
        },
        "cta_analysis": {
            "total_ctas": cta_result["summary"]["total_ctas"],
            "avg_quality_score": cta_result["summary"]["average_quality_score"],
            "distribution_score": cta_result["summary"]["distribution_score"],
            "goal_alignment_score": cta_result["summary"]["goal_alignment_score"],
            "overall_effectiveness": cta_score,
            "ctas_found": [
                {
                    "text": c["text"],
                    "position_pct": c["position_pct"],
                    "quality_score": c["quality_score"],
                }
                for c in cta_result["ctas"][:8]
            ],
            "distribution": {
                "first_cta_position": cta_result["distribution"]["first_cta_position"],
                "has_above_fold": cta_result["distribution"]["has_above_fold"],
                "has_closing": cta_result["distribution"]["has_closing"],
                "distribution_quality": cta_result["distribution"]["distribution_quality"],
            },
            "recommendations": cta_result["recommendations"],
        },
        "above_fold_analysis": {
            "overall_score": atf_score,
            "grade": above_fold_result["grade"],
            "passes_5_second_test": above_fold_result["passes_5_second_test"],
            "element_scores": above_fold_result["element_scores"],
            "headline_quality": above_fold_result["headline"]["quality"],
            "headline_text": above_fold_result["headline"].get("text"),
            "cta_above_fold": above_fold_result["cta"]["present"],
            "cta_text": above_fold_result["cta"].get("first_cta"),
            "trust_signal_above_fold": above_fold_result["trust_signal"]["present"],
            "issues": above_fold_result["issues"],
            "recommendations": above_fold_result["recommendations"],
        },
        "trust_signals": {
            "overall_score": trust_score,
            "grade": trust_result["grade"],
            "summary": trust_result["summary"],
            "strengths": trust_result["strengths"],
            "weaknesses": trust_result["weaknesses"],
            "testimonials": [
                {"quote": t["quote"], "attribution": t["attribution"]}
                for t in trust_result["details"]["testimonials"]["testimonials"][:5]
            ],
            "social_proof": {
                "customer_counts": [
                    {"value": c["value"]} for c in
                    trust_result["details"]["social_proof"]["customer_counts"]
                ],
                "specific_results": [
                    {"value": r["value"]} for r in
                    trust_result["details"]["social_proof"]["specific_results"]
                ],
            },
            "risk_reversals": {
                "free_trial_found": trust_result["details"]["risk_reversals"]["free_trial"]["found"],
                "no_credit_card_found": trust_result["details"]["risk_reversals"]["no_card"]["found"],
                "cancel_anytime_found": trust_result["details"]["risk_reversals"]["cancel_anytime"]["found"],
                "guarantee_found": trust_result["details"]["risk_reversals"]["guarantee"]["found"],
            },
            "authority_signals": {
                "media_mentions": trust_result["details"]["authority"].get("media_mentions", {}).get("found", False),
                "awards": trust_result["details"]["authority"].get("awards", {}).get("found", False),
                "years_in_business": trust_result["details"]["authority"].get("experience", {}).get("found", False),
            },
            "recommendations": trust_result["recommendations"],
        },
        "sales_risk_alerts": _build_sales_risk_alerts(cro_result, cta_result, trust_result, above_fold_result),
    }


def _build_sales_risk_alerts(
    cro: Dict, cta: Dict, trust: Dict, atf: Dict
) -> list:
    """Derive human-readable sales risk alerts from analysis results."""
    alerts = []
    severity = "medium"

    # CRO risk
    if not cro["passes_audit"] or cro["score"] < 60:
        alerts.append({"severity": "high", "message": "Low CRO score — page unlikely to convert visitors."})
    if cro["summary"]["critical_failures"] > 0:
        alerts.append({"severity": "high", "message": f"{cro['summary']['critical_failures']} critical CRO failure(s) detected."})

    # CTA risk
    if cta["summary"]["total_ctas"] == 0:
        alerts.append({"severity": "high", "message": "No CTAs found — visitors have no clear action to take."})
    elif not cta["distribution"]["has_above_fold"]:
        alerts.append({"severity": "medium", "message": "No CTA above the fold — first impression has no conversion path."})
    if cta["summary"]["goal_alignment_score"] < 50:
        alerts.append({"severity": "medium", "message": "CTAs not aligned with conversion goal."})

    # Trust risk
    if not trust["details"]["testimonials"]["count"] > 0:
        if not trust["details"]["social_proof"]["has_any"]:
            alerts.append({"severity": "high", "message": "No social proof — low trust signals for new visitors."})
    if not trust["details"]["risk_reversals"]["has_any"]:
        alerts.append({"severity": "medium", "message": "No risk reversal (guarantee/trial/no-card) — visitors may hesitate to convert."})

    # Above-fold risk
    if not atf["passes_5_second_test"]:
        alerts.append({"severity": "high", "message": "Page fails the 5-second test — visitors likely leave immediately."})
    if not atf["cta"]["present"]:
        alerts.append({"severity": "high", "message": "No CTA visible above the fold."})

    return alerts


def _cro_grade(score: float) -> str:
    if score >= 90: return "A (Excellent)"
    if score >= 80: return "B (Good)"
    if score >= 70: return "C (Acceptable)"
    if score >= 60: return "D (Needs Work)"
    return "F (Poor)"


# ─── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/audit-url")
async def audit_url(body: AuditUrlRequest):
    """
    Phase 3 — Full marketing audit from a live URL.

    1. Fetches HTML via httpx (async I/O, non-blocking).
    2. Extracts <title> and visible text via BeautifulSoup.
    3. Offloads CPU-heavy SEO + CRO analysis to a thread pool
       (asyncio.to_thread) so the async event loop is never blocked.
    4. Returns combined JSON: seo_quality + keyword_analysis + cro_analysis.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; AI-Marketing-Hub/3.0; "
                "+https://example.com/bot)"
            )
        }
        async with httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(15.0, connect=10.0),
            follow_redirects=True,
        ) as client:
            response = await client.get(str(body.url))
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Extract <title>
        meta_title = (
            soup.title.string.strip() if soup.title and soup.title.string else ""
        )

        # Strip noise tags
        for tag in soup(["nav", "script", "style", "footer", "header", "noscript"]):
            tag.decompose()

        # Collect visible text
        content = soup.get_text(separator="\n", strip=True)
        content = re.sub(r"\n{3,}", "\n\n", content)

        if not content.strip():
            raise HTTPException(
                status_code=422,
                detail="No readable content found on the page.",
            )

        # ── Phase 1: SEO analysis in threadpool ────────────────────────────
        seo_result = await asyncio.to_thread(
            _run_seo_analysis,
            content,
            meta_title,
            body.primary_keyword,
        )

        # ── Phase 3: CRO + Trust analysis in threadpool ─────────────────────
        cro_result = await asyncio.to_thread(_run_cro_analysis, content)

        # Merge
        return {**seo_result, "cro_analysis": cro_result}

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to target URL timed out.") from None
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream returned {exc.response.status_code} for {body.url}",
        ) from exc
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to reach target URL.") from None


@router.post("/audit-seo")
def audit_seo(body: AuditSeoRequest):
    """
    Phase 1 — SEO audit from raw article text.
    Returns same JSON shape as /api/audit-url (without cro_analysis).
    """
    try:
        return _run_seo_analysis(
            body.content,
            body.meta_title,
            body.primary_keyword,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
