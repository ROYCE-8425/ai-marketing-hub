import { useState } from "react";
import type { PublishResponse } from "../types/phase5";
import { API_BASE } from "../lib/apiConfig";

export function usePublish() {
  const [data, setData] = useState<PublishResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const publish = async (payload: {
    wordpress_url: string;
    username: string;
    app_password: string;
    article_title: string;
    article_content: string;
    slug?: string;
    excerpt?: string;
    category?: string;
    tags?: string;
    post_status?: string;
  }) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/publish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
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

  return { data, loading, error, publish };
}
