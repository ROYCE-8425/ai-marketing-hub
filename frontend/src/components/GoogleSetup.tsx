import { useState, useEffect, useCallback } from "react";
import { API_BASE } from "../lib/apiConfig";

// Key configuration definition
interface KeyInfo {
  id: string;
  label: string;
  group: string;
  icon: string;
  description: string;
  placeholder: string;
  isSecret: boolean;
  docsUrl?: string;
}

interface KeyStatus {
  configured: boolean;
  masked: string;
}

const KEY_CONFIGS: KeyInfo[] = [
  {
    id: "groq_api_key",
    label: "Groq API Key",
    group: "ai",
    icon: "🤖",
    description: "AI Engine — LLaMA 3.3 70B cho viết bài, phân tích từ khóa, lập kế hoạch nội dung",
    placeholder: "gsk_xxx...",
    isSecret: true,
    docsUrl: "https://console.groq.com/keys",
  },
  {
    id: "pagespeed_api_key",
    label: "PageSpeed Insights API Key",
    group: "google",
    icon: "⚡",
    description: "Core Web Vitals — Kiểm tra LCP, INP, CLS, Lighthouse scores",
    placeholder: "AIzaSy...",
    isSecret: true,
    docsUrl: "https://developers.google.com/speed/docs/insights/v5/get-started",
  },
  {
    id: "ga4_property_id",
    label: "GA4 Property ID",
    group: "google",
    icon: "📊",
    description: "Google Analytics 4 — Theo dõi sessions, users, pageviews, traffic sources",
    placeholder: "534300482",
    isSecret: false,
  },
  {
    id: "gsc_client_id",
    label: "Google OAuth Client ID",
    group: "google",
    icon: "🔑",
    description: "OAuth2 Client — Xác thực Google Search Console + GA4",
    placeholder: "xxx.apps.googleusercontent.com",
    isSecret: false,
  },
  {
    id: "gsc_client_secret",
    label: "Google OAuth Client Secret",
    group: "google",
    icon: "🔐",
    description: "OAuth2 Secret — Kết hợp với Client ID để xác thực",
    placeholder: "GOCSPX-xxx",
    isSecret: true,
  },
  {
    id: "gsc_refresh_token",
    label: "Google OAuth Refresh Token",
    group: "google",
    icon: "🔄",
    description: "OAuth2 Refresh Token — Duy trì kết nối GSC + GA4 không cần đăng nhập lại",
    placeholder: "1//0gxxx...",
    isSecret: true,
  },
  {
    id: "gsc_site_url",
    label: "GSC Site URL",
    group: "google",
    icon: "🌐",
    description: "URL website đã xác minh trên Google Search Console",
    placeholder: "https://yourdomain.com",
    isSecret: false,
  },
  {
    id: "dataforseo_login",
    label: "DataForSEO Login",
    group: "serp",
    icon: "🔍",
    description: "SERP Live + Backlink analysis — Tra cứu kết quả tìm kiếm real-time",
    placeholder: "email@example.com",
    isSecret: false,
    docsUrl: "https://app.dataforseo.com/",
  },
  {
    id: "dataforseo_password",
    label: "DataForSEO Password",
    group: "serp",
    icon: "🔒",
    description: "Mật khẩu API DataForSEO",
    placeholder: "xxx",
    isSecret: true,
  },
  {
    id: "jwt_secret_key",
    label: "JWT Secret Key",
    group: "auth",
    icon: "🛡️",
    description: "Khóa bí mật cho JWT authentication — Mã hóa access token & refresh token",
    placeholder: "your-secret-key-here",
    isSecret: true,
  },
];

const GROUPS = [
  { id: "ai", label: "🤖 AI Engine", color: "#a78bfa" },
  { id: "google", label: "🔗 Google APIs", color: "#06b6d4" },
  { id: "serp", label: "🔍 SERP & Backlinks", color: "#f59e0b" },
  { id: "auth", label: "🛡️ Bảo mật", color: "#10b981" },
];

export default function GoogleSetup() {
  const [serverKeys, setServerKeys] = useState<Record<string, KeyStatus>>({});
  const [editValues, setEditValues] = useState<Record<string, string>>({});
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [showSecret, setShowSecret] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState("");
  const [healthStatus, setHealthStatus] = useState<{ version: string; phase: number } | null>(null);

  const fetchConfig = useCallback(async () => {
    try {
      const [configRes, healthRes] = await Promise.all([
        fetch(`${API_BASE}/api/server-config`),
        fetch(`${API_BASE}/health`),
      ]);
      if (configRes.ok) {
        const data = await configRes.json();
        setServerKeys(data);
      }
      if (healthRes.ok) {
        setHealthStatus(await healthRes.json());
      }
    } catch {
      // Backend unavailable
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const configuredCount = Object.values(serverKeys).filter((v) => v?.configured).length;
  const totalCount = KEY_CONFIGS.length;
  const missingKeys = KEY_CONFIGS.filter((k) => !serverKeys[k.id]?.configured);

  const handleEdit = (keyId: string) => {
    setEditingKey(keyId);
    setEditValues((prev) => ({ ...prev, [keyId]: "" }));
  };

  const handleCancel = () => {
    setEditingKey(null);
  };

  const handleSave = async (keyId: string) => {
    const value = editValues[keyId];
    if (!value?.trim()) return;

    setSaving(true);
    setSaveMsg("");
    try {
      const res = await fetch(`${API_BASE}/api/server-config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ [keyId]: value.trim() }),
      });
      const data = await res.json();
      if (data.status === "ok") {
        setSaveMsg(`✅ ${data.message}`);
        setEditingKey(null);
        setEditValues((prev) => ({ ...prev, [keyId]: "" }));
        await fetchConfig();
      } else {
        setSaveMsg(`❌ ${data.message}`);
      }
    } catch {
      setSaveMsg("❌ Không thể kết nối backend.");
    } finally {
      setSaving(false);
      setTimeout(() => setSaveMsg(""), 4000);
    }
  };

  const toggleShowSecret = (keyId: string) => {
    setShowSecret((prev) => ({ ...prev, [keyId]: !prev[keyId] }));
  };

  if (loading) {
    return (
      <div className="server-config-loading">
        <div className="loading-spinner" />
        <p>Đang tải cấu hình server...</p>
      </div>
    );
  }

  return (
    <div className="server-config-page">
      {/* Header */}
      <div className="sc-header">
        <div className="sc-header-left">
          <h2>⚙️ Cấu hình Server</h2>
          <p>Quản lý API keys và kết nối dịch vụ bên ngoài cho hệ thống AI Marketing Hub</p>
        </div>
        {healthStatus && (
          <div className="sc-health-badge">
            <span className="sc-health-dot" />
            Backend v{healthStatus.version} — Phase {healthStatus.phase}
          </div>
        )}
      </div>

      {/* Status Summary */}
      <div className="sc-summary">
        <div className="sc-summary-bar">
          <div className="sc-summary-fill" style={{ width: `${(configuredCount / totalCount) * 100}%` }} />
        </div>
        <div className="sc-summary-text">
          <span className="sc-summary-count">{configuredCount}/{totalCount}</span> API keys đã cấu hình
        </div>
      </div>

      {/* Warnings for missing keys */}
      {missingKeys.length > 0 && (
        <div className="sc-warning-box">
          <div className="sc-warning-icon">⚠️</div>
          <div className="sc-warning-content">
            <strong>Cảnh báo: {missingKeys.length} key chưa được cấu hình</strong>
            <p>Các tính năng sau sẽ không hoạt động:</p>
            <ul>
              {missingKeys.map((k) => (
                <li key={k.id}>
                  <span className="sc-warning-key">{k.icon} {k.label}</span> — {k.description.split("—")[0]}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Save message toast */}
      {saveMsg && (
        <div className={`sc-toast ${saveMsg.startsWith("✅") ? "sc-toast-ok" : "sc-toast-err"}`}>
          {saveMsg}
        </div>
      )}

      {/* Key Groups */}
      {GROUPS.map((group) => {
        const groupKeys = KEY_CONFIGS.filter((k) => k.group === group.id);
        if (groupKeys.length === 0) return null;
        const groupConfigured = groupKeys.filter((k) => serverKeys[k.id]?.configured).length;

        return (
          <div className="sc-group" key={group.id}>
            <div className="sc-group-header" style={{ borderLeftColor: group.color }}>
              <span className="sc-group-title">{group.label}</span>
              <span className="sc-group-badge" style={{ background: groupConfigured === groupKeys.length ? "rgba(16,185,129,0.15)" : "rgba(245,158,11,0.15)", color: groupConfigured === groupKeys.length ? "#10b981" : "#f59e0b" }}>
                {groupConfigured}/{groupKeys.length}
              </span>
            </div>

            {groupKeys.map((keyInfo) => {
              const status = serverKeys[keyInfo.id];
              const isConfigured = status?.configured;
              const isEditing = editingKey === keyInfo.id;
              const isVisible = showSecret[keyInfo.id];

              return (
                <div className={`sc-key-card ${isConfigured ? "sc-key-ok" : "sc-key-missing"}`} key={keyInfo.id}>
                  <div className="sc-key-top">
                    <div className="sc-key-info">
                      <div className="sc-key-name">
                        <span className="sc-key-icon">{keyInfo.icon}</span>
                        <span>{keyInfo.label}</span>
                        <span className={`sc-key-status ${isConfigured ? "sc-status-ok" : "sc-status-missing"}`}>
                          {isConfigured ? "✅ Đã cấu hình" : "❌ Chưa cấu hình"}
                        </span>
                      </div>
                      <p className="sc-key-desc">{keyInfo.description}</p>
                    </div>
                    <div className="sc-key-actions">
                      {isConfigured && !isEditing && (
                        <>
                          {keyInfo.isSecret && (
                            <button className="sc-btn sc-btn-ghost" onClick={() => toggleShowSecret(keyInfo.id)} title={isVisible ? "Ẩn" : "Hiển thị"}>
                              {isVisible ? "🙈" : "👁️"}
                            </button>
                          )}
                          <button className="sc-btn sc-btn-edit" onClick={() => handleEdit(keyInfo.id)}>
                            ✏️ Sửa
                          </button>
                        </>
                      )}
                      {!isConfigured && !isEditing && (
                        <button className="sc-btn sc-btn-add" onClick={() => handleEdit(keyInfo.id)}>
                          ➕ Thêm
                        </button>
                      )}
                      {keyInfo.docsUrl && (
                        <a href={keyInfo.docsUrl} target="_blank" rel="noopener noreferrer" className="sc-btn sc-btn-docs" title="Hướng dẫn lấy key">
                          📖
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Current value display */}
                  {isConfigured && !isEditing && (
                    <div className="sc-key-value">
                      <code>{keyInfo.isSecret && !isVisible ? "•".repeat(Math.min(20, status.masked.length || 20)) : status.masked}</code>
                    </div>
                  )}

                  {/* Edit form */}
                  {isEditing && (
                    <div className="sc-key-edit">
                      <input
                        className="sc-edit-input"
                        type={keyInfo.isSecret ? "password" : "text"}
                        value={editValues[keyInfo.id] || ""}
                        onChange={(e) => setEditValues((prev) => ({ ...prev, [keyInfo.id]: e.target.value }))}
                        placeholder={keyInfo.placeholder}
                        autoFocus
                        onKeyDown={(e) => { if (e.key === "Enter") handleSave(keyInfo.id); if (e.key === "Escape") handleCancel(); }}
                      />
                      <div className="sc-edit-btns">
                        <button className="sc-btn sc-btn-save" onClick={() => handleSave(keyInfo.id)} disabled={saving || !editValues[keyInfo.id]?.trim()}>
                          {saving ? "⏳" : "💾"} Lưu
                        </button>
                        <button className="sc-btn sc-btn-cancel" onClick={handleCancel}>
                          Hủy
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        );
      })}

      {/* Footer note */}
      <div className="sc-footer">
        <p>💡 Các key được lưu trong file <code>.env</code> trên backend server. Thay đổi có hiệu lực ngay lập tức.</p>
        <p>⚠️ Không chia sẻ API keys cho người khác. Keys được mã hóa (masked) khi hiển thị.</p>
      </div>
    </div>
  );
}
