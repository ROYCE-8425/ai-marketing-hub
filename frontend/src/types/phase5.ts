// ─── Phase 5: Publish & Opportunity types ───────────────────────────────────

// ── Publish ────────────────────────────────────────────────────────────────────

export interface PublishMeta {
  title: string;
  description: string;
  focus_keyword: string;
}

export interface PublishResponse {
  success: boolean;
  post_id: number;
  edit_url: string;
  view_url: string;
  title: string;
  slug: string;
  word_count: number;
  categories: string[];
  tags: string[];
  post_status: string;
  meta: PublishMeta;
  message: string;
}

// ── Opportunities ─────────────────────────────────────────────────────────────

export interface IntentConfidence {
  informational: number;
  navigational: number;
  transactional: number;
  commercial_investigation: number;
}

export interface IntentAnalysisResult {
  keyword: string;
  primary_intent: string;
  secondary_intent: string | null;
  confidence: IntentConfidence;
  signals_detected: Record<string, string[]>;
  recommendations: string[];
}

export interface CategoryScores {
  above_fold: number;
  ctas: number;
  trust_signals: number;
  structure: number;
  seo: number;
}

export interface LandingPageResult {
  overall_score: number;
  grade: string;
  page_type: string;
  conversion_goal: string;
  category_scores: CategoryScores;
  critical_issues: string[];
  warnings: string[];
  suggestions: string[];
  publishing_ready: boolean;
  word_count: number;
  cta_count: number;
}

export interface ScoreBreakdown {
  volume_score: number;
  position_score: number;
  intent_score: number;
  competition_score: number;
  cluster_score: number;
  ctr_score: number;
  freshness_score: number;
  trend_score: number;
}

export interface OpportunityScoreResult {
  final_score: number;
  score_breakdown: ScoreBreakdown;
  priority: string;
  primary_factor: string;
  score_explanation: string;
}

export interface TrafficProjection {
  current_clicks: number;
  current_position: number;
  target_position: number;
  target_expected_ctr: number;
  potential_clicks: number;
  additional_clicks: number;
  percent_increase: number;
}

export interface OpportunitiesResponse {
  keyword: string;
  url: string;
  low_hanging_fruit: boolean;
  effort_level: "low" | "medium" | "high";
  verdict: string;
  intent_analysis: IntentAnalysisResult;
  landing_page: LandingPageResult;
  opportunity_score: OpportunityScoreResult;
  traffic_projection: TrafficProjection | null;
  insight_adjustments: string[];
  action_items: string[];
}
