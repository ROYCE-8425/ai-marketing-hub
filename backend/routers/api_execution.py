"""
API Execution Router — Phase 5

Provides:
- POST /api/publish          — Publish article content to WordPress
- POST /api/opportunities    — Score a URL/keyword for SEO opportunity
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from core.search_intent_analyzer import SearchIntentAnalyzer
from core.opportunity_scorer import OpportunityScorer, OpportunityType
from core.landing_page_scorer import LandingPageScorer
from core.wordpress_publisher import WordPressPublisher

router = APIRouter(prefix="/api", tags=["execution"])


# ─────────────────────────────────────────────────────────────────────────────
# Publish Request / Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class PublishRequest(BaseModel):
    wordpress_url: str = Field(
        ...,
        description="WordPress site URL, e.g. https://yoursite.com",
    )
    username: str = Field(..., description="WordPress username")
    app_password: str = Field(..., description="WordPress application password")
    article_title: str = Field(..., min_length=1, description="Article title")
    article_content: str = Field(..., min_length=10, description="Article body (HTML or Markdown)")
    slug: Optional[str] = Field(None, description="URL slug (auto-generated if omitted)")
    excerpt: Optional[str] = Field(None, description="Post excerpt")
    category: Optional[str] = Field(None, description="Category name (created if missing)")
    tags: Optional[str] = Field(None, description="Comma-separated tag names")
    post_status: Optional[str] = Field(
        "draft",
        description="Post status: 'draft' or 'publish'"
    )


class PublishMeta(BaseModel):
    title: str
    description: str
    focus_keyword: str


class PublishResponse(BaseModel):
    success: bool
    post_id: int
    edit_url: str
    view_url: str
    title: str
    slug: str
    word_count: int
    categories: List[str]
    tags: List[str]
    post_status: str
    meta: PublishMeta
    message: str


# ─────────────────────────────────────────────────────────────────────────────
# Opportunities Request / Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class IntentConfidence(BaseModel):
    informational: float
    navigational: float
    transactional: float
    commercial_investigation: float


class IntentAnalysisResult(BaseModel):
    keyword: str
    primary_intent: str
    secondary_intent: Optional[str]
    confidence: IntentConfidence
    signals_detected: Dict[str, List[str]]
    recommendations: List[str]


class CategoryScores(BaseModel):
    above_fold: float
    ctas: float
    trust_signals: float
    structure: float
    seo: float


class LandingPageResult(BaseModel):
    overall_score: float
    grade: str
    page_type: str
    conversion_goal: str
    category_scores: CategoryScores
    critical_issues: List[str]
    warnings: List[str]
    suggestions: List[str]
    publishing_ready: bool
    word_count: int
    cta_count: int


class ScoreBreakdown(BaseModel):
    volume_score: float
    position_score: float
    intent_score: float
    competition_score: float
    cluster_score: float
    ctr_score: float
    freshness_score: float
    trend_score: float


class OpportunityScoreResult(BaseModel):
    final_score: float
    score_breakdown: ScoreBreakdown
    priority: str
    primary_factor: str
    score_explanation: str


class TrafficProjection(BaseModel):
    current_clicks: int
    current_position: float
    target_position: int
    target_expected_ctr: float
    potential_clicks: int
    additional_clicks: int
    percent_increase: float


class OpportunitiesResponse(BaseModel):
    keyword: str
    url: str
    low_hanging_fruit: bool
    effort_level: str  # "low", "medium", "high"
    verdict: str  # Human-readable one-liner

    intent_analysis: IntentAnalysisResult
    landing_page: LandingPageResult
    opportunity_score: OpportunityScoreResult
    traffic_projection: Optional[TrafficProjection]

    insight_adjustments: List[str]  # Search-intent-driven recommendations
    action_items: List[str]        # Concrete next steps


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _scrape_page(url: str, _keyword: str) -> tuple[str, str, str]:
    """Fetch URL, return (url, title, content)."""
    headers = {"User-Agent": "AI-Marketing-Hub/5.0 (+https://example.com/bot)"}
    try:
        resp = httpx.get(url, headers=headers, timeout=15.0, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream returned {exc.response.status_code} for {url}",
        ) from None
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to reach {url}: {exc}") from None

    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    for tag in soup(["nav", "script", "style", "header", "footer", "noscript"]):
        tag.decompose()

    content = soup.get_text(separator="\n", strip=True)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return url, title, content


def _build_intent_result(raw: Dict[str, Any]) -> IntentAnalysisResult:
    conf = raw["confidence"]
    return IntentAnalysisResult(
        keyword=raw["keyword"],
        primary_intent=raw["primary_intent"],
        secondary_intent=raw.get("secondary_intent"),
        confidence=IntentConfidence(
            informational=round(conf.get("informational", 0), 1),
            navigational=round(conf.get("navigational", 0), 1),
            transactional=round(conf.get("transactional", 0), 1),
            commercial_investigation=round(conf.get("commercial_investigation", 0), 1),
        ),
        signals_detected=raw.get("signals_detected", {}),
        recommendations=raw.get("recommendations", []),
    )


def _build_landing_page_result(raw: Dict[str, Any]) -> LandingPageResult:
    cats = raw.get("category_scores", {})
    detail = raw.get("details", {})
    return LandingPageResult(
        overall_score=raw.get("overall_score", 0),
        grade=raw.get("grade", "N/A"),
        page_type=raw.get("page_type", "seo"),
        conversion_goal=raw.get("conversion_goal", "trial"),
        category_scores=CategoryScores(
            above_fold=round(cats.get("above_fold", 0), 1),
            ctas=round(cats.get("ctas", 0), 1),
            trust_signals=round(cats.get("trust_signals", 0), 1),
            structure=round(cats.get("structure", 0), 1),
            seo=cats.get("seo") if isinstance(cats.get("seo"), (int, float)) else 0,
        ),
        critical_issues=raw.get("critical_issues", []),
        warnings=raw.get("warnings", []),
        suggestions=raw.get("suggestions", []),
        publishing_ready=raw.get("publishing_ready", False),
        word_count=detail.get("word_count", 0),
        cta_count=detail.get("cta_count", 0),
    )


def _build_opp_score_result(raw: Dict[str, Any]) -> OpportunityScoreResult:
    bd = raw.get("score_breakdown", {})
    return OpportunityScoreResult(
        final_score=raw.get("final_score", 0),
        score_breakdown=ScoreBreakdown(
            volume_score=round(bd.get("volume_score", 0), 1),
            position_score=round(bd.get("position_score", 0), 1),
            intent_score=round(bd.get("intent_score", 0), 1),
            competition_score=round(bd.get("competition_score", 0), 1),
            cluster_score=round(bd.get("cluster_score", 0), 1),
            ctr_score=round(bd.get("ctr_score", 0), 1),
            freshness_score=round(bd.get("freshness_score", 0), 1),
            trend_score=round(bd.get("trend_score", 0), 1),
        ),
        priority=raw.get("priority", "LOW"),
        primary_factor=raw.get("primary_factor", "volume_score"),
        score_explanation=raw.get("score_explanation", ""),
    )


def _classify_effort(landing_score: float, opp_score: float, intent: str) -> tuple[bool, str, str]:
    """
    Determine if this is a LOW-HANGING-FRUIT opportunity and effort level.

    Low-hanging fruit = high opportunity score + low-to-medium landing page effort.
    Effort is "how hard is it to win this keyword?".
    """
    # Effort: lower landing page score = more work needed
    if landing_score >= 75:
        effort = "low"
    elif landing_score >= 50:
        effort = "medium"
    else:
        effort = "high"

    # Low-hanging fruit thresholds
    if opp_score >= 70 and effort in ("low", "medium"):
        verdict = (
            "LOW-HANGING FRUIT — High opportunity with manageable effort. "
            "Optimize the page and you can rank quickly."
        )
        return True, effort, verdict
    elif opp_score >= 50 and effort == "low":
        verdict = (
            "QUICK WIN — Good opportunity and your page is already strong. "
            "Minor optimizations should push you to page 1."
        )
        return True, effort, verdict
    elif opp_score >= 55 and intent in ("informational", "commercial_investigation"):
        verdict = (
            "MEDIUM EFFORT — Solid opportunity. Improve content depth and "
            "on-page SEO to compete."
        )
        return False, effort, verdict
    else:
        effort_adj = "high-difficulty" if effort == "high" else "competitive niche"
        verdict = (
            f"HIGH EFFORT — {effort_adj}. This keyword requires significant "
            "investment in content quality, backlinks, and technical SEO."
        )
        return False, effort, verdict


def _intent_adjustments(intent_result: IntentAnalysisResult) -> List[str]:
    """Derive actionable insight adjustments from search intent analysis."""
    adjustments = []
    primary = intent_result.primary_intent

    if primary == "informational":
        adjustments.extend([
            "Add an FAQ section targeting 'People Also Ask' features",
            "Include a concise summary/definition box near the top",
            "Structure content to answer the query in the first 100 words",
            "Use descriptive H2s that mirror common question patterns",
        ])
    elif primary == "commercial_investigation":
        adjustments.extend([
            "Add a comparison table or pros/cons section",
            "Include social proof (customer logos, usage stats)",
            "Add a 'Best For' section targeting different user personas",
            "Ensure pricing or free-trial CTA is above the fold",
        ])
    elif primary == "transactional":
        adjustments.extend([
            "Move purchase/demo CTA above the fold",
            "Add trust signals near CTAs (guarantee, no-credit-card)",
            "Remove navigation clutter that distracts from conversion",
            "Ensure pricing is visible without scrolling",
        ])
    elif primary == "navigational":
        adjustments.extend([
            "This keyword is brand-intent — ensure your brand page ranks first",
            "Claim/reclaim brand SERP real estate with a strong homepage or landing page",
        ])

    # Signal-based nudges
    signals = intent_result.signals_detected
    if signals.get("informational"):
        adjustments.append(f"Detected informational signals: {signals['informational'][0]}")
    if signals.get("commercial_investigation"):
        adjustments.append(f"Detected comparison intent: {signals['commercial_investigation'][0]}")

    return adjustments


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/publish", response_model=PublishResponse)
async def publish_article(body: PublishRequest):
    """
    Publish an article draft directly to WordPress.

    Authenticates via WordPress Application Password.
    Converts Markdown → HTML, creates a post/page, and sets Yoast SEO fields.
    """
    try:
        publisher = WordPressPublisher(
            url=body.wordpress_url,
            username=body.username,
            app_password=body.app_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None

    try:
        # Convert Markdown to HTML
        html_content = publisher.markdown_to_html(body.article_content)
        word_count = len(body.article_content.split())

        # Generate slug if not provided
        slug = body.slug
        if not slug:
            slug = re.sub(r"[^\w\s-]", "", body.article_title.lower())
            slug = re.sub(r"[\s_]+", "-", slug)

        # Process categories
        category_ids: Optional[List[int]] = None
        category_list: List[str] = []
        if body.category:
            cat_id = publisher.get_or_create_category(body.category.strip())
            category_ids = [cat_id]
            category_list = [body.category.strip()]

        # Process tags
        tag_ids: Optional[List[int]] = None
        tag_list: List[str] = []
        if body.tags:
            tag_list = [t.strip() for t in body.tags.split(",") if t.strip()]
            tag_ids = [publisher.get_or_create_tag(t) for t in tag_list]

        # Create the draft post
        post = publisher.create_draft(
            title=body.article_title,
            content=html_content,
            slug=slug,
            excerpt=body.excerpt or "",
            category_ids=category_ids,
            tag_ids=tag_ids,
            post_type="posts",
        )

        post_id = post["id"]
        status = body.post_status or "draft"

        # Update status if publish requested
        if status == "publish":
            # Patch the post status
            import requests
            resp = requests.post(
                f"{publisher.api_base}/posts/{post_id}",
                json={"status": "publish"},
                auth=(body.username, body.app_password),
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            post = resp.json()

        # Try to set Yoast meta (non-fatal if plugin missing)
        meta_title = f"{body.article_title} | {publisher.url}"
        meta_desc = body.excerpt or ""
        try:
            publisher.set_yoast_meta(
                post_id=post_id,
                meta_title=meta_title,
                meta_description=meta_desc,
                focus_keyphrase="",
            )
        except Exception:
            pass  # Non-critical if MU plugin not installed

        edit_url = f"{body.wordpress_url.rstrip('/')}/wp-admin/post.php?post={post_id}&action=edit"
        view_url = post.get("link", "")

        return PublishResponse(
            success=True,
            post_id=post_id,
            edit_url=edit_url,
            view_url=view_url,
            title=body.article_title,
            slug=slug,
            word_count=word_count,
            categories=category_list,
            tags=tag_list,
            post_status=status,
            meta=PublishMeta(
                title=meta_title,
                description=meta_desc,
                focus_keyphrase="",
            ),
            message=f"Article {'published' if status == 'publish' else 'saved as draft'} successfully.",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"WordPress publish failed — check your site URL, credentials, and that the site is reachable. Details: {exc}",
        ) from exc


@router.post("/opportunities", response_model=OpportunitiesResponse)
async def score_opportunities(
    url: str = Query(..., description="URL of the page to analyze"),
    keyword: str = Query(..., description="Target keyword for the opportunity"),
    search_intent: Optional[str] = Query(
        None,
        description="Override search intent: informational, navigational, transactional, commercial"
    ),
    current_position: Optional[float] = Query(
        None,
        description="Current SERP position (from GSC)"
    ),
    monthly_impressions: Optional[int] = Query(
        None,
        description="Monthly impressions (from GSC)"
    ),
    monthly_clicks: Optional[int] = Query(
        None,
        description="Monthly clicks (from GSC)"
    ),
    search_volume: Optional[int] = Query(
        None,
        description="Monthly search volume (from DataForSEO)"
    ),
    difficulty: Optional[int] = Query(
        None,
        description="SEO difficulty 0-100 (from DataForSEO)"
    ),
    serp_features: Optional[str] = Query(
        None,
        description="Comma-separated SERP feature list"
    ),
):
    """
    Score a keyword/page opportunity.

    1. Scrape the page to get title + content.
    2. Run SearchIntentAnalyzer to validate/override search intent.
    3. Run LandingPageScorer to evaluate on-page quality.
    4. Run OpportunityScorer to compute the 8-factor score.
    5. Classify as LOW-HANGING FRUIT or HIGH EFFORT.
    6. Return intent-driven insight adjustments.
    """
    # ── Scrape page ───────────────────────────────────────────────────────────
    page_url, page_title, page_content = await asyncio.to_thread(
        _scrape_page, url, keyword
    )

    if len(page_content.strip()) < 100:
        raise HTTPException(
            status_code=422,
            detail="Page content too thin to analyze.",
        )

    # ── Intent analysis ───────────────────────────────────────────────────────
    serp_list: Optional[List[str]] = None
    if serp_features:
        serp_list = [s.strip() for s in serp_features.split(",") if s.strip()]

    intent_analyzer = SearchIntentAnalyzer()
    # Use override if provided, otherwise auto-detect
    if search_intent:
        raw_intent = intent_analyzer.analyze(keyword, serp_list)
        # Override primary intent
        raw_intent["primary_intent"] = search_intent
        raw_intent["confidence"] = {
            k: (100.0 if k == search_intent else 0.0)
            for k in ("informational", "navigational", "transactional", "commercial_investigation")
        }
    else:
        raw_intent = intent_analyzer.analyze(keyword, serp_list)

    intent_result = _build_intent_result(raw_intent)

    # ── Landing page scoring ───────────────────────────────────────────────────
    lp_scorer = LandingPageScorer(page_type="seo", conversion_goal="trial")
    raw_lp = await asyncio.to_thread(
        lp_scorer.score,
        page_content,
        page_title,
        "",  # meta_description not extracted here
        keyword,
    )
    lp_result = _build_landing_page_result(raw_lp)

    # ── Opportunity scoring ───────────────────────────────────────────────────
    opp_scorer = OpportunityScorer()

    keyword_data: Dict[str, Any] = {
        "keyword": keyword,
        "position": current_position or 50.0,
        "impressions": monthly_impressions or 0,
        "clicks": monthly_clicks or 0,
        "ctr": (
            (monthly_clicks or 0) / monthly_impressions
            if monthly_impressions and monthly_impressions > 0
            else 0.0
        ),
        "commercial_intent": 1.5,  # default mid-level
    }

    # Elevate commercial intent for transactional/commercial keywords
    if intent_result.primary_intent in ("transactional", "commercial_investigation"):
        keyword_data["commercial_intent"] = 2.5

    # Determine opportunity type from position
    pos = current_position or 50.0
    if pos <= 20:
        opp_type = OpportunityType.QUICK_WIN
    elif pos <= 10:
        opp_type = OpportunityType.IMPROVEMENT
    elif pos <= 50:
        opp_type = OpportunityType.MEDIUM_TERM
    else:
        opp_type = OpportunityType.NEW_CONTENT

    raw_opp = opp_scorer.calculate_score(
        keyword_data=keyword_data,
        opportunity_type=opp_type,
        search_volume=search_volume,
        difficulty=difficulty,
        serp_features=serp_list,
        cluster_value=65,  # default
        trend_direction="stable",
        trend_percent=0,
    )
    opp_result = _build_opp_score_result(raw_opp)

    # ── Classification ────────────────────────────────────────────────────────
    is_low_hf, effort, verdict = _classify_effort(
        lp_result.overall_score,
        opp_result.final_score,
        intent_result.primary_intent,
    )

    # ── Traffic projection ────────────────────────────────────────────────────
    traffic_proj = None
    if current_position and monthly_impressions:
        traffic = opp_scorer.calculate_potential_traffic(
            current_position=current_position,
            target_position=7,
            impressions=monthly_impressions,
            current_clicks=monthly_clicks or 0,
        )
        traffic_proj = TrafficProjection(
            current_clicks=traffic["current_clicks"],
            current_position=traffic["current_position"],
            target_position=traffic["target_position"],
            target_expected_ctr=traffic["target_expected_ctr"],
            potential_clicks=traffic["potential_clicks"],
            additional_clicks=traffic["additional_clicks"],
            percent_increase=traffic["percent_increase"],
        )

    # ── Insight adjustments ──────────────────────────────────────────────────
    adjustments = _intent_adjustments(intent_result)

    # Add landing page specific advice
    if not lp_result.publishing_ready:
        adjustments.append(
            f"Landing page needs work ({lp_result.overall_score}/100). "
            f"Address {len(lp_result.critical_issues)} critical issue(s) before publishing."
        )
    if lp_result.category_scores.above_fold < 60:
        adjustments.append("Above-the-fold section is weak — improve headline and first CTA placement.")

    # Action items
    action_items: List[str] = []
    if is_low_hf:
        action_items.extend([
            "Optimize meta title and description for the target keyword",
            "Add or reinforce the primary CTA above the fold",
            "Ensure the URL slug contains the target keyword",
            "Submit updated sitemap to Google Search Console",
        ])
    else:
        action_items.extend([
            "Audit top-ranking competitors for content gaps to fill",
            "Build 3-5 contextual backlinks from related pages",
            "Expand content depth to match or exceed competitor average",
            "Track ranking progress weekly via GSC",
        ])

    return OpportunitiesResponse(
        keyword=keyword,
        url=page_url,
        low_hanging_fruit=is_low_hf,
        effort_level=effort,
        verdict=verdict,
        intent_analysis=intent_result,
        landing_page=lp_result,
        opportunity_score=opp_result,
        traffic_projection=traffic_proj,
        insight_adjustments=adjustments,
        action_items=action_items,
    )
