import { useState, useCallback } from "react";
import type { BulkSyncResponse } from "../types/phase6";
import { API_BASE } from "../lib/apiConfig";

export interface AutoFillResult {
  bulk: BulkSyncResponse | null;
  gscStatus: { gsc: string; ga4: string; dataforseo: string };
  /** The actual error that triggered mock fallback. Shown in the UI so the user knows the connection failed. */
  fallbackReason: string | null;
}

export interface UseAutoFillReturn {
  result: AutoFillResult | null;
  loading: boolean;
  error: string | null;
  autoFill: (url: string, keyword: string) => Promise<AutoFillResult | null>;
  reset: () => void;
}

/**
 * useAutoFill — calls the bulk-data-sync endpoint to pull live (or mock) metrics
 * and returns them ready for auto-population into the Campaign Tracker form.
 */
export function useAutoFill(): UseAutoFillReturn {
  const [result, setResult] = useState<AutoFillResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const autoFill = useCallback(async (url: string, keyword: string): Promise<AutoFillResult | null> => {
    if (!url.trim() || !keyword.trim()) {
      setError("URL and keyword are required.");
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/data/bulk-sync`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), keyword: keyword.trim() }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? `HTTP ${res.status}`);
      }

      const bulk: BulkSyncResponse = await res.json();

      // Determine data-source health from raw responses
      const gscSource = bulk._raw_gsc?.source ?? "unknown";
      const serpSource = bulk._raw_serp?.source ?? "unknown";
      const gscStatus = bulk._raw_gsc?.gsc;

      const connectorResult: AutoFillResult = {
        bulk,
        gscStatus: {
          gsc: gscSource === "live_gsc" ? "connected" : "disconnected",
          ga4: gscStatus != null ? "connected" : "disconnected",
          dataforseo: serpSource === "live_dataforseo" ? "connected" : "pending",
        },
        fallbackReason: null,
      };

      setResult(connectorResult);
      return connectorResult;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Auto-fill failed";
      setError(msg);
      // Graceful degradation: return mock data with explicit flag,
      // so the form still works but the UI makes it clear the data is synthetic.
      const dummy: AutoFillResult = {
        bulk: { ..._buildDummyBulk(url, keyword), _is_mock_fallback: true },
        gscStatus: { gsc: "disconnected", ga4: "disconnected", dataforseo: "pending" },
        fallbackReason: msg,
      };
      setResult(dummy);
      return dummy;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, loading, error, autoFill, reset };
}

// ─── Dummy data fallback (no credentials needed) ─────────────────────────────

function _buildDummyBulk(url: string, keyword: string): BulkSyncResponse {
  const kw = keyword.toLowerCase();
  const isCommercial = /best|top|review|vs|compare|alternative|pricing|hosting/i.test(kw);
  const isTransactional = /buy|pricing|cost|plan/i.test(kw);

  const vol = isTransactional ? 3200 : isCommercial ? 5800 : 2400;
  const diff = isTransactional ? 68 : isCommercial ? 55 : 42;
  const pos = 12;
  const imp = 2400;
  const clk = Math.round(imp * 0.04);

  return {
    url,
    keyword,
    analyzed_at: new Date().toISOString(),
    data_sources: { gsc: "mock", serp: "mock" },
    current_position: pos,
    monthly_clicks: clk,
    monthly_impressions: imp,
    ctr: Math.round((clk / imp) * 10000) / 10000,
    search_volume: vol,
    difficulty: diff,
    serp_features: isCommercial ? "featured_snippet,people_also_ask,local_pack" : "featured_snippet,people_also_ask",
    search_intent: isTransactional ? "transactional" : isCommercial ? "commercial_investigation" : "informational",
    _raw_gsc: {
      url, keyword, analyzed_at: new Date().toISOString(), period_days: 30,
      source: "mock", gsc: { keyword, clicks: clk, impressions: imp, ctr: clk / imp, position: pos, source: "mock_gsc" },
      ga4: { url, total_pageviews: 4820, sessions: 3640, avg_engagement_rate: 0.61, bounce_rate: 0.38, trend_direction: "rising", trend_percent: 12.4, source: "mock_ga4" },
      page_content: null,
    },
    _raw_serp: {
      keyword, location_code: 2840, analyzed_at: new Date().toISOString(), source: "mock",
      search_volume: vol, difficulty: diff, serp_features: ["featured_snippet", "people_also_ask"],
    },
  };
}
