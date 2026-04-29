import { useState } from "react";
import { API_BASE } from "../lib/apiConfig";

interface GeoBreakdown {
  score: number;
  max: number;
  details: {
    recommendations: string[];
    [key: string]: any;
  };
}

interface GeoResult {
  url: string;
  keyword: string;
  geo_score: number;
  grade: string;
  grade_label: string;
  breakdown: {
    schema: GeoBreakdown;
    structure: GeoBreakdown;
    eeat: GeoBreakdown;
    multimodal: GeoBreakdown;
    ai_visibility: GeoBreakdown;
  };
  recommendations: { category: string; recommendation: string }[];
  total_recommendations: number;
}

interface FaqItem {
  question: string;
  answer: string;
}

interface FaqResult {
  faqs: FaqItem[];
  schema_code: string;
  total_faqs: number;
}

const CATEGORY_META: Record<string, { icon: string; label: string; color: string }> = {
  schema: { icon: "🏗️", label: "Schema & Dữ liệu cấu trúc", color: "#8b5cf6" },
  structure: { icon: "📐", label: "Cấu trúc nội dung", color: "#3b82f6" },
  eeat: { icon: "🛡️", label: "E-E-A-T (Uy tín)", color: "#22c55e" },
  multimodal: { icon: "🖼️", label: "Đa phương tiện", color: "#f59e0b" },
  ai_visibility: { icon: "🤖", label: "AI Visibility", color: "#ec4899" },
};

export function GeoOptimizer() {
  const [url, setUrl] = useState("https://binhphuocmitsubishi.com");
  const [keyword, setKeyword] = useState("mitsubishi bình phước");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GeoResult | null>(null);
  const [error, setError] = useState("");

  // FAQ generator state
  const [faqLoading, setFaqLoading] = useState(false);
  const [faqResult, setFaqResult] = useState<FaqResult | null>(null);
  const [faqError, setFaqError] = useState("");
  const [showSchemaCode, setShowSchemaCode] = useState(false);
  const [codeCopied, setCodeCopied] = useState(false);

  // Schema generator state
  const [showSchemaGen, setShowSchemaGen] = useState(false);
  const [schemaForm, setSchemaForm] = useState({
    name: "Mitsubishi Bình Phước",
    address: "Quốc lộ 14, P. Tân Bình, TP. Đồng Xoài, Bình Phước",
    phone: "0707 199 279",
    url: "https://binhphuocmitsubishi.com",
    business_type: "AutoDealer",
  });
  const [schemaCode, setSchemaCode] = useState("");

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const r = await fetch(`${API_BASE}/geo/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), keyword: keyword.trim() }),
      });
      const d = await r.json();
      if (d.error) setError(d.error);
      else setResult(d);
    } catch (e: any) {
      setError(e.message || "Lỗi kết nối");
    }
    setLoading(false);
  };

  const handleGenerateFaq = async () => {
    setFaqLoading(true);
    setFaqError("");
    setFaqResult(null);
    try {
      const r = await fetch(`${API_BASE}/geo/generate-faq`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      const d = await r.json();
      if (d.error) setFaqError(d.error);
      else setFaqResult(d);
    } catch (e: any) {
      setFaqError(e.message || "Lỗi");
    }
    setFaqLoading(false);
  };

  const handleGenerateSchema = async () => {
    try {
      const r = await fetch(`${API_BASE}/geo/generate-schema`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(schemaForm),
      });
      const d = await r.json();
      if (d.schema_code) setSchemaCode(d.schema_code);
    } catch { /* ignore */ }
  };

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCodeCopied(true);
    setTimeout(() => setCodeCopied(false), 2000);
  };

  const gradeColor = (grade: string) => {
    switch (grade) {
      case "A": return "#22c55e";
      case "B": return "#3b82f6";
      case "C": return "#f59e0b";
      case "D": return "#ef4444";
      default: return "#ef4444";
    }
  };

  return (
    <div className="geo-optimizer">
      <form className="audit-form" onSubmit={handleAnalyze}>
        <div className="hint-box">
          🤖 <strong>GEO — Generative Engine Optimization:</strong> Kiểm tra mức độ
          "AI-friendly" + tạo FAQ Schema + LocalBusiness Schema cho website.
        </div>

        <div className="input-row">
          <div className="input-group" style={{ flex: 2 }}>
            <label className="input-label">URL trang web</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
                <path d="M3.6 9h16.8M3.6 15h16.8" />
              </svg>
              <input type="url" className="text-input" placeholder="https://example.com"
                value={url} onChange={e => setUrl(e.target.value)} required />
            </div>
          </div>

          <div className="input-group" style={{ flex: 1 }}>
            <label className="input-label">Từ khóa chính</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
              </svg>
              <input type="text" className="text-input" placeholder="từ khóa..."
                value={keyword} onChange={e => setKeyword(e.target.value)} />
            </div>
          </div>

          <button className={`submit-btn ${loading ? "loading" : ""}`}
            type="submit" disabled={loading || !url.trim()} style={{ alignSelf: "flex-end" }}>
            {loading ? (
              <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="spin-icon">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /></svg> Đang phân tích...</>
            ) : (
              <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" /></svg> Phân tích GEO</>
            )}
          </button>
        </div>

        {error && <p className="error-msg" role="alert">{error}</p>}
      </form>

      {result && (
        <div className="geo-result">
          {/* Score hero */}
          <div className="geo-score-hero">
            <div className="geo-score-ring">
              <svg viewBox="0 0 120 120" width="140" height="140">
                <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
                <circle cx="60" cy="60" r="52" fill="none" stroke={gradeColor(result.grade)}
                  strokeWidth="8" strokeLinecap="round"
                  strokeDasharray={`${(result.geo_score / 100) * 327} 327`}
                  transform="rotate(-90 60 60)" style={{ transition: "stroke-dasharray 1s ease" }} />
              </svg>
              <div className="geo-score-inner">
                <span className="geo-score-num">{result.geo_score}</span>
                <span className="geo-score-max">/100</span>
              </div>
            </div>
            <div className="geo-score-info">
              <span className="geo-grade" style={{ color: gradeColor(result.grade) }}>{result.grade}</span>
              <span className="geo-grade-label">{result.grade_label}</span>
              <p className="geo-url">{result.url}</p>
            </div>
          </div>

          {/* Breakdown */}
          <div className="geo-breakdown">
            <h3 className="section-title">📊 Chi tiết điểm GEO</h3>
            <div className="geo-bars">
              {Object.entries(result.breakdown).map(([key, val]) => {
                const meta = CATEGORY_META[key] || { icon: "📌", label: key, color: "#888" };
                const pct = (val.score / val.max) * 100;
                return (
                  <div key={key} className="geo-bar-item">
                    <div className="geo-bar-label">
                      <span>{meta.icon} {meta.label}</span>
                      <span style={{ color: meta.color, fontWeight: 700 }}>{val.score}/{val.max}</span>
                    </div>
                    <div className="geo-bar-track">
                      <div className="geo-bar-fill" style={{ width: `${pct}%`, background: meta.color }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recommendations */}
          <div className="geo-recs">
            <h3 className="section-title">💡 Khuyến nghị ({result.total_recommendations})</h3>
            <div className="geo-recs-list">
              {result.recommendations.map((rec, i) => (
                <div key={i} className="geo-rec-item">
                  <span className="geo-rec-category">{rec.category}</span>
                  <span className="geo-rec-text">{rec.recommendation}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Action buttons: FAQ + Schema */}
          <div className="geo-actions">
            <button className="rt-btn rt-btn-add" onClick={handleGenerateFaq} disabled={faqLoading}>
              {faqLoading ? "⏳ Đang tạo FAQ..." : "🤖 Tạo FAQ Schema từ AI"}
            </button>
            <button className="rt-btn rt-btn-sync" onClick={() => setShowSchemaGen(!showSchemaGen)}>
              🏢 Tạo LocalBusiness Schema
            </button>
          </div>

          {/* FAQ Result */}
          {faqError && <p className="error-msg">{faqError}</p>}
          {faqResult && (
            <div className="geo-faq-result">
              <h3 className="section-title">❓ FAQ Schema ({faqResult.total_faqs} câu hỏi)</h3>
              <div className="geo-faq-list">
                {faqResult.faqs.map((faq, i) => (
                  <div key={i} className="geo-faq-item">
                    <div className="geo-faq-q">❓ {faq.question}</div>
                    <div className="geo-faq-a">{faq.answer}</div>
                  </div>
                ))}
              </div>
              <div className="geo-code-section">
                <button className="spin-view-btn active" onClick={() => setShowSchemaCode(!showSchemaCode)}>
                  {showSchemaCode ? "Ẩn code" : "📋 Xem JSON-LD code"}
                </button>
                {showSchemaCode && (
                  <div className="geo-code-block">
                    <div className="geo-code-header">
                      <span>{'<script type="application/ld+json">'}</span>
                      <button className="spin-copy-btn" onClick={() => copyCode(faqResult.schema_code)}>
                        {codeCopied ? "✅ Đã copy" : "📋 Copy"}
                      </button>
                    </div>
                    <pre className="geo-code-pre">{faqResult.schema_code}</pre>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* LocalBusiness Schema Generator */}
          {showSchemaGen && (
            <div className="geo-schema-gen">
              <h3 className="section-title">🏢 Tạo LocalBusiness Schema</h3>
              <div className="geo-schema-form">
                <div className="input-group">
                  <label className="input-label">Tên doanh nghiệp</label>
                  <input className="text-input" value={schemaForm.name}
                    onChange={e => setSchemaForm({ ...schemaForm, name: e.target.value })} />
                </div>
                <div className="input-group">
                  <label className="input-label">Địa chỉ</label>
                  <input className="text-input" value={schemaForm.address}
                    onChange={e => setSchemaForm({ ...schemaForm, address: e.target.value })} />
                </div>
                <div className="input-group">
                  <label className="input-label">Số điện thoại</label>
                  <input className="text-input" value={schemaForm.phone}
                    onChange={e => setSchemaForm({ ...schemaForm, phone: e.target.value })} />
                </div>
                <div className="input-group">
                  <label className="input-label">Loại hình</label>
                  <select className="text-input" value={schemaForm.business_type}
                    onChange={e => setSchemaForm({ ...schemaForm, business_type: e.target.value })}
                    style={{ paddingLeft: 12 }}>
                    <option value="AutoDealer">Đại lý ô tô</option>
                    <option value="LocalBusiness">Doanh nghiệp địa phương</option>
                    <option value="Store">Cửa hàng</option>
                    <option value="Restaurant">Nhà hàng</option>
                    <option value="MedicalBusiness">Y tế</option>
                  </select>
                </div>
                <button className="rt-btn rt-btn-add" onClick={handleGenerateSchema}>⚡ Tạo Schema</button>
              </div>

              {schemaCode && (
                <div className="geo-code-block" style={{ marginTop: 12 }}>
                  <div className="geo-code-header">
                    <span>{'<script type="application/ld+json">'}</span>
                    <button className="spin-copy-btn" onClick={() => copyCode(schemaCode)}>
                      {codeCopied ? "✅ Đã copy" : "📋 Copy"}
                    </button>
                  </div>
                  <pre className="geo-code-pre">{schemaCode}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
