// ─── SEO types (Phase 1) ─────────────────────────────────────────────────────

export interface AuditUrlRequest {
  url: string;
  primary_keyword: string;
}

export interface KeywordAnalysis {
  word_count: number;
  primary_keyword: {
    keyword: string;
    density: number;
    density_status: string;
    exact_matches: number;
    total_occurrences: number;
    critical_placements: Record<string, boolean | string | number>;
  };
  keyword_stuffing: {
    risk_level: string;
    safe: boolean;
    warnings: string[];
  };
  distribution_heatmap: Array<{
    section: string;
    heat_level: number;
    keyword_count: number;
    density: number;
  }>;
  lsi_keywords: string[];
  recommendations: string[];
}

export interface SeoQuality {
  overall_score: number;
  grade: string;
  publishing_ready: boolean;
  category_scores: Record<string, number>;
  critical_issues: string[];
  warnings: string[];
  suggestions: string[];
  details: Record<string, unknown>;
}

// ─── CRO/Trust types (Phase 3) ──────────────────────────────────────────────

export interface CroChecklistSummary {
  total_checks: number;
  passed: number;
  failed: number;
  critical_failures: number;
  warnings: number;
}

export interface CtaFound {
  text: string;
  position_pct: number;
  quality_score: number;
}

export interface CtaDistribution {
  first_cta_position: number | null;
  has_above_fold: boolean;
  has_closing: boolean;
  distribution_quality: string;
}

export interface CroRecommendation {
  priority: string;
  category: string;
  check: string;
  recommendation: string;
}

export interface CtaRecommendation {
  priority: string;
  category: string;
  issue: string;
  recommendation: string;
}

export interface CroChecklist {
  score: number;
  grade: string;
  passes_audit: boolean;
  summary: CroChecklistSummary;
  critical_failures: string[];
  warnings: string[];
  category_scores: Record<string, number>;
  recommendations: CroRecommendation[];
}

export interface CtaAnalysis {
  total_ctas: number;
  avg_quality_score: number;
  distribution_score: number;
  goal_alignment_score: number;
  overall_effectiveness: number;
  ctas_found: CtaFound[];
  distribution: CtaDistribution;
  recommendations: CtaRecommendation[];
}

export interface ElementScores {
  headline: number;
  value_prop: number;
  cta: number;
  trust: number;
}

export interface AboveFoldIssue {
  severity: string;
  element: string;
  issue: string;
}

export interface AboveFoldAnalysis {
  overall_score: number;
  grade: string;
  passes_5_second_test: boolean;
  element_scores: ElementScores;
  headline_quality: string;
  headline_text: string | null;
  cta_above_fold: boolean;
  cta_text: string | null;
  trust_signal_above_fold: boolean;
  issues: AboveFoldIssue[];
  recommendations: string[];
}

export interface TrustSummary {
  testimonials_found: number;
  has_social_proof: boolean;
  has_risk_reversal: boolean;
  authority_signals: number;
  security_present: boolean;
}

export interface Testimonial {
  quote: string;
  attribution: string | null;
}

export interface SocialProof {
  customer_counts: Array<{ value: string }>;
  specific_results: Array<{ value: string }>;
}

export interface RiskReversals {
  free_trial_found: boolean;
  no_credit_card_found: boolean;
  cancel_anytime_found: boolean;
  guarantee_found: boolean;
}

export interface AuthoritySignals {
  media_mentions: boolean;
  awards: boolean;
  years_in_business: boolean;
}

export interface TrustRecommendation {
  priority: string;
  category: string;
  issue: string;
  recommendation: string;
}

export interface TrustSignals {
  overall_score: number;
  grade: string;
  summary: TrustSummary;
  strengths: string[];
  weaknesses: string[];
  testimonials: Testimonial[];
  social_proof: SocialProof;
  risk_reversals: RiskReversals;
  authority_signals: AuthoritySignals;
  recommendations: TrustRecommendation[];
}

export interface SalesRiskAlert {
  severity: "high" | "medium";
  message: string;
}

export interface CroAnalysis {
  overall_cro_score: number;
  cro_grade: string;
  cro_checklist: CroChecklist;
  cta_analysis: CtaAnalysis;
  above_fold_analysis: AboveFoldAnalysis;
  trust_signals: TrustSignals;
  sales_risk_alerts: SalesRiskAlert[];
}

// ─── Combined response ───────────────────────────────────────────────────────

export interface AuditResponse {
  primary_keyword: string;
  keyword_analysis: KeywordAnalysis;
  seo_quality: SeoQuality;
  cro_analysis: CroAnalysis;
}