import React, { useState, useEffect, useCallback } from "react";
import { API_BASE } from "../lib/apiConfig";
import { authFetch } from "../lib/auth";
import "./DashboardOverview.css"; // Reuse dashboard grids/charts styling

interface ManagedSite {
  id: number;
  name: string;
  url: string;
  is_active: number;
  niche?: string;
}

interface ActionPlanItem {
  day?: string;
  week?: string;
  task: string;
  priority: "high" | "medium" | "low";
  impact: string;
}

interface DeterministicIssue {
  severity: "critical" | "warning" | "info";
  category: string;
  message: string;
  fix: string;
}

interface QuickWin {
  keyword: string;
  current_position: number;
  impressions: number;
  action: string;
}

interface ContentOpportunity {
  keyword: string;
  search_intent: string;
  reason: string;
}

interface SourceStatus {
  gsc: string;
  ga4: string;
  serp: string;
  technical: string;
  cwv: string;
  schema: string;
  broken: string;
  rank_tracking: string;
  usage: string;
}

interface AdvisorResponse {
  site_url: string;
  analyzed_at: string;
  confidence: "high" | "medium" | "low";
  confidence_score: number;
  summary: string;
  top_issues: DeterministicIssue[];
  quick_wins: QuickWin[];
  technical_blockers: DeterministicIssue[];
  content_opportunities: ContentOpportunity[];
  action_plan_7d: ActionPlanItem[];
  action_plan_30d: ActionPlanItem[];
  source_status: SourceStatus;
  ai_provider: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data_snapshot: any;
}

export function AiAdvisor() {
  // Site resolution & Form states
  const [sites, setSites] = useState<ManagedSite[]>([]);
  const [activeSite, setActiveSite] = useState<ManagedSite | null>(null);
  const [selectedSiteUrl, setSelectedSiteUrl] = useState("");
  const [targetKeyword, setTargetKeyword] = useState("");
  const [days, setDays] = useState(30);

  // Toggle checks
  const [includeGsc, setIncludeGsc] = useState(true);
  const [includeGa4, setIncludeGa4] = useState(true);
  const [includeSerp, setIncludeSerp] = useState(true);
  const [includeRankTracking, setIncludeRankTracking] = useState(true);
  const [includeTechnical, setIncludeTechnical] = useState(true);
  const [includeCwv, setIncludeCwv] = useState(true);
  const [includeSchema, setIncludeSchema] = useState(true);
  const [includeUsageHistory, setIncludeUsageHistory] = useState(true);

  // Analysis result & Loading states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AdvisorResponse | null>(null);

  // Fetch managed sites list & Active site prefill
  const loadSites = useCallback(async () => {
    try {
      const res = await authFetch(`${API_BASE}/sites/list`);
      if (res.ok) {
        const data = await res.json();
        const siteList = data.sites || [];
        setSites(siteList);

        // Fetch active site
        const activeRes = await authFetch(`${API_BASE}/sites/active`);
        if (activeRes.ok) {
          const activeData = await activeRes.json();
          if (activeData && activeData.url) {
            setActiveSite(activeData);
            setSelectedSiteUrl(activeData.url);
          } else if (siteList.length > 0) {
            setSelectedSiteUrl(siteList[0].url);
          }
        }
      }
    } catch {
      setError("Không thể tải danh sách website từ hệ thống.");
    }
  }, []);

  useEffect(() => {
    loadSites();
  }, [loadSites]);

  // Handle Analysis submit
  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await authFetch(`${API_BASE}/advisor/analyze`, {
        method: "POST",
        body: JSON.stringify({
          site_url: selectedSiteUrl || undefined,
          target_keyword: targetKeyword.trim() || undefined,
          days,
          include_gsc: includeGsc,
          include_ga4: includeGa4,
          include_serp: includeSerp,
          include_rank_tracking: includeRankTracking,
          include_technical: includeTechnical,
          include_cwv: includeCwv,
          include_schema: includeSchema,
          include_usage_history: includeUsageHistory,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? `Lỗi hệ thống (HTTP ${res.status})`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Có lỗi xảy ra trong quá trình phân tích.");
    } finally {
      setLoading(false);
    }
  };

  // Helper styles & icons
  const severityBadge = (sev: "critical" | "warning" | "info") => {
    if (sev === "critical") return <span className="issue-badge badge-critical">Nghiêm trọng</span>;
    if (sev === "warning") return <span className="issue-badge badge-warning">Cảnh báo</span>;
    return <span className="issue-badge badge-suggestion">Gợi ý</span>;
  };

  const priorityLabel = (pri: "high" | "medium" | "low") => {
    if (pri === "high") return <span className="issue-badge badge-critical" style={{ padding: "2px 6px" }}>Ưu tiên cao</span>;
    if (pri === "medium") return <span className="issue-badge badge-warning" style={{ padding: "2px 6px" }}>Trung bình</span>;
    return <span className="issue-badge badge-suggestion" style={{ padding: "2px 6px" }}>Thấp</span>;
  };

  const sourceStatusLabel = (status: string) => {
    const s = (status || "").toLowerCase();
    if (s === "ok" || s === "gsc_real" || s === "live_ga4" || s === "partial_live_ga4") {
      return <span style={{ color: "#10b981", fontWeight: "bold" }}>● Hoạt động</span>;
    }
    if (s === "disabled") {
      return <span style={{ color: "#94a3b8", fontWeight: "bold" }}>○ Bị tắt</span>;
    }
    if (s === "missing_credentials") {
      return <span style={{ color: "#f59e0b", fontWeight: "bold" }}>⚠ Thiếu cấu hình</span>;
    }
    return <span style={{ color: "#ef4444", fontWeight: "bold" }}>✕ Lỗi/Không có dữ liệu</span>;
  };

  return (
    <div className="geo-optimizer" style={{ paddingBottom: "3rem" }}>
      <div className="hint-box">
        💡 <strong>AI Cố vấn website:</strong> Hợp nhất toàn bộ dữ liệu Marketing (GSC, GA4, Technical SEO, rank tracker, v.v.), tính toán deterministic insights trước, sau đó dùng AI của Groq LLaMA 3.3 để xây dựng kế hoạch bứt phá traffic.
      </div>

      {/* Inputs Form */}
      <form className="audit-form" style={{ marginTop: "1rem" }} onSubmit={handleAnalyze}>
        <div className="geo-schema-form" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "12px" }}>
          
          <div className="input-group">
            <label className="input-label" htmlFor="site-select">Chọn Website phân tích</label>
            <select
              id="site-select"
              className="text-input"
              value={selectedSiteUrl}
              onChange={(e) => setSelectedSiteUrl(e.target.value)}
              style={{ background: "var(--surface)", color: "var(--text)" }}
            >
              {activeSite && <option value={activeSite.url}>{activeSite.name} (Active - {activeSite.url})</option>}
              {sites
                .filter((s) => !activeSite || s.url !== activeSite.url)
                .map((site) => (
                  <option key={site.id} value={site.url}>
                    {site.name} ({site.url})
                  </option>
                ))}
              <option value="">-- Dùng cấu hình mặc định trong .env --</option>
            </select>
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="kw-input">Từ khóa mục tiêu (SEO Target)</label>
            <input
              id="kw-input"
              className="text-input"
              type="text"
              placeholder="Ví dụ: dịch vụ seo bình phước (Cần thiết cho SERP)"
              value={targetKeyword}
              onChange={(e) => setTargetKeyword(e.target.value)}
              style={{ paddingLeft: "12px" }}
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="days-select">Khoảng thời gian</label>
            <select
              id="days-select"
              className="text-input"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              style={{ background: "var(--surface)", color: "var(--text)" }}
            >
              <option value={30}>30 ngày qua</option>
              <option value={60}>60 ngày qua</option>
              <option value={90}>90 ngày qua</option>
            </select>
          </div>

        </div>

        {/* Checkbox triggers */}
        <div style={{ marginTop: "1rem" }}>
          <label className="input-label" style={{ marginBottom: "6px" }}>Nguồn dữ liệu đưa vào cố vấn</label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "16px", padding: "10px", background: "rgba(255,255,255,0.03)", borderRadius: "8px", border: "1px solid var(--border)" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeGsc} onChange={(e) => setIncludeGsc(e.target.checked)} />
              Google Search Console
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeGa4} onChange={(e) => setIncludeGa4(e.target.checked)} />
              Google Analytics 4
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeSerp} onChange={(e) => setIncludeSerp(e.target.checked)} />
              SERP Live
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeRankTracking} onChange={(e) => setIncludeRankTracking(e.target.checked)} />
              Rank Tracker Local
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeTechnical} onChange={(e) => setIncludeTechnical(e.target.checked)} />
              Technical SEO
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeCwv} onChange={(e) => setIncludeCwv(e.target.checked)} />
              Core Web Vitals
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeSchema} onChange={(e) => setIncludeSchema(e.target.checked)} />
              Schema Validation
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeUsageHistory} onChange={(e) => setIncludeUsageHistory(e.target.checked)} />
              Lịch sử sử dụng
            </label>
          </div>
        </div>

        <div style={{ marginTop: "1rem", display: "flex", gap: "8px" }}>
          <button
            type="submit"
            className="rt-btn rt-btn-add"
            style={{ width: "fit-content", padding: "8px 24px", display: "flex", alignItems: "center", gap: "8px" }}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="btn-spinner" aria-label="Loading" />
                Đang chẩn đoán website...
              </>
            ) : (
              <>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
                Phân tích &amp; Cố vấn AI
              </>
            )}
          </button>
        </div>
      </form>

      {/* Error display */}
      {error && (
        <div className="mock-warning-banner" role="alert" style={{ borderColor: "#ef4444", marginTop: "1rem" }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span><strong>Lỗi phân tích:</strong> {error}</span>
        </div>
      )}

      {/* Results Workspace */}
      {result && (
        <div style={{ marginTop: "1.5rem" }} className="result-wrapper">
          
          {/* Executive Summary Card */}
          <div className="section-block" style={{ padding: "20px", background: "rgba(255,255,255,0.02)", borderRadius: "12px", border: "1px solid var(--border)" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "8px", margin: "0 0 10px 0", color: "#8b5cf6", fontSize: "17px", fontWeight: "700" }}>
              💎 Tóm tắt điều hành (Executive Summary)
              <span style={{ fontSize: "10px", background: "rgba(139,92,246,0.15)", color: "#c4b5fd", padding: "2px 8px", borderRadius: "99px", marginLeft: "auto", border: "1px solid rgba(139,92,246,0.2)" }}>
                AI: {result.ai_provider}
              </span>
            </h3>
            <p style={{ fontSize: "14px", lineHeight: "1.6", color: "var(--text-h)", margin: 0 }}>
              {result.summary}
            </p>
          </div>

          {/* 3 Largest Issues */}
          {result.top_issues && result.top_issues.length > 0 && (
            <div className="section-block" style={{ marginTop: "1rem" }}>
              <h3 className="section-title critical-title" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                🔴 Các vấn đề cần ưu tiên xử lý hàng đầu
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "10px" }}>
                {result.top_issues.slice(0, 5).map((issue, idx) => (
                  <div key={idx} className="geo-faq-item" style={{ borderLeft: "3px solid #ef4444" }}>
                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                      {severityBadge(issue.severity)}
                      <span className="rt-tag-badge">{issue.category}</span>
                    </div>
                    <p style={{ fontSize: "14px", color: "var(--text-h)", fontWeight: "600", margin: "8px 0 4px 0" }}>
                      {issue.message}
                    </p>
                    <p style={{ fontSize: "12px", color: "#10b981", margin: 0 }}>
                      👉 <strong>Khắc phục:</strong> {issue.fix}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Wins Table */}
          {result.quick_wins && result.quick_wins.length > 0 && (
            <div className="section-block" style={{ marginTop: "1.5rem" }}>
              <h3 className="section-title" style={{ display: "flex", alignItems: "center", gap: "6px", color: "#06b6d4" }}>
                🚀 Cơ hội thăng hạng nhanh (Quick Wins)
              </h3>
              <div className="top-pages-table" style={{ marginTop: "10px" }}>
                <table>
                  <thead>
                    <tr>
                      <th>Từ khóa cơ hội</th>
                      <th>Vị trí hiện tại</th>
                      <th>Lượt hiển thị GSC</th>
                      <th>Khuyến nghị hành động</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.quick_wins.map((qw, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: "700", color: "#e2e8f0" }}>{qw.keyword}</td>
                        <td style={{ color: "#3b82f6", fontWeight: "bold" }}>#{qw.current_position}</td>
                        <td>{qw.impressions.toLocaleString()}</td>
                        <td style={{ fontSize: "12px", color: "var(--text-dim)" }}>{qw.action}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Technical Blockers & Core Web Vitals */}
          {result.technical_blockers && result.technical_blockers.length > 0 && (
            <div className="section-block" style={{ marginTop: "1.5rem" }}>
              <h3 className="section-title warning-title" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                ⚡ Rào cản kỹ thuật &amp; Core Web Vitals
              </h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "10px", marginTop: "10px" }}>
                {result.technical_blockers.slice(0, 6).map((blocker, idx) => (
                  <div key={idx} className="geo-faq-item" style={{ borderLeft: "3px solid #f59e0b" }}>
                    <span className="rt-tag-badge" style={{ background: "rgba(245,158,11,0.15)", color: "#f59e0b" }}>{blocker.category}</span>
                    <p style={{ fontSize: "13px", color: "var(--text-h)", fontWeight: "600", margin: "6px 0" }}>{blocker.message}</p>
                    <p style={{ fontSize: "12px", color: "#10b981", margin: 0 }}>👉 {blocker.fix}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Content Opportunities */}
          {result.content_opportunities && result.content_opportunities.length > 0 && (
            <div className="section-block" style={{ marginTop: "1.5rem" }}>
              <h3 className="section-title" style={{ display: "flex", alignItems: "center", gap: "6px", color: "#ec4899" }}>
                ✍️ Cơ hội mở rộng nội dung (Content Gaps)
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "10px" }}>
                {result.content_opportunities.map((opp, idx) => (
                  <div key={idx} className="geo-faq-item" style={{ borderLeft: "3px solid #ec4899" }}>
                    <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                      <span className="rt-tag-badge" style={{ background: "rgba(236,72,153,0.15)", color: "#ec4899" }}>{opp.search_intent}</span>
                    </div>
                    <p style={{ fontSize: "13px", color: "var(--text-h)", margin: "4px 0 0 0" }}>{opp.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Plans 7d & 30d */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "16px", marginTop: "1.5rem" }}>
            
            {/* 7 Days Plan */}
            <div className="section-block" style={{ margin: 0 }}>
              <h3 className="section-title" style={{ color: "#8b5cf6" }}>📅 Kế hoạch hành động 7 ngày tới</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "10px" }}>
                {result.action_plan_7d.map((plan, i) => (
                  <div key={i} className="geo-faq-item" style={{ borderLeft: "2px solid #8b5cf6", background: "rgba(255,255,255,0.01)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <strong style={{ color: "#c4b5fd", fontSize: "13px" }}>{plan.day || `Giai đoạn ${i+1}`}</strong>
                      {priorityLabel(plan.priority)}
                    </div>
                    <p style={{ fontSize: "13px", color: "var(--text-h)", margin: "6px 0" }}>{plan.task}</p>
                    <p style={{ fontSize: "11px", color: "var(--text-dim)", margin: 0 }}>
                      ⚡ <strong>Tác động:</strong> {plan.impact}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* 30 Days Plan */}
            <div className="section-block" style={{ margin: 0 }}>
              <h3 className="section-title" style={{ color: "#06b6d4" }}>📅 Chiến lược tăng trưởng 30 ngày</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "10px" }}>
                {result.action_plan_30d.map((plan, i) => (
                  <div key={i} className="geo-faq-item" style={{ borderLeft: "2px solid #06b6d4", background: "rgba(255,255,255,0.01)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <strong style={{ color: "#94a3b8", fontSize: "13px" }}>{plan.week || `Tuần ${i+1}`}</strong>
                      {priorityLabel(plan.priority)}
                    </div>
                    <p style={{ fontSize: "13px", color: "var(--text-h)", margin: "6px 0" }}>{plan.task}</p>
                    <p style={{ fontSize: "11px", color: "var(--text-dim)", margin: 0 }}>
                      ⚡ <strong>Tác động:</strong> {plan.impact}
                    </p>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Sources and Data Coverage Status */}
          <div className="section-block" style={{ marginTop: "1.5rem" }}>
            <h3 className="section-title" style={{ fontSize: "15px" }}>📊 Bản đồ phủ dữ liệu &amp; Mức độ tin cậy</h3>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px", background: "rgba(255,255,255,0.02)", borderRadius: "8px", border: "1px solid var(--border)", margin: "10px 0" }}>
              <span style={{ fontSize: "13px" }}>Website chẩn đoán: <strong>{result.site_url}</strong></span>
              <span style={{ fontSize: "13px" }}>
                Độ tin cậy cố vấn:{" "}
                <strong style={{ color: result.confidence === "high" ? "#10b981" : result.confidence === "medium" ? "#3b82f6" : "#ef4444" }}>
                  {result.confidence.toUpperCase()} ({result.confidence_score}%)
                </strong>
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "8px" }}>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Google Search Console</span>
                {sourceStatusLabel(result.source_status.gsc)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Google Analytics 4</span>
                {sourceStatusLabel(result.source_status.ga4)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>SERP Live</span>
                {sourceStatusLabel(result.source_status.serp)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Technical SEO</span>
                {sourceStatusLabel(result.source_status.technical)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Core Web Vitals</span>
                {sourceStatusLabel(result.source_status.cwv)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Schema.org validation</span>
                {sourceStatusLabel(result.source_status.schema)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Link hỏng</span>
                {sourceStatusLabel(result.source_status.broken)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Thứ hạng theo dõi</span>
                {sourceStatusLabel(result.source_status.rank_tracking)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Lịch sử hệ thống</span>
                {sourceStatusLabel(result.source_status.usage)}
              </div>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
export default AiAdvisor;
