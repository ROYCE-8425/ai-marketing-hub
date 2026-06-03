export interface ManagedSite {
  id: number;
  name: string;
  url: string;
  is_active: number;
  niche?: string;
}

export interface ActionPlanItem {
  day?: string;
  week?: string;
  task: string;
  priority: "high" | "medium" | "low" | string;
  impact: string;
  is_recurring?: boolean;
  seen_before_count?: number;
  pending_before_count?: number;
  history_note?: string | null;
  pattern_related?: boolean;
  pattern_label?: string | null;
  pattern_occurrences?: number;
  pattern_note?: string | null;
  was_completed_before?: boolean;
  completed_before_count?: number;
  failed_before_count?: number;
  has_measured_delta_before?: boolean;
  outcome_note?: string | null;
}

export interface DeterministicIssue {
  severity: "critical" | "warning" | "info";
  category: string;
  message: string;
  fix: string;
}

export interface QuickWin {
  keyword: string;
  current_position: number;
  impressions: number;
  action: string;
}

export interface ContentOpportunity {
  keyword: string;
  search_intent: string;
  reason: string;
}

export interface SourceStatus {
  gsc: string;
  ga4: string;
  serp: string;
  technical: string;
  cwv: string;
  schema: string;
  broken: string;
  rank_tracking: string;
  usage: string;
}

export interface GscQueryItem {
  keyword: string;
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

export interface GscQuickWinItem {
  keyword: string;
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

export interface GscSnapshot {
  clicks: number;
  impressions: number;
  ctr: number;
  avg_position: number;
  top_queries: GscQueryItem[];
  quick_wins: GscQuickWinItem[];
}

export interface Ga4PageItem {
  path: string;
  pageviews: number;
  sessions?: number;
  engagement_rate?: number;
  bounce_rate?: number;
}

export interface Ga4ChannelItem {
  source: string;
  sessions: number;
  conversions: number;
}

export interface Ga4Snapshot {
  total_sessions: number;
  total_pageviews: number;
  engagement_rate: number;
  bounce_rate: number;
  top_pages: Ga4PageItem[];
  top_channels: Ga4ChannelItem[];
}

export interface TechnicalIssueItem {
  category: string;
  message: string;
  fix: string;
}

export interface CwvOpportunityItem {
  title: string;
  description: string;
  score: number;
  displayValue: string;
}

export interface CwvSnapshot {
  overall_status?: string;
  error?: string;
  lighthouse_scores?: {
    performance?: number;
    accessibility?: number;
    best_practices?: number;
    seo?: number;
  };
  metrics?: Record<string, {
    value: number;
    unit: string;
    rating: string;
  }>;
  opportunities?: CwvOpportunityItem[];
}

export interface SchemaSnapshot {
  schemas_found?: number;
  valid: boolean;
  types_found?: string[];
  errors?: string[];
  warnings?: string[];
}

export interface TechnicalSnapshot {
  seo_score: number;
  grade: string;
  load_time: number;
  broken_links_count: number;
  critical_issues: TechnicalIssueItem[];
  warnings: TechnicalIssueItem[];
  cwv: CwvSnapshot;
  schema: SchemaSnapshot;
}

export interface TrackedKeywordItem {
  id?: number;
  keyword: string;
  site_url: string;
  tag?: string;
  created_at?: string;
}

export interface RankAlertItem {
  keyword: string;
  severity: "critical" | "warning";
  drop: number;
  current_position: number;
}

export interface RankTrackingSnapshot {
  tracked_keywords: TrackedKeywordItem[];
  alerts: RankAlertItem[];
}

export interface UsageHistorySnapshot {
  total_calls: number;
  success_rate: number;
  error_count: number;
  anomalies: string[];
}

export interface SerpOrganicResultItem {
  position: number;
  title: string;
  url: string;
  domain: string;
}

export interface SerpSnapshot {
  keyword: string;
  organic_results: SerpOrganicResultItem[];
  search_intent?: {
    primary: string;
    content_recommendations?: string[];
  };
}

export interface DataSnapshot {
  gsc: GscSnapshot;
  ga4: Ga4Snapshot;
  technical: TechnicalSnapshot;
  rank_tracking: RankTrackingSnapshot;
  usage_history: UsageHistorySnapshot;
  serp: SerpSnapshot | null;
}

export interface MemoryContext {
  keyword_memory_records: number;
  recommendation_outcomes: number;
  top_recurring_keywords: string[];
  top_recurring_recommendation_types: string[];
  pending_recommendations_count: number;
}

export interface RecurringOpportunityItem {
  keyword: string;
  opportunity_type: string;
  occurrences: number;
  clicks?: number;
  impressions?: number;
  ctr?: number;
  avg_position?: number;
}

export interface RepeatedRecommendationItem {
  recommendation_text: string;
  recommendation_type: string;
  priority?: string | null;
  occurrences: number;
  last_seen?: string | null;
}

export interface PendingRecommendationItem {
  id: number;
  recommendation_type: string;
  recommendation_text: string;
  priority?: string | null;
  impact?: string | null;
  status: string;
  page_url?: string | null;
  keyword?: string | null;
  created_at?: string | null;
  reviewed_at?: string | null;
  execution_note?: string | null;
  measured_delta_json?: Record<string, number> | null;
  outcome?: string | null;
}

export interface RecommendationOutcomeUpdatePayload {
  status: string;
  outcome?: string | null;
  execution_note?: string | null;
  measured_delta_json?: Record<string, number> | null;
}

export interface RecentCompletedRecommendation {
  recommendation_text: string;
  recommendation_type: string;
  priority?: string | null;
  updated_at?: string | null;
  measured_delta?: Record<string, number> | null;
}

export interface RecentFailedRecommendation {
  recommendation_text: string;
  recommendation_type: string;
  priority?: string | null;
  updated_at?: string | null;
  execution_note?: string | null;
}

export interface OutcomeTrackingContext {
  total_outcomes: number;
  pending_count: number;
  in_progress_count: number;
  completed_count: number;
  failed_count: number;
  completed_with_delta_count: number;
  recent_completed_recommendations?: RecentCompletedRecommendation[] | null;
  recent_failed_recommendations?: RecentFailedRecommendation[] | null;
}

export interface RoadmapTask {
  id: string;
  phase: "7d" | "30d" | string;
  day?: string | null;
  week?: string | null;
  task: string;
  priority: "high" | "medium" | "low" | string;
  impact: string;
  is_recurring: boolean;
  pending_before_count: number;
  history_note?: string | null;
  pattern_related: boolean;
  pattern_label?: string | null;
  pattern_occurrences: number;
  pattern_note?: string | null;
  was_completed_before: boolean;
  completed_before_count: number;
  failed_before_count: number;
  has_measured_delta_before: boolean;
  outcome_note?: string | null;
  roadmap_priority_score: number;
  priority_reasons: string[];
  stream_reason: string;
}

export interface RoadmapStream {
  id: string;
  title: string;
  description: string;
  priority: "high" | "medium" | "low" | string;
  max_score: number;
  children: RoadmapTask[];
}

export interface RoadmapTree {
  goal: string;
  streams: RoadmapStream[];
}

export interface AdvisorResponse {
  site_url: string;
  analyzed_at: string;
  confidence: "high" | "medium" | "low";
  confidence_score: number;
  summary: string;
  top_issues: DeterministicIssue[];
  quick_wins: QuickWin[];
  technical_blockers: DeterministicIssue[];
  content_opportunities: ContentOpportunity[];
  action_plan_7d: ActionPlanItem[];
  action_plan_30d: ActionPlanItem[];
  source_status: SourceStatus;
  ai_provider: string;
  data_snapshot: DataSnapshot;
  memory_context?: MemoryContext | null;
  recurring_opportunities?: RecurringOpportunityItem[] | null;
  repeated_recommendations?: RepeatedRecommendationItem[] | null;
  pending_recommendations?: PendingRecommendationItem[] | null;
  in_progress_recommendations?: PendingRecommendationItem[] | null;
  new_vs_recurring_summary?: string | null;
  outcome_tracking_context?: OutcomeTrackingContext | null;
  completed_recommendations_summary?: string | null;
  failed_recommendations_summary?: string | null;
  effective_recommendation_summary?: string | null;
  roadmap_tree?: RoadmapTree | null;
  roadmap_summary?: string | null;
}
