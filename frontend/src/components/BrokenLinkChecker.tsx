import { useState, useMemo } from "react";
import { API_BASE } from "../lib/apiConfig";

// ─── Types ─────────────────────────────────────────────────────────────────────

interface LinkResult {
  url: string;
  source_page: string;
  status_code: number;
  link_type: string;  // "internal" | "external"
  status: string;     // "ok" | "broken" | "redirect"
}

interface ScanResult {
  url: string;
  total_links: number;
  ok_links: number;
  broken_links: number;
  redirect_links: number;
  broken_rate: number;
  links: LinkResult[];
}

type FilterTab = "all" | "broken" | "redirect" | "ok";

// ─── Helpers ───────────────────────────────────────────────────────────────────

/** Status row background color */
function statusRowBg(status: string): string {
  if (status === "broken") return "rgba(239,68,68,0.06)";
  if (status === "redirect") return "rgba(234,179,8,0.06)";
  return "transparent";
}

/** Status badge color */
function statusColor(status: string): string {
  if (status === "broken") return "#ef4444";
  if (status === "redirect") return "#eab308";
  return "#15803d";
}

/** Status badge label in Vietnamese */
function statusLabel(status: string): string {
  if (status === "broken") return "Hỏng";
  if (status === "redirect") return "Redirect";
  return "Tốt";
}

/** Link type label */
function typeLabel(type: string): string {
  return type === "internal" ? "Nội bộ" : "Bên ngoài";
}

/** Export data as CSV */
function exportCsv(links: LinkResult[], filename: string) {
  const header = "URL,Trang nguồn,Status Code,Loại,Trạng thái\n";
  const rows = links.map(l =>
    `"${l.url}","${l.source_page}",${l.status_code},"${typeLabel(l.link_type)}","${statusLabel(l.status)}"`
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
  const [filter, setFilter] = useState<FilterTab>("all");

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
    if (filter === "all") return result.links;
    return result.links.filter(l => l.status === filter);
  }, [result, filter]);

  const tabs: { key: FilterTab; label: string }[] = [
    { key: "all", label: "Tất cả" },
    { key: "broken", label: "Links hỏng" },
    { key: "redirect", label: "Redirect" },
    { key: "ok", label: "Tốt" },
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
              <span style={cardValue}>{result.total_links}</span>
            </div>
            <div style={cardStyle}>
              <span style={cardLabel}>Links hoạt động</span>
              <span style={{ ...cardValue, color: "#15803d" }}>{result.ok_links}</span>
            </div>
            <div style={cardStyle}>
              <span style={cardLabel}>Links hỏng</span>
              <span style={{ ...cardValue, color: "#ef4444" }}>{result.broken_links}</span>
            </div>
            <div style={cardStyle}>
              <span style={cardLabel}>Tỷ lệ hỏng</span>
              <span style={{
                ...cardValue,
                color: result.broken_rate > 5 ? "#ef4444" : result.broken_rate > 1 ? "#eab308" : "#15803d",
              }}>
                {result.broken_rate.toFixed(1)}%
              </span>
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
                  {t.key === "broken" && result.broken_links > 0 && (
                    <span style={{
                      background: "rgba(239,68,68,0.2)", color: "#ef4444",
                      fontSize: 10, fontWeight: 700, padding: "2px 6px", borderRadius: 99,
                    }}>
                      {result.broken_links}
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
                    {["URL", "Trang nguồn", "Status Code", "Loại", "Trạng thái"].map(h => (
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
                          {link.url.replace(/^https?:\/\//, "").slice(0, 60)}
                        </a>
                      </td>
                      <td style={{
                        padding: "10px 14px", fontSize: 12, color: "var(--text)",
                        maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                        borderBottom: "1px solid rgba(22,163,74,0.5)",
                      }}>
                        {link.source_page.replace(/^https?:\/\//, "").slice(0, 40)}
                      </td>
                      <td style={{
                        padding: "10px 14px",
                        fontFamily: '"DM Mono", monospace', fontWeight: 600,
                        color: statusColor(link.status),
                        borderBottom: "1px solid rgba(22,163,74,0.5)",
                      }}>
                        {link.status_code}
                      </td>
                      <td style={{
                        padding: "10px 14px", fontSize: 12,
                        borderBottom: "1px solid rgba(22,163,74,0.5)",
                      }}>
                        <span style={{
                          display: "inline-block", fontSize: 11, fontWeight: 600,
                          padding: "2px 8px", borderRadius: 99,
                          background: link.link_type === "internal"
                            ? "rgba(59,130,246,0.12)" : "rgba(245,158,11,0.12)",
                          color: link.link_type === "internal" ? "#3b82f6" : "#f59e0b",
                        }}>
                          {typeLabel(link.link_type)}
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
            Hiển thị {filteredLinks.length} / {result.total_links} links
          </p>
        </div>
      )}
    </div>
  );
}
