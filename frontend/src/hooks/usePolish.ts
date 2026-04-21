import { useState, useCallback } from "react";
import { API_BASE } from "../lib/apiConfig";

export interface PolishResult {
  humanized_content: string;
  ai_watermarks_removed: number;
  readability_grade: string;
  readability_score: number;
  flesch_reading_ease: number;
  engagement_score: number;
  scrub_stats: {
    unicode_removed: number;
    format_control_removed: number;
    ai_phrases_replaced: number;
    emdashes_replaced: number;
  };
}

export interface PolishSuccess extends PolishResult {
  success: true;
}

export interface PolishError {
  success: false;
  error: string;
}

export type PolishResponse = PolishSuccess | PolishError;

export function usePolish() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PolishResponse | null>(null);

  const polish = useCallback(async (rawContent: string): Promise<PolishResponse> => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API_BASE}/content/polish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_content: rawContent }),
      });

      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        const msg = errBody.detail ?? `HTTP ${res.status}`;
        setError(msg);
        const err: PolishError = { success: false, error: msg };
        setResult(err);
        return err;
      }

      const data: PolishResult = await res.json();
      const success: PolishSuccess = { ...data, success: true };
      setResult(success);
      return success;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Network error";
      setError(msg);
      const err: PolishError = { success: false, error: msg };
      setResult(err);
      return err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setResult(null);
  }, []);

  return { loading, error, result, polish, reset };
}
