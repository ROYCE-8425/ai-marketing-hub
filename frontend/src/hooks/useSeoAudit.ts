import { useState } from "react";
import type { AuditUrlRequest, AuditResponse } from "../types/seo";
import { API_BASE } from "../lib/apiConfig";

interface UseSeoAuditReturn {
  data: AuditResponse | null;
  loading: boolean;
  error: string | null;
  analyze: (req: AuditUrlRequest) => Promise<void>;
  reset: () => void;
}

export function useSeoAudit(): UseSeoAuditReturn {
  const [data, setData] = useState<AuditResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (req: AuditUrlRequest) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/audit-url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
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

  const reset = () => {
    setData(null);
    setError(null);
  };

  return { data, loading, error, analyze, reset };
}
