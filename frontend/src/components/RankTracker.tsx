import { useState, useEffect, useCallback } from "react";
import { API_BASE } from "../lib/apiConfig";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine
} from "recharts";

interface TrackedKeyword {
  keyword: string;
  tag: string;
  position: number | null;
  previous_position: number | null;
  change: number | null;
  clicks: number;
  impressions: number;
  ctr: number;
  source: string;
  last_checked: string | null;
}

interface HistoryPoint {
  date: string;
  position: number;
  clicks: number;
  impressions: number;
}

interface Alert {
  keyword: string;
  current_position: number;
  previous_position: number;
  drop: number;
  severity: string;
}

export function RankTracker() {
  const [keywords, setKeywords] = useState<TrackedKeyword[]>([]);
  const [newKeyword, setNewKeyword] = useState("");
  const [newTag, setNewTag] = useState("");
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [selectedKw, setSelectedKw] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [historyDays, setHistoryDays] = useState(30);
  const [error, setError] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [activeTag, setActiveTag] = useState("");
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [showImport, setShowImport] = useState(false);
  const [csvText, setCsvText] = useState("");
  const [importResult, setImportResult] = useState("");

  const fetchKeywords = useCallback(async () => {
    try {
      const params = activeTag ? `?tag=${encodeURIComponent(activeTag)}` : "";
      const r = await fetch(`${API_BASE}/rank-tracker/keywords${params}`);
      const d = await r.json();
      setKeywords(d.keywords || []);
    } catch { /* ignore */ }
  }, [activeTag]);

  const fetchTags = async () => {
    try {
      const r = await fetch(`${API_BASE}/rank-tracker/tags`);
      const d = await r.json();
      setTags(d.tags || []);
    } catch { /* ignore */ }
  };

  const fetchAlerts = async () => {
    try {
      const r = await fetch(`${API_BASE}/rank-tracker/alerts`);
      const d = await r.json();
      setAlerts(d.alerts || []);
    } catch { /* ignore */ }
  };

  useEffect(() => { fetchKeywords(); fetchTags(); fetchAlerts(); }, [fetchKeywords]);

  const addKeyword = async () => {
    if (!newKeyword.trim()) return;
    setLoading(true);
    setError("");
    try {
      await fetch(`${API_BASE}/rank-tracker/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword: newKeyword.trim(), tag: newTag.trim() }),
      });
      setNewKeyword("");
      setNewTag("");
      await fetchKeywords();
      await fetchTags();
    } catch (e: any) { setError(e.message); }
    setLoading(false);
  };

  const removeKeyword = async (kw: string) => {
    await fetch(`${API_BASE}/rank-tracker/remove`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keyword: kw }),
    });
    if (selectedKw === kw) { setSelectedKw(null); setHistory([]); }
    await fetchKeywords();
  };

  const syncRankings = async () => {
    setSyncing(true); setError("");
    try {
      const r = await fetch(`${API_BASE}/rank-tracker/sync`, { method: "POST" });
      const d = await r.json();
      if (d.error) setError(d.error);
      await fetchKeywords();
      await fetchAlerts();
    } catch (e: any) { setError(e.message); }
    setSyncing(false);
  };

  const loadHistory = async (kw: string) => {
    setSelectedKw(kw);
    try {
      const r = await fetch(`${API_BASE}/rank-tracker/history?keyword=${encodeURIComponent(kw)}&days=${historyDays}`);
      const d = await r.json();
      setHistory(d.history || []);
    } catch { setHistory([]); }
  };

  const handleImportCsv = async () => {
    if (!csvText.trim()) return;
    try {
      const r = await fetch(`${API_BASE}/rank-tracker/import-csv`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ csv_text: csvText }),
      });
      const d = await r.json();
      setImportResult(`✅ Đã thêm ${d.added} keyword${d.skipped > 0 ? `, bỏ qua ${d.skipped}` : ""}`);
      setCsvText("");
      await fetchKeywords();
      await fetchTags();
    } catch (e: any) { setImportResult(`❌ Lỗi: ${e.message}`); }
  };

  const exportCsv = () => {
    window.open(`${API_BASE}/rank-tracker/export-csv`, "_blank");
  };

  const posColor = (pos: number | null) => {
    if (pos === null || pos === 0) return "var(--text-dim)";
    if (pos <= 3) return "#22c55e";
    if (pos <= 10) return "#3b82f6";
    if (pos <= 20) return "#f59e0b";
    return "#ef4444";
  };

  const changeIcon = (change: number | null) => {
    if (change === null) return <span style={{ color: "var(--text-dim)" }}>━</span>;
    if (change > 0) return <span style={{ color: "#22c55e" }}>▲{change}</span>;
    if (change < 0) return <span style={{ color: "#ef4444" }}>▼{Math.abs(change)}</span>;
    return <span style={{ color: "var(--text-dim)" }}>━ 0</span>;
  };

  return (
    <div className="rank-tracker">
      <div className="hint-box">
        📊 <strong>Theo dõi Keyword:</strong> Thêm từ khóa, phân nhóm bằng tag,
        đồng bộ GSC, import CSV, và xuất báo cáo.
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="rt-alerts">
          {alerts.map(a => (
            <div key={a.keyword} className={`rt-alert rt-alert-${a.severity}`}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              <span><strong>{a.keyword}</strong> tụt {a.drop} bậc (#{a.previous_position} → #{a.current_position})</span>
            </div>
          ))}
        </div>
      )}

      {/* Tag filter */}
      {tags.length > 0 && (
        <div className="rt-tags-row">
          <button className={`rt-tag-chip ${activeTag === "" ? "active" : ""}`}
            onClick={() => setActiveTag("")}>Tất cả</button>
          {tags.map(t => (
            <button key={t}
              className={`rt-tag-chip ${activeTag === t ? "active" : ""}`}
              onClick={() => setActiveTag(t)}>{t}</button>
          ))}
        </div>
      )}

      {/* Add keyword */}
      <div className="rt-add-row">
        <div className="input-wrap" style={{ flex: 1 }}>
          <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
          </svg>
          <input type="text" className="text-input" placeholder="Nhập từ khóa..."
            value={newKeyword} onChange={e => setNewKeyword(e.target.value)}
            onKeyDown={e => e.key === "Enter" && addKeyword()} />
        </div>
        <div className="input-wrap" style={{ width: 120 }}>
          <input type="text" className="text-input" placeholder="Tag..."
            value={newTag} onChange={e => setNewTag(e.target.value)}
            style={{ paddingLeft: 12 }} />
        </div>
        <button className="rt-btn rt-btn-add" onClick={addKeyword} disabled={loading || !newKeyword.trim()}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 5v14M5 12h14" /></svg>
          Thêm
        </button>
        <button className={`rt-btn rt-btn-sync ${syncing ? "syncing" : ""}`}
          onClick={syncRankings} disabled={syncing || keywords.length === 0}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
            className={syncing ? "spin-icon" : ""}>
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /><path d="M3 3v5h5" />
          </svg>
          {syncing ? "Đồng bộ..." : "Đồng bộ GSC"}
        </button>
        <button className="rt-btn" style={{ background: "rgba(245,158,11,0.12)", color: "#f59e0b", border: "1px solid rgba(245,158,11,0.2)" }}
          onClick={() => setShowImport(!showImport)}>
          📥 CSV
        </button>
        <button className="rt-btn" style={{ background: "rgba(34,197,94,0.12)", color: "#22c55e", border: "1px solid rgba(34,197,94,0.2)" }}
          onClick={exportCsv} disabled={keywords.length === 0}>
          📤 Export
        </button>
      </div>

      {/* CSV Import panel */}
      {showImport && (
        <div className="rt-import-panel">
          <textarea className="spin-textarea" rows={4} placeholder={`Dán CSV: keyword,tag\nmitsubishi xpander,xe\nbảng giá mitsubishi 2025,giá`}
            value={csvText} onChange={e => setCsvText(e.target.value)} />
          <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
            <button className="rt-btn rt-btn-add" onClick={handleImportCsv} disabled={!csvText.trim()}>Import</button>
            <button className="rt-btn" onClick={() => { setShowImport(false); setCsvText(""); setImportResult(""); }}
              style={{ background: "var(--surface2)", color: "var(--text)" }}>Đóng</button>
            {importResult && <span style={{ alignSelf: "center", fontSize: 13 }}>{importResult}</span>}
          </div>
        </div>
      )}

      {error && (
        <p className="error-msg" role="alert">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
          {error}
        </p>
      )}

      {/* Keywords table */}
      {keywords.length > 0 ? (
        <div className="rt-table-wrap">
          <table className="rt-table">
            <thead>
              <tr>
                <th>Từ khóa</th>
                <th>Tag</th>
                <th>Vị trí</th>
                <th>Thay đổi</th>
                <th>Clicks</th>
                <th>Hiển thị</th>
                <th>CTR</th>
                <th>Nguồn</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {keywords.map(kw => (
                <tr key={kw.keyword}
                  className={selectedKw === kw.keyword ? "rt-row-active" : ""}
                  onClick={() => loadHistory(kw.keyword)} style={{ cursor: "pointer" }}>
                  <td className="rt-kw-cell"><span className="rt-kw-text">{kw.keyword}</span></td>
                  <td>{kw.tag && <span className="rt-tag-badge">{kw.tag}</span>}</td>
                  <td>
                    <span className="rt-pos-badge" style={{ color: posColor(kw.position) }}>
                      {kw.position ? `#${kw.position}` : "—"}
                    </span>
                  </td>
                  <td className="rt-change">{changeIcon(kw.change)}</td>
                  <td>{kw.clicks}</td>
                  <td>{kw.impressions.toLocaleString()}</td>
                  <td>{kw.ctr > 0 ? `${kw.ctr}%` : "—"}</td>
                  <td>
                    <span className={`rt-source-badge ${kw.source}`}>
                      {kw.source === "gsc" ? "GSC" : kw.source === "pending" ? "Chờ" : kw.source}
                    </span>
                  </td>
                  <td>
                    <button className="rt-del-btn" onClick={e => { e.stopPropagation(); removeKeyword(kw.keyword); }} title="Xóa">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12" /></svg>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="rt-empty">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.3">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" />
          </svg>
          <p>Chưa có từ khóa nào. Thêm từ khóa hoặc import CSV.</p>
        </div>
      )}

      {/* History chart */}
      {selectedKw && (
        <div className="rt-chart-section">
          <div className="rt-chart-header">
            <h3 className="section-title">📈 Lịch sử: <em>{selectedKw}</em></h3>
            <div className="rt-days-selector">
              {[7, 14, 30, 90].map(d => (
                <button key={d} className={`rt-day-btn ${historyDays === d ? "active" : ""}`}
                  onClick={() => { setHistoryDays(d); loadHistory(selectedKw); }}>{d} ngày</button>
              ))}
            </div>
          </div>
          {history.length > 0 ? (
            <div className="rt-chart">
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={history} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="date" tick={{ fill: "var(--text-dim)", fontSize: 11 }} />
                  <YAxis reversed domain={[1, "auto"]} tick={{ fill: "var(--text-dim)", fontSize: 11 }}
                    label={{ value: "Vị trí", angle: -90, position: "insideLeft", fill: "var(--text-dim)", fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: "var(--glass)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
                    labelStyle={{ color: "var(--text-h)" }} />
                  <ReferenceLine y={10} stroke="rgba(245,158,11,0.3)" strokeDasharray="3 3" label={{ value: "Top 10", fill: "#f59e0b", fontSize: 10 }} />
                  <ReferenceLine y={3} stroke="rgba(34,197,94,0.3)" strokeDasharray="3 3" label={{ value: "Top 3", fill: "#22c55e", fontSize: 10 }} />
                  <Line type="monotone" dataKey="position" stroke="#8b5cf6" strokeWidth={2.5}
                    dot={{ fill: "#8b5cf6", r: 4 }} activeDot={{ r: 6, fill: "#a78bfa" }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="rt-no-history"><p>Chưa có dữ liệu. Nhấn <strong>Đồng bộ GSC</strong> để lấy dữ liệu.</p></div>
          )}
        </div>
      )}
    </div>
  );
}
