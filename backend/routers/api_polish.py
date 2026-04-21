"""
API Polish Router — Phase 7

Anti-Detection & Content Polish (Humanize AI text):
- Removes invisible Unicode watermarks, zero-width chars, format-control
- Replaces AI-telltale phrases with natural alternatives
- Scores readability & engagement after scrubbing
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.content_scrubber import ContentScrubber
from core.readability_scorer import ReadabilityScorer
from core.engagement_analyzer import EngagementAnalyzer

router = APIRouter(prefix="/api", tags=["content"])


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────

class PolishRequest(BaseModel):
    """Request for content polishing / humanizing."""
    raw_content: str = Field(
        ...,
        min_length=1,
        description="Raw AI-generated content to polish and humanize",
    )


class PolishResponse(BaseModel):
    """Result of the content polishing pipeline."""
    humanized_content: str = Field(..., description="Cleaned, humanized content")
    ai_watermarks_removed: int = Field(..., description="Total AI watermark signs removed")
    readability_grade: str = Field(..., description="Readability grade, e.g. '8th Grade'")
    readability_score: float = Field(..., description="Readability overall score 0-100")
    flesch_reading_ease: float = Field(..., description="Flesch Reading Ease score")
    engagement_score: int = Field(..., description="Engagement score 0-100")
    scrub_stats: dict = Field(..., description="Breakdown of what was scrubbed")


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────────────────────────────────────

def _to_ordinal_grade(grade_float: float) -> str:
    """Convert a float like 8.4 to '8th Grade'."""
    grade_int = int(round(grade_float))
    ordinal = {
        1: "1st", 2: "2nd", 3: "3rd",
    }.get(grade_int, f"{grade_int}th")
    return f"{ordinal} Grade"


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/content/polish", response_model=PolishResponse)
async def polish_content(req: PolishRequest):
    """
    Polish & humanize AI-generated content via a sequential pipeline:

    1. ContentScrubber — strips zero-width chars, removes AI-telltale phrases
    2. ReadabilityScorer — scores Flesch, grade level, structure
    3. EngagementAnalyzer — evaluates hook, rhythm, CTA distribution, paragraph length

    Returns the humanized content plus metadata for UI feedback.
    """
    raw = req.raw_content

    # Step 1: Scrub
    scrubber = ContentScrubber()
    humanized, scrub_stats = scrubber.scrub(raw)

    # Tally total removed
    ai_watermarks_removed = (
        scrub_stats.get("unicode_removed", 0)
        + scrub_stats.get("format_control_removed", 0)
        + scrub_stats.get("ai_phrases_replaced", 0)
    )

    # Step 2: Readability scoring (run in thread — CPU-bound)
    readability_scorer = ReadabilityScorer()
    # textstat is CPU-bound; offload from the async event loop
    import asyncio
    import concurrent.futures

    def score_readability():
        return readability_scorer.analyze(humanized)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        read_result = await asyncio.get_event_loop().run_in_executor(
            pool, score_readability
        )

    flesch_grade = read_result.get("reading_level", 0)
    readability_score = read_result.get("overall_score", 0)
    flesch_ease = read_result.get(
        "readability_metrics", {}
    ).get("flesch_reading_ease", 0)
    readability_grade = _to_ordinal_grade(flesch_grade)

    # Step 3: Engagement analysis (CPU-bound, also offload)
    analyzer = EngagementAnalyzer()

    def analyze_engagement():
        return analyzer.analyze(humanized)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        engage_result = await asyncio.get_event_loop().run_in_executor(
            pool, analyze_engagement
        )

    rhythm_score = engage_result.get("rhythm", {}).get("score", 0)
    passed_count = engage_result.get("passed_count", 0)
    total_criteria = engage_result.get("total_criteria", 4)
    engagement_score = int(round((passed_count / total_criteria) * 100 + rhythm_score) / 2)

    return PolishResponse(
        humanized_content=humanized,
        ai_watermarks_removed=ai_watermarks_removed,
        readability_grade=readability_grade,
        readability_score=round(readability_score, 1),
        flesch_reading_ease=round(flesch_ease, 1),
        engagement_score=engagement_score,
        scrub_stats=scrub_stats,
    )