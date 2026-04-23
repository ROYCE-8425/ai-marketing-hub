import { useEffect, useState, useCallback } from "react";
import { getHistory, clearHistory, deleteHistoryEntry } from "../lib/history";
import type { HistoryEntry } from "../lib/history";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area, CartesianGrid,
  RadarChart, PolarGrid, PolarAngleAxis, Radar
} from "recharts";
import "./DashboardOverview.css";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

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

  useEffect(() => {
    fetchGscData();
  }, [fetchGscData]);

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
  const totalAnalyses = history.length;
  const seoCount = history.filter((h) => h.type === "seo").length;
  const serpCount = history.filter((h) => h.type === "serp").length;
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
  const topByClicks = [...gscKeywords].sort((a, b) => b.clicks - a.clicks).slice(0, 8);

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
    { subject: "Clicks", value: Math.min((gscData?.total_clicks || 0) * 5, 100) },
    { subject: "Hiển thị", value: Math.min((gscData?.total_impressions || 0), 100) },
    { subject: "Vị trí", value: Math.max(0, 100 - avgPos * 3) },
    { subject: "SEO Score", value: avgScore },
  ];

  // Activity data from history (last 7 days)
  const activityData = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    const dayStr = date.toLocaleDateString("vi-VN", { weekday: "short" });
    const dayStart = new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
    const dayEnd = dayStart + 86400000;
    const count = history.filter(h => {
      const t = new Date(h.timestamp).getTime();
      return t >= dayStart && t < dayEnd;
    }).length;
    return { name: dayStr, analyses: count };
  });

  return (
    <div className="dashboard-v2">
      {/* GSC Live Banner */}
      {gscData && gscData.data_source === "live_gsc" && (
        <div className="gsc-live-banner">
          <div className="gsc-live-dot" />
          <span>Dữ liệu thật từ Google Search Console — {gscKeywords.length} từ khóa · {gscData.total_clicks} clicks · {gscData.total_impressions} hiển thị (30 ngày)</span>
        </div>
      )}

      {/* Stat cards row */}
      <div className="dashboard-grid">
        <StatCard
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" /></svg>}
          value={totalAnalyses} label="Tổng phân tích"
          accent="linear-gradient(90deg, #8b5cf6, #6366f1)"
          subValue={gscData ? `${gscKeywords.length} từ khóa GSC` : undefined}
          subColor={COLORS.cyan}
        />
        <StatCard
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" /><polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" /></svg>}
          value={gscData?.total_clicks || 0} label="Clicks (30 ngày)"
          accent="linear-gradient(90deg, #3b82f6, #2563eb)"
          subValue={`CTR ${avgCtr.toFixed(1)}%`}
          subColor={COLORS.green}
        />
        <StatCard
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>}
          value={gscData?.total_impressions || 0} label="Hiển thị (30 ngày)"
          accent="linear-gradient(90deg, #a855f7, #7c3aed)"
          subValue={avgPos > 0 ? `Trung bình vị trí ${avgPos.toFixed(1)}` : undefined}
          subColor={COLORS.amber}
        />
        <StatCard
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 20V10" /><path d="M18 20V4" /><path d="M6 20v-4" /></svg>}
          value={avgScore > 0 ? `${avgScore}/100` : "—"} label="Điểm SEO TB"
          accent="linear-gradient(90deg, #10b981, #059669)"
          subValue={seoCount > 0 ? `${seoCount} audits` : undefined}
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

      {/* Charts Row 2 */}
      <div className="charts-row">
        {/* Activity Area Chart */}
        <div className="chart-card">
          <h3 className="chart-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>
            Hoạt động phân tích (7 ngày)
          </h3>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={activityData} margin={{ top: 5, right: 10, left: -15, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: "rgba(255,255,255,0.4)" }} />
              <YAxis tick={{ fontSize: 11, fill: "rgba(255,255,255,0.4)" }} allowDecimals={false} />
              <Tooltip content={<ChartTooltip />} />
              <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.purple} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={COLORS.purple} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="analyses" name="Phân tích" stroke={COLORS.purple} fill="url(#areaGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
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
          So sánh đối thủ
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
