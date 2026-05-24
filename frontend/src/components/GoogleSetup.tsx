import { useState, useEffect, useCallback } from "react";
import { API_BASE } from "../lib/apiConfig";

interface KeyStatus {
  configured: boolean;
  masked: string;
}

interface KeyInfo {
  id: string;
  label: string;
  group: string;
  icon: string;
  desc: string;
  placeholder: string;
  secret: boolean;
  docs?: string;
}

const KEYS: KeyInfo[] = [
  { id: "groq_api_key", label: "Groq API Key", group: "ai", icon: "", desc: "AI Engine — LLaMA 3.3 70B", placeholder: "gsk_xxx...", secret: true, docs: "https://console.groq.com/keys" },
  { id: "pagespeed_api_key", label: "PageSpeed API Key", group: "google", icon: "", desc: "Core Web Vitals — LCP, INP, CLS", placeholder: "AIzaSy...", secret: true },
  { id: "ga4_property_id", label: "GA4 Property ID", group: "google", icon: "", desc: "Google Analytics 4", placeholder: "534300482", secret: false },
  { id: "gsc_client_id", label: "OAuth Client ID", group: "google", icon: "", desc: "Google OAuth2 Client", placeholder: "xxx.apps.googleusercontent.com", secret: false },
  { id: "gsc_client_secret", label: "OAuth Client Secret", group: "google", icon: "", desc: "OAuth2 Secret", placeholder: "GOCSPX-xxx", secret: true },
  { id: "gsc_refresh_token", label: "OAuth Refresh Token", group: "google", icon: "", desc: "Duy trì kết nối GSC + GA4", placeholder: "1//0gxxx...", secret: true },
  { id: "gsc_site_url", label: "GSC Site URL", group: "google", icon: "", desc: "URL website trên Search Console", placeholder: "https://yourdomain.com", secret: false },
  { id: "dataforseo_login", label: "DataForSEO Login", group: "serp", icon: "", desc: "SERP & Backlink API", placeholder: "email@example.com", secret: false, docs: "https://app.dataforseo.com/" },
  { id: "dataforseo_password", label: "DataForSEO Password", group: "serp", icon: "", desc: "Mật khẩu API", placeholder: "xxx", secret: true },
  { id: "jwt_secret_key", label: "JWT Secret Key", group: "auth", icon: "", desc: "Khóa JWT authentication", placeholder: "your-secret-key", secret: true },
];

const GROUPS: Record<string, { label: string; color: string }> = {
  ai: { label: "AI Engine", color: "#8b5cf6" },
  google: { label: "Google APIs", color: "#16a34a" },
  serp: { label: "SERP & Backlinks", color: "#f59e0b" },
  auth: { label: "Bảo mật", color: "#059669" },
};

export default function GoogleSetup() {
  const [keys, setKeys] = useState<Record<string, KeyStatus>>({});
  const [editing, setEditing] = useState<string | null>(null);
  const [editVal, setEditVal] = useState("");
  const [visible, setVisible] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState("");
  const [health, setHealth] = useState<{ version: string; phase: number } | null>(null);

  const load = useCallback(async () => {
    try {
      const r = await fetch(`${API_BASE}/server-config`);
      if (r.ok) setKeys(await r.json());
    } catch { /* noop */ }
    try {
      const h = await fetch(`${API_BASE.replace(/\/api\/?$/, "")}/health`);
      if (h.ok) setHealth(await h.json());
    } catch { /* noop */ }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const configured = Object.values(keys).filter(v => v?.configured).length;
  const missing = KEYS.filter(k => !keys[k.id]?.configured);

  const save = async (id: string) => {
    if (!editVal.trim()) return;
    setSaving(true);
    try {
      const r = await fetch(`${API_BASE}/server-config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ [id]: editVal.trim() }),
      });
      const d = await r.json();
      if (d.status === "ok") {
        showToast(`✅ ${d.message}`);
        setEditing(null);
        setEditVal("");
        await load();
      } else {
        showToast(`❌ ${d.message}`);
      }
    } catch {
      showToast("❌ Không thể kết nối backend.");
    }
    setSaving(false);
  };

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 4000);
  };

  if (loading) return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 300, gap: 16 }}>
      <div className="loading-spinner" />
      <span style={{ color: "var(--text-s)", fontSize: 13 }}>Đang tải cấu hình server...</span>
    </div>
  );

  return (
    <div className="server-config-page">
      {/* Health badge */}
      {health && (
        <div className="sc-health-badge">
          <span className="sc-health-dot" />
          Backend v{health.version} — Phase {health.phase}
        </div>
      )}

      {/* Progress bar */}
      <div className="sc-summary">
        <div className="sc-summary-bar">
          <div className="sc-summary-fill" style={{ width: `${(configured / KEYS.length) * 100}%` }} />
        </div>
        <div className="sc-summary-text">
          <span className="sc-summary-count">{configured}/{KEYS.length}</span> API keys đã cấu hình
        </div>
      </div>

      {/* Warning */}
      {missing.length > 0 && (
        <div className="sc-warning-box">
          <div className="sc-warning-icon">!</div>
          <div className="sc-warning-content">
            <strong>Cảnh báo: {missing.length} key chưa cấu hình</strong>
            <p>Các tính năng sau sẽ không hoạt động:</p>
            <ul>
              {missing.map(k => (
                <li key={k.id}><span className="sc-warning-key">{k.label}</span> — {k.desc}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div className={`sc-toast ${toast.startsWith("✅") ? "sc-toast-ok" : "sc-toast-err"}`}>{toast}</div>
      )}

      {/* Groups */}
      {Object.entries(GROUPS).map(([gid, g]) => {
        const gKeys = KEYS.filter(k => k.group === gid);
        if (!gKeys.length) return null;
        const gOk = gKeys.filter(k => keys[k.id]?.configured).length;

        return (
          <div className="sc-group" key={gid}>
            <div className="sc-group-header" style={{ borderLeftColor: g.color }}>
              <span className="sc-group-title">{g.label}</span>
              <span className="sc-group-badge" style={{
                background: gOk === gKeys.length ? "rgba(16,185,129,0.15)" : "rgba(245,158,11,0.15)",
                color: gOk === gKeys.length ? "#10b981" : "#f59e0b",
              }}>{gOk}/{gKeys.length}</span>
            </div>

            {gKeys.map(k => {
              const s = keys[k.id];
              const ok = s?.configured;
              const isEdit = editing === k.id;
              const show = visible[k.id];

              return (
                <div className={`sc-key-card ${ok ? "sc-key-ok" : "sc-key-missing"}`} key={k.id}>
                  <div className="sc-key-top">
                    <div className="sc-key-info">
                      <div className="sc-key-name">
                        <span>{k.label}</span>
                        <span className={`sc-key-status ${ok ? "sc-status-ok" : "sc-status-missing"}`}>
                          {ok ? "Đã cấu hình" : "Chưa cấu hình"}
                        </span>
                      </div>
                      <p className="sc-key-desc">{k.desc}</p>
                    </div>
                    <div className="sc-key-actions">
                      {ok && !isEdit && k.secret && (
                        <button className="sc-btn sc-btn-ghost" onClick={() => setVisible(p => ({ ...p, [k.id]: !p[k.id] }))}>
                          {show ? "Ẩn" : "Hiện"}
                        </button>
                      )}
                      {!isEdit && (
                        <button className={`sc-btn ${ok ? "sc-btn-edit" : "sc-btn-add"}`}
                          onClick={() => { setEditing(k.id); setEditVal(""); }}>
                          {ok ? "Sửa" : "Thêm"}
                        </button>
                      )}
                      {k.docs && (
                        <a href={k.docs} target="_blank" rel="noopener noreferrer" className="sc-btn sc-btn-docs" title="Hướng dẫn">Docs</a>
                      )}
                    </div>
                  </div>

                  {ok && !isEdit && (
                    <div className="sc-key-value">
                      <code>{k.secret && !show ? "•".repeat(20) : s.masked}</code>
                    </div>
                  )}

                  {isEdit && (
                    <div className="sc-key-edit">
                      <input
                        className="sc-edit-input"
                        type={k.secret ? "password" : "text"}
                        value={editVal}
                        onChange={e => setEditVal(e.target.value)}
                        placeholder={k.placeholder}
                        autoFocus
                        onKeyDown={e => { if (e.key === "Enter") save(k.id); if (e.key === "Escape") setEditing(null); }}
                      />
                      <div className="sc-edit-btns">
                        <button className="sc-btn sc-btn-save" onClick={() => save(k.id)} disabled={saving || !editVal.trim()}>
                          {saving ? "Đang lưu..." : "Lưu"}
                        </button>
                        <button className="sc-btn sc-btn-cancel" onClick={() => setEditing(null)}>Hủy</button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        );
      })}

      <div className="sc-footer">
        <p>Các key được lưu trong file <code>.env</code> trên backend server. Thay đổi có hiệu lực ngay.</p>
        <p>Không chia sẻ API keys. Keys được mã hóa (masked) khi hiển thị.</p>
      </div>
    </div>
  );
}
