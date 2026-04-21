"""
API Content Router — Phase 4
Endpoints for competitor gap analysis and AI-powered article planning.
"""

from __future__ import annotations

import asyncio
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.competitor_gap_analyzer import (
    CompetitorAnalysis,
    CompetitorGapAnalyzer,
    GapBlueprint,
)
from core.article_planner import (
    ArticlePlan,
    ArticlePlanner,
    SectionPlan,
    create_default_structure,
    format_article_plan,
)

router = APIRouter(prefix="/api", tags=["content"])


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class CompetitorGapRequest(BaseModel):
    my_url: str = Field(..., description="Your page URL (optional — analyzed as baseline)")
    competitor_urls: List[str] = Field(
        ...,
        min_length=1,
        description="List of competitor page URLs to analyze"
    )
    primary_keyword: Optional[str] = Field(
        None,
        description="Primary keyword for context"
    )


class GapItem(BaseModel):
    type: str
    description: str
    location: str
    url: str
    priority: str
    opportunity: str


class CompetitorResult(BaseModel):
    url: str
    title: str
    word_count: int
    structure: List[str]
    strengths: List[str]
    gaps: List[GapItem]
    outdated_items: List[str]


class BlueprintResult(BaseModel):
    must_fill_gaps: List[GapItem]
    differentiation_opportunities: List[str]
    data_needed: List[str]
    outdated_to_update: List[str]
    structure_to_match: List[str]


class CompetitorGapResponse(BaseModel):
    competitors_analyzed: int
    total_gaps_found: int
    my_url: str
    primary_keyword: Optional[str]
    competitors: List[CompetitorResult]
    blueprint: BlueprintResult
    scraping_errors: List[str] = []


class PlanContentRequest(BaseModel):
    primary_keyword: str = Field(..., description="Primary keyword to target")
    target_audience: str = Field(..., description="Target audience description")
    competitor_gaps: Optional[List[str]] = Field(
        None,
        description="Optional gap descriptions to address in plan"
    )
    competitor_structure: Optional[List[str]] = Field(
        None,
        description="Optional competitor H2 structure to incorporate"
    )


class MetaResult(BaseModel):
    title_options: List[str]
    meta_title: str
    meta_description: str
    url_slug: str
    primary_keyword: str
    secondary_keywords: List[str]


class SectionResult(BaseModel):
    section_number: int
    type: str
    heading: str
    word_target: int
    strategic_angle: str
    engagement_hook: Optional[str]
    knowledge_gaps: List[str]
    unique_data: List[str]
    internal_links: List[str]
    cta: Optional[str]
    mini_story: bool
    featured_snippet: bool


class EngagementMapResult(BaseModel):
    mini_stories: List[int]
    ctas: dict
    featured_snippets: List[int]


class PlanContentResponse(BaseModel):
    topic: str
    date: str
    meta: MetaResult
    total_word_target: int
    sections: List[SectionResult]
    engagement_map: EngagementMapResult
    gap_mapping: dict
    insight_mapping: dict
    markdown_outline: str  # Rendered tree/timeline version


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def fetch_page(url: str, client: httpx.AsyncClient) -> tuple[str, str, str]:
    """
    Fetch a URL and extract title + full text content.
    Returns (url, title, content).
    """
    try:
        resp = await client.get(url, timeout=15.0, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"HTTP {e.response.status_code} for {url}")
    except Exception as e:
        raise RuntimeError(str(e))

    soup = BeautifulSoup(resp.text, "lxml")

    # Extract title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Remove script, style, nav, header, footer
    for tag in soup.find_all(["script", "style", "nav", "header", "footer",
                               "noscript", "iframe", "svg"]):
        tag.decompose()

    # Extract visible text
    text = soup.get_text(separator=" ", strip=True)
    # Collapse whitespace
    import re
    text = re.sub(r"\s+", " ", text).strip()

    return url, title, text


def _analysis_to_result(a: CompetitorAnalysis) -> CompetitorResult:
    return CompetitorResult(
        url=a.url,
        title=a.title,
        word_count=a.word_count,
        structure=a.structure,
        strengths=a.strengths,
        gaps=[GapItem(**g.to_dict()) for g in a.gaps],
        outdated_items=a.outdated_items
    )


def _blueprint_to_result(b: GapBlueprint) -> BlueprintResult:
    return BlueprintResult(
        must_fill_gaps=[GapItem(**g.to_dict()) for g in b.must_fill_gaps],
        differentiation_opportunities=b.differentiation_opportunities,
        data_needed=b.data_needed,
        outdated_to_update=b.outdated_to_update,
        structure_to_match=b.structure_to_match
    )


def _plan_to_response(plan: ArticlePlan, keyword: str, audience: str) -> PlanContentResponse:
    return PlanContentResponse(
        topic=plan.topic,
        date=plan.date,
        meta=MetaResult(**plan.meta.to_dict()),
        total_word_target=plan.total_word_target,
        sections=[SectionResult(**s.to_dict()) for s in plan.sections],
        engagement_map=EngagementMapResult(**plan.engagement_map.to_dict()),
        gap_mapping=plan.gap_to_section_mapping,
        insight_mapping=plan.insight_to_section_mapping,
        markdown_outline=format_article_plan(plan)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/competitor-gap", response_model=CompetitorGapResponse)
async def competitor_gap_analysis(req: CompetitorGapRequest):
    """
    Analyze competitor content to identify gaps and build a beat-them blueprint.

    All competitor URLs are fetched in parallel using asyncio.gather.
    """
    all_urls = [req.my_url] + req.competitor_urls

    async with httpx.AsyncClient(headers={"User-Agent": "AI-Marketing-Hub/1.0"}) as client:
        tasks = [fetch_page(url, client) for url in all_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    scraping_errors: List[str] = []
    analyses: List[CompetitorAnalysis] = []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            scraping_errors.append(f"{all_urls[i]}: {result}")
        else:
            url, title, content = result
            if content and len(content) > 100:
                analyzer = CompetitorGapAnalyzer()
                analysis = analyzer.analyze_content(content, url, title)
                analyses.append(analysis)
            else:
                scraping_errors.append(f"{url}: content too thin to analyze")

    if not analyses:
        raise HTTPException(
            status_code=422,
            detail="No competitor content could be fetched. Check URLs and try again."
        )

    # Build blueprint from all analyses
    gap_analyzer = CompetitorGapAnalyzer()
    blueprint = gap_analyzer.create_blueprint(analyses)

    # Separate my_url analysis from competitors
    my_analysis = next(
        (a for a in analyses if a.url == req.my_url), None
    )
    competitor_analyses = [a for a in analyses if a.url != req.my_url]

    total_gaps = sum(len(a.gaps) for a in analyses)

    return CompetitorGapResponse(
        competitors_analyzed=len(analyses),
        total_gaps_found=total_gaps,
        my_url=req.my_url,
        primary_keyword=req.primary_keyword,
        competitors=[_analysis_to_result(a) for a in analyses],
        blueprint=_blueprint_to_result(blueprint),
        scraping_errors=scraping_errors
    )


@router.post("/plan-content", response_model=PlanContentResponse)
async def plan_content(req: PlanContentRequest):
    """
    Generate a strategic article plan (outline) from a keyword and audience.

    Uses ArticlePlanner — a pure rule-based engine (no LLM required).
    Set OPENAI_API_KEY in .env if you want LLM-enhanced suggestions.
    """
    import os
    openai_key = os.getenv("OPENAI_API_KEY", "")

    planner = ArticlePlanner()

    # Build section headings from gaps/structure or use defaults
    if req.competitor_structure:
        headings = req.competitor_structure[:8]
    else:
        headings = create_default_structure(req.primary_keyword)

    # Create gap-to-section mappings
    gap_mapping: dict = {}
    insight_mapping: dict = {}
    if req.competitor_gaps:
        for i, gap in enumerate(req.competitor_gaps[:6]):
            section_num = (i % (len(headings) - 2)) + 2  # Skip intro, spread across body
            gap_mapping[gap[:80]] = section_num

    # Create section plans
    engagement = planner.plan_engagement_distribution(len(headings))
    section_plans: List[SectionPlan] = []

    for i, heading in enumerate(headings):
        gaps_here = [
            g for g, s in gap_mapping.items() if s == i + 1
        ]
        insights_here = []  # Could be populated from social research if available

        plan = planner.create_section_plan(
            section_number=i + 1,
            heading=heading,
            gaps_to_address=gaps_here,
            insights_to_include=insights_here,
            internal_links=[],  # Populate from internal linking map
            engagement_map=engagement
        )
        section_plans.append(plan)

    # Build meta elements
    keyword_slug = req.primary_keyword.lower().replace(" ", "-")[:50]
    meta = planner._build_meta(  # type: ignore[attr-defined]
        req.primary_keyword,
        req.target_audience
    ) if hasattr(planner, "_build_meta") else _build_meta_fallback(
        req.primary_keyword, req.target_audience
    )

    article_plan = ArticlePlan(
        topic=req.primary_keyword,
        date=__import__("datetime").datetime.now().strftime("%Y-%m-%d"),
        meta=meta,
        total_word_target=sum(s.word_target for s in section_plans),
        sections=section_plans,
        engagement_map=engagement,
        gap_to_section_mapping=gap_mapping,
        insight_to_section_mapping=insight_mapping
    )

    return _plan_to_response(article_plan, req.primary_keyword, req.target_audience)


def _build_meta_fallback(keyword: str, audience: str):
    """Fallback meta builder when planner doesn't expose _build_meta."""
    from core.article_planner import MetaElements
    slug = keyword.lower().replace(" ", "-").replace("?", "")[:50]
    return MetaElements(
        title_options=[
            f"The Ultimate Guide to {keyword}",
            f"{keyword}: Everything You Need to Know",
            f"How to {keyword} (Expert Guide)",
        ],
        meta_title=f"{keyword} Guide — Complete Resource",
        meta_description=(
            f"Learn everything about {keyword} in this comprehensive guide. "
            f"Perfect for {audience}. Step-by-step advice, expert tips, and real examples."
        ),
        url_slug=slug,
        primary_keyword=keyword,
        secondary_keywords=[]
    )
