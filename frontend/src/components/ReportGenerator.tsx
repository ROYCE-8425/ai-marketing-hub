import { useState } from "react";
import { API_BASE } from "../lib/apiConfig";

interface ReportSection {
  title: string;
  score?: number;
  max?: number;
  grade?: string;
  error?: string;
  load_time?: number;
  critical_count?: number;
  warning_count?: number;
  issues?: any[];
  recommendations?: any[];
  total_tracked?: number;
  top_keywords?: any[];
  dropping?: any[];
}

interface Report {
  url: string;
  generated_at: string;
  overall_score: number;
  overall_grade: string;
  ai_summary: string;
  sections: Record<string, ReportSection>;
  all_issues: any[];
  total_issues: number;
}

export function ReportGenerator() {
  const [url, setUrl] = useState("https://binhphuocmitsubishi.com");
  const [keyword, setKeyword] = useState("mitsubishi bình phước");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState("");

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true); setError(""); setReport(null);
    try {
      const r = await fetch(`${API_BASE}/report/generate`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), keyword: keyword.trim() }),
      });
      const d = await r.json();
      if (d.error) setError(d.error); else setReport(d);
    } catch (e: any) { setError(e.message); }
    setLoading(false);
  };

  const exportReport = async () => {
    try {
      const r = await fetch(`${API_BASE}/report/export`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), keyword: keyword.trim() }),
      });
      const text = await r.text();
      const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `seo_report_${url.split("//")[1]?.split("/")[0] || "report"}.txt`;
      a.click();
    } catch { /* ignore */ }
  };

  const gradeColor = (g: string) => ({ A: "#22c55e", B: "#3b82f6", C: "#f59e0b", D: "#ef4444" }[g] || "#888");

  return (
    <div className="geo-optimizer">
      <form className="audit-form" onSubmit={handleGenerate}>
        <div className="hint-box">📊 <strong>AI Report Generator:</strong> Tạo báo cáo SEO tổng hợp từ Technical SEO + GEO + Rankings với AI summary.</div>
        <div className="input-row">
          <div className="input-group" style={{ flex: 2 }}>
            <label className="input-label">URL</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" /><path d="M3.6 9h16.8M3.6 15h16.8" /></svg>
              <input type="url" className="text-input" value={url} onChange={e => setUrl(e.target.value)} required />
            </div>
          </div>
          <div className="input-group" style={{ flex: 1 }}>
            <label className="input-label">Từ khóa</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" /></svg>
              <input type="text" className="text-input" value={keyword} onChange={e => setKeyword(e.target.value)} />
            </div>
          </div>
          <button className={`submit-btn ${loading ? "loading" : ""}`} type="submit" disabled={loading} style={{ alignSelf: "flex-end" }}>
            {loading ? (<><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="spin-icon"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /></svg> Đang tạo...</>) : "📊 Tạo báo cáo"}
          </button>
        </div>
        {error && <p className="error-msg">{error}</p>}
      </form>

      {report && (
        <div className="geo-result">
          {/* Overall score */}
          <div className="geo-score-hero">
            <div className="geo-score-ring">
              <svg viewBox="0 0 120 120" width="140" height="140">
                <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
                <circle cx="60" cy="60" r="52" fill="none" stroke={gradeColor(report.overall_grade)}
                  strokeWidth="8" strokeLinecap="round"
                  strokeDasharray={`${(report.overall_score / 100) * 327} 327`}
                  transform="rotate(-90 60 60)" style={{ transition: "stroke-dasharray 1s ease" }} />
              </svg>
              <div className="geo-score-inner">
                <span className="geo-score-num">{report.overall_score}</span>
                <span className="geo-score-max">/100</span>
              </div>
            </div>
            <div className="geo-score-info">
              <span className="geo-grade" style={{ color: gradeColor(report.overall_grade) }}>{report.overall_grade}</span>
              <span className="geo-grade-label">Tổng điểm SEO</span>
              <p className="geo-url">{report.url} — {report.generated_at?.slice(0, 10)}</p>
            </div>
          </div>

          {/* AI Summary */}
          <div className="geo-recs" style={{ borderLeftColor: "#8b5cf6" }}>
            <h3 className="section-title">🤖 AI Tóm tắt</h3>
            <p style={{ color: "var(--text)", lineHeight: 1.8, fontSize: 14, marginTop: 10 }}>{report.ai_summary}</p>
          </div>

          {/* Sections */}
          <div className="geo-breakdown">
            <h3 className="section-title">📈 Chi tiết theo module</h3>
            <div className="geo-bars" style={{ marginTop: 12 }}>
              {Object.entries(report.sections).map(([key, sec]) => {
                if (!sec.score && !sec.max) return null;
                const pct = sec.max ? (sec.score! / sec.max) * 100 : 0;
                return (
                  <div key={key} className="geo-bar-item">
                    <div className="geo-bar-label">
                      <span>{sec.title}</span>
                      <span style={{ fontWeight: 700, color: pct >= 70 ? "#22c55e" : pct >= 40 ? "#f59e0b" : "#ef4444" }}>
                        {sec.score}/{sec.max} {sec.grade && `(${sec.grade})`}
                      </span>
                    </div>
                    <div className="geo-bar-track">
                      <div className="geo-bar-fill" style={{ width: `${pct}%`, background: pct >= 70 ? "#22c55e" : pct >= 40 ? "#f59e0b" : "#ef4444" }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Issues */}
          {report.all_issues.length > 0 && (
            <div className="geo-recs">
              <h3 className="section-title">🔍 Vấn đề cần sửa ({report.total_issues})</h3>
              <div className="geo-recs-list">
                {report.all_issues.slice(0, 12).map((issue, i) => (
                  <div key={i} className="geo-rec-item">
                    <span className="geo-rec-category">
                      {{ critical: "🔴", warning: "🟡", info: "🔵" }[issue.severity as string] || "⚪"} {issue.category}
                    </span>
                    <span className="geo-rec-text">{issue.message}</span>
                    {issue.fix && <span className="geo-rec-text" style={{ opacity: 0.6, fontSize: 12 }}>→ {issue.fix}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Export button */}
          <div className="geo-actions">
            <button className="rt-btn rt-btn-add" onClick={exportReport}>📥 Download báo cáo (.txt)</button>
            <button className="rt-btn rt-btn-sync" onClick={handleGenerate}>🔄 Tạo lại</button>
          </div>
        </div>
      )}
    </div>
  );
}
