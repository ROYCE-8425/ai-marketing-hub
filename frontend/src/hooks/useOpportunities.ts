import { useState } from "react";
import type { OpportunitiesResponse } from "../types/phase5";
import { API_BASE } from "../lib/apiConfig";

export function useOpportunities() {
  const [data, setData] = useState<OpportunitiesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (params: {
    url: string;
    keyword: string;
    current_position?: number;
    monthly_impressions?: number;
    monthly_clicks?: number;
    search_volume?: number;
    difficulty?: number;
    serp_features?: string;
    search_intent?: string;
  }) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const qs = new URLSearchParams();
      qs.set("url", params.url);
      qs.set("keyword", params.keyword);
      if (params.current_position !== undefined)
        qs.set("current_position", String(params.current_position));
      if (params.monthly_impressions !== undefined)
        qs.set("monthly_impressions", String(params.monthly_impressions));
      if (params.monthly_clicks !== undefined)
        qs.set("monthly_clicks", String(params.monthly_clicks));
      if (params.search_volume !== undefined)
        qs.set("search_volume", String(params.search_volume));
      if (params.difficulty !== undefined)
        qs.set("difficulty", String(params.difficulty));
      if (params.serp_features)
        qs.set("serp_features", params.serp_features);
      if (params.search_intent)
        qs.set("search_intent", params.search_intent);

      const res = await fetch(
        `${API_BASE}/opportunities?${qs.toString()}`,
        { method: "POST" }
      );
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
