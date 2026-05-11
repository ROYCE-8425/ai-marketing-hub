import { useEffect, useState, useCallback } from "react";
import { getHistory, clearHistory, deleteHistoryEntry } from "../lib/history";
import type { HistoryEntry } from "../lib/history";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area, CartesianGrid,
  RadarChart, PolarGrid, PolarAngleAxis, Radar
} from "recharts";
import { API_BASE } from "../lib/apiConfig";
import "./DashboardOverview.css";

// ─── Colors ─────────────────────────────────────────────────────────────────

const COLORS = {
  purple: "#8b5cf6",
  blue: "#3b82f6",
  green: "#10b981",
  amber: "#f59e0b",
  red: "#ef4444",
  cyan: "#06b6d4",
  pink: "#ec4899",
};
const PIE_COLORS = ["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#06b6d4", "#ec4899"];

// ─── Stat Card ──────────────────────────────────────────────────────────────

function StatCard({
  icon, value, label, accent, subValue, subColor,
}: {
  icon: React.ReactNode; value: string | number; label: string;
  accent?: string; subValue?: string; subColor?: string;
}) {
  return (
    <div className="dash-card" style={{ "--card-accent": accent } as React.CSSProperties}>
      <div className="dash-card-icon">{icon}</div>
      <div className="dash-card-value">{value}</div>
      <div className="dash-card-label">{label}</div>
      {subValue && (
        <div className="dash-card-change positive" style={subColor ? { color: subColor } : {}}>
          {subValue}
        </div>
      )}
    </div>
  );
}

// ─── Mini chart tooltip ─────────────────────────────────────────────────────

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} style={{ color: p.color }}>
          {p.name}: <strong>{typeof p.value === "number" ? p.value.toLocaleString() : p.value}</strong>
        </p>
      ))}
    </div>
  );
}

// ─── Type badge ─────────────────────────────────────────────────────────────

const TYPE_LABELS: Record<string, { label: string; cls: string }> = {
  seo: { label: "SEO", cls: "type-seo" },
  serp: { label: "SERP", cls: "type-serp" },
  competitor: { label: "COMP", cls: "type-competitor" },
  content: { label: "CONTENT", cls: "type-content" },
};

function timeAgo(isoStr: string): string {
  const diff = Date.now() - new Date(isoStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "vừa xong";
  if (mins < 60) return `${mins} phút trước`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} giờ trước`;
  return `${Math.floor(hours / 24)} ngày trước`;
}

// ─── GSC data types ─────────────────────────────────────────────────────────

interface GscKeyword {
  keyword: string;
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

// ─── Dashboard Panel ────────────────────────────────────────────────────────

export function DashboardOverview({ onNavigate }: { onNavigate: (tab: string) => void }) {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [gscData, setGscData] = useState<{
    gsc_keywords: GscKeyword[];
    total_clicks: number;
    total_impressions: number;
    data_source: string;
  } | null>(null);
  const [gscLoading, setGscLoading] = useState(false);
  const [ga4Data, setGa4Data] = useState<any>(null);
  const [ga4Loading, setGa4Loading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState(false);
  const [serpOverview, setSerpOverview] = useState<any>(null);
  const [serpLoading, setSerpLoading] = useState(false);

  useEffect(() => {
    setHistory(getHistory());
  }, []);

  // Fetch GSC data for charts
  const fetchGscData = useCallback(async () => {
    setGscLoading(true);
    try {
      const res = await fetch(`${API_BASE}/ai-keywords`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (res.ok) {
        setGscData(await res.json());
      }
    } catch {
      // silent fail
    } finally {
      setGscLoading(false);
    }
  }, []);

  // Fetch GA4 data for charts
  const fetchGa4Data = useCallback(async () => {
    setGa4Loading(true);
    try {
      const res = await fetch(`${API_BASE}/ga4-overview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ days: 30 }),
      });
      if (res.ok) {
        setGa4Data(await res.json());
      }
    } catch {
      // silent fail
    } finally {
      setGa4Loading(false);
    }
  }, []);

  // Fetch SERP overview for dashboard (when GSC not connected)
  const fetchSerpOverview = useCallback(async () => {
    setSerpLoading(true);
    try {
      const r = await fetch(`${API_BASE}/serp/live`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword: "mitsubishi binh phuoc", location: "vn", num_results: 10 }),
      });
      if (r.ok) {
        const data = await r.json();
        if (data.organic_results?.length > 0) setSerpOverview(data);
      }
    } catch { /* silent */ }
    finally { setSerpLoading(false); }
  }, []);

  useEffect(() => {
    fetchGscData();
    fetchGa4Data();
    // Auto-fetch SERP overview
    fetchSerpOverview();
  }, [fetchGscData, fetchGa4Data, fetchSerpOverview]);

  // Listen for OAuth2 callback completion (postMessage from popup)
  useEffect(() => {
    const handler = (event: MessageEvent) => {
      if (event.data?.type === "google-oauth-complete") {
        // OAuth flow completed — reload GA4 data
        fetchGa4Data();
        fetchGscData();
      }
    };
    window.addEventListener("message", handler);
    return () => window.removeEventListener("message", handler);
  }, [fetchGa4Data, fetchGscData]);

  // 1-click Google OAuth2 setup
  const handleConnectGoogle = useCallback(async () => {
    setOauthLoading(true);
    try {
      const res = await fetch(`${API_BASE.replace('/api', '')}/auth/google/setup`);
      const data = await res.json();
      if (data.auth_url) {
        window.open(data.auth_url, "_blank", "width=600,height=700,scrollbars=yes");
      } else if (data.error) {
        alert(data.error);
      }
    } catch (err) {
      alert("Không thể kết nối đến backend. Kiểm tra server đang chạy.");
    } finally {
      setOauthLoading(false);
    }
  }, []);

  const handleClear = () => {
    if (confirm("Xóa toàn bộ lịch sử phân tích?")) {
      clearHistory();
      setHistory([]);
    }
  };

  const handleDelete = (id: string) => {
    deleteHistoryEntry(id);
    setHistory(getHistory());
  };

  // Stats
  const seoCount = history.filter((h) => h.type === "seo").length;
  const avgScore = seoCount > 0
    ? Math.round(
        history.filter((h) => h.type === "seo" && h.score != null)
          .reduce((sum, h) => sum + (h.score || 0), 0) /
          Math.max(1, history.filter((h) => h.type === "seo" && h.score != null).length)
      )
    : 0;

  // GSC chart data
  const gscKeywords = gscData?.gsc_keywords || [];
  const topByImpressions = [...gscKeywords].sort((a, b) => b.impressions - a.impressions).slice(0, 8);

  // Position distribution for pie chart
  const positionBuckets = [
    { name: "Top 3", value: gscKeywords.filter(k => k.position <= 3).length, color: COLORS.green },
    { name: "4-10", value: gscKeywords.filter(k => k.position > 3 && k.position <= 10).length, color: COLORS.blue },
    { name: "11-20", value: gscKeywords.filter(k => k.position > 10 && k.position <= 20).length, color: COLORS.amber },
    { name: "20+", value: gscKeywords.filter(k => k.position > 20).length, color: COLORS.red },
  ].filter(b => b.value > 0);

  // Performance radar data
  const avgCtr = gscKeywords.length > 0 ? gscKeywords.reduce((s, k) => s + k.ctr, 0) / gscKeywords.length * 100 : 0;
  const avgPos = gscKeywords.length > 0 ? gscKeywords.reduce((s, k) => s + k.position, 0) / gscKeywords.length : 0;
  const radarData = [
    { subject: "Từ khóa", value: Math.min(gscKeywords.length * 10, 100) },
    { subject: "CTR", value: Math.min(avgCtr * 10, 100) },
    { subject: "Lượt nhấp", value: Math.min((gscData?.total_clicks || 0) * 5, 100) },
    { subject: "Hiển thị", value: Math.min((gscData?.total_impressions || 0), 100) },
    { subject: "Vị trí", value: Math.max(0, 100 - avgPos * 3) },
    { subject: "Điểm SEO", value: avgScore },
  ];

  return (
    <div className="dashboard-v2">
      {/* Live Banners */}
      <div className="live-banners">
        {gscData && gscData.data_source === "live_gsc" && (
          <div className="gsc-live-banner">
            <div className="gsc-live-dot" />
            <span>GSC: {gscKeywords.length} từ khóa · {gscData.total_clicks} lượt nhấp · {gscData.total_impressions} hiển thị</span>
          </div>
        )}
        {gscData && gscData.data_source !== "live_gsc" && (
          <div className="gsc-live-banner" style={{ borderColor: 'rgba(245,158,11,0.2)', background: 'rgba(245,158,11,0.05)' }}>
            <div className="gsc-live-dot" style={{ background: '#f59e0b' }} />
            <span style={{ color: '#fcd34d' }}>GSC: 🟡 Chưa kết nối — Cấu hình OAuth2 credentials để xem dữ liệu thật</span>
            <button
              className="dash-connect-btn"
              onClick={handleConnectGoogle}
              disabled={oauthLoading}
            >
              {oauthLoading ? "⏳" : "🔗"} Kết nối Google
            </button>
          </div>
        )}
        {ga4Data && (() => {
          const isLive = ga4Data.data_source === 'live_ga4';
          const isPartial = ga4Data.data_source === 'partial_live_ga4';
          const hasError = !isLive && !isPartial;
          const borderColor = isLive ? 'rgba(99,102,241,0.3)' : isPartial ? 'rgba(245,158,11,0.25)' : 'rgba(239,68,68,0.2)';
          const bg = isLive ? 'rgba(99,102,241,0.06)' : hasError ? 'rgba(239,68,68,0.05)' : 'rgba(245,158,11,0.05)';
          const dotColor = isLive ? '#6366f1' : hasError ? '#ef4444' : '#f59e0b';
          const textColor = isLive ? '#a5b4fc' : hasError ? '#fca5a5' : '#fcd34d';
          const label = isLive
            ? `✅ Dữ liệu thật · ${ga4Data.overview?.sessions || 0} phiên · ${ga4Data.overview?.pageviews || 0} lượt xem`
            : isPartial
            ? `⚠️ Dữ liệu một phần · ${ga4Data.overview?.sessions || 0} phiên`
            : `🔴 Chưa kết nối`;
          return (
            <div className="gsc-live-banner" style={{ borderColor, background: bg }}>
              <div className="gsc-live-dot" style={{ background: dotColor }} />
              <span style={{ color: textColor }}>
                GA4: {label}
                {hasError && ga4Data.error && <> — {ga4Data.error}</>}
              </span>
              {hasError && (
                <button
                  className="dash-connect-btn"
                  onClick={handleConnectGoogle}
                  disabled={oauthLoading}
                >
                  {oauthLoading ? "⏳" : "🔗"} Kết nối Google Analytics
                </button>
              )}
            </div>
          );
        })()}
      </div>

      {/* SERP Quick Overview — shows when GSC is not connected */}
      {serpOverview && serpOverview.organic_results?.length > 0 && (
        <div className="chart-card" style={{ marginBottom: '0.5rem' }}>
          <h3 className="chart-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" /></svg>
            🌐 SERP Overview — "{serpOverview.keyword}" ({serpOverview.results_count} kết quả)
            {serpOverview._cached && <span style={{ fontSize: 10, color: '#6ee7b7', marginLeft: 8 }}>⚡ cached</span>}
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
            {serpOverview.organic_results.slice(0, 5).map((r: any, i: number) => (
              <a
                key={i}
                href={r.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'flex', alignItems: 'center', gap: '8px',
                  background: i === 0 ? 'rgba(16,185,129,0.1)' : 'var(--surface2)',
                  border: `1px solid ${i === 0 ? 'rgba(16,185,129,0.3)' : 'var(--border)'}`,
                  borderRadius: '8px', padding: '8px 12px', flex: '1 1 45%', minWidth: 0,
                  textDecoration: 'none', transition: 'border-color 0.2s',
                }}
              >
                <span style={{ fontSize: 18, fontWeight: 800, color: i === 0 ? '#10b981' : i < 3 ? '#3b82f6' : '#8892b0', fontFamily: 'DM Mono, monospace', flexShrink: 0, width: 28 }}>#{r.position}</span>
                <div style={{ minWidth: 0, flex: 1 }}>
                  <div style={{ fontSize: 12, color: '#e2e8f0', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.title}</div>
                  <div style={{ fontSize: 10, color: '#4a5578' }}>{r.domain}</div>
                </div>
              </a>
            ))}
          </div>
          {serpOverview.serp_features?.length > 0 && (
            <div style={{ display: 'flex', gap: '6px', marginTop: '8px', flexWrap: 'wrap' }}>
              {serpOverview.serp_features.map((f: string, i: number) => (
                <span key={i} style={{ fontSize: 10, background: 'rgba(139,92,246,0.15)', color: '#c4b5fd', padding: '2px 8px', borderRadius: '99px', border: '1px solid rgba(139,92,246,0.2)' }}>{f.replace(/_/g, ' ')}</span>
              ))}
            </div>
          )}
          <button className="dash-action-btn" onClick={() => onNavigate('serp')} style={{ marginTop: 8, fontSize: 12, padding: '6px 14px', width: 'fit-content' }}>
            🔍 Xem chi tiết SERP
          </button>
        </div>
      )}
      {serpLoading && !serpOverview && (
        <div className="chart-card" style={{ marginBottom: '0.5rem' }}>
          <div className="chart-empty">🔄 Đang tải SERP overview...</div>
        </div>
      )}

      {/* GSC + GA4 Stat cards */}
      <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
        <StatCard
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" /></svg>}
          value={ga4Data?.overview?.sessions || 0} label="Phiên truy cập"
          accent="linear-gradient(90deg, #6366f1, #8b5cf6)"
          subValue={ga4Data?.overview?.new_users ? `${ga4Data.overview.new_users} mới` : undefined}
          subColor={COLORS.cyan}
        />
        <StatCard
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>}
          value={ga4Data?.overview?.active_users || 0} label="Người dùng"
          accent="linear-gradient(90deg, #3b82f6, #2563eb)"
        />
        <StatCard
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>}
          value={ga4Data?.overview?.pageviews || 0} label="Lượt xem"
          accent="linear-gradient(90deg, #a855f7, #7c3aed)"
        />
        <StatCard
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" /><polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" /></svg>}
          value={gscData?.total_clicks || 0} label="Lượt nhấp GSC"
          accent="linear-gradient(90deg, #10b981, #059669)"
          subValue={`CTR ${avgCtr.toFixed(1)}%`}
          subColor={COLORS.green}
        />
        <StatCard
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>}
          value={`${ga4Data?.overview?.bounce_rate?.toFixed(1) || 0}%`} label="Tỷ lệ thoát"
          accent="linear-gradient(90deg, #f59e0b, #d97706)"
        />
        <StatCard
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 20V10" /><path d="M18 20V4" /><path d="M6 20v-4" /></svg>}
          value={`${ga4Data?.overview?.engagement_rate?.toFixed(1) || 0}%`} label="Tương tác"
          accent="linear-gradient(90deg, #06b6d4, #0891b2)"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="charts-row">
        {/* Keyword Impressions Bar Chart */}
        <div className="chart-card">
          <h3 className="chart-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" /></svg>
            Top từ khóa theo lượt hiển thị
          </h3>
          {topByImpressions.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={topByImpressions} margin={{ top: 5, right: 10, left: -15, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="keyword" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.4)" }} interval={0} angle={-25} textAnchor="end" height={60} />
                <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.4)" }} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="impressions" name="Hiển thị" fill={COLORS.purple} radius={[4, 4, 0, 0]} />
                <Bar dataKey="clicks" name="Clicks" fill={COLORS.cyan} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="chart-empty">{gscLoading ? "Đang tải dữ liệu GSC..." : "Chưa có dữ liệu"}</div>
          )}
        </div>

        {/* Position Distribution Pie Chart */}
        <div className="chart-card chart-card-sm">
          <h3 className="chart-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><path d="M12 2a10 10 0 0 1 10 10" /><path d="M12 12L12 2" /><path d="M12 12L22 12" /></svg>
            Phân bố vị trí
          </h3>
          {positionBuckets.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={positionBuckets} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" label={({ name, value }) => `${name} (${value})`} labelLine={false}>
                  {positionBuckets.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="chart-empty">{gscLoading ? "Đang tải..." : "Chưa có dữ liệu"}</div>
          )}
        </div>
      </div>

      {/* Charts Row 2: GA4 Sessions Timeline + Traffic Sources */}
      <div className="charts-row">
        {/* GA4 Sessions Timeline */}
        <div className="chart-card">
          <h3 className="chart-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>
            📈 Phiên & Lượt xem trang (30 ngày)
          </h3>
          {(ga4Data?.daily_sessions?.length || 0) > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={ga4Data.daily_sessions} margin={{ top: 5, right: 10, left: -15, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fontSize: 9, fill: "rgba(255,255,255,0.35)" }} interval={Math.max(0, Math.floor((ga4Data.daily_sessions.length - 1) / 8))} />
                <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.4)" }} />
                <Tooltip content={<ChartTooltip />} />
                <defs>
                  <linearGradient id="sessGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.blue} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={COLORS.blue} stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="pvGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.purple} stopOpacity={0.2} />
                    <stop offset="95%" stopColor={COLORS.purple} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area type="monotone" dataKey="sessions" name="Phiên" stroke={COLORS.blue} fill="url(#sessGrad)" strokeWidth={2} />
                <Area type="monotone" dataKey="pageviews" name="Lượt xem" stroke={COLORS.purple} fill="url(#pvGrad)" strokeWidth={1.5} strokeDasharray="4 2" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="chart-empty">{ga4Loading ? "Đang tải GA4..." : (ga4Data?.error ? `⚠️ ${ga4Data.error}` : "Chưa có dữ liệu GA4")}</div>
          )}
        </div>

        {/* Traffic Sources Pie */}
        <div className="chart-card chart-card-sm">
          <h3 className="chart-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><path d="M12 2a10 10 0 0 1 10 10" /><path d="M12 12L12 2" /><path d="M12 12L22 12" /></svg>
            🌐 Nguồn lưu lượng
          </h3>
          {(ga4Data?.traffic_sources?.length || 0) > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={ga4Data.traffic_sources.map((s: any) => ({ name: s.source, value: s.sessions }))} cx="50%" cy="50%" innerRadius={45} outerRadius={75} dataKey="value" label={({ name, value }: any) => `${name} (${value})`} labelLine={false}>
                  {ga4Data.traffic_sources.map((_: any, i: number) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="chart-empty">Chưa có dữ liệu</div>
          )}
        </div>
      </div>

      {/* Charts Row 3: Top Pages Table + Radar */}
      <div className="charts-row">
        {/* Top Pages Table */}
        <div className="chart-card">
          <h3 className="chart-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>
            📄 Trang hàng đầu (GA4)
          </h3>
          {(ga4Data?.top_pages?.length || 0) > 0 ? (
            <div className="top-pages-table">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Trang</th>
                    <th>Lượt xem</th>
                    <th>Phiên</th>
                    <th>Thoát</th>
                  </tr>
                </thead>
                <tbody>
                  {ga4Data.top_pages.slice(0, 8).map((p: any, i: number) => (
                    <tr key={i}>
                      <td className="rank">{i + 1}</td>
                      <td className="page-path" title={p.title || p.path}>{p.title || p.path}</td>
                      <td>{p.pageviews}</td>
                      <td>{p.sessions}</td>
                      <td style={{ color: p.bounce_rate > 60 ? '#fca5a5' : p.bounce_rate > 40 ? '#fcd34d' : '#6ee7b7' }}>{p.bounce_rate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="chart-empty">Chưa có dữ liệu</div>
          )}
        </div>

        {/* Performance Radar */}
        <div className="chart-card chart-card-sm">
          <h3 className="chart-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
            Hiệu suất tổng quan
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.5)" }} />
              <Radar name="Score" dataKey="value" stroke={COLORS.cyan} fill={COLORS.cyan} fillOpacity={0.2} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick actions */}
      <div className="dash-actions">
        <button className="dash-action-btn dash-action-primary" onClick={() => onNavigate("aikeys")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" /></svg>
          🤖 Phân tích từ khóa AI
        </button>
        <button className="dash-action-btn" onClick={() => onNavigate("seo")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" /></svg>
          Kiểm tra SEO
        </button>
        <button className="dash-action-btn" onClick={() => onNavigate("serp")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" /><path d="M3.6 9h16.8" /></svg>
          SERP trực tiếp
        </button>
        <button className="dash-action-btn" onClick={() => onNavigate("competitor")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
          Phân tích đối thủ
        </button>
        <button className="dash-action-btn" onClick={() => onNavigate("tracker")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" /></svg>
          Theo dõi chiến dịch
        </button>
        <button className="dash-action-btn" onClick={() => onNavigate("planner")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" /></svg>
          Viết nội dung
        </button>
      </div>

      {/* History */}
      <div className="dash-history">
        <div className="dash-history-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>
          Lịch sử phân tích
          {history.length > 0 && (
            <button className="export-btn" onClick={handleClear} style={{ marginLeft: "auto" }}>Xóa tất cả</button>
          )}
        </div>

        {history.length === 0 ? (
          <div className="dash-empty">
            <div className="dash-empty-icon">📊</div>
            <div className="dash-empty-text">Chưa có phân tích nào</div>
            <div className="dash-empty-sub">Bắt đầu bằng cách chạy SEO Audit hoặc Phân tích từ khóa AI</div>
          </div>
        ) : (
          <div className="dash-history-list">
            {history.slice(0, 15).map((entry) => {
              const typeInfo = TYPE_LABELS[entry.type] || { label: entry.type, cls: "" };
              return (
                <div key={entry.id} className="dash-history-item">
                  <span className={`history-type-badge ${typeInfo.cls}`}>{typeInfo.label}</span>
                  <span className="history-keyword">{entry.keyword}</span>
                  <span className="history-time">{timeAgo(entry.timestamp)}</span>
                  {entry.score != null && (
                    <span className="history-score" style={{
                      color: entry.score >= 80 ? "#6ee7b7" : entry.score >= 50 ? "#fcd34d" : "#fca5a5",
                    }}>{entry.score}</span>
                  )}
                  <button className="export-btn" onClick={(e) => { e.stopPropagation(); handleDelete(entry.id); }} title="Xóa" style={{ padding: "0.2rem 0.4rem" }}>✕</button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
