import { useState, useMemo } from "react";
import { API_BASE } from "../lib/apiConfig";

// ─── Types ─────────────────────────────────────────────────────────────────────

interface LinkResult {
  url: string;
  source_tag: string;
  anchor_text: string;
  type: string;
  status: number | string | null;
}

interface ScanResult {
  url: string;
  duration_seconds: number;
  summary: {
    total_links_found: number;
    total_checked: number;
    broken_count: number;
    redirected_count: number;
    ok_count: number;
    internal_broken: number;
    external_broken: number;
  };
  broken_links: LinkResult[];
  redirected_links: LinkResult[];
  health_score: { score: number; grade: string; label: string };
  recommendations: string[];
}

type FilterTab = "broken" | "redirect";

// ─── Helpers ───────────────────────────────────────────────────────────────────


/** Status badge color */
const statusColor = (code: number | string | null) => {
  const c = typeof code === "number" ? code : parseInt(String(code), 10);
  if (isNaN(c)) return "#ef4444";
  if (c >= 400 || c === 0) return "#ef4444";
  if (c >= 300) return "#f59e0b";
  return "#10b981";
};

const statusLabel = (code: number | string | null) => {
  const c = typeof code === "number" ? code : parseInt(String(code), 10);
  if (isNaN(c)) return "Lỗi";
  if (c === 0) return "Lỗi mạng";
  if (c >= 400) return `Lỗi ${c}`;
  if (c >= 300) return `Chuyển hướng ${c}`;
  return "OK";
};

const statusRowBg = (code: number | string | null) => {
  const c = typeof code === "number" ? code : parseInt(String(code), 10);
  if (isNaN(c) || c >= 400 || c === 0) return "rgba(239,68,68,0.05)";
  if (c >= 300) return "rgba(245,158,11,0.05)";
  return "transparent";
};

/** Link type label */
function typeLabel(type: string): string {
  return type === "internal" ? "Nội bộ" : "Bên ngoài";
}

/** Export data as CSV */
function exportCsv(links: LinkResult[], filename: string) {
  const header = "URL,Thẻ nguồn,Mỏ neo,Loại,Mã HTTP\n";
  const rows = links.map(l =>
    `"${l.url}","${l.source_tag || ""}","${(l.anchor_text || "").replace(/"/g, '""')}","${l.type || ""}","${l.status || ""}"`
  ).join("\n");
  const blob = new Blob([header + rows], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

// ─── Shared inline styles (matching dark glass theme) ──────────────────────────

const cardStyle: React.CSSProperties = {
  background: "var(--surface2)",
  border: "1px solid var(--border)",
  borderRadius: "var(--radius-sm)",
  padding: "14px 16px",
  display: "flex",
  flexDirection: "column",
  gap: 4,
  flex: "1 1 0",
  minWidth: 140,
};
const cardLabel: React.CSSProperties = {
  fontSize: 11,
  color: "var(--text-dim)",
  textTransform: "uppercase" as const,
  letterSpacing: "0.06em",
  fontWeight: 600,
};
const cardValue: React.CSSProperties = {
  fontSize: 22,
  fontWeight: 700,
  color: "var(--text-h)",
  fontFamily: '"DM Mono", monospace',
};

// ─── Component ─────────────────────────────────────────────────────────────────

export function BrokenLinkChecker() {
  const [url, setUrl] = useState("");
  const [maxLinks, setMaxLinks] = useState(100);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<FilterTab>("broken");

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const r = await fetch(`${API_BASE}/seo-tools/broken-links`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), max_links: maxLinks }),
      });
      const d = await r.json();
      if (!r.ok || d.error) {
        setError(d.error || d.detail || `HTTP ${r.status}`);
      } else {
        setResult(d);
      }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
    } catch (err: any) {
      setError(err.message || "Lỗi kết nối");
    }
    setLoading(false);
  };

  // Filter links by tab
  const filteredLinks = useMemo(() => {
    if (!result) return [];
    if (filter === "broken") return result.broken_links;
    if (filter === "redirect") return result.redirected_links;
    return result.broken_links;
  }, [result, filter]);

  const tabs: { key: FilterTab; label: string }[] = [
    { key: "broken", label: "Links hỏng" },
    { key: "redirect", label: "Redirect" },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fade-up 0.5s ease both" }}>
      {/* ── Input Form ── */}
      <form className="audit-form" onSubmit={handleScan}>
        <div className="hint-box">
          🔗 <strong>Kiểm tra link hỏng:</strong> Quét trang web để tìm link hỏng (404), redirect, và phân loại link nội bộ / bên ngoài.
        </div>

        <div className="input-row">
          <div className="input-group" style={{ flex: 1 }}>
            <label className="input-label">URL trang web</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
              </svg>
              <input
                type="url" className="text-input" value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="https://example.com" required
              />
            </div>
          </div>

          <div className="input-group" style={{ maxWidth: 140 }}>
            <label className="input-label">Giới hạn link</label>
            <input
              type="number" className="text-input" value={maxLinks}
              onChange={e => setMaxLinks(Math.max(1, parseInt(e.target.value) || 100))}
              min={1} max={500} style={{ paddingLeft: 14 }}
            />
          </div>

          <button
            className="analyze-btn" type="submit"
            disabled={loading || !url.trim()}
            style={{ alignSelf: "flex-end" }}
          >
            {loading ? <span className="btn-spinner" /> : "🔍 Quét"}
          </button>
        </div>

        {error && <p className="error-msg">❌ {error}</p>}
      </form>

      {/* ── Results ── */}
      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: 20, animation: "fade-up 0.5s ease both" }}>
          {/* Summary cards */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
            <div style={cardStyle}>
              <span style={cardLabel}>Tổng links</span>
              <span style={cardValue}>{result.summary.total_checked}</span>
            </div>
            <div style={cardStyle}>
              <span style={cardLabel}>Links hoạt động</span>
              <span style={{ ...cardValue, color: "#15803d" }}>{result.summary.ok_count}</span>
            </div>
            <div style={cardStyle}>
              <span style={cardLabel}>Links hỏng</span>
              <span style={{ ...cardValue, color: "#ef4444" }}>{result.summary.broken_count}</span>
            </div>
            <div style={cardStyle}>
              <span style={cardLabel}>Tỷ lệ hỏng</span>
              <span style={{
                ...cardValue,
                color: (result.summary.broken_count / (result.summary.total_checked || 1) * 100) > 5 ? "#ef4444" : "#15803d",
              }}>
                {((result.summary.broken_count / (result.summary.total_checked || 1)) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="score-ring">
              <div className="ring-bg"></div>
              <div
                className="ring-progress"
                style={{
                  background: `conic-gradient(var(--green) ${result.health_score.score}%, transparent 0)`,
                }}
              ></div>
              <div className="ring-inner">
                <span style={{ fontSize: 28, fontWeight: 800 }}>{result.health_score.score}</span>
                <span style={{ fontSize: 11, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Điểm</span>
              </div>
            </div>
            <div style={{ flex: 1, minWidth: 200 }}>
              <h4 style={{ fontSize: 18, color: "var(--text-h)", marginBottom: 8, display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 24 }}>{result.health_score.score >= 90 ? "🏆" : result.health_score.score >= 70 ? "✅" : "⚠️"}</span>
                Đánh giá: {result.health_score.grade}
              </h4>
              <p style={{ color: "var(--text)", fontSize: 14, lineHeight: 1.5, marginBottom: 12 }}>
                Trang web có <strong>{result.summary.broken_count}</strong> link hỏng trên tổng số <strong>{result.summary.total_checked}</strong> link được kiểm tra.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {result.recommendations?.map((rec, i) => (
                  <div key={i} style={{
                    display: "flex", alignItems: "flex-start", gap: 8,
                    background: "rgba(0,0,0,0.15)", padding: "10px 14px", borderRadius: 6,
                    fontSize: 13, borderLeft: "3px solid var(--primary)"
                  }}>
                    <span style={{ color: "var(--primary)" }}>💡</span>
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Filter tabs + Export */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
            <div className="tab-bar">
              {tabs.map(t => (
                <button
                  key={t.key}
                  className={`tab-btn ${filter === t.key ? "tab-active" : ""}`}
                  onClick={() => setFilter(t.key)}
                  type="button"
                >
                  {t.label}
                  {t.key === "broken" && result.summary.broken_count > 0 && (
                    <span style={{
                      background: "rgba(239,68,68,0.2)", color: "#ef4444",
                      padding: "2px 6px", borderRadius: 99, fontSize: 11, fontWeight: 700
                    }}>
                      {result.summary.broken_count}
                    </span>
                  )}
                  {t.key === "redirect" && result.summary.redirected_count > 0 && (
                    <span style={{
                      background: "rgba(234,179,8,0.2)", color: "#eab308",
                      padding: "2px 6px", borderRadius: 99, fontSize: 11, fontWeight: 700
                    }}>
                      {result.summary.redirected_count}
                    </span>
                  )}
                </button>
              ))}
            </div>

            <button
              type="button" className="reset-btn"
              onClick={() => exportCsv(filteredLinks, `broken-links-${new Date().toISOString().slice(0,10)}.csv`)}
            >
              📥 Xuất CSV
            </button>
          </div>

          {/* Results table */}
          <div style={{
            background: "linear-gradient(145deg, rgba(255,255,255,0.85), rgba(255,255,255,0.6))",
            border: "1px solid rgba(22,163,74,0.1)",
            borderRadius: "var(--radius)",
            padding: 0,
            overflow: "hidden",
            boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
          }}>
            <div style={{ overflowX: "auto" }}>
              <table style={{
                width: "100%", borderCollapse: "collapse", fontSize: 13,
              }}>
                <thead>
                  <tr>
                    {["URL", "Thẻ nguồn", "Mỏ neo", "Loại", "Mã HTTP"].map(h => (
                      <th key={h} style={{
                        textAlign: "left", padding: "12px 14px",
                        fontSize: 11, fontWeight: 600, color: "var(--text-dim)",
                        textTransform: "uppercase" as const, letterSpacing: "0.06em",
                        borderBottom: "1px solid var(--border)", whiteSpace: "nowrap",
                      }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filteredLinks.length === 0 && (
                    <tr>
                      <td colSpan={5} style={{
                        padding: 24, textAlign: "center", color: "var(--text-dim)",
                      }}>
                        Không có kết quả cho bộ lọc này
                      </td>
                    </tr>
                  )}
                  {filteredLinks.map((link, i) => (
                    <tr key={i} style={{ background: statusRowBg(link.status) }}>
                      <td style={{
                        padding: "10px 14px", maxWidth: 280,
                        overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                        borderBottom: "1px solid rgba(22,163,74,0.5)",
                      }}>
                        <a
                          href={link.url} target="_blank" rel="noopener noreferrer"
                          style={{ color: "#3b82f6", fontSize: 12, textDecoration: "none" }}
                        >
                          {(link.url || "").replace(/^https?:\/\//, "").slice(0, 60)}
                        </a>
                      </td>
                      <td style={{
                        padding: "10px 14px", fontSize: 12, color: "var(--text)",
                        borderBottom: "1px solid rgba(22,163,74,0.5)",
                      }}>
                        {link.source_tag || "-"}
                      </td>
                      <td style={{
                        padding: "10px 14px", fontSize: 12, color: "var(--text)",
                        maxWidth: 150, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                        borderBottom: "1px solid rgba(22,163,74,0.5)",
                      }}>
                        {link.anchor_text || "-"}
                      </td>
                      <td style={{
                        padding: "10px 14px", fontSize: 12,
                        borderBottom: "1px solid rgba(22,163,74,0.5)",
                      }}>
                        <span style={{
                          display: "inline-block", fontSize: 11, fontWeight: 600,
                          padding: "2px 8px", borderRadius: 99,
                          background: link.type === "internal"
                            ? "rgba(59,130,246,0.12)" : "rgba(245,158,11,0.12)",
                          color: link.type === "internal" ? "#3b82f6" : "#f59e0b",
                        }}>
                          {typeLabel(link.type || "")}
                        </span>
                      </td>
                      <td style={{
                        padding: "10px 14px",
                        borderBottom: "1px solid rgba(22,163,74,0.5)",
                      }}>
                        <span style={{
                          display: "inline-flex", alignItems: "center", gap: 5,
                          fontSize: 12, fontWeight: 600,
                          padding: "3px 10px", borderRadius: 99,
                          background: `${statusColor(link.status)}15`,
                          color: statusColor(link.status),
                          border: `1px solid ${statusColor(link.status)}40`,
                        }}>
                          <span style={{
                            width: 6, height: 6, borderRadius: "50%",
                            background: statusColor(link.status),
                          }} />
                          {statusLabel(link.status)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Count summary */}
          <p style={{ fontSize: 12, color: "var(--text-dim)", textAlign: "right" }}>
            Hiển thị {filteredLinks.length} / {result.summary.total_checked} links
          </p>
        </div>
      )}
    </div>
  );
}
