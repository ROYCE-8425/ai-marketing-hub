import { useState } from "react";
import { API_BASE } from "../lib/apiConfig";

interface Issue {
  severity: string;
  message: string;
  fix?: string;
  category?: string;
}

interface BreakdownItem {
  score: number;
  max: number;
  details: any;
}

interface ScanResult {
  url: string;
  score: number;
  max_score: number;
  grade: string;
  grade_label: string;
  load_time: number;
  breakdown: Record<string, BreakdownItem>;
  issues: Issue[];
  total_issues: number;
  critical_count: number;
  warning_count: number;
}

const SECTION_META: Record<string, { icon: string; label: string; color: string }> = {
  meta_tags: { icon: "🏷️", label: "Meta Tags", color: "#8b5cf6" },
  headings: { icon: "📑", label: "Headings", color: "#3b82f6" },
  images: { icon: "🖼️", label: "Hình ảnh", color: "#f59e0b" },
  mobile: { icon: "📱", label: "Mobile", color: "#22c55e" },
  links: { icon: "🔗", label: "Links", color: "#ec4899" },
  sitemap_robots: { icon: "🗺️", label: "Sitemap/Robots", color: "#06b6d4" },
  performance: { icon: "⚡", label: "Performance", color: "#eab308" },
  security: { icon: "🔒", label: "Bảo mật", color: "#10b981" },
};

export function TechnicalSeo() {
  const [url, setUrl] = useState("https://binhphuocmitsubishi.com");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState("");

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const r = await fetch(`${API_BASE}/tech-seo/scan`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      const d = await r.json();
      if (d.error) setError(d.error); else setResult(d);
    } catch (e: any) { setError(e.message); }
    setLoading(false);
  };

  const gradeColor = (g: string) => ({ A: "#22c55e", B: "#3b82f6", C: "#f59e0b", D: "#ef4444", F: "#ef4444" }[g] || "#888");
  const sevIcon = (s: string) => ({ critical: "🔴", warning: "🟡", info: "🔵" }[s] || "⚪");

  return (
    <div className="geo-optimizer">
      <form className="audit-form" onSubmit={handleScan}>
        <div className="hint-box">🔧 <strong>Technical SEO Scanner:</strong> Kiểm tra meta tags, headings, hình ảnh, mobile, links, sitemap, performance, bảo mật.</div>
        <div className="input-row">
          <div className="input-group" style={{ flex: 1 }}>
            <label className="input-label">URL trang web</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" /><path d="M3.6 9h16.8M3.6 15h16.8" /></svg>
              <input type="url" className="text-input" value={url} onChange={e => setUrl(e.target.value)} required />
            </div>
          </div>
          <button className={`submit-btn ${loading ? "loading" : ""}`} type="submit" disabled={loading} style={{ alignSelf: "flex-end" }}>
            {loading ? (<><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="spin-icon"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /></svg> Đang scan...</>) : "🔍 Scan Technical SEO"}
          </button>
        </div>
        {error && <p className="error-msg">{error}</p>}
      </form>

      {result && (
        <div className="geo-result">
          {/* Score */}
          <div className="geo-score-hero">
            <div className="geo-score-ring">
              <svg viewBox="0 0 120 120" width="140" height="140">
                <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
                <circle cx="60" cy="60" r="52" fill="none" stroke={gradeColor(result.grade)}
                  strokeWidth="8" strokeLinecap="round"
                  strokeDasharray={`${(result.score / 100) * 327} 327`}
                  transform="rotate(-90 60 60)" style={{ transition: "stroke-dasharray 1s ease" }} />
              </svg>
              <div className="geo-score-inner">
                <span className="geo-score-num">{result.score}</span>
                <span className="geo-score-max">/100</span>
              </div>
            </div>
            <div className="geo-score-info">
              <span className="geo-grade" style={{ color: gradeColor(result.grade) }}>{result.grade}</span>
              <span className="geo-grade-label">{result.grade_label}</span>
              <p className="geo-url">⚡ {result.load_time}s &nbsp;|&nbsp; {result.total_issues} vấn đề ({result.critical_count} critical)</p>
            </div>
          </div>

          {/* Breakdown */}
          <div className="geo-breakdown">
            <h3 className="section-title">📊 Chi tiết</h3>
            <div className="geo-bars">
              {Object.entries(result.breakdown).map(([key, val]) => {
                const meta = SECTION_META[key] || { icon: "📌", label: key, color: "#888" };
                return (
                  <div key={key} className="geo-bar-item">
                    <div className="geo-bar-label">
                      <span>{meta.icon} {meta.label}</span>
                      <span style={{ color: meta.color, fontWeight: 700 }}>{val.score}/{val.max}</span>
                    </div>
                    <div className="geo-bar-track">
                      <div className="geo-bar-fill" style={{ width: `${(val.score / val.max) * 100}%`, background: meta.color }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Issues */}
          {result.issues.length > 0 && (
            <div className="geo-recs">
              <h3 className="section-title">🔍 Vấn đề ({result.total_issues})</h3>
              <div className="geo-recs-list">
                {result.issues.map((issue, i) => (
                  <div key={i} className="geo-rec-item">
                    <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                      <span>{sevIcon(issue.severity)}</span>
                      <span className="geo-rec-category">{issue.category}</span>
                    </div>
                    <span className="geo-rec-text" style={{ fontWeight: 600 }}>{issue.message}</span>
                    {issue.fix && <span className="geo-rec-text" style={{ opacity: 0.7, fontSize: 12 }}>→ {issue.fix}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
