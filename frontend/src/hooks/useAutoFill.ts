import { useState, useCallback } from "react";
import type { BulkSyncResponse } from "../types/phase6";
import { API_BASE } from "../lib/apiConfig";

export interface AutoFillResult {
  bulk: BulkSyncResponse | null;
  gscStatus: { gsc: string; ga4: string; dataforseo: string };
  /** Error message when auto-fill fails */
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
 * useAutoFill — calls the bulk-data-sync endpoint to pull live metrics
 * and returns them ready for auto-population into the Campaign Tracker form.
 *
 * When the backend returns error responses (missing credentials), this hook
 * surfaces the error clearly — it does NOT generate dummy/mock data.
 */
export function useAutoFill(): UseAutoFillReturn {
  const [result, setResult] = useState<AutoFillResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const autoFill = useCallback(async (url: string, keyword: string): Promise<AutoFillResult | null> => {
    if (!url.trim() || !keyword.trim()) {
      setError("Cần nhập URL và từ khóa.");
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

      // Determine connector status from actual backend responses
      const gscData = bulk._raw_gsc;
      const serpData = bulk._raw_serp;

      // GSC status: only "connected" if source is live_gsc (not error)
      const gscSource = gscData?.source ?? "unknown";
      const gscConnected = gscSource === "live" || gscData?.gsc?.source === "live_gsc";

      // GA4 status: independent — check ga4 sub-object, NOT derived from GSC
      const ga4Source = gscData?.ga4?.source ?? "unknown";
      const ga4Connected = ga4Source === "live_ga4";

      // DataForSEO status: check serp source
      const serpSource = serpData?.source ?? "unknown";
      const dfsConnected = serpSource === "live_dataforseo";

      const connectorResult: AutoFillResult = {
        bulk,
        gscStatus: {
          gsc: gscConnected ? "connected" : "disconnected",
          ga4: ga4Connected ? "connected" : "disconnected",
          dataforseo: dfsConnected ? "connected" : "disconnected",
        },
        fallbackReason: null,
      };

      // Check for errors from backend (missing credentials, API failures)
      const gscError = gscData?.gsc?.error;
      const ga4Error = (gscData?.ga4 as any)?.error;
      const serpError = serpData?.error;

      const errorParts: string[] = [];
      if (gscError) errorParts.push(`GSC: ${gscError}`);
      if (ga4Error) errorParts.push(`GA4: ${ga4Error}`);
      if (serpError) errorParts.push(`SERP: ${serpError}`);

      if (errorParts.length > 0) {
        connectorResult.fallbackReason = errorParts.join(" · ");
      }

      setResult(connectorResult);
      return connectorResult;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Auto-fill thất bại";
      setError(msg);
      // Return error state — NO dummy data generation
      const errorResult: AutoFillResult = {
        bulk: null,
        gscStatus: { gsc: "disconnected", ga4: "disconnected", dataforseo: "disconnected" },
        fallbackReason: msg,
      };
      setResult(errorResult);
      return errorResult;
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
