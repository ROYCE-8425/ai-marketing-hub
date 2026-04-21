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
import { PublishModal } from "./components/PublishModal";
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

type TabId = "seo" | "cro" | "competitor" | "planner" | "tracker" | "serp";

const TABS: { id: TabId; label: string; icon: JSX.Element }[] = [
  {
    id: "seo",
    label: "SEO Audit",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
      </svg>
    ),
  },
  {
    id: "cro",
    label: "CRO & Trust",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
        <polyline points="16 7 22 7 22 13" />
      </svg>
    ),
  },
  {
    id: "competitor",
    label: "Competitor Radar",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
    ),
  },
  {
    id: "planner",
    label: "AI Content Writer",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
      </svg>
    ),
  },
  {
    id: "tracker",
    label: "Campaign Tracker",
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
    label: "SERP Live",
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
        <path d="M3.6 9h16.8M3.6 15h16.8" />
        <path d="M12 3a15 15 0 0 1 0 18 15 15 0 0 1 0-18z" />
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
  const [activeTab, setActiveTab] = useState<TabId>("seo");
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

  // Data connection status (updated by AutoFill)
  const [trackGscStatus, setTrackGscStatus] = useState<"connected" | "disconnected" | "pending">("pending");
  const [trackDfsStatus, setTrackDfsStatus] = useState<"connected" | "disconnected" | "pending">("pending");
  const [trackMockFallback, setTrackMockFallback] = useState(false);
  const [trackFallbackReason, setTrackFallbackReason] = useState<string | null>(null);
  const { loading: autofillLoading, error: autofillError, autoFill } = useAutoFill();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || !keyword.trim()) return;
    analyze({ url: url.trim(), primary_keyword: keyword.trim() });
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
          <span className="nav-phase">Phase 8</span>
        </div>
      </nav>

      <main className="main-content">
        {/* Hero — only shown on SEO tab */}
        {activeTab === "seo" && (
          <div className="hero-block">
            <h1 className="hero-title">
              Full <span className="hero-accent">Marketing Audit</span>
              <br />from any URL
            </h1>
            <p className="hero-sub">
              Paste a link, add your target keyword — get SEO quality, CRO insights,
              and trust signal analysis in one click.
            </p>
          </div>
        )}

        <TabBar active={activeTab} onChange={setActiveTab} />

        {/* ── SEO Audit Tab ── */}
        {activeTab === "seo" && (
          <>
            <form className="audit-form" onSubmit={handleSubmit} noValidate>
              <div className="input-row">
                <div className="input-group">
                  <label htmlFor="url-input" className="input-label">Page URL</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                    </svg>
                    <input id="url-input" type="url" className="text-input"
                      placeholder="https://example.com/blog/post"
                      value={url} onChange={(e) => setUrl(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <div className="input-group">
                  <label htmlFor="keyword-input" className="input-label">Primary Keyword</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                    </svg>
                    <input id="keyword-input" type="text" className="text-input"
                      placeholder="e.g. best podcast hosting 2025"
                      value={keyword} onChange={(e) => setKeyword(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <LoadingBtn loading={auditLoading} disabled={!url.trim() || !keyword.trim()}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                  Analyze
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
                  New Audit
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
                <p>Run an SEO Audit first to see CRO &amp; Trust insights for that page.</p>
              </div>
            )}
            {auditData && (
              <div className="result-wrapper">
                <button className="reset-btn" onClick={resetAudit} aria-label="New audit">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                    <path d="M3 3v5h5" />
                  </svg>
                  New Audit
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
              <div className="input-group">
                <label htmlFor="comp-my-url" className="input-label">Your URL (optional — baseline)</label>
                <div className="input-wrap">
                  <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" />
                  </svg>
                  <input id="comp-my-url" type="url" className="text-input"
                    placeholder="https://yoursite.com/blog/your-post"
                    value={compMyUrl} onChange={(e) => setCompMyUrl(e.target.value)}
                    autoComplete="off" />
                </div>
              </div>
              <div className="input-group">
                <label htmlFor="comp-urls" className="input-label">Competitor URLs (one per line)</label>
                <textarea
                  id="comp-urls"
                  className="text-input"
                  rows={4}
                  placeholder={"https://competitor.com/article-1\nhttps://competitor.com/article-2\nhttps://rival.com/best-guide"}
                  value={compUrls} onChange={(e) => setCompUrls(e.target.value)}
                />
              </div>
              <div className="input-group">
                <label htmlFor="comp-keyword" className="input-label">Primary Keyword</label>
                <div className="input-wrap">
                  <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                  </svg>
                  <input id="comp-keyword" type="text" className="text-input"
                    placeholder="e.g. best podcast hosting 2025"
                    value={compKeyword} onChange={(e) => setCompKeyword(e.target.value)}
                    autoComplete="off" />
                </div>
              </div>
              <LoadingBtn loading={compLoading} disabled={!compUrls.trim()}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                </svg>
                Analyze Competitors
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
                  <label htmlFor="plan-keyword" className="input-label">Primary Keyword</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                    </svg>
                    <input id="plan-keyword" type="text" className="text-input"
                      placeholder="e.g. best podcast hosting 2025"
                      value={planKeyword} onChange={(e) => setPlanKeyword(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <div className="input-group">
                  <label htmlFor="plan-audience" className="input-label">Target Audience</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" />
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </svg>
                    <input id="plan-audience" type="text" className="text-input"
                      placeholder="e.g. podcast creators, 1K–50K listeners"
                      value={planAudience} onChange={(e) => setPlanAudience(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <LoadingBtn loading={planLoading} disabled={!planKeyword.trim() || !planAudience.trim()}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                    <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                  </svg>
                  Generate Plan
                </LoadingBtn>
              </div>
              {compData && compData.blueprint.must_fill_gaps.length > 0 && (
                <p className="gap-hint">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                  {compData.blueprint.must_fill_gaps.length} competitor gaps will be addressed in the outline.
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
                Data Connections
              </div>
              <div className="connector-cards">
                <div className={`connector-card ${trackGscStatus === "connected" ? "conn-ok" : trackGscStatus === "pending" ? "conn-pending" : "conn-off"}`}>
                  <div className="conn-dot" />
                  <span className="conn-name">Google Workspace</span>
                  <span className="conn-status">
                    {trackGscStatus === "connected" ? "Live" : trackGscStatus === "pending" ? "Pending" : "Disconnected"}
                  </span>
                </div>
                <div className={`connector-card ${trackDfsStatus === "connected" ? "conn-ok" : trackDfsStatus === "pending" ? "conn-pending" : "conn-off"}`}>
                  <div className="conn-dot" />
                  <span className="conn-name">DataForSEO</span>
                  <span className="conn-status">
                    {trackDfsStatus === "connected" ? "Live" : trackDfsStatus === "pending" ? "Pending" : "Disconnected"}
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
                      <strong>Auto-fill failed:</strong> {trackFallbackReason} —{" "}
                      Form was populated with estimated metrics. Configure GSC / DataForSEO credentials for live data.
                    </>
                  ) : (
                    <>
                      <strong>Mock data:</strong> No GSC or DataForSEO credentials are configured — results are for preview only.
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
                  <strong>Auto-fill error:</strong> {autofillError} — Form was populated with estimated metrics instead.
                </span>
              </div>
            )}

            <form className="audit-form" onSubmit={handleTrackerSubmit} noValidate>
              <div className="input-row">
                <div className="input-group">
                  <label htmlFor="track-url" className="input-label">Your URL</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                    </svg>
                    <input id="track-url" type="url" className="text-input"
                      placeholder="https://yoursite.com/blog/post"
                      value={trackUrl} onChange={(e) => setTrackUrl(e.target.value)}
                      required autoComplete="off" />
                  </div>
                </div>
                <div className="input-group">
                  <label htmlFor="track-kw" className="input-label">Target Keyword</label>
                  <div className="input-wrap">
                    <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                    </svg>
                    <input id="track-kw" type="text" className="text-input"
                      placeholder="e.g. best podcast hosting"
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
                  Analyze Opportunity
                </LoadingBtn>
                <button
                  type="button"
                  className="autofill-btn"
                  onClick={handleAutoFill}
                  disabled={autofillLoading || !trackUrl.trim() || !trackKeyword.trim()}
                  title="Fetch live metrics from GSC & DataForSEO, or mock data if not configured"
                >
                  {autofillLoading ? (
                    <span className="btn-spinner" aria-label="Auto-filling" />
                  ) : (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                    </svg>
                  )}
                  Auto-Fill Metrics
                </button>
              </div>
              {/* Optional GSC fields */}
              <div className="gsc-row">
                <div className="input-group">
                  <label htmlFor="track-pos" className="input-label-sm">Current Position (GSC)</label>
                  <input id="track-pos" type="number" className="text-input" placeholder="e.g. 12"
                    value={trackPosition} onChange={(e) => setTrackPosition(e.target.value)} min="1" max="200" />
                </div>
                <div className="input-group">
                  <label htmlFor="track-imp" className="input-label-sm">Monthly Impressions</label>
                  <input id="track-imp" type="number" className="text-input" placeholder="e.g. 1500"
                    value={trackImpressions} onChange={(e) => setTrackImpressions(e.target.value)} min="0" />
                </div>
                <div className="input-group">
                  <label htmlFor="track-clk" className="input-label-sm">Monthly Clicks</label>
                  <input id="track-clk" type="number" className="text-input" placeholder="e.g. 45"
                    value={trackClicks} onChange={(e) => setTrackClicks(e.target.value)} min="0" />
                </div>
                <div className="input-group">
                  <label htmlFor="track-vol" className="input-label-sm">Search Volume (optional)</label>
                  <input id="track-vol" type="number" className="text-input" placeholder="e.g. 2400"
                    value={trackVolume} onChange={(e) => setTrackVolume(e.target.value)} min="0" />
                </div>
                <div className="input-group">
                  <label htmlFor="track-diff" className="input-label-sm">Difficulty 0–100 (optional)</label>
                  <input id="track-diff" type="number" className="text-input" placeholder="e.g. 45"
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
              searchSerp(serpKeyword.trim(), serpLocation, serpNumResults);
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
                  <label htmlFor="serp-loc" className="input-label">Thị trường</label>
                  <select id="serp-loc" className="text-input" value={serpLocation}
                    onChange={(e) => setSerpLocation(e.target.value)}>
                    <option value="vn">🇻🇳 Việt Nam</option>
                    <option value="us">🇺🇸 United States</option>
                    <option value="uk">🇬🇧 United Kingdom</option>
                    <option value="au">🇦🇺 Australia</option>
                    <option value="sg">🇸🇬 Singapore</option>
                    <option value="in">🇮🇳 India</option>
                    <option value="jp">🇯🇵 Japan</option>
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
      </main>

      <footer className="page-footer">
        AI Marketing Hub — Phase 8 &nbsp;&middot;&nbsp; Built with FastAPI + React
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
