import { useState, useCallback } from "react";
import { API_BASE } from "../lib/apiConfig";

// ─── Types ─────────────────────────────────────────────────────────────────────

interface SchemaItem {
  type: string;
  status: string;       // "valid" | "warning" | "error"
  errors: string[];
  warnings: string[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
  raw: Record<string, any>;
}

interface ValidationResult {
  url?: string;
  schemas: SchemaItem[];
  total_schemas: number;
  valid_count: number;
  warning_count: number;
  error_count: number;
}

type InputMode = "url" | "paste";

// ─── Helpers ───────────────────────────────────────────────────────────────────

/** Schema type icon mapping */
function schemaIcon(type: string): string {
  const map: Record<string, string> = {
    Organization: "🏢",
    WebSite: "🌐",
    WebPage: "📄",
    Article: "📰",
    BlogPosting: "✍️",
    Product: "🛒",
    FAQPage: "❓",
    BreadcrumbList: "🔗",
    LocalBusiness: "📍",
    Person: "👤",
    Event: "📅",
    Review: "⭐",
    HowTo: "📋",
    Recipe: "🍳",
    VideoObject: "🎥",
    ImageObject: "🖼️",
    SoftwareApplication: "💻",
  };
  return map[type] || "📦";
}

/** Status color */
function statusColor(status: string): string {
  if (status === "valid") return "#7c3aed";
  if (status === "warning") return "#eab308";
  return "#ef4444";
}

/** Status Vietnamese label */
function statusLabel(status: string): string {
  if (status === "valid") return "Hợp lệ";
  if (status === "warning") return "Cảnh báo";
  return "Lỗi";
}

/** Simple client-side JSON-LD validation */
function validateJsonLdLocally(jsonStr: string): ValidationResult {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
  let parsed: any;
  try {
    parsed = JSON.parse(jsonStr);
  } catch {
    return {
      schemas: [{ type: "Unknown", status: "error", errors: ["JSON không hợp lệ — kiểm tra lại cú pháp"], warnings: [], raw: {} }],
      total_schemas: 0, valid_count: 0, warning_count: 0, error_count: 1,
    };
  }

  // Normalize: single object → array
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
  const items: any[] = Array.isArray(parsed) ? parsed : [parsed];
  const schemas: SchemaItem[] = items.map(item => {
    const errors: string[] = [];
    const warnings: string[] = [];
    const type = item["@type"] || "Unknown";

    // Basic checks
    if (!item["@context"]) errors.push("Thiếu @context (nên dùng https://schema.org)");
    if (!item["@type"]) errors.push("Thiếu @type");
    if (item["@context"] && !String(item["@context"]).includes("schema.org")) {
      warnings.push("@context không phải schema.org");
    }

    // Common required fields checks
    if (type === "Article" || type === "BlogPosting") {
      if (!item.headline) warnings.push("Thiếu headline");
      if (!item.author) warnings.push("Thiếu author");
      if (!item.datePublished) warnings.push("Thiếu datePublished");
    }
    if (type === "Product") {
      if (!item.name) errors.push("Thiếu name (bắt buộc)");
      if (!item.offers) warnings.push("Thiếu offers");
    }
    if (type === "Organization") {
      if (!item.name) errors.push("Thiếu name (bắt buộc)");
      if (!item.url) warnings.push("Thiếu url");
    }

    const status = errors.length > 0 ? "error" : warnings.length > 0 ? "warning" : "valid";
    return { type, status, errors, warnings, raw: item };
  });

  return {
    schemas,
    total_schemas: schemas.length,
    valid_count: schemas.filter(s => s.status === "valid").length,
    warning_count: schemas.filter(s => s.status === "warning").length,
    error_count: schemas.filter(s => s.status === "error").length,
  };
}

/** Syntax-highlight JSON string for display */
function highlightJson(json: string): string {
  return json
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"(\\u[a-fA-F0-9]{4}|\\[^u]|[^"\\])*"(\s*:)?/g, (match) => {
      let cls = "json-string";  // string value
      if (match.endsWith(":")) cls = "json-key";
      else if (/true|false/.test(match)) cls = "json-bool";
      else if (/null/.test(match)) cls = "json-null";
      return `<span class="${cls}">${match}</span>`;
    })
    .replace(/\b(\d+\.?\d*)\b/g, '<span class="json-number">$1</span>');
}

// ─── Inline styles matching dark glass theme ───────────────────────────────────

const panelStyle: React.CSSProperties = {
  background: "linear-gradient(145deg, rgba(255,255,255,0.85), rgba(255,255,255,0.6))",
  border: "1px solid rgba(139,92,246,0.1)",
  borderRadius: "var(--radius)",
  padding: 24,
  boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
  display: "flex",
  flexDirection: "column",
  gap: 16,
};

const summaryCard: React.CSSProperties = {
  background: "var(--surface2)",
  border: "1px solid var(--border)",
  borderRadius: "var(--radius-sm)",
  padding: "14px 16px",
  display: "flex",
  flexDirection: "column",
  gap: 4,
  flex: "1 1 0",
  minWidth: 120,
  alignItems: "center",
};

// ─── Component ─────────────────────────────────────────────────────────────────

export function SchemaValidator() {
  const [mode, setMode] = useState<InputMode>("url");
  const [url, setUrl] = useState("");
  const [jsonInput, setJsonInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [error, setError] = useState("");
  const [expandedSchema, setExpandedSchema] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);

  const handleValidate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (mode === "paste") {
      // Client-side validation
      if (!jsonInput.trim()) return;
      setLoading(true);
      // Small delay to show loading state
      await new Promise(r => setTimeout(r, 200));
      const res = validateJsonLdLocally(jsonInput.trim());
      setResult(res);
      setLoading(false);
      return;
    }

    // URL mode — call API
    if (!url.trim()) return;
    setLoading(true);
    try {
      const r = await fetch(`${API_BASE}/seo-tools/validate-schema`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
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

  const handleCopy = useCallback(() => {
    if (!result?.schemas?.length) return;
    const allJson = result.schemas.map(s => s.raw);
    const text = JSON.stringify(allJson.length === 1 ? allJson[0] : allJson, null, 2);
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [result]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fade-up 0.5s ease both" }}>
      {/* ── Input Form ── */}
      <form className="audit-form" onSubmit={handleValidate}>
        <div className="hint-box">
          📋 <strong>Xác thực Schema:</strong> Kiểm tra JSON-LD structured data từ URL hoặc dán JSON trực tiếp.
        </div>

        {/* Mode toggle */}
        <div style={{ display: "flex", gap: 8 }}>
          <div className="tab-bar">
            <button
              type="button"
              className={`tab-btn ${mode === "url" ? "tab-active" : ""}`}
              onClick={() => setMode("url")}
            >
              🌐 Từ URL
            </button>
            <button
              type="button"
              className={`tab-btn ${mode === "paste" ? "tab-active" : ""}`}
              onClick={() => setMode("paste")}
            >
              📝 Dán JSON-LD
            </button>
          </div>
        </div>

        {mode === "url" ? (
          <div className="input-row">
            <div className="input-group" style={{ flex: 1 }}>
              <label className="input-label">URL trang web</label>
              <div className="input-wrap">
                <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
                  <path d="M3.6 9h16.8M3.6 15h16.8" />
                </svg>
                <input
                  type="url" className="text-input" value={url}
                  onChange={e => setUrl(e.target.value)}
                  placeholder="https://example.com" required
                />
              </div>
            </div>
            <button
              className="analyze-btn" type="submit"
              disabled={loading || !url.trim()}
              style={{ alignSelf: "flex-end" }}
            >
              {loading ? <span className="btn-spinner" /> : "🔍 Xác thực"}
            </button>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div className="input-group">
              <label className="input-label">Dán JSON-LD</label>
              <textarea
                className="text-input"
                rows={8}
                value={jsonInput}
                onChange={e => setJsonInput(e.target.value)}
                placeholder='{\n  "@context": "https://schema.org",\n  "@type": "Article",\n  "headline": "...",\n  "author": { "@type": "Person", "name": "..." }\n}'
                style={{
                  paddingLeft: 14,
                  fontFamily: '"JetBrains Mono", "DM Mono", monospace',
                  fontSize: 12,
                  lineHeight: 1.6,
                  resize: "vertical",
                  minHeight: 120,
                }}
              />
            </div>
            <button
              className="analyze-btn" type="submit"
              disabled={loading || !jsonInput.trim()}
              style={{ alignSelf: "flex-start" }}
            >
              {loading ? <span className="btn-spinner" /> : "📋 Xác thực"}
            </button>
          </div>
        )}

        {error && <p className="error-msg">❌ {error}</p>}
      </form>

      {/* ── Results ── */}
      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: 20, animation: "fade-up 0.5s ease both" }}>
          {/* Summary cards */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
            <div style={summaryCard}>
              <span style={{ fontSize: 11, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600 }}>
                Schema phát hiện
              </span>
              <span style={{ fontSize: 22, fontWeight: 700, color: "var(--text-h)", fontFamily: '"DM Mono", monospace' }}>
                {result.total_schemas}
              </span>
            </div>
            <div style={summaryCard}>
              <span style={{ fontSize: 11, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600 }}>
                Hợp lệ
              </span>
              <span style={{ fontSize: 22, fontWeight: 700, color: "#7c3aed", fontFamily: '"DM Mono", monospace' }}>
                {result.valid_count}
              </span>
            </div>
            <div style={summaryCard}>
              <span style={{ fontSize: 11, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600 }}>
                Cảnh báo
              </span>
              <span style={{ fontSize: 22, fontWeight: 700, color: "#eab308", fontFamily: '"DM Mono", monospace' }}>
                {result.warning_count}
              </span>
            </div>
            <div style={summaryCard}>
              <span style={{ fontSize: 11, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600 }}>
                Lỗi
              </span>
              <span style={{ fontSize: 22, fontWeight: 700, color: "#ef4444", fontFamily: '"DM Mono", monospace' }}>
                {result.error_count}
              </span>
            </div>
          </div>

          {/* Copy button */}
          {result.schemas.length > 0 && (
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button type="button" className="reset-btn" onClick={handleCopy}>
                {copied ? "✅ Đã sao chép!" : "📋 Sao chép JSON"}
              </button>
            </div>
          )}

          {/* Schema items */}
          {result.schemas.map((schema, i) => (
            <div key={i} style={panelStyle}>
              {/* Header */}
              <div
                style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  cursor: "pointer", gap: 12,
                }}
                onClick={() => setExpandedSchema(expandedSchema === i ? null : i)}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 22 }}>{schemaIcon(schema.type)}</span>
                  <div>
                    <span style={{ fontSize: 15, fontWeight: 700, color: "var(--text-h)" }}>
                      {schema.type}
                    </span>
                    {schema.errors.length > 0 && (
                      <span style={{ fontSize: 11, color: "#ef4444", marginLeft: 8 }}>
                        {schema.errors.length} lỗi
                      </span>
                    )}
                    {schema.warnings.length > 0 && (
                      <span style={{ fontSize: 11, color: "#eab308", marginLeft: 8 }}>
                        {schema.warnings.length} cảnh báo
                      </span>
                    )}
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{
                    display: "inline-flex", alignItems: "center", gap: 5,
                    fontSize: 12, fontWeight: 600, padding: "4px 12px",
                    borderRadius: 99, border: "1px solid",
                    background: `${statusColor(schema.status)}12`,
                    color: statusColor(schema.status),
                    borderColor: `${statusColor(schema.status)}40`,
                  }}>
                    <span style={{
                      width: 6, height: 6, borderRadius: "50%",
                      background: statusColor(schema.status),
                    }} />
                    {statusLabel(schema.status)}
                  </span>
                  <span style={{ color: "var(--text-dim)", fontSize: 12 }}>
                    {expandedSchema === i ? "▲" : "▼"}
                  </span>
                </div>
              </div>

              {/* Expanded details */}
              {expandedSchema === i && (
                <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 4 }}>
                  {/* Errors */}
                  {schema.errors.length > 0 && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                      {schema.errors.map((err, j) => (
                        <div key={j} style={{
                          display: "flex", alignItems: "center", gap: 8,
                          fontSize: 13, color: "#ef4444",
                          background: "rgba(239,68,68,0.06)", padding: "8px 12px",
                          borderRadius: "var(--radius-sm)",
                          border: "1px solid rgba(239,68,68,0.2)",
                        }}>
                          🔴 {err}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Warnings */}
                  {schema.warnings.length > 0 && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                      {schema.warnings.map((warn, j) => (
                        <div key={j} style={{
                          display: "flex", alignItems: "center", gap: 8,
                          fontSize: 13, color: "#eab308",
                          background: "rgba(234,179,8,0.06)", padding: "8px 12px",
                          borderRadius: "var(--radius-sm)",
                          border: "1px solid rgba(234,179,8,0.2)",
                        }}>
                          🟡 {warn}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* JSON preview */}
                  <div style={{
                    background: "rgba(0,0,0,0.3)", borderRadius: "var(--radius-sm)",
                    padding: 16, overflow: "auto", maxHeight: 300,
                    border: "1px solid var(--border)",
                  }}>
                    <pre
                      style={{
                        margin: 0, fontSize: 12, lineHeight: 1.6,
                        fontFamily: '"JetBrains Mono", "DM Mono", monospace',
                        color: "var(--text)",
                        whiteSpace: "pre-wrap", wordBreak: "break-all",
                      }}
                      dangerouslySetInnerHTML={{
                        __html: highlightJson(JSON.stringify(schema.raw, null, 2)),
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          ))}

          {result.schemas.length === 0 && (
            <div style={{
              ...panelStyle,
              textAlign: "center",
              color: "var(--text-dim)", fontSize: 14,
              padding: 40,
            }}>
              📭 Không tìm thấy JSON-LD structured data trên trang này
            </div>
          )}
        </div>
      )}

      {/* JSON syntax highlight inline styles */}
      <style>{`
        .json-key   { color: #7c3aed; }
        .json-string { color: #10b981; }
        .json-number { color: #f59e0b; }
        .json-bool   { color: #7c3aed; }
        .json-null   { color: #ef4444; }
      `}</style>
    </div>
  );
}
