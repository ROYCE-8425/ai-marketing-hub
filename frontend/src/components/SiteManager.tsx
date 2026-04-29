import { useState, useEffect } from "react";
import { API_BASE } from "../lib/apiConfig";

interface Site {
  id: number;
  name: string;
  url: string;
  description: string;
  niche: string;
  is_active: number;
  last_scan_score: number;
  last_scan_date: string;
}

export function SiteManager() {
  const [sites, setSites] = useState<Site[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", url: "", description: "", niche: "" });
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState<number | null>(null);

  const fetchSites = async () => {
    try {
      const r = await fetch(`${API_BASE}/sites/list`);
      const d = await r.json();
      setSites(d.sites || []);
    } catch { /* ignore */ }
  };

  useEffect(() => { fetchSites(); }, []);

  const handleAdd = async () => {
    if (!form.name.trim() || !form.url.trim()) return;
    setLoading(true);
    await fetch(`${API_BASE}/sites/add`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setForm({ name: "", url: "", description: "", niche: "" });
    setShowForm(false);
    await fetchSites();
    setLoading(false);
  };

  const handleRemove = async (id: number) => {
    await fetch(`${API_BASE}/sites/remove`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    await fetchSites();
  };

  const handleSetActive = async (id: number) => {
    await fetch(`${API_BASE}/sites/set-active`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    await fetchSites();
  };

  const handleQuickScan = async (site: Site) => {
    setScanning(site.id);
    try {
      const r = await fetch(`${API_BASE}/tech-seo/scan`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: site.url }),
      });
      const d = await r.json();
      if (d.score !== undefined) {
        // Refresh to show updated score
        await fetchSites();
      }
    } catch { /* ignore */ }
    setScanning(null);
  };

  const scoreColor = (s: number) => {
    if (s >= 80) return "#22c55e";
    if (s >= 60) return "#3b82f6";
    if (s >= 40) return "#f59e0b";
    return "#ef4444";
  };

  return (
    <div className="geo-optimizer">
      <div className="hint-box">🏢 <strong>Multi-site Manager:</strong> Quản lý nhiều website, chuyển đổi nhanh giữa các site.</div>

      <div className="geo-actions" style={{ marginTop: 16 }}>
        <button className="rt-btn rt-btn-add" onClick={() => setShowForm(!showForm)}>➕ Thêm website</button>
      </div>

      {showForm && (
        <div className="rt-import-panel" style={{ marginTop: 12 }}>
          <div className="geo-schema-form">
            <div className="input-group">
              <label className="input-label">Tên website *</label>
              <input className="text-input" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Mitsubishi Bình Phước" style={{ paddingLeft: 12 }} />
            </div>
            <div className="input-group">
              <label className="input-label">URL *</label>
              <input className="text-input" value={form.url} onChange={e => setForm({ ...form, url: e.target.value })} placeholder="https://example.com" style={{ paddingLeft: 12 }} />
            </div>
            <div className="input-group">
              <label className="input-label">Mô tả</label>
              <input className="text-input" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Mô tả ngắn..." style={{ paddingLeft: 12 }} />
            </div>
            <div className="input-group">
              <label className="input-label">Ngành</label>
              <input className="text-input" value={form.niche} onChange={e => setForm({ ...form, niche: e.target.value })} placeholder="ô tô, bất động sản..." style={{ paddingLeft: 12 }} />
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <button className="rt-btn rt-btn-add" onClick={handleAdd} disabled={loading || !form.name.trim() || !form.url.trim()}>💾 Lưu</button>
            <button className="rt-btn" onClick={() => setShowForm(false)} style={{ background: "var(--surface2)", color: "var(--text)" }}>Hủy</button>
          </div>
        </div>
      )}

      {/* Site cards */}
      {sites.length > 0 ? (
        <div className="site-cards" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 12, marginTop: 16 }}>
          {sites.map(site => (
            <div key={site.id} className="geo-faq-item" style={{
              borderLeft: site.is_active ? "3px solid #8b5cf6" : "3px solid var(--border)",
              position: "relative",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <div style={{ fontWeight: 700, color: "var(--text-h)", fontSize: 15, display: "flex", alignItems: "center", gap: 6 }}>
                    {site.name}
                    {site.is_active === 1 && <span style={{ fontSize: 10, background: "#8b5cf6", color: "#fff", padding: "1px 6px", borderRadius: 4, fontWeight: 700 }}>ACTIVE</span>}
                  </div>
                  <a href={site.url} target="_blank" rel="noopener noreferrer" style={{ color: "#3b82f6", fontSize: 12, textDecoration: "none" }}>{site.url}</a>
                  {site.description && <p style={{ fontSize: 12, color: "var(--text-dim)", margin: "4px 0 0" }}>{site.description}</p>}
                  {site.niche && <span className="rt-tag-badge" style={{ marginTop: 4 }}>{site.niche}</span>}
                </div>
                {site.last_scan_score > 0 && (
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 24, fontWeight: 800, color: scoreColor(site.last_scan_score) }}>{site.last_scan_score}</div>
                    <div style={{ fontSize: 10, color: "var(--text-dim)" }}>SEO Score</div>
                  </div>
                )}
              </div>
              <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
                {site.is_active !== 1 && (
                  <button className="rt-btn" style={{ fontSize: 11, padding: "4px 10px", background: "rgba(139,92,246,0.12)", color: "#8b5cf6", border: "1px solid rgba(139,92,246,0.2)" }}
                    onClick={() => handleSetActive(site.id)}>⭐ Set Active</button>
                )}
                <button className="rt-btn" style={{ fontSize: 11, padding: "4px 10px", background: "rgba(34,197,94,0.12)", color: "#22c55e", border: "1px solid rgba(34,197,94,0.2)" }}
                  onClick={() => handleQuickScan(site)} disabled={scanning === site.id}>
                  {scanning === site.id ? "⏳ Scanning..." : "🔍 Quick Scan"}
                </button>
                <button className="rt-del-btn" onClick={() => handleRemove(site.id)} title="Xóa" style={{ marginLeft: "auto" }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12" /></svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="rt-empty" style={{ marginTop: 20 }}>
          <p>Chưa có website nào. Nhấn <strong>➕ Thêm website</strong> để bắt đầu.</p>
        </div>
      )}
    </div>
  );
}
