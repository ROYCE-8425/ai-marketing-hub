import { useState } from "react";
import { API_BASE } from "../lib/apiConfig";

interface GeoBreakdown {
  score: number;
  max: number;
  details: {
    recommendations: string[];
    [key: string]: any;
  };
}

interface GeoResult {
  url: string;
  keyword: string;
  geo_score: number;
  grade: string;
  grade_label: string;
  breakdown: {
    schema: GeoBreakdown;
    structure: GeoBreakdown;
    eeat: GeoBreakdown;
    multimodal: GeoBreakdown;
    ai_visibility: GeoBreakdown;
  };
  recommendations: { category: string; recommendation: string }[];
  total_recommendations: number;
  error?: string;
}

const CATEGORY_META: Record<string, { icon: string; label: string; color: string }> = {
  schema: { icon: "🏗️", label: "Schema & Dữ liệu cấu trúc", color: "#8b5cf6" },
  structure: { icon: "📐", label: "Cấu trúc nội dung", color: "#3b82f6" },
  eeat: { icon: "🛡️", label: "E-E-A-T (Uy tín)", color: "#22c55e" },
  multimodal: { icon: "🖼️", label: "Đa phương tiện", color: "#f59e0b" },
  ai_visibility: { icon: "🤖", label: "AI Visibility", color: "#ec4899" },
};

export function GeoOptimizer() {
  const [url, setUrl] = useState("https://binhphuocmitsubishi.com");
  const [keyword, setKeyword] = useState("mitsubishi bình phước");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GeoResult | null>(null);
  const [error, setError] = useState("");

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const r = await fetch(`${API_BASE}/geo/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), keyword: keyword.trim() }),
      });
      const d = await r.json();
      if (d.error) setError(d.error);
      else setResult(d);
    } catch (e: any) {
      setError(e.message || "Lỗi kết nối");
    }
    setLoading(false);
  };

  const gradeColor = (grade: string) => {
    switch (grade) {
      case "A": return "#22c55e";
      case "B": return "#3b82f6";
      case "C": return "#f59e0b";
      case "D": return "#ef4444";
      default: return "#ef4444";
    }
  };

  return (
    <div className="geo-optimizer">
      <form className="audit-form" onSubmit={handleAnalyze}>
        <div className="hint-box">
          🤖 <strong>GEO — Generative Engine Optimization:</strong> Kiểm tra mức độ
          "AI-friendly" của website. Đảm bảo nội dung xuất hiện trong câu trả lời của
          ChatGPT, Google AI, Gemini, Perplexity.
        </div>

        <div className="input-row">
          <div className="input-group" style={{ flex: 2 }}>
            <label className="input-label">URL trang web</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
                <path d="M3.6 9h16.8M3.6 15h16.8" />
              </svg>
              <input type="url" className="text-input" placeholder="https://example.com"
                value={url} onChange={e => setUrl(e.target.value)} required />
            </div>
          </div>

          <div className="input-group" style={{ flex: 1 }}>
            <label className="input-label">Từ khóa chính</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
              </svg>
              <input type="text" className="text-input" placeholder="từ khóa..."
                value={keyword} onChange={e => setKeyword(e.target.value)} />
            </div>
          </div>

          <button
            className={`submit-btn ${loading ? "loading" : ""}`}
            type="submit"
            disabled={loading || !url.trim()}
            style={{ alignSelf: "flex-end" }}
          >
            {loading ? (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="spin-icon">
                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                </svg>
                Đang phân tích...
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M12 2L2 7l10 5 10-5-10-5z" />
                  <path d="M2 17l10 5 10-5" />
                  <path d="M2 12l10 5 10-5" />
                </svg>
                Phân tích GEO
              </>
            )}
          </button>
        </div>

        {error && (
          <p className="error-msg" role="alert">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
            </svg>
            {error}
          </p>
        )}
      </form>

      {result && (
        <div className="geo-result">
          {/* Big score */}
          <div className="geo-score-hero">
            <div className="geo-score-ring" style={{ "--score-color": gradeColor(result.grade) } as any}>
              <svg viewBox="0 0 120 120" width="140" height="140">
                <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
                <circle cx="60" cy="60" r="52" fill="none" stroke={gradeColor(result.grade)}
                  strokeWidth="8" strokeLinecap="round"
                  strokeDasharray={`${(result.geo_score / 100) * 327} 327`}
                  transform="rotate(-90 60 60)" style={{ transition: "stroke-dasharray 1s ease" }} />
              </svg>
              <div className="geo-score-inner">
                <span className="geo-score-num">{result.geo_score}</span>
                <span className="geo-score-max">/100</span>
              </div>
            </div>
            <div className="geo-score-info">
              <span className="geo-grade" style={{ color: gradeColor(result.grade) }}>{result.grade}</span>
              <span className="geo-grade-label">{result.grade_label}</span>
              <p className="geo-url">{result.url}</p>
            </div>
          </div>

          {/* Breakdown bars */}
          <div className="geo-breakdown">
            <h3 className="section-title">📊 Chi tiết điểm GEO</h3>
            <div className="geo-bars">
              {Object.entries(result.breakdown).map(([key, val]) => {
                const meta = CATEGORY_META[key] || { icon: "📌", label: key, color: "#888" };
                const pct = (val.score / val.max) * 100;
                return (
                  <div key={key} className="geo-bar-item">
                    <div className="geo-bar-label">
                      <span>{meta.icon} {meta.label}</span>
                      <span style={{ color: meta.color, fontWeight: 700 }}>{val.score}/{val.max}</span>
                    </div>
                    <div className="geo-bar-track">
                      <div className="geo-bar-fill" style={{ width: `${pct}%`, background: meta.color }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recommendations */}
          <div className="geo-recs">
            <h3 className="section-title">💡 Khuyến nghị ({result.total_recommendations})</h3>
            <div className="geo-recs-list">
              {result.recommendations.map((rec, i) => (
                <div key={i} className="geo-rec-item">
                  <span className="geo-rec-category">{rec.category}</span>
                  <span className="geo-rec-text">{rec.recommendation}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
