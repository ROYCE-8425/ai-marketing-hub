import { useState, useEffect, useCallback } from "react";
import { API_BASE } from "../lib/apiConfig";

interface CalendarItem {
  id: number;
  title: string;
  description: string;
  content_type: string;
  status: string;
  scheduled_date: string;
  author: string;
  keywords: string;
  priority: string;
}

interface Stats {
  total: number;
  draft: number;
  review: number;
  published: number;
  upcoming: number;
  overdue: number;
}

interface TopicSuggestion {
  title: string;
  description: string;
  content_type: string;
  priority: string;
  keywords: string;
}

const STATUS_META: Record<string, { label: string; color: string; bg: string }> = {
  draft: { label: "Nháp", color: "#94a3b8", bg: "rgba(148,163,184,0.12)" },
  review: { label: "Đang duyệt", color: "#f59e0b", bg: "rgba(245,158,11,0.12)" },
  published: { label: "Đã đăng", color: "#22c55e", bg: "rgba(34,197,94,0.12)" },
};

const PRIORITY_META: Record<string, { label: string; color: string }> = {
  high: { label: "Cao", color: "#ef4444" },
  medium: { label: "TB", color: "#f59e0b" },
  low: { label: "Thấp", color: "#3b82f6" },
};

const TYPE_LABELS: Record<string, string> = {
  blog: "📝 Blog", guide: "📚 Guide", comparison: "⚖️ So sánh",
  news: "📰 Tin tức", landing: "🎯 Landing", video: "🎬 Video",
};

export function ContentCalendar() {
  const [items, setItems] = useState<CalendarItem[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", content_type: "blog", scheduled_date: "", author: "", keywords: "", priority: "medium" });
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestLoading, setSuggestLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<TopicSuggestion[]>([]);
  const [editId, setEditId] = useState<number | null>(null);

  const fetchItems = useCallback(async () => {
    try {
      const params = statusFilter ? `?status=${statusFilter}` : "";
      const r = await fetch(`${API_BASE}/calendar/items${params}`);
      const d = await r.json();
      setItems(d.items || []);
    } catch { /* ignore */ }
  }, [statusFilter]);

  const fetchStats = async () => {
    try {
      const r = await fetch(`${API_BASE}/calendar/stats`);
      setStats(await r.json());
    } catch { /* ignore */ }
  };

  useEffect(() => { fetchItems(); fetchStats(); }, [fetchItems]);

  const handleAdd = async () => {
    if (!form.title.trim()) return;
    setLoading(true);
    await fetch(`${API_BASE}/calendar/add`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setForm({ title: "", description: "", content_type: "blog", scheduled_date: "", author: "", keywords: "", priority: "medium" });
    setShowForm(false);
    await fetchItems(); await fetchStats();
    setLoading(false);
  };

  const handleStatusChange = async (id: number, status: string) => {
    await fetch(`${API_BASE}/calendar/update`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, status }),
    });
    await fetchItems(); await fetchStats();
  };

  const handleDelete = async (id: number) => {
    await fetch(`${API_BASE}/calendar/delete`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    await fetchItems(); await fetchStats();
  };

  const handleSuggest = async () => {
    setSuggestLoading(true);
    try {
      const r = await fetch(`${API_BASE}/calendar/suggest-topics`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ niche: "ô tô", count: 5 }),
      });
      const d = await r.json();
      setSuggestions(d.topics || []);
    } catch { /* ignore */ }
    setSuggestLoading(false);
  };

  const addSuggestion = async (s: TopicSuggestion) => {
    await fetch(`${API_BASE}/calendar/add`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...s, scheduled_date: "" }),
    });
    setSuggestions(suggestions.filter(x => x.title !== s.title));
    await fetchItems(); await fetchStats();
  };

  return (
    <div className="geo-optimizer">
      <div className="hint-box">📅 <strong>Content Calendar:</strong> Lập lịch nội dung, theo dõi trạng thái, AI đề xuất chủ đề mới.</div>

      {/* Stats */}
      {stats && (
        <div className="spin-stats">
          <div className="spin-stat"><span className="spin-stat-label">Tổng</span><span className="spin-stat-value">{stats.total}</span></div>
          <div className="spin-stat"><span className="spin-stat-label">Nháp</span><span className="spin-stat-value" style={{ color: "#94a3b8" }}>{stats.draft}</span></div>
          <div className="spin-stat"><span className="spin-stat-label">Đang duyệt</span><span className="spin-stat-value" style={{ color: "#f59e0b" }}>{stats.review}</span></div>
          <div className="spin-stat"><span className="spin-stat-label">Đã đăng</span><span className="spin-stat-value" style={{ color: "#22c55e" }}>{stats.published}</span></div>
          {stats.overdue > 0 && <div className="spin-stat"><span className="spin-stat-label">Quá hạn</span><span className="spin-stat-value" style={{ color: "#ef4444" }}>{stats.overdue}</span></div>}
          {stats.upcoming > 0 && <div className="spin-stat"><span className="spin-stat-label">Sắp tới</span><span className="spin-stat-value" style={{ color: "#8b5cf6" }}>{stats.upcoming}</span></div>}
        </div>
      )}

      {/* Actions */}
      <div className="geo-actions" style={{ marginTop: 16 }}>
        <button className="rt-btn rt-btn-add" onClick={() => setShowForm(!showForm)}>➕ Thêm bài viết</button>
        <button className="rt-btn rt-btn-sync" onClick={handleSuggest} disabled={suggestLoading}>
          {suggestLoading ? "⏳ Đang tạo..." : "🤖 AI đề xuất chủ đề"}
        </button>
        <div className="spin-version-tabs">
          {["", "draft", "review", "published"].map(s => (
            <button key={s} className={`spin-version-tab ${statusFilter === s ? "active" : ""}`}
              onClick={() => setStatusFilter(s)}>
              {s ? STATUS_META[s]?.label : "Tất cả"}
            </button>
          ))}
        </div>
      </div>

      {/* Add form */}
      {showForm && (
        <div className="rt-import-panel" style={{ marginTop: 12 }}>
          <div className="geo-schema-form">
            <div className="input-group">
              <label className="input-label">Tiêu đề *</label>
              <input className="text-input" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} placeholder="Tên bài viết..." style={{ paddingLeft: 12 }} />
            </div>
            <div className="input-group">
              <label className="input-label">Loại</label>
              <select className="text-input" value={form.content_type} onChange={e => setForm({ ...form, content_type: e.target.value })} style={{ paddingLeft: 12 }}>
                {Object.entries(TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div className="input-group">
              <label className="input-label">Ngày đăng</label>
              <input type="date" className="text-input" value={form.scheduled_date} onChange={e => setForm({ ...form, scheduled_date: e.target.value })} style={{ paddingLeft: 12 }} />
            </div>
            <div className="input-group">
              <label className="input-label">Ưu tiên</label>
              <select className="text-input" value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })} style={{ paddingLeft: 12 }}>
                <option value="high">🔴 Cao</option><option value="medium">🟡 Trung bình</option><option value="low">🔵 Thấp</option>
              </select>
            </div>
            <div className="input-group" style={{ gridColumn: "1 / -1" }}>
              <label className="input-label">Mô tả</label>
              <input className="text-input" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Mô tả ngắn..." style={{ paddingLeft: 12 }} />
            </div>
            <div className="input-group">
              <label className="input-label">Keywords</label>
              <input className="text-input" value={form.keywords} onChange={e => setForm({ ...form, keywords: e.target.value })} placeholder="kw1, kw2" style={{ paddingLeft: 12 }} />
            </div>
            <div className="input-group">
              <label className="input-label">Tác giả</label>
              <input className="text-input" value={form.author} onChange={e => setForm({ ...form, author: e.target.value })} placeholder="Tên" style={{ paddingLeft: 12 }} />
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <button className="rt-btn rt-btn-add" onClick={handleAdd} disabled={loading || !form.title.trim()}>💾 Lưu</button>
            <button className="rt-btn" onClick={() => setShowForm(false)} style={{ background: "var(--surface2)", color: "var(--text)" }}>Hủy</button>
          </div>
        </div>
      )}

      {/* AI Suggestions */}
      {suggestions.length > 0 && (
        <div className="geo-faq-result" style={{ marginTop: 12 }}>
          <h3 className="section-title">🤖 AI đề xuất ({suggestions.length})</h3>
          <div className="geo-faq-list">
            {suggestions.map((s, i) => (
              <div key={i} className="geo-faq-item" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div className="geo-faq-q">{s.title}</div>
                  <div className="geo-faq-a">{s.description} · <em>{TYPE_LABELS[s.content_type] || s.content_type}</em> · Keywords: {s.keywords}</div>
                </div>
                <button className="rt-btn rt-btn-add" onClick={() => addSuggestion(s)} style={{ whiteSpace: "nowrap" }}>➕ Thêm</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Items list */}
      {items.length > 0 ? (
        <div className="rt-table-wrap" style={{ marginTop: 16 }}>
          <table className="rt-table">
            <thead><tr><th>Tiêu đề</th><th>Loại</th><th>Ngày</th><th>Ưu tiên</th><th>Trạng thái</th><th></th></tr></thead>
            <tbody>
              {items.map(item => {
                const st = STATUS_META[item.status] || STATUS_META.draft;
                const pr = PRIORITY_META[item.priority] || PRIORITY_META.medium;
                return (
                  <tr key={item.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: "var(--text-h)" }}>{item.title}</div>
                      {item.description && <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 2 }}>{item.description}</div>}
                    </td>
                    <td><span style={{ fontSize: 12 }}>{TYPE_LABELS[item.content_type] || item.content_type}</span></td>
                    <td style={{ fontSize: 12, whiteSpace: "nowrap" }}>{item.scheduled_date || "—"}</td>
                    <td><span style={{ color: pr.color, fontWeight: 700, fontSize: 12 }}>{pr.label}</span></td>
                    <td>
                      <select value={item.status} onChange={e => handleStatusChange(item.id, e.target.value)}
                        style={{ background: st.bg, color: st.color, border: `1px solid ${st.color}30`, borderRadius: 6, padding: "3px 8px", fontSize: 11, fontWeight: 700, fontFamily: "inherit", cursor: "pointer" }}>
                        <option value="draft">Nháp</option><option value="review">Đang duyệt</option><option value="published">Đã đăng</option>
                      </select>
                    </td>
                    <td>
                      <button className="rt-del-btn" onClick={() => handleDelete(item.id)} title="Xóa">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12" /></svg>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="rt-empty" style={{ marginTop: 20 }}>
          <p>Chưa có bài viết nào. Nhấn <strong>➕ Thêm bài viết</strong> hoặc <strong>🤖 AI đề xuất</strong>.</p>
        </div>
      )}
    </div>
  );
}
