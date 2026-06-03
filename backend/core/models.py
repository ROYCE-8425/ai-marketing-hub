from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime

from .database import Base

# ═══════════════════════════════════════════════════════════════
# 1. AUTHENTICATION & USERS
# ═══════════════════════════════════════════════════════════════

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="viewer")  # admin, editor, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # ── Relationships (1:N) ──
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    managed_sites = relationship("ManagedSite", back_populates="owner", cascade="all, delete-orphan")
    authored_contents = relationship("ContentItem", back_populates="author_user", foreign_keys="ContentItem.author_id")
    created_ab_tests = relationship("AbTest", back_populates="creator", foreign_keys="AbTest.created_by")
    usage_logs = relationship("UsageLog", back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


# ═══════════════════════════════════════════════════════════════
# 2. SITE MANAGEMENT
# ═══════════════════════════════════════════════════════════════

class ManagedSite(Base):
    __tablename__ = "managed_sites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    description = Column(Text, default="")
    niche = Column(String, default="")
    is_active = Column(Boolean, default=False)
    last_scan_score = Column(Integer, default=0)
    last_scan_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ── Relationships ──
    # N:1 — site thuộc về 1 user (chủ sở hữu)
    owner = relationship("User", back_populates="managed_sites")
    # 1:N — 1 site có nhiều keywords, nội dung, tests
    tracked_keywords = relationship("TrackedKeyword", back_populates="site", cascade="all, delete-orphan")
    content_items = relationship("ContentItem", back_populates="site", cascade="all, delete-orphan")
    ab_tests = relationship("AbTest", back_populates="site", cascade="all, delete-orphan")

    # ── SEO Intelligence Data Layer Relationships ──
    raw_snapshots = relationship("SEORawSnapshot", back_populates="site", cascade="all, delete-orphan")
    normalized_pages = relationship("SEONormalizedPage", back_populates="site", cascade="all, delete-orphan")
    normalized_issues = relationship("SEONormalizedIssue", back_populates="site", cascade="all, delete-orphan")
    advisor_runs = relationship("SEOAdvisorRun", back_populates="site", cascade="all, delete-orphan")
    derived_signals = relationship("SEODerivedSignal", back_populates="site", cascade="all, delete-orphan")
    recommendation_memories = relationship("SEORecommendationMemory", back_populates="site", cascade="all, delete-orphan")
    keyword_memories = relationship("SEOKeywordMemory", back_populates="site", cascade="all, delete-orphan")
    recommendation_outcomes = relationship("SEORecommendationOutcome", back_populates="site", cascade="all, delete-orphan")
    pattern_memories = relationship("SEOPatternMemory", back_populates="site", cascade="all, delete-orphan")


# ═══════════════════════════════════════════════════════════════
# 3. RANK TRACKER
# ═══════════════════════════════════════════════════════════════

class TrackedKeyword(Base):
    __tablename__ = "tracked_keywords"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False)
    keyword = Column(String, nullable=False)
    tag = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Unique: 1 site không track trùng keyword
    __table_args__ = (UniqueConstraint('keyword', 'site_id', name='_keyword_site_uc'),)

    # ── Relationships ──
    site = relationship("ManagedSite", back_populates="tracked_keywords")
    ranking_history = relationship("RankingHistory", back_populates="keyword_ref", cascade="all, delete-orphan")


class RankingHistory(Base):
    __tablename__ = "ranking_history"

    id = Column(Integer, primary_key=True, index=True)
    tracked_keyword_id = Column(Integer, ForeignKey("tracked_keywords.id", ondelete="CASCADE"), nullable=False)
    position = Column(Float, nullable=True)
    clicks = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    source = Column(String, default="gsc")  # gsc, dataforseo, manual, sample
    checked_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    keyword_ref = relationship("TrackedKeyword", back_populates="ranking_history")


# ═══════════════════════════════════════════════════════════════
# 4. CONTENT CALENDAR
# ═══════════════════════════════════════════════════════════════

class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    content_type = Column(String, default="blog")  # blog, page, guide, comparison, promotion
    status = Column(String, default="draft")  # draft, review, scheduled, published
    scheduled_date = Column(String, nullable=True)
    published_date = Column(String, nullable=True)
    primary_keyword = Column(String, default="")
    meta_description = Column(Text, default="")
    notes = Column(Text, default="")
    author = Column(String, default="")  # Giữ lại tên author dạng text để backward-compatible
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ── Relationships ──
    site = relationship("ManagedSite", back_populates="content_items")
    author_user = relationship("User", back_populates="authored_contents", foreign_keys=[author_id])


# ═══════════════════════════════════════════════════════════════
# 5. A/B TESTS
# ═══════════════════════════════════════════════════════════════

class AbTest(Base):
    __tablename__ = "ab_tests"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String, nullable=False)
    test_type = Column(String, default="title")  # title, description, heading, content
    url = Column(String, default="")
    primary_keyword = Column(String, default="")
    variant_a = Column(Text, nullable=False)
    variant_b = Column(Text, nullable=False)
    winner = Column(String, default="")  # A, B, hoặc rỗng
    ai_analysis = Column(Text, default="")
    score_a = Column(Float, default=0.0)
    score_b = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending, evaluated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    evaluated_at = Column(DateTime(timezone=True), nullable=True)

    # ── Relationships ──
    site = relationship("ManagedSite", back_populates="ab_tests")
    creator = relationship("User", back_populates="created_ab_tests", foreign_keys=[created_by])


# ═══════════════════════════════════════════════════════════════
# 6. USAGE HISTORY (SYSTEM LOGS)
# ═══════════════════════════════════════════════════════════════

class UsageLog(Base):
    __tablename__ = "usage_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    endpoint = Column(String, index=True, nullable=False)
    method = Column(String, default="POST")
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    status_code = Column(Integer, default=200)
    duration_ms = Column(Float, default=0.0)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="usage_logs")


# ═══════════════════════════════════════════════════════════════
# 7. SEO INTELLIGENCE DATA LAYER
# ═══════════════════════════════════════════════════════════════

class SEORawSnapshot(Base):
    __tablename__ = "seo_raw_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String, nullable=False)  # gsc, ga4, technical_scan, cwv, schema, broken_links, serp
    raw_data = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    site = relationship("ManagedSite", back_populates="raw_snapshots")


class SEONormalizedPage(Base):
    __tablename__ = "seo_normalized_pages"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    meta_description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    site = relationship("ManagedSite", back_populates="normalized_pages")


class SEONormalizedIssue(Base):
    __tablename__ = "seo_normalized_issues"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    page_url = Column(String, nullable=True)
    category = Column(String, nullable=False)  # Technical, Speed, Links, Schema, Content
    severity = Column(String, nullable=False)  # critical, warning, notice
    message = Column(Text, nullable=False)
    fix_action = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    site = relationship("ManagedSite", back_populates="normalized_issues")


class SEOAdvisorRun(Base):
    __tablename__ = "seo_advisor_runs"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    days = Column(Integer, nullable=False)
    target_keyword = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=False)
    summary = Column(Text, nullable=False)
    action_plan_7d = Column(Text, nullable=False)   # JSON string
    action_plan_30d = Column(Text, nullable=False)  # JSON string
    ai_provider = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    site = relationship("ManagedSite", back_populates="advisor_runs")


class SEODerivedSignal(Base):
    __tablename__ = "seo_derived_signals"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    advisor_run_id = Column(Integer, ForeignKey("seo_advisor_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    signal_type = Column(String, nullable=False)  # quick_wins, ctr_opportunity, rank_drops, technical_blockers, schema_gaps, cwv_risks, content_gaps, geo_readiness
    entity_identifier = Column(String, nullable=False, index=True)  # query/keyword text or page URL
    signal_data = Column(Text, nullable=False)  # JSON string
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    site = relationship("ManagedSite", back_populates="derived_signals")
    advisor_run = relationship("SEOAdvisorRun")


class SEORecommendationMemory(Base):
    """
    SEO Recommendation Strategic Catalog / Memory Layer (strategic level).
    Tracks the catalog of general SEO rules/recommendations patterns 
    offered to the user for the site, along with general user feedback/status (applied, rejected).
    """
    __tablename__ = "seo_rec_memory"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_name = Column(String, nullable=False, index=True)
    recommendation_text = Column(Text, nullable=False)
    outcome = Column(String, default="pending")  # pending, applied, rejected
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    site = relationship("ManagedSite", back_populates="recommendation_memories")


class SEOKeywordMemory(Base):
    """
    SEO Keyword Intelligence Memory (observed queries level).
    Stores high-value query opportunities observed or derived during site audits
    and traces them back to the advisor run that analyzed them.
    """
    __tablename__ = "seo_keyword_memory"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    advisor_run_id = Column(Integer, ForeignKey("seo_advisor_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    site_url = Column(String, nullable=False)
    keyword = Column(String, nullable=False)
    normalized_keyword = Column(String, nullable=False, index=True)
    page_url = Column(String, nullable=True)
    page_type = Column(String, nullable=True)
    search_intent = Column(String, nullable=True)
    source = Column(String, nullable=False)
    clicks = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    avg_position = Column(Float, default=0.0)
    trend_direction = Column(String, nullable=True)
    opportunity_type = Column(String, nullable=False)
    confidence_score = Column(Float, default=100.0)
    evidence_json = Column(Text, nullable=False)  # JSON string
    observed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Composite Index for fast lookup and de-duplication queries
    __table_args__ = (
        Index('idx_kw_memory_lookup', 'site_id', 'normalized_keyword', 'opportunity_type'),
    )

    # Relationships
    site = relationship("ManagedSite", back_populates="keyword_memories")
    advisor_run = relationship("SEOAdvisorRun")


class SEORecommendationOutcome(Base):
    """
    SEO Recommendation In-Run Execution Instances (instance level).
    Stores individual execution instances of advisor recommendations generated
    in a specific SEOAdvisorRun, capturing their priority, impact, specific page,
    target keyword, current status (pending, in_progress, completed, failed), and measured deltas.
    """
    __tablename__ = "seo_recommendation_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    advisor_run_id = Column(Integer, ForeignKey("seo_advisor_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    recommendation_type = Column(String, nullable=False)
    recommendation_text = Column(Text, nullable=False)
    priority = Column(String, nullable=True, index=True)  # high, medium, low
    impact = Column(String, nullable=True)
    page_url = Column(String, nullable=True)
    keyword = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    outcome = Column(String, nullable=True)
    execution_note = Column(Text, nullable=True)
    measured_delta_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Composite Index for reporting status by site
    __table_args__ = (
        Index('idx_rec_outcome_lookup', 'site_id', 'status'),
    )

    # Relationships
    site = relationship("ManagedSite", back_populates="recommendation_outcomes")
    advisor_run = relationship("SEOAdvisorRun")


class SEOPatternMemory(Base):
    """
    SEO Pattern Memory Layer.
    Stores observed high-value patterns (title structures, meta structures, 
    schema combinations, content templates, local SEO templates, etc.) 
    to be utilized by AI Advisor, Content Planner, GEO Optimizer, and reporting modules.
    """
    __tablename__ = "seo_pattern_memory"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("managed_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    advisor_run_id = Column(Integer, ForeignKey("seo_advisor_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    pattern_type = Column(String, nullable=False, index=True)  # title_pattern, meta_pattern, schema_pattern, content_structure_pattern, local_seo_pattern, cwv_pattern
    pattern_label = Column(String, nullable=False, index=True)  # unique label for logic matching e.g., title_has_location_and_trust
    page_type = Column(String, nullable=True, index=True)  # home, service, article, category
    search_intent = Column(String, nullable=True, index=True)  # commercial, informational, transactional
    source = Column(String, nullable=False)  # advisor, crawler, search_console, analytics
    confidence_score = Column(Float, default=100.0)
    outcome_score = Column(Float, nullable=True)
    pattern_payload_json = Column(Text, nullable=False)  # JSON payload string containing attributes/metrics
    observed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    site = relationship("ManagedSite", back_populates="pattern_memories")
    advisor_run = relationship("SEOAdvisorRun")
