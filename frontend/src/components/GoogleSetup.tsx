import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function GoogleSetup() {
  const [gscClientId, setGscClientId] = useState(() => localStorage.getItem("gsc_client_id") || "");
  const [gscClientSecret, setGscClientSecret] = useState(() => localStorage.getItem("gsc_client_secret") || "");
  const [gscSiteUrl, setGscSiteUrl] = useState(() => localStorage.getItem("gsc_site_url") || "");
  const [ga4PropertyId, setGa4PropertyId] = useState(() => localStorage.getItem("ga4_property_id") || "");
  const [serpApiKey, setSerpApiKey] = useState(() => localStorage.getItem("serp_api_key") || "");
  const [pagespeedApiKey, setPagespeedApiKey] = useState(() => localStorage.getItem("pagespeed_api_key") || "");
  const [saved, setSaved] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
  const [healthStatus, setHealthStatus] = useState<any>(null);

  useEffect(() => {
    fetch(`${API}/health`).then(r => r.json()).then(setHealthStatus).catch(() => null);
  }, []);

  const handleSave = () => {
    localStorage.setItem("gsc_client_id", gscClientId);
    localStorage.setItem("gsc_client_secret", gscClientSecret);
    localStorage.setItem("gsc_site_url", gscSiteUrl);
    localStorage.setItem("ga4_property_id", ga4PropertyId);
    localStorage.setItem("serp_api_key", serpApiKey);
    localStorage.setItem("pagespeed_api_key", pagespeedApiKey);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const inputStyle = {
    width: "100%",
    padding: "10px 14px",
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(0,0,0,0.08)",
    borderRadius: 8,
    color: "#fff",
    fontSize: 13,
    marginTop: 4,
  };

  const labelStyle = {
    fontSize: 12,
    fontWeight: 600 as const,
    color: "rgba(255,255,255,0.7)",
    marginBottom: 2,
    display: "block" as const,
  };

  const sectionStyle = {
    background: "rgba(255,255,255,0.02)",
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    border: "1px solid rgba(0,0,0,0.05)",
  };

  return (
    <div>
      <h2 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-h)", marginBottom: 8 }}>
        ⚙️ Google API Setup
      </h2>
      <p style={{ fontSize: 13, color: "#6b7280", marginBottom: 20 }}>
        Cấu hình kết nối Google Search Console, GA4, và SerpAPI cho hệ thống.
      </p>

      {healthStatus && (
        <div style={{ ...sectionStyle, borderColor: "rgba(74,222,128,0.2)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ color: "#4ade80", fontSize: 16 }}>✅</span>
            <span style={{ color: "#4ade80", fontWeight: 600, fontSize: 13 }}>
              Backend v{healthStatus.version} — Phase {healthStatus.phase}
            </span>
          </div>
        </div>
      )}

      {/* GSC Section */}
      <div style={sectionStyle}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: "var(--text-h)", marginBottom: 12 }}>
          🔍 Google Search Console
        </h3>
        <div style={{ display: "grid", gap: 12 }}>
          <div>
            <label style={labelStyle}>Client ID</label>
            <input style={inputStyle} type="text" value={gscClientId} onChange={e => setGscClientId(e.target.value)} placeholder="xxx.apps.googleusercontent.com" />
          </div>
          <div>
            <label style={labelStyle}>Client Secret</label>
            <input style={inputStyle} type="password" value={gscClientSecret} onChange={e => setGscClientSecret(e.target.value)} placeholder="GOCSPX-xxx" />
          </div>
          <div>
            <label style={labelStyle}>Site URL</label>
            <input style={inputStyle} type="text" value={gscSiteUrl} onChange={e => setGscSiteUrl(e.target.value)} placeholder="https://yourdomain.com/" />
          </div>
        </div>
      </div>

      {/* GA4 Section */}
      <div style={sectionStyle}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: "var(--text-h)", marginBottom: 12 }}>
          📊 Google Analytics 4
        </h3>
        <div>
          <label style={labelStyle}>GA4 Property ID</label>
          <input style={inputStyle} type="text" value={ga4PropertyId} onChange={e => setGa4PropertyId(e.target.value)} placeholder="properties/123456789" />
        </div>
      </div>

      {/* SerpAPI Section */}
      <div style={sectionStyle}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: "var(--text-h)", marginBottom: 12 }}>
          🌐 SerpAPI
        </h3>
        <div>
          <label style={labelStyle}>API Key</label>
          <input style={inputStyle} type="password" value={serpApiKey} onChange={e => setSerpApiKey(e.target.value)} placeholder="xxx" />
        </div>
      </div>

      {/* PageSpeed Section */}
      <div style={sectionStyle}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: "var(--text-h)", marginBottom: 12 }}>
          ⚡ PageSpeed Insights (Core Web Vitals)
        </h3>
        <div>
          <label style={labelStyle}>API Key</label>
          <input style={inputStyle} type="password" value={pagespeedApiKey} onChange={e => setPagespeedApiKey(e.target.value)} placeholder="AIzaSy..." />
        </div>
      </div>

      {/* Save Button */}
      <button
        onClick={handleSave}
        style={{
          padding: "12px 28px",
          background: saved ? "rgba(74,222,128,0.15)" : "rgba(22,163,74,0.15)",
          border: `1px solid ${saved ? "rgba(74,222,128,0.3)" : "rgba(22,163,74,0.3)"}`,
          color: saved ? "#4ade80" : "#4ade80",
          fontSize: 14,
          fontWeight: 600,
          borderRadius: 10,
          cursor: "pointer",
        }}
      >
        {saved ? "✅ Đã lưu!" : "💾 Lưu cấu hình"}
      </button>

      <p style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", marginTop: 12 }}>
        💡 Cấu hình backend (.env): Đặt GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GSC_SITE_URL, GA4_PROPERTY_ID, SERPAPI_KEY, PAGESPEED_API_KEY
      </p>
    </div>
  );
}
