import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface HistoryEntry {
  id: number;
  timestamp: string;
  endpoint: string;
  method: string;
  input: any;
  output: any;
  status_code: number;
  duration_ms: number;
  error: string | null;
  success: boolean;
}

interface Stats {
  total_calls: number;
  success: number;
  errors: number;
  success_rate: number;
  endpoints: Record<string, { calls: number; success: number; errors: number; avg_ms: number }>;
  last_call: string | null;
}

export default function UsageHistory() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<HistoryEntry | null>(null);
  const [filter, setFilter] = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      const [hRes, sRes] = await Promise.all([
        fetch(`${API}/api/usage-history?limit=100${filter ? `&endpoint=${filter}` : ""}`),
        fetch(`${API}/api/usage-stats`),
      ]);
      if (hRes.ok) setHistory(await hRes.json());
      if (sRes.ok) setStats(await sRes.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [filter]);

  const handleClear = async () => {
    if (!confirm("Xóa toàn bộ lịch sử?")) return;
    await fetch(`${API}/api/usage-history`, { method: "DELETE" });
    fetchData();
  };

  const statusColor = (code: number) => {
    if (code < 300) return "#4ade80";
    if (code < 400) return "#fbbf24";
    return "#f87171";
  };

  const methodColor = (m: string) => {
    switch (m) {
      case "GET": return "rgba(34,197,94,0.15)";
      case "POST": return "rgba(59,130,246,0.15)";
      case "DELETE": return "rgba(239,68,68,0.15)";
      default: return "rgba(255,255,255,0.05)";
    }
  };

  return (
    <div>
      <h2 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-h)", marginBottom: 16 }}>
        📊 Lịch sử sử dụng
      </h2>

      {/* Stats Cards */}
      {stats && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 16 }}>
          <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 12, padding: 16, border: "1px solid rgba(255,255,255,0.06)" }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: "var(--text-h)" }}>{stats.total_calls}</div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>Tổng API calls</div>
          </div>
          <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 12, padding: 16, border: "1px solid rgba(255,255,255,0.06)" }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: "#4ade80" }}>{stats.success}</div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>Thành công</div>
          </div>
          <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 12, padding: 16, border: "1px solid rgba(255,255,255,0.06)" }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: "#f87171" }}>{stats.errors}</div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>Lỗi</div>
          </div>
          <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 12, padding: 16, border: "1px solid rgba(255,255,255,0.06)" }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: stats.success_rate > 80 ? "#4ade80" : "#fbbf24" }}>{stats.success_rate}%</div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>Tỷ lệ thành công</div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div style={{ display: "flex", gap: 8, marginBottom: 12, alignItems: "center" }}>
        <input
          type="text"
          placeholder="Lọc theo endpoint..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ flex: 1, padding: "8px 12px", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#fff", fontSize: 12 }}
        />
        <button onClick={fetchData} style={{ padding: "8px 16px", background: "rgba(139,92,246,0.1)", border: "1px solid rgba(139,92,246,0.2)", color: "#a78bfa", borderRadius: 8, cursor: "pointer", fontSize: 12, fontWeight: 600 }}>
          🔄 Refresh
        </button>
        <button onClick={handleClear} style={{ padding: "8px 16px", background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.15)", color: "#f87171", borderRadius: 8, cursor: "pointer", fontSize: 12 }}>
          🗑️ Xóa
        </button>
      </div>

      {/* History Table */}
      {loading ? (
        <div style={{ textAlign: "center", padding: 40, color: "rgba(255,255,255,0.4)" }}>⏳ Đang tải...</div>
      ) : history.length === 0 ? (
        <div style={{ textAlign: "center", padding: 40, color: "rgba(255,255,255,0.4)" }}>
          Chưa có lịch sử. Sử dụng các tính năng để bắt đầu ghi log.
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table className="serp-table">
            <thead>
              <tr>
                <th style={{ width: 30 }}>#</th>
                <th>Thời gian</th>
                <th>Method</th>
                <th>Endpoint</th>
                <th>Status</th>
                <th>Thời gian (ms)</th>
                <th>Input</th>
                <th>Output</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h) => (
                <tr key={h.id} onClick={() => setSelected(h)} style={{ cursor: "pointer" }}>
                  <td style={{ color: "rgba(255,255,255,0.3)" }}>{h.id}</td>
                  <td style={{ fontSize: 11, whiteSpace: "nowrap" }}>
                    {new Date(h.timestamp).toLocaleString("vi-VN")}
                  </td>
                  <td>
                    <span style={{ padding: "2px 8px", borderRadius: 4, fontSize: 10, fontWeight: 700, background: methodColor(h.method), color: "var(--text-h)" }}>
                      {h.method}
                    </span>
                  </td>
                  <td style={{ fontFamily: "monospace", fontSize: 11, color: "var(--text-h)" }}>
                    {h.endpoint}
                  </td>
                  <td>
                    <span style={{ padding: "2px 8px", borderRadius: 4, fontSize: 10, fontWeight: 700, background: `${statusColor(h.status_code)}20`, color: statusColor(h.status_code) }}>
                      {h.status_code}
                    </span>
                  </td>
                  <td style={{ color: h.duration_ms > 5000 ? "#f87171" : h.duration_ms > 2000 ? "#fbbf24" : "var(--text)" }}>
                    {h.duration_ms.toLocaleString()}ms
                  </td>
                  <td style={{ maxWidth: 150, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontSize: 11, color: "rgba(255,255,255,0.5)" }}>
                    {h.input ? JSON.stringify(h.input).slice(0, 50) : "—"}
                  </td>
                  <td style={{ maxWidth: 150, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontSize: 11, color: h.error ? "#f87171" : "rgba(255,255,255,0.5)" }}>
                    {h.error || (h.output ? JSON.stringify(h.output).slice(0, 50) : "—")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Detail Modal */}
      {selected && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 9999 }} onClick={() => setSelected(null)}>
          <div onClick={(e) => e.stopPropagation()} style={{ background: "var(--card-bg, #1a1a2e)", borderRadius: 16, padding: 24, maxWidth: 700, width: "90%", maxHeight: "80vh", overflow: "auto", border: "1px solid rgba(255,255,255,0.1)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
              <h3 style={{ color: "var(--text-h)", margin: 0 }}>
                #{selected.id} — {selected.endpoint}
              </h3>
              <button onClick={() => setSelected(null)} style={{ background: "none", border: "none", color: "rgba(255,255,255,0.5)", fontSize: 18, cursor: "pointer" }}>✕</button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
              <div style={{ fontSize: 12, color: "rgba(255,255,255,0.6)" }}>
                <strong>Method:</strong> {selected.method}<br />
                <strong>Status:</strong> <span style={{ color: statusColor(selected.status_code) }}>{selected.status_code}</span><br />
                <strong>Duration:</strong> {selected.duration_ms}ms<br />
                <strong>Time:</strong> {new Date(selected.timestamp).toLocaleString("vi-VN")}
              </div>
              {selected.error && (
                <div style={{ padding: 8, background: "rgba(239,68,68,0.1)", borderRadius: 8, fontSize: 12, color: "#f87171" }}>
                  <strong>Error:</strong> {selected.error}
                </div>
              )}
            </div>

            <div style={{ marginBottom: 12 }}>
              <h4 style={{ color: "var(--text-h)", fontSize: 13, marginBottom: 4 }}>📥 Input</h4>
              <pre style={{ background: "rgba(0,0,0,0.3)", borderRadius: 8, padding: 12, fontSize: 11, color: "#4ade80", overflow: "auto", maxHeight: 200, whiteSpace: "pre-wrap" }}>
                {selected.input ? JSON.stringify(selected.input, null, 2) : "— No input —"}
              </pre>
            </div>

            <div>
              <h4 style={{ color: "var(--text-h)", fontSize: 13, marginBottom: 4 }}>📤 Output</h4>
              <pre style={{ background: "rgba(0,0,0,0.3)", borderRadius: 8, padding: 12, fontSize: 11, color: "#60a5fa", overflow: "auto", maxHeight: 300, whiteSpace: "pre-wrap" }}>
                {selected.output ? JSON.stringify(selected.output, null, 2) : "— No output —"}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Endpoint Stats */}
      {stats && Object.keys(stats.endpoints).length > 0 && (
        <div style={{ marginTop: 16 }}>
          <h3 style={{ color: "var(--text-h)", fontSize: 14, marginBottom: 8 }}>📊 Thống kê theo endpoint</h3>
          <table className="serp-table">
            <thead>
              <tr>
                <th>Endpoint</th>
                <th>Calls</th>
                <th>Success</th>
                <th>Errors</th>
                <th>Avg Time</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(stats.endpoints).sort(([, a], [, b]) => b.calls - a.calls).map(([ep, data]) => (
                <tr key={ep} onClick={() => setFilter(ep)} style={{ cursor: "pointer" }}>
                  <td style={{ fontFamily: "monospace", fontSize: 11, color: "var(--text-h)" }}>{ep}</td>
                  <td>{data.calls}</td>
                  <td style={{ color: "#4ade80" }}>{data.success}</td>
                  <td style={{ color: data.errors > 0 ? "#f87171" : "var(--text)" }}>{data.errors}</td>
                  <td style={{ color: data.avg_ms > 5000 ? "#f87171" : data.avg_ms > 2000 ? "#fbbf24" : "var(--text)" }}>
                    {data.avg_ms.toFixed(0)}ms
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
