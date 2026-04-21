// ─── Phase 4: Content & Competitor types ────────────────────────────────────

export interface GapItem {
  type: string;
  description: string;
  location: string;
  url: string;
  priority: string;
  opportunity: string;
}

export interface CompetitorResult {
  url: string;
  title: string;
  word_count: number;
  structure: string[];
  strengths: string[];
  gaps: GapItem[];
  outdated_items: string[];
}

export interface BlueprintResult {
  must_fill_gaps: GapItem[];
  differentiation_opportunities: string[];
  data_needed: string[];
  outdated_to_update: string[];
  structure_to_match: string[];
}

export interface CompetitorGapResponse {
  competitors_analyzed: number;
  total_gaps_found: number;
  my_url: string;
  primary_keyword: string | null;
  competitors: CompetitorResult[];
  blueprint: BlueprintResult;
  scraping_errors: string[];
}

export interface MetaResult {
  title_options: string[];
  meta_title: string;
  meta_description: string;
  url_slug: string;
  primary_keyword: string;
  secondary_keywords: string[];
}

export interface SectionResult {
  section_number: number;
  type: string;
  heading: string;
  word_target: number;
  strategic_angle: string;
  engagement_hook: string | null;
  knowledge_gaps: string[];
  unique_data: string[];
  internal_links: string[];
  cta: string | null;
  mini_story: boolean;
  featured_snippet: boolean;
}

export interface EngagementMapResult {
  mini_stories: number[];
  ctas: Record<string, number>;
  featured_snippets: number[];
}

export interface PlanContentResponse {
  topic: string;
  date: string;
  meta: MetaResult;
  total_word_target: number;
  sections: SectionResult[];
  engagement_map: EngagementMapResult;
  gap_mapping: Record<string, number>;
  insight_mapping: Record<string, number>;
  markdown_outline: string;
}