import { useState, type JSX } from "react";
import { useSeoAudit } from "./hooks/useSeoAudit";
import { useOpportunities } from "./hooks/useOpportunities";
import { useAutoFill } from "./hooks/useAutoFill";
import { useSerpLive } from "./hooks/useSerpLive";
import { ScoreRing } from "./components/ScoreRing";
import { CroDashboard } from "./components/CroDashboard";
import { CompetitorRadarPanel } from "./components/CompetitorRadar";
import { ContentPlannerPanel } from "./components/ContentPlanner";
import { CampaignTrackerPanel } from "./components/CampaignTracker";
import { SerpResultsPanel } from "./components/SerpResultsPanel";
import { DashboardOverview } from "./components/DashboardOverview";
import { PublishModal } from "./components/PublishModal";
import { RankTracker } from "./components/RankTracker";
import { SpinEditor } from "./components/SpinEditor";
import { GeoOptimizer } from "./components/GeoOptimizer";
import { addToHistory } from "./lib/history";
import type { AuditResponse } from "./types/seo";
import type { CompetitorGapResponse, PlanContentResponse } from "./types/content";
import { API_BASE } from "./lib/apiConfig";
import "./index.css";

// ─── Error Boundary ──────────────────────────────────────────────────────────

import React from "react";

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: string }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: "" };
  }
  static getDerivedStateFromError(err: Error) {
    return { hasError: true, error: err?.message ?? String(err) };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: "40px", textAlign: "center", color: "#ef4444",
          background: "rgba(239,68,68,0.06)", borderRadius: "12px",
          margin: "40px auto", maxWidth: "600px",
          border: "1px solid rgba(239,68,68,0.2)",
        }}>
          <h2 style={{ marginBottom: "8px" }}>⚠️ Render Error</h2>
          <p style={{ fontSize: "14px", color: "#ccc" }}>{this.state.error}</p>
          <button
            onClick={() => this.setState({ hasError: false, error: "" })}
            style={{
              marginTop: "16px", padding: "8px 24px",
              background: "#ef4444", color: "#fff", border: "none",
              borderRadius: "8px", cursor: "pointer", fontSize: "14px",
            }}
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ─── Tab types ─────────────────────────────────────────────────────────────────

type TabId = "dashboard" | "seo" | "cro" | "competitor" | "planner" | "tracker" | "serp" | "aikeys" | "ranktracker" | "spineditor" | "geo";

const TABS: { id: TabId; label: string; icon: JSX.Element }[] = [
  {
    id: "dashboard",
    label: "Tổng quan",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </svg>
    ),
  },
  {
    id: "seo",
    label: "Kiểm tra SEO",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
      </svg>
    ),
  },
  {
    id: "cro",
    label: "CRO & Uy tín",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
        <polyline points="16 7 22 7 22 13" />
      </svg>
    ),
  },
  {
    id: "competitor",
    label: "Phân tích đối thủ",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
    ),
  },
  {
    id: "planner",
    label: "Viết nội dung AI",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
      </svg>
    ),
  },
  {
    id: "tracker",
    label: "Theo dõi chiến dịch",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <line x1="18" y1="20" x2="18" y2="10" />
        <line x1="12" y1="20" x2="12" y2="4" />
        <line x1="6"  y1="20" x2="6"  y2="14" />
      </svg>
    ),
  },
  {
    id: "serp",
    label: "SERP trực tiếp",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
        <path d="M3.6 9h16.8M3.6 15h16.8" />
        <path d="M12 3a15 15 0 0 1 0 18 15 15 0 0 1 0-18z" />
      </svg>
    ),
  },
  {
    id: "aikeys",
    label: "\uD83E\uDD16 Phân tích từ khóa AI",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M2 17l10 5 10-5" />
        <path d="M2 12l10 5 10-5" />
      </svg>
    ),
  },
  {
    id: "ranktracker" as TabId,
    label: "Theo dõi Keyword",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
        <polyline points="16 7 22 7 22 13" />
      </svg>
    ),
  },
  {
    id: "spineditor" as TabId,
    label: "Spin Editor",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
        <path d="M3 3v5h5" />
      </svg>
    ),
  },
  {
    id: "geo" as TabId,
    label: "🤖 Tối ưu GEO",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M2 17l10 5 10-5" />
        <path d="M2 12l10 5 10-5" />
      </svg>
    ),
  },
];

function TabBar({ active, onChange }: { active: TabId; onChange: (t: TabId) => void }) {
  return (
    <div className="tab-bar">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          className={`tab-btn ${active === tab.id ? "tab-active" : ""}`}
          onClick={() => onChange(tab.id)}
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  );
}

// ─── Shared result panel layout ────────────────────────────────────────────────

function ResultPanel({ children }: { children: React.ReactNode }) {
  return <div className="result-panel">{children}</div>;
}

// ─── SEO Panel ────────────────────────────────────────────────────────────────

function IssueBadge({ text, type }: { text: string; type: "critical" | "warning" | "suggestion" }) {
  const cls = type === "critical" ? "badge-critical" : type === "warning" ? "badge-warning" : "badge-suggestion";
  return <span className={`issue-badge ${cls}`}>{String(text)}</span>;
}

function HeatBar({ level }: { level: number }) {
  return (
    <div className="heat-bar" aria-label={`Heat level ${level}`}>
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className={`heat-cell ${i <= level ? `heat-on-${level}` : ""}`} />
      ))}
    </div>
  );
}

function ResultCard({ label, value }: { label: string; value: string | number }) {
  // Safety: coerce to string in case API returns unexpected type
  const display = typeof value === "object" && value !== null ? JSON.stringify(value) : String(value);
  return (
    <div className="result-card">
      <span className="result-label">{label}</span>
      <span className="result-value">{display}</span>
    </div>
  );
}

function CategoryBar({ name, score }: { name: string; score: number }) {
  const color = score >= 80 ? "#10b981" : score >= 60 ? "#f59e0b" : "#ef4444";
  return (
    <div className="category-bar-row">
      <span className="category-name">{name}</span>
      <div className="category-track">
        <div className="category-fill" style={{ width: `${score}%`, background: color }} />
      </div>
      <span className="category-score" style={{ color }}>{score}</span>
    </div>
  );
}

function SeoPanel({ data }: { data: AuditResponse }) {
  const q = data.seo_quality;
  const kw = data.keyword_analysis;
  return (
    <ResultPanel>
      <div className="result-header">
        <ScoreRing score={Math.round(q.overall_score)} grade={q.grade} />
        <div className="result-meta">
          <h2 className="result-title">SEO Audit Report</h2>
          <p className="result-keyword">Keyword: <strong>{data.primary_keyword}</strong></p>
          <p className="result-wordcount">{kw.word_count.toLocaleString()} words analyzed</p>
          {q.publishing_ready && <span className="publishing-ready">Publishing Ready</span>}
        </div>
      </div>
      <div className="section-block">
        <h3 className="section-title">Category Scores</h3>
        {Object.entries(q.category_scores).map(([name, score]) => (
          <CategoryBar key={name} name={name.replace(/_/g, " ")} score={Math.round(score)} />
        ))}
      </div>
      <div className="section-block">
        <h3 className="section-title">Keyword Analysis</h3>
        <div className="result-grid">
          <ResultCard label="Density" value={`${kw.primary_keyword.density}%`} />
          <ResultCard label="Status" value={kw.primary_keyword.density_status} />
          <ResultCard label="Exact Matches" value={kw.primary_keyword.exact_matches} />
          <ResultCard label="Stuffing Risk" value={kw.keyword_stuffing.risk_level} />
        </div>
        <div className="lsi-row">
          <span className="lsi-label">LSI Keywords</span>
          <div className="lsi-tags">
            {kw.lsi_keywords.slice(0, 10).map((k) => (
              <span key={k} className="lsi-tag">{k}</span>
            ))}
          </div>
        </div>
      </div>
      <div className="section-block">
        <h3 className="section-title">Distribution Heatmap</h3>
        <div className="heatmap-list">
          {kw.distribution_heatmap.map((s, i) => (
            <div key={i} className="heatmap-row">
              <HeatBar level={s.heat_level} />
              <span className="heatmap-section">{s.section}</span>
              <span className="heatmap-density">{s.density}%</span>
            </div>
          ))}
        </div>
      </div>
      {q.critical_issues.length > 0 && (
        <div className="section-block">
          <h3 className="section-title critical-title">Critical Issues</h3>
          <div className="issues-list">
            {q.critical_issues.map((t, i) => <IssueBadge key={i} text={t} type="critical" />)}
          </div>
        </div>
      )}
      {q.warnings.length > 0 && (
        <div className="section-block">
          <h3 className="section-title warning-title">Warnings</h3>
          <div className="issues-list">
            {q.warnings.map((t, i) => <IssueBadge key={i} text={t} type="warning" />)}
          </div>
        </div>
      )}
      {q.suggestions.length > 0 && (
        <div className="section-block">
          <h3 className="section-title">Suggestions</h3>
          <div className="issues-list">
            {q.suggestions.map((t, i) => <IssueBadge key={i} text={t} type="suggestion" />)}
          </div>
        </div>
      )}
    </ResultPanel>
  );
}

// ─── Competitor Radar form ─────────────────────────────────────────────────────

function useCompetitorGap() {
  const [data, setData] = useState<CompetitorGapResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const analyze = async (myUrl: string, competitorUrls: string[], keyword: string) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/competitor-gap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ my_url: myUrl, competitor_urls: competitorUrls, primary_keyword: keyword }),
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.detail ?? `HTTP ${res.status}`);
      }
      setData(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };
  return { data, loading, error, analyze };
}

// ─── Content Planner form ─────────────────────────────────────────────────────

function usePlanContent() {
  const [data, setData] = useState<PlanContentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const plan = async (keyword: string, audience: string, gaps?: string[]) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/plan-content`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ primary_keyword: keyword, target_audience: audience, competitor_gaps: gaps }),
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.detail ?? `HTTP ${res.status}`);
      }
      setData(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };
  return { data, loading, error, plan };
}

// ─── Generic Loading button ────────────────────────────────────────────────────

function LoadingBtn({ type = "submit", loading, onClick, children, disabled }: {
  type?: "button" | "submit"; loading: boolean; onClick?: () => void; children: React.ReactNode; disabled?: boolean
}) {
  return (
    <button
      type={type}
      className="analyze-btn"
      onClick={onClick}
      disabled={loading || disabled}
    >
      {loading ? (
        <span className="btn-spinner" aria-label="Loading" />
      ) : children}
    </button>
  );
}

// ─── App root ─────────────────────────────────────────────────────────────────

export default function App() {
  const [url, setUrl] = useState("");
  const [keyword, setKeyword] = useState("");
  const [activeTab, setActiveTab] = useState<TabId>("dashboard");
  const { data: auditData, loading: auditLoading, error: auditError, analyze, reset: resetAudit } = useSeoAudit();

  // Competitor state
  const [compMyUrl, setCompMyUrl] = useState("");
  const [compUrls, setCompUrls] = useState("");
  const [compKeyword, setCompKeyword] = useState("");
  const { data: compData, loading: compLoading, error: compError, analyze: analyzeComp } = useCompetitorGap();

  // Planner state
  const [planKeyword, setPlanKeyword] = useState("");
  const [planAudience, setPlanAudience] = useState("");
  const { data: planData, loading: planLoading, error: planError, plan: generatePlan } = usePlanContent();

  // Publish modal state
  const [publishModal, setPublishModal] = useState<{
    articleTitle: string;
    articleContent: string;
  } | null>(null);

  // Tracker state
  const [trackUrl, setTrackUrl] = useState("");
  const [trackKeyword, setTrackKeyword] = useState("");
  const [trackPosition, setTrackPosition] = useState("");
  const [trackImpressions, setTrackImpressions] = useState("");
  const [trackClicks, setTrackClicks] = useState("");
  const [trackVolume, setTrackVolume] = useState("");
  const [trackDifficulty, setTrackDifficulty] = useState("");
  const { data: trackData, loading: trackLoading, error: trackError, analyze: analyzeTrack } =
    useOpportunities();

  // SERP Live state
  const [serpKeyword, setSerpKeyword] = useState("");
  const [serpLocation, setSerpLocation] = useState("vn");
  const [serpNumResults, setSerpNumResults] = useState(10);
  const { data: serpData, loading: serpLoading, error: serpError, search: searchSerp, reset: resetSerp } = useSerpLive();

  // AI Keywords state
  const [aiKeysTarget, setAiKeysTarget] = useState("");
  const [aiKeysData, setAiKeysData] = useState<any>(null);
  const [aiKeysLoading, setAiKeysLoading] = useState(false);
  const [aiKeysError, setAiKeysError] = useState<string | null>(null);

  const handleAiKeysAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setAiKeysLoading(true);
    setAiKeysError(null);
    setAiKeysData(null);
    try {
      const res = await fetch(`${API_BASE}/ai-keywords`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_keyword: aiKeysTarget.trim() || null }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? `HTTP ${res.status}`);
      }
      setAiKeysData(await res.json());
    } catch (err) {
      setAiKeysError(err instanceof Error ? err.message : "Error");
    } finally {
      setAiKeysLoading(false);
    }
  };

  // Data connection status (updated by AutoFill)
  const [trackGscStatus, setTrackGscStatus] = useState<"connected" | "disconnected" | "pending">("pending");
  const [trackDfsStatus, setTrackDfsStatus] = useState<"connected" | "disconnected" | "pending">("pending");
  const [trackMockFallback, setTrackMockFallback] = useState(false);
  const [trackFallbackReason, setTrackFallbackReason] = useState<string | null>(null);
  const { loading: autofillLoading, error: autofillError, autoFill } = useAutoFill();

  // GSC Config state (stored in localStorage)
  const [gscConfigOpen, setGscConfigOpen] = useState(false);
  const [gscClientId, setGscClientId] = useState(() => localStorage.getItem("gsc_client_id") || "");
  const [gscSecret, setGscSecret] = useState(() => localStorage.getItem("gsc_secret") || "");
  const [gscRefreshToken, setGscRefreshToken] = useState(() => localStorage.getItem("gsc_refresh_token") || "");
  const [gscSiteUrl, setGscSiteUrl] = useState(() => localStorage.getItem("gsc_site_url") || "");
  const [gscSaveMsg, setGscSaveMsg] = useState<string | null>(null);

  const handleSaveGscConfig = async () => {
    localStorage.setItem("gsc_client_id", gscClientId);
    localStorage.setItem("gsc_secret", gscSecret);
    localStorage.setItem("gsc_refresh_token", gscRefreshToken);
    localStorage.setItem("gsc_site_url", gscSiteUrl);
    // Also send to backend to update .env
    try {
      await fetch(`${API_BASE}/config/gsc`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: gscClientId,
          client_secret: gscSecret,
          refresh_token: gscRefreshToken,
          site_url: gscSiteUrl,
        }),
      });
      setGscSaveMsg("✅ Đã lưu thành công! Bấm 'Tự động điền' để lấy dữ liệu thật.");
      setTimeout(() => setGscSaveMsg(null), 5000);
    } catch {
      setGscSaveMsg("✅ Đã lưu vào trình duyệt. Khởi động lại backend để áp dụng.");
      setTimeout(() => setGscSaveMsg(null), 5000);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || !keyword.trim()) return;
    analyze({ url: url.trim(), primary_keyword: keyword.trim() }).then(() => {
      // Save to history after analysis completes (auditData will be set by then)
    });
    setActiveTab("seo");
  };

  const handleCompetitorSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const urls = compUrls.split("\n").map((u) => u.trim()).filter(Boolean);
    if (!urls.length) return;
    analyzeComp(compMyUrl.trim(), urls, compKeyword.trim());
  };

  const handlePlanSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!planKeyword.trim() || !planAudience.trim()) return;
    generatePlan(planKeyword.trim(), planAudience.trim(), compData?.blueprint.must_fill_gaps.map((g) => g.opportunity));
    setActiveTab("planner");
  };

  const handleTrackerSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!trackUrl.trim() || !trackKeyword.trim()) return;
    analyzeTrack({
      url: trackUrl.trim(),
      keyword: trackKeyword.trim(),
      current_position: trackPosition ? parseFloat(trackPosition) : undefined,
      monthly_impressions: trackImpressions ? parseInt(trackImpressions) : undefined,
      monthly_clicks: trackClicks ? parseInt(trackClicks) : undefined,
      search_volume: trackVolume ? parseInt(trackVolume) : undefined,
      difficulty: trackDifficulty ? parseInt(trackDifficulty) : undefined,
    });
  };

  const handleAutoFill = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (!trackUrl.trim() || !trackKeyword.trim()) {
      alert("Enter URL and keyword first, then click Auto-Fill.");
      return;
    }
    const res = await autoFill(trackUrl.trim(), trackKeyword.trim());
    if (!res) return;
    const bulk = res.bulk;
    // Update connector status cards
    setTrackGscStatus(res.gscStatus.gsc as "connected" | "disconnected" | "pending");
    setTrackDfsStatus(res.gscStatus.dataforseo as "connected" | "disconnected" | "pending");
    setTrackMockFallback(!!bulk?._is_mock_fallback);
    setTrackFallbackReason(res.fallbackReason);
    if (!bulk) return;
    // Auto-populate form fields
    if (bulk.current_position != null)     setTrackPosition(String(bulk.current_position));
    if (bulk.monthly_impressions != null)  setTrackImpressions(String(bulk.monthly_impressions));
    if (bulk.monthly_clicks != null)        setTrackClicks(String(bulk.monthly_clicks));
    if (bulk.search_volume != null)         setTrackVolume(String(bulk.search_volume));
    if (bulk.difficulty != null)           setTrackDifficulty(String(bulk.difficulty));
  };

  return (
    <ErrorBoundary>
    <div className="app-shell" translate="no">
      <div className="blob blob-1" />
      <div className="blob blob-2" />

      <nav className="top-nav">
        <div className="nav-brand">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
            <circle cx="14" cy="14" r="13" stroke="#8b5cf6" strokeWidth="2" />
            <path d="M9 14 L14 9 L19 14 L14 19 Z" fill="#8b5cf6" />
          </svg>
          <span>AI Marketing Hub</span>
        </div>
        <div className="nav-links">
          <span className="nav-phase">Phiên bản 9</span>
        </div>
      </nav>

      <main className="main-content">
        {/* Hero — only shown on SEO tab */}
        {activeTab === "seo" && (
          <div className="hero-block">
            <h1 className="hero-title">
              Kiểm tra <span className="hero-accent">Marketing</span> toàn diện
              <br />từ bất kỳ URL nào
            </h1>
            <p className="hero-sub">
              Dán liên kết, thêm từ khóa mục tiêu — nhận phân tích chất lượng SEO,
              CRO và tín hiệu uy tín chỉ trong một cú nhấp.
            </p>
          </div>
        )}

        <TabBar active={activeTab} onChange={setActiveTab} />

        {/* ── Dashboard Tab ── */}
        {activeTab === "dashboard" && (
          <DashboardOverview onNavigate={(tab) => setActiveTab(tab as TabId)} />
        )}

        {/* ── SEO Audit Tab ── */}
        {activeTab === "seo" && (
          <>
            <form className="audit-form" onSubmit={handleSubmit} noValidate>
              <div className="hint-box">
                💡 <strong>Gợi ý:</strong> Nhập URL trang có nhiều nội dung (bài viết, sản phẩm chi tiết) để có phân tích chính xác nhất. Tránh dùng trang chủ hoặc trang chỉ có hình ảnh.
              </div>
              <div className="input-row">
                <div className="input-group">
                  <label htmlFor="url-input" className="input-label">Đường dẫn trang</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                    </svg>
                    <input id="url-input" type="url" className="text-input"
                      placeholder="https://example.com/bai-viet"
                      value={url} onChange={(e) => setUrl(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <div className="input-group">
                  <label htmlFor="keyword-input" className="input-label">Từ khóa chính</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                    </svg>
                    <input id="keyword-input" type="text" className="text-input"
                      placeholder="ví dụ: dịch vụ hosting tốt nhất 2025"
                      value={keyword} onChange={(e) => setKeyword(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <LoadingBtn loading={auditLoading} disabled={!url.trim() || !keyword.trim()}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                  Phân tích
                </LoadingBtn>
              </div>
              {auditError && (
                <p className="error-msg" role="alert">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                  </svg>
                  {auditError}
                </p>
              )}
            </form>

            {auditData && (
              <div className="result-wrapper">
                <button className="reset-btn" onClick={resetAudit} aria-label="New audit">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                    <path d="M3 3v5h5" />
                  </svg>
                  Kiểm tra mới
                </button>
                <SeoPanel data={auditData} />
              </div>
            )}
          </>
        )}

        {/* ── CRO & Trust Tab ── */}
        {activeTab === "cro" && (
          <>
            {!auditData && (
              <div className="phase3-prompt">
                <p>Hãy chạy Kiểm tra SEO trước để xem phân tích CRO &amp; Uy tín cho trang đó.</p>
              </div>
            )}
            {auditData && (
              <div className="result-wrapper">
                <button className="reset-btn" onClick={resetAudit} aria-label="New audit">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                    <path d="M3 3v5h5" />
                  </svg>
                  Kiểm tra mới
                </button>
                <CroDashboard cro={auditData.cro_analysis} />
              </div>
            )}
          </>
        )}

        {/* ── Competitor Radar Tab ── */}
        {activeTab === "competitor" && (
          <>
            <form className="audit-form" onSubmit={handleCompetitorSubmit} noValidate>
              <div className="hint-box">
                📊 <strong>Gợi ý:</strong> Nhập URL bài viết của bạn và 2–5 URL đối thủ cùng chủ đề để so sánh nội dung. Mỗi dòng một URL đối thủ.
              </div>
              <div className="input-group">
                <label htmlFor="comp-my-url" className="input-label">URL trang của bạn (tùy chọn — làm cơ sở so sánh)</label>
                <div className="input-wrap">
                  <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" />
                  </svg>
                  <input id="comp-my-url" type="url" className="text-input"
                    placeholder="https://trangcuaban.com/bai-viet"
                    value={compMyUrl} onChange={(e) => setCompMyUrl(e.target.value)}
                    autoComplete="off" />
                </div>
              </div>
              <div className="input-group">
                <label htmlFor="comp-urls" className="input-label">URL đối thủ (mỗi dòng một URL)</label>
                <textarea
                  id="comp-urls"
                  className="text-input"
                  rows={4}
                  placeholder={"https://competitor.com/article-1\nhttps://competitor.com/article-2\nhttps://rival.com/best-guide"}
                  value={compUrls} onChange={(e) => setCompUrls(e.target.value)}
                />
              </div>
              <div className="input-group">
                <label htmlFor="comp-keyword" className="input-label">Từ khóa chính</label>
                <div className="input-wrap">
                  <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                  </svg>
                  <input id="comp-keyword" type="text" className="text-input"
                    placeholder="ví dụ: dịch vụ hosting tốt nhất 2025"
                    value={compKeyword} onChange={(e) => setCompKeyword(e.target.value)}
                    autoComplete="off" />
                </div>
              </div>
              <LoadingBtn loading={compLoading} disabled={!compUrls.trim()}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                </svg>
                Phân tích đối thủ
              </LoadingBtn>
              {compError && (
                <p className="error-msg" role="alert">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                  </svg>
                  {compError}
                </p>
              )}
            </form>

            {compData && (
              <div className="result-wrapper">
                <CompetitorRadarPanel data={compData} />
              </div>
            )}
          </>
        )}

        {/* ── AI Content Writer Tab ── */}
        {activeTab === "planner" && (
          <>
            <form className="audit-form" onSubmit={handlePlanSubmit} noValidate>
              <div className="input-row">
                <div className="input-group">
                  <label htmlFor="plan-keyword" className="input-label">Từ khóa chính</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                    </svg>
                    <input id="plan-keyword" type="text" className="text-input"
                      placeholder="ví dụ: dịch vụ hosting tốt nhất 2025"
                      value={planKeyword} onChange={(e) => setPlanKeyword(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <div className="input-group">
                  <label htmlFor="plan-audience" className="input-label">Đối tượng mục tiêu</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" />
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </svg>
                    <input id="plan-audience" type="text" className="text-input"
                      placeholder="ví dụ: người làm podcast, 1K–50K lượt nghe"
                      value={planAudience} onChange={(e) => setPlanAudience(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <LoadingBtn loading={planLoading} disabled={!planKeyword.trim() || !planAudience.trim()}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                    <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                  </svg>
                  Tạo kế hoạch
                </LoadingBtn>
              </div>
              {compData && compData.blueprint.must_fill_gaps.length > 0 && (
                <p className="gap-hint">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                  {compData.blueprint.must_fill_gaps.length} lỗ hổng đối thủ sẽ được xử lý trong dàn ý.
                </p>
              )}
              {planError && (
                <p className="error-msg" role="alert">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                  </svg>
                  {planError}
                </p>
              )}
            </form>

            {planData && (
              <div className="result-wrapper">
                <ContentPlannerPanel
                  plan={planData}
                  onPublish={(title, content) =>
                    setPublishModal({ articleTitle: title, articleContent: content })
                  }
                />
                <button
                  type="button"
                  className="publish-wp-btn"
                  onClick={() => {
                    // Guard: prevent publishing placeholder skeleton without warning.
                    // Users must use the Polish panel to write real content first.
                    const placeholders = planData.sections
                      .map((s) => `[Write section ${s.section_number} here`)
                      .join(", ");
                    const confirmed = window.confirm(
                      `⚠️ Publishing this outline will send placeholder content:\n"${placeholders}"\n\n` +
                      `Use the AI Writer tab to generate full article sections before publishing. ` +
                      `Are you sure you want to publish anyway?`
                    );
                    if (!confirmed) return;
                    const outlineText = planData.sections
                      .map((s) => `## ${s.heading}\n\n[Write section ${s.section_number} here — ${s.word_target} words]`)
                      .join("\n\n");
                    const draftContent = `# ${planData.topic}\n\n${outlineText}`;
                    setPublishModal({
                      articleTitle: planData.meta.title_options[0] || planData.topic,
                      articleContent: draftContent,
                    });
                  }}
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                  </svg>
                  Publish to WordPress
                </button>
              </div>
            )}
          </>
        )}

        {/* ── Campaign Tracker Tab ── */}
        {activeTab === "tracker" && (
          <>
            {/* ── Data Connections ── */}
            <div className="data-connections-bar">
              <div className="data-conn-label">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                  <path d="M21 2H3v16h5v-4l4-4 4 4v-6h7V2z"/>
                </svg>
                Kết nối dữ liệu
              </div>
              <div className="connector-cards">
                <div className={`connector-card ${trackGscStatus === "connected" ? "conn-ok" : trackGscStatus === "pending" ? "conn-pending" : "conn-off"}`}>
                  <div className="conn-dot" />
                  <span className="conn-name">Google Workspace</span>
                  <span className="conn-status">
                    {trackGscStatus === "connected" ? "Hoạt động" : trackGscStatus === "pending" ? "Chờ kết nối" : "Ngắt"}
                  </span>
                </div>
                <div className={`connector-card ${trackDfsStatus === "connected" ? "conn-ok" : trackDfsStatus === "pending" ? "conn-pending" : "conn-off"}`}>
                  <div className="conn-dot" />
                  <span className="conn-name">DataForSEO</span>
                  <span className="conn-status">
                    {trackDfsStatus === "connected" ? "Hoạt động" : trackDfsStatus === "pending" ? "Chờ kết nối" : "Ngắt"}
                  </span>
                </div>
              </div>
            </div>
            {trackMockFallback && (
              <div className="mock-warning-banner" role="alert">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>
                  {trackFallbackReason ? (
                    <>
                      <strong>Tự động điền thất bại:</strong> {trackFallbackReason} —{" "}
                      Biểu mẫu đã được điền bằng số liệu ước tính. Cấu hình GSC / DataForSEO để có dữ liệu thật.
                    </>
                  ) : (
                    <>
                      <strong>Dữ liệu ước tính:</strong> Chưa cấu hình GSC hoặc DataForSEO — kết quả chỉ mang tính tham khảo.
                    </>
                  )}
                </span>
              </div>
            )}
            {autofillError && (
              <div className="mock-warning-banner" role="alert" style={{ borderColor: "#ef4444" }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" aria-hidden="true">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>
                  <strong>Lỗi tự điền:</strong> {autofillError} — Biểu mẫu đã được điền bằng số liệu ước tính.
                </span>
              </div>
            )}

            {/* ── GSC Config Panel ── */}
            <div className="gsc-config-section">
              <button className="gsc-config-toggle" type="button" onClick={() => setGscConfigOpen(!gscConfigOpen)}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                </svg>
                {gscConfigOpen ? "▲ Đóng cấu hình GSC" : "▼ Cấu hình Google Search Console (lấy dữ liệu thật)"}
              </button>

              {gscConfigOpen && (
                <div className="gsc-config-panel">
                  <div className="gsc-guide">
                    <h4>📖 Hướng dẫn lấy thông tin:</h4>
                    <ol>
                      <li>Truy cập <a href="https://console.cloud.google.com" target="_blank" rel="noreferrer">Google Cloud Console</a> → tạo Project mới</li>
                      <li>Vào <strong>APIs & Services</strong> → <strong>Library</strong> → tìm "Google Search Console API" → <strong>Enable</strong></li>
                      <li>Vào <strong>OAuth consent screen</strong> → chọn External → điền tên app → thêm email vào Test users</li>
                      <li>Vào <strong>Credentials</strong> → <strong>Create OAuth client ID</strong> → Web application</li>
                      <li>Thêm Redirect URI: <code>http://localhost:8000/callback</code></li>
                      <li>Copy <strong>Client ID</strong> và <strong>Client Secret</strong> điền vào bên dưới</li>
                      <li>Để lấy <strong>Refresh Token</strong>: mở link OAuth (xem TECH_REPORT.md mục 11) → cấp quyền → đổi code</li>
                    </ol>
                  </div>

                  <div className="gsc-fields">
                    <div className="input-group">
                      <label className="input-label">Client ID</label>
                      <input className="text-input gsc-input" type="text"
                        placeholder="xxxx.apps.googleusercontent.com"
                        value={gscClientId} onChange={e => setGscClientId(e.target.value)} />
                    </div>
                    <div className="input-group">
                      <label className="input-label">Client Secret</label>
                      <input className="text-input gsc-input" type="password"
                        placeholder="GOCSPX-xxxxxxxxxxxx"
                        value={gscSecret} onChange={e => setGscSecret(e.target.value)} />
                    </div>
                    <div className="input-group">
                      <label className="input-label">Refresh Token</label>
                      <input className="text-input gsc-input" type="password"
                        placeholder="1//xxxxxxxxxxxx"
                        value={gscRefreshToken} onChange={e => setGscRefreshToken(e.target.value)} />
                    </div>
                    <div className="input-group">
                      <label className="input-label">URL Website (từ GSC)</label>
                      <input className="text-input gsc-input" type="url"
                        placeholder="https://yourwebsite.com/"
                        value={gscSiteUrl} onChange={e => setGscSiteUrl(e.target.value)} />
                    </div>
                    <button type="button" className="analyze-btn" style={{alignSelf:"flex-start"}} onClick={handleSaveGscConfig}
                      disabled={!gscClientId || !gscSecret || !gscRefreshToken || !gscSiteUrl}>
                      💾 Lưu cấu hình
                    </button>
                    {gscSaveMsg && <p className="gsc-save-msg">{gscSaveMsg}</p>}
                  </div>
                </div>
              )}
            </div>

            <form className="audit-form" onSubmit={handleTrackerSubmit} noValidate>
              <div className="hint-box">
                📍 <strong>Gợi ý:</strong> Nhập URL thuộc domain đã cấu hình trong GSC để lấy dữ liệu thật. Domain khác sẽ dùng số liệu ước tính.
              </div>
              <div className="input-row">
                <div className="input-group">
                  <label htmlFor="track-url" className="input-label">URL trang của bạn</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                    </svg>
                    <input id="track-url" type="url" className="text-input"
                      placeholder="https://trangcuaban.com/bai-viet"
                      value={trackUrl} onChange={(e) => setTrackUrl(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <div className="input-group">
                  <label htmlFor="track-kw" className="input-label">Từ khóa mục tiêu</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                    </svg>
                    <input id="track-kw" type="text" className="text-input"
                      placeholder="ví dụ: dịch vụ hosting tốt nhất"
                      value={trackKeyword} onChange={(e) => setTrackKeyword(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <LoadingBtn loading={trackLoading} disabled={!trackUrl.trim() || !trackKeyword.trim()}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                    <line x1="18" y1="20" x2="18" y2="10" />
                    <line x1="12" y1="20" x2="12" y2="4" />
                    <line x1="6"  y1="20" x2="6"  y2="14" />
                  </svg>
                  Phân tích cơ hội
                </LoadingBtn>
                <button
                  type="button"
                  className="autofill-btn"
                  onClick={handleAutoFill}
                  disabled={autofillLoading || !trackUrl.trim() || !trackKeyword.trim()}
                  title="Lấy số liệu thực từ GSC & DataForSEO, hoặc dữ liệu mẫu nếu chưa cấu hình"
                >
                  {autofillLoading ? (
                    <span className="btn-spinner" aria-label="Auto-filling" />
                  ) : (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                    </svg>
                  )}
                  Tự động điền
                </button>
              </div>
              {/* Optional GSC fields */}
              <div className="gsc-row">
                <div className="input-group">
                  <label htmlFor="track-pos" className="input-label-sm">Vị trí hiện tại (GSC)</label>
                  <input id="track-pos" type="number" className="text-input" placeholder="VD: 12"
                    value={trackPosition} onChange={(e) => setTrackPosition(e.target.value)} min="1" max="200" />
                </div>
                <div className="input-group">
                  <label htmlFor="track-imp" className="input-label-sm">Lượt hiển thị/tháng</label>
                  <input id="track-imp" type="number" className="text-input" placeholder="VD: 1500"
                    value={trackImpressions} onChange={(e) => setTrackImpressions(e.target.value)} min="0" />
                </div>
                <div className="input-group">
                  <label htmlFor="track-clk" className="input-label-sm">Lượt nhấp/tháng</label>
                  <input id="track-clk" type="number" className="text-input" placeholder="VD: 45"
                    value={trackClicks} onChange={(e) => setTrackClicks(e.target.value)} min="0" />
                </div>
                <div className="input-group">
                  <label htmlFor="track-vol" className="input-label-sm">Lượng tìm kiếm (tùy chọn)</label>
                  <input id="track-vol" type="number" className="text-input" placeholder="VD: 2400"
                    value={trackVolume} onChange={(e) => setTrackVolume(e.target.value)} min="0" />
                </div>
                <div className="input-group">
                  <label htmlFor="track-diff" className="input-label-sm">Độ khó 0–100 (tùy chọn)</label>
                  <input id="track-diff" type="number" className="text-input" placeholder="VD: 45"
                    value={trackDifficulty} onChange={(e) => setTrackDifficulty(e.target.value)} min="0" max="100" />
                </div>
              </div>
              {trackError && (
                <p className="error-msg" role="alert">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                  </svg>
                  {trackError}
                </p>
              )}
            </form>

            {trackData && (
              <div className="result-wrapper">
                <CampaignTrackerPanel data={trackData} />
              </div>
            )}
          </>
        )}

        {/* ── SERP Live Tab ── */}
        {activeTab === "serp" && (
          <>
            <form className="audit-form" onSubmit={(e) => {
              e.preventDefault();
              if (!serpKeyword.trim()) return;
              searchSerp(serpKeyword.trim(), serpLocation, serpNumResults).then(() => {
                addToHistory({
                  type: "serp",
                  keyword: serpKeyword.trim(),
                  summary: `SERP search: ${serpKeyword.trim()} (${serpLocation})`,
                });
              });
            }} noValidate>
              <div className="input-row">
                <div className="input-group">
                  <label htmlFor="serp-kw" className="input-label">Từ khóa tìm kiếm</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                    </svg>
                    <input id="serp-kw" type="text" className="text-input"
                      placeholder="ví dụ: dịch vụ hosting tốt nhất"
                      value={serpKeyword} onChange={(e) => setSerpKeyword(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <div className="input-group" style={{ maxWidth: "160px" }}>
                  <label htmlFor="serp-loc" className="input-label">Khu vực ưu tiên</label>
                  <select id="serp-loc" className="text-input" value={serpLocation}
                    onChange={(e) => setSerpLocation(e.target.value)}
                    title="DuckDuckGo ưu tiên kết quả theo khu vực. Từ khóa tiếng Việt luôn trả về kết quả VN.">
                    <option value="vn">🇻🇳 Việt Nam</option>
                    <option value="us">🇺🇸 Hoa Kỳ</option>
                    <option value="uk">🇬🇧 Anh</option>
                    <option value="au">🇦🇺 Úc</option>
                    <option value="sg">🇸🇬 Singapore</option>
                    <option value="in">🇮🇳 Ấn Độ</option>
                    <option value="jp">🇯🇵 Nhật Bản</option>
                  </select>
                </div>
                <div className="input-group" style={{ maxWidth: "100px" }}>
                  <label htmlFor="serp-num" className="input-label">Kết quả</label>
                  <select id="serp-num" className="text-input" value={serpNumResults}
                    onChange={(e) => setSerpNumResults(parseInt(e.target.value))}>
                    <option value={10}>Top 10</option>
                    <option value={15}>Top 15</option>
                    <option value={20}>Top 20</option>
                  </select>
                </div>
                <LoadingBtn loading={serpLoading} disabled={!serpKeyword.trim()}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                    <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
                    <path d="M3.6 9h16.8" />
                  </svg>
                  Tìm kiếm SERP
                </LoadingBtn>
              </div>
              {serpError && (
                <p className="error-msg" role="alert">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                  </svg>
                  {serpError}
                </p>
              )}
            </form>

            {serpData && (
              <div className="result-wrapper">
                <button className="reset-btn" onClick={resetSerp} aria-label="New search">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                    <path d="M3 3v5h5" />
                  </svg>
                  Tìm kiếm mới
                </button>
                <SerpResultsPanel data={serpData} />
              </div>
            )}
          </>
        )}

        {/* AI Keywords Tab */}
        {activeTab === "aikeys" && (
          <>
            <form className="audit-form" onSubmit={handleAiKeysAnalyze} noValidate>
              <div className="hint-box">
                🤖 <strong>Phân tích từ khóa AI:</strong> Lấy toàn bộ từ khóa từ Google Search Console, phân tích hiệu suất và đề xuất chiến lược từ khóa mới.
              </div>
              <div className="input-row">
                <div className="input-group">
                  <label htmlFor="aikeys-target" className="input-label">Từ khóa mục tiêu (tùy chọn)</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" /></svg>
                    <input id="aikeys-target" type="text" className="text-input"
                      placeholder="ví dụ: mitsubishi bình phước"
                      value={aiKeysTarget} onChange={e => setAiKeysTarget(e.target.value)} />
                  </div>
                </div>
                <LoadingBtn loading={aiKeysLoading}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /></svg>
                  Phân tích GSC + AI
                </LoadingBtn>
              </div>
              {aiKeysError && (
                <p className="error-msg" role="alert">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" /></svg>
                  {aiKeysError}
                </p>
              )}
            </form>

            {aiKeysData && (
              <div className="result-wrapper">
                <button className="reset-btn" onClick={() => setAiKeysData(null)}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /><path d="M3 3v5h5" /></svg>
                  Phân tích mới
                </button>

                <ResultPanel>
                  <div className="result-header">
                    <div className="result-meta">
                      <h2 className="result-title">📊 Phân tích từ khóa — {aiKeysData.site_url}</h2>
                      <p className="result-keyword">Nguồn: <strong>{aiKeysData.data_source === "live_gsc" ? "✅ GSC thật" : "🟡 Ước tính"}</strong> | AI: <strong>{aiKeysData.ai_provider === "ai" ? "✅ AI" : "⚙️ Thuật toán"}</strong></p>
                    </div>
                  </div>
                  <div className="result-grid">
                    <ResultCard label="Từ khóa GSC" value={aiKeysData.gsc_keywords?.length || 0} />
                    <ResultCard label="Tổng clicks" value={aiKeysData.total_clicks || 0} />
                    <ResultCard label="Tổng hiển thị" value={aiKeysData.total_impressions || 0} />
                    <ResultCard label="Quick wins" value={aiKeysData.quick_wins?.length || 0} />
                  </div>
                  {aiKeysData.summary && (
                    <div className="section-block">
                      <h3 className="section-title">Tóm tắt</h3>
                      <p style={{fontSize:"13px",lineHeight:1.7,color:"var(--text)"}}>{aiKeysData.summary}</p>
                    </div>
                  )}
                </ResultPanel>

                {aiKeysData.gsc_keywords?.length > 0 && (
                  <ResultPanel>
                    <h3 className="section-title">📊 Từ khóa từ Google Search Console ({aiKeysData.gsc_keywords.length})</h3>
                    <div style={{overflowX:"auto"}}>
                      <table className="serp-table">
                        <thead><tr><th>#</th><th>Từ khóa</th><th>Vị trí</th><th>Clicks</th><th>Hiển thị</th><th>CTR</th></tr></thead>
                        <tbody>
                          {aiKeysData.gsc_keywords.slice(0, 30).map((kw: any, i: number) => (
                            <tr key={i}>
                              <td>{i + 1}</td>
                              <td style={{fontWeight:600,color:"var(--text-h)"}}>{kw.keyword}</td>
                              <td style={{color: kw.position <= 10 ? "var(--green)" : kw.position <= 20 ? "var(--amber)" : "var(--red)"}}>{kw.position}</td>
                              <td>{kw.clicks}</td>
                              <td>{kw.impressions}</td>
                              <td>{(kw.ctr * 100).toFixed(1)}%</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </ResultPanel>
                )}

                {aiKeysData.quick_wins?.length > 0 && (
                  <ResultPanel>
                    <h3 className="section-title">⚡ Quick Wins</h3>
                    <div style={{display:"flex",flexDirection:"column",gap:"8px"}}>
                      {aiKeysData.quick_wins.map((qw: any, i: number) => (
                        <div key={i} className="rec-badge priority-important">
                          <span className="rec-tag" style={{background:"rgba(245,158,11,0.3)",color:"var(--amber)"}}>pos {qw.current_position}</span>
                          <div>
                            <strong style={{color:"var(--text-h)"}}>{qw.keyword}</strong>
                            <p style={{fontSize:"12px",margin:"4px 0 0",color:"var(--text)"}}>{qw.action}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ResultPanel>
                )}

                {aiKeysData.keyword_clusters?.length > 0 && (
                  <ResultPanel>
                    <h3 className="section-title">🗂️ Nhóm từ khóa (Clusters)</h3>
                    <div className="cro-grid">
                      {aiKeysData.keyword_clusters.map((c: any, i: number) => (
                        <div key={i} className="glass-card">
                          <h4 className="glass-card-title">{c.cluster_name}</h4>
                          <div className="lsi-tags">
                            {(c.keywords || []).map((k: string, j: number) => (
                              <span key={j} className="lsi-tag">{k}</span>
                            ))}
                          </div>
                          {c.suggested_content && <p style={{fontSize:"12px",color:"var(--text)",marginTop:"4px"}}>📝 {c.suggested_content}</p>}
                        </div>
                      ))}
                    </div>
                  </ResultPanel>
                )}

                {aiKeysData.recommended_keywords?.length > 0 && (
                  <ResultPanel>
                    <h3 className="section-title">🎯 Từ khóa đề xuất mới</h3>
                    <div style={{display:"flex",flexDirection:"column",gap:"8px"}}>
                      {aiKeysData.recommended_keywords.map((r: any, i: number) => (
                        <div key={i} className="rec-badge priority-nice_to_have">
                          <span className="rec-tag">{r.priority}</span>
                          <div>
                            <strong style={{color:"var(--text-h)"}}>{r.keyword}</strong>
                            <p style={{fontSize:"12px",margin:"4px 0 0",color:"var(--text)"}}>{r.reason}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ResultPanel>
                )}

                {aiKeysData.content_strategy?.length > 0 && (
                  <ResultPanel>
                    <h3 className="section-title">📝 Chiến lược nội dung</h3>
                    <div style={{display:"flex",flexDirection:"column",gap:"8px"}}>
                      {aiKeysData.content_strategy.map((s: any, i: number) => (
                        <div key={i} className="rec-badge priority-nice_to_have">
                          <span className="rec-tag">{s.content_type || "blog"}</span>
                          <div>
                            <strong style={{color:"var(--text-h)"}}>{s.title}</strong>
                            <p style={{fontSize:"12px",margin:"4px 0 0",color:"var(--text)"}}>{s.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ResultPanel>
                )}

                {aiKeysData.ai_error && (
                  <div className="mock-warning-banner">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    <span><strong>AI không khả dụng:</strong> {aiKeysData.ai_error} — Đang dùng phân tích thuật toán.</span>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Rank Tracker Tab */}
        {activeTab === "ranktracker" && <RankTracker />}

        {/* Spin Editor Tab */}
        {activeTab === "spineditor" && <SpinEditor />}

        {/* GEO Optimizer Tab */}
        {activeTab === "geo" && <GeoOptimizer />}

      </main>

      <footer className="page-footer">
        AI Marketing Hub — Phiên bản 13 &nbsp;&middot;&nbsp; Xây dựng với FastAPI + React
      </footer>

      {publishModal && (
        <PublishModal
          articleTitle={publishModal.articleTitle}
          articleContent={publishModal.articleContent}
          onClose={() => setPublishModal(null)}
        />
      )}
    </div>
    </ErrorBoundary>
  );
}
