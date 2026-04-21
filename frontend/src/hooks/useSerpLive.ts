import { useState } from "react";
import { API_BASE } from "../lib/apiConfig";

// ─── Types ─────────────────────────────────────────────────────────────────────

export interface SerpResult {
  position: number;
  title: string;
  url: string;
  domain: string;
  snippet: string;
  breadcrumb?: string;
}

export interface SerpLiveResponse {
  keyword: string;
  location?: string;
  organic_results: SerpResult[];
  serp_features: string[];
  total_results: number;
  results_count: number;
  source: string;
  analyzed_at: string;
  error?: string;
  note?: string;
  // DataForSEO bonus fields
  search_volume?: number;
  cpc?: number;
  competition?: number;
}

export interface PageAnalysis {
  url: string;
  title?: string;
  word_count: number;
  headings?: number;
  images?: number;
  links?: number;
  paragraphs?: number;
  reading_time_min?: number;
  status: string;
}

export interface DeepAnalyzeResponse {
  keyword: string;
  analyzed_at: string;
  pages_requested: number;
  pages_analyzed: number;
  pages: PageAnalysis[];
  statistics: {
    min?: number;
    max?: number;
    mean?: number;
    median?: number;
    std_dev?: number;
    percentile_25?: number;
    percentile_75?: number;
  };
  recommendation: {
    recommended_min?: number;
    recommended_optimal?: number;
    recommended_max?: number;
    your_status?: string;
    your_percentile?: number;
    message?: string;
    reasoning?: string;
    error?: string;
  };
}

// ─── Hook: SERP Live ───────────────────────────────────────────────────────────

export function useSerpLive() {
  const [data, setData] = useState<SerpLiveResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = async (keyword: string, location = "vn", numResults = 10) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/serp/live`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          keyword,
          location,
          num_results: numResults,
        }),
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.detail ?? `HTTP ${res.status}`);
      }
      const result = await res.json();
      if (result.error && !result.organic_results?.length) {
        throw new Error(result.error);
      }
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setData(null);
    setError(null);
  };

  return { data, loading, error, search, reset };
}

// ─── Hook: Deep Analyze ────────────────────────────────────────────────────────

export function useDeepAnalyze() {
  const [data, setData] = useState<DeepAnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (keyword: string, urls: string[], yourWordCount?: number) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/serp/deep-analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          keyword,
          urls,
          your_word_count: yourWordCount,
        }),
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.detail ?? `HTTP ${res.status}`);
      }
      setData(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, analyze };
}
