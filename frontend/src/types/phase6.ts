// Phase 6 — Live Data Connector types

export type ConnectorStatus = "connected" | "disconnected" | "pending";

export interface DataConnectorStatus {
  gsc: ConnectorStatus;
  ga4: ConnectorStatus;
  dataforseo: ConnectorStatus;
  last_checked: string | null;
}

// ─── GSC Sync ──────────────────────────────────────────────────────────────────

export interface GscKeywordResult {
  keyword: string;
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
  source: "live_gsc" | "mock_gsc";
  error?: string;
}

export interface GscSyncResponse {
  url: string;
  keyword: string;
  analyzed_at: string;
  period_days: number;
  source: string;
  gsc: GscKeywordResult | null;
  ga4: {
    url: string;
    total_pageviews: number;
    sessions: number;
    avg_engagement_rate: number;
    bounce_rate: number;
    trend_direction: string;
    trend_percent: number;
    source: "live_ga4" | "mock_ga4";
  } | null;
  page_content: { title: string; content: string } | null;
}

// ─── SERP Sync ─────────────────────────────────────────────────────────────────

export interface SerpSyncResponse {
  keyword: string;
  location_code: number;
  analyzed_at: string;
  source: "live_dataforseo" | "mock";
  search_volume?: number;
  difficulty?: number;
  cpc?: number;
  competition?: number;
  serp_features?: string[];
  estimated_ctr_position_1?: number;
  estimated_ctr_position_3?: number;
  estimated_ctr_position_10?: number;
  search_intent?: {
    primary: string;
    secondary: string;
    confidence: Record<string, number>;
    content_recommendations: string[];
  };
  error?: string;
  note?: string;
}

// ─── Bulk Sync (unified auto-fill payload) ────────────────────────────────────

export interface BulkSyncResponse {
  url: string;
  keyword: string;
  analyzed_at: string;
  data_sources: {
    gsc: string;
    serp: string;
  };
  /** True when the backend returned mock data because credentials are not configured. */
  _is_mock_fallback?: boolean;
  current_position?: number;
  monthly_clicks?: number;
  monthly_impressions?: number;
  ctr?: number;
  search_volume?: number;
  difficulty?: number;
  serp_features?: string;
  search_intent?: string;
  _raw_gsc?: GscSyncResponse;
  _raw_serp?: SerpSyncResponse;
}
