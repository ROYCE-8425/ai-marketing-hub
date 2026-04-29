import { useState } from "react";
import { API_BASE } from "../lib/apiConfig";

interface LinkItem {
  url: string;
  anchor: string;
  nofollow: boolean;
  domain?: string;
}

interface QualityInfo {
  score: number;
  total: number;
  dofollow: number;
  nofollow: number;
  unique_domains: number;
  branded_anchors: number;
  generic_anchors: number;
  quality: string;
}

interface Domain {
  domain: string;
  links: number;
  dofollow: number;
  nofollow: number;
  anchors: string[];
}

interface BacklinkResult {
  url: string;
  overall_score: number;
  grade: string;
  internal_links: { total: number; quality: QualityInfo; sample: LinkItem[] };
  external_links: { total: number; quality: QualityInfo; sample: LinkItem[] };
  referring_domains: Domain[];
  total_domains: number;
  suggestions: string[];
}

export function BacklinkAnalyzer() {
  const [url, setUrl] = useState("https://binhphuocmitsubishi.com");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacklinkResult | null>(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"internal" | "external" | "domains">("internal");

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const r = await fetch(`${API_BASE}/backlinks/analyze`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      const d = await r.json();
      if (d.error) setError(d.error); else setResult(d);
    } catch (e: any) { setError(e.message); }
    setLoading(false);
  };

  const gradeColor = (g: string) => ({ A: "#22c55e", B: "#3b82f6", C: "#f59e0b", D: "#ef4444" }[g] || "#888");

  return (
    <div className="geo-optimizer">
      <form className="audit-form" onSubmit={handleAnalyze}>
        <div className="hint-box">🔗 <strong>Backlink Analyzer:</strong> Phân tích liên kết nội bộ và liên kết ngoài, đánh giá chất lượng anchor text.</div>
        <div className="input-row">
          <div className="input-group" style={{ flex: 1 }}>
            <label className="input-label">URL trang web</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" /><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" /></svg>
              <input type="url" className="text-input" value={url} onChange={e => setUrl(e.target.value)} required />
            </div>
          </div>
          <button className={`submit-btn ${loading ? "loading" : ""}`} type="submit" disabled={loading} style={{ alignSelf: "flex-end" }}>
            {loading ? "⏳ Đang phân tích..." : "🔗 Phân tích Backlinks"}
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
                  strokeDasharray={`${(result.overall_score / 100) * 327} 327`}
                  transform="rotate(-90 60 60)" style={{ transition: "stroke-dasharray 1s ease" }} />
              </svg>
              <div className="geo-score-inner">
                <span className="geo-score-num">{result.overall_score}</span>
                <span className="geo-score-max">/100</span>
              </div>
            </div>
            <div className="geo-score-info">
              <span className="geo-grade" style={{ color: gradeColor(result.grade) }}>{result.grade}</span>
              <span className="geo-grade-label">Link Quality</span>
              <p className="geo-url">Internal: {result.internal_links.total} | External: {result.external_links.total} | Domains: {result.total_domains}</p>
            </div>
          </div>

          {/* Stats */}
          <div className="spin-stats">
            <div className="spin-stat">
              <span className="spin-stat-label">Internal Links</span>
              <span className="spin-stat-value" style={{ color: "#3b82f6" }}>{result.internal_links.total}</span>
            </div>
            <div className="spin-stat">
              <span className="spin-stat-label">External Links</span>
              <span className="spin-stat-value" style={{ color: "#f59e0b" }}>{result.external_links.total}</span>
            </div>
            <div className="spin-stat">
              <span className="spin-stat-label">Dofollow</span>
              <span className="spin-stat-value" style={{ color: "#22c55e" }}>
                {result.internal_links.quality.dofollow + result.external_links.quality.dofollow}
              </span>
            </div>
            <div className="spin-stat">
              <span className="spin-stat-label">Nofollow</span>
              <span className="spin-stat-value" style={{ color: "#ef4444" }}>
                {result.internal_links.quality.nofollow + result.external_links.quality.nofollow}
              </span>
            </div>
          </div>

          {/* Tabs */}
          <div className="spin-version-tabs" style={{ marginTop: 16 }}>
            <button className={`spin-version-tab ${tab === "internal" ? "active" : ""}`} onClick={() => setTab("internal")}>
              🏠 Internal ({result.internal_links.total})
            </button>
            <button className={`spin-version-tab ${tab === "external" ? "active" : ""}`} onClick={() => setTab("external")}>
              🌐 External ({result.external_links.total})
            </button>
            <button className={`spin-version-tab ${tab === "domains" ? "active" : ""}`} onClick={() => setTab("domains")}>
              🏢 Domains ({result.total_domains})
            </button>
          </div>

          {/* Link table */}
          {(tab === "internal" || tab === "external") && (
            <div className="rt-table-wrap">
              <table className="rt-table">
                <thead>
                  <tr>
                    <th>URL</th>
                    <th>Anchor Text</th>
                    <th>Type</th>
                  </tr>
                </thead>
                <tbody>
                  {(tab === "internal" ? result.internal_links.sample : result.external_links.sample).map((link, i) => (
                    <tr key={i}>
                      <td style={{ maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        <a href={link.url} target="_blank" rel="noopener noreferrer" style={{ color: "#3b82f6", fontSize: 12 }}>
                          {link.url.replace(/^https?:\/\//, "").slice(0, 50)}
                        </a>
                      </td>
                      <td style={{ maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontSize: 13 }}>{link.anchor}</td>
                      <td>
                        <span className={`rt-source-badge ${link.nofollow ? "pending" : "gsc"}`}>
                          {link.nofollow ? "nofollow" : "dofollow"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Domains tab */}
          {tab === "domains" && result.referring_domains.length > 0 && (
            <div className="rt-table-wrap">
              <table className="rt-table">
                <thead>
                  <tr><th>Domain</th><th>Links</th><th>Dofollow</th><th>Nofollow</th><th>Anchors</th></tr>
                </thead>
                <tbody>
                  {result.referring_domains.map((d, i) => (
                    <tr key={i}>
                      <td style={{ fontSize: 13, fontWeight: 600 }}>{d.domain}</td>
                      <td>{d.links}</td>
                      <td style={{ color: "#22c55e" }}>{d.dofollow}</td>
                      <td style={{ color: "#ef4444" }}>{d.nofollow}</td>
                      <td style={{ fontSize: 11, opacity: 0.7, maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{d.anchors.join(", ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Suggestions */}
          {result.suggestions.length > 0 && (
            <div className="geo-recs">
              <h3 className="section-title">💡 Gợi ý Link Building ({result.suggestions.length})</h3>
              <div className="geo-recs-list">
                {result.suggestions.map((s, i) => (
                  <div key={i} className="geo-rec-item">
                    <span className="geo-rec-text">{s}</span>
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
