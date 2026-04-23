import { useEffect, useState } from "react";
import { getHistory, clearHistory, deleteHistoryEntry } from "../lib/history";
import type { HistoryEntry } from "../lib/history";
import "./DashboardOverview.css";

// ─── Stat Card ─────────────────────────────────────────────────────────────────

function StatCard({
  icon,
  value,
  label,
  accent,
}: {
  icon: React.ReactNode;
  value: string | number;
  label: string;
  accent?: string;
}) {
  return (
    <div className="dash-card" style={{ "--card-accent": accent } as React.CSSProperties}>
      <div className="dash-card-icon">{icon}</div>
      <div className="dash-card-value">{value}</div>
      <div className="dash-card-label">{label}</div>
    </div>
  );
}

// ─── Type badge colors ─────────────────────────────────────────────────────────

const TYPE_LABELS: Record<string, { label: string; cls: string }> = {
  seo: { label: "SEO", cls: "type-seo" },
  serp: { label: "SERP", cls: "type-serp" },
  competitor: { label: "COMP", cls: "type-competitor" },
  content: { label: "CONTENT", cls: "type-content" },
};

// ─── Format time ago ───────────────────────────────────────────────────────────

function timeAgo(isoStr: string): string {
  const diff = Date.now() - new Date(isoStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "vừa xong";
  if (mins < 60) return `${mins} phút trước`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} giờ trước`;
  const days = Math.floor(hours / 24);
  return `${days} ngày trước`;
}

// ─── Dashboard Panel ───────────────────────────────────────────────────────────

export function DashboardOverview({
  onNavigate,
}: {
  onNavigate: (tab: string) => void;
}) {
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    setHistory(getHistory());
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

  // Compute stats
  const totalAnalyses = history.length;
  const seoCount = history.filter((h) => h.type === "seo").length;
  const serpCount = history.filter((h) => h.type === "serp").length;
  const avgScore = seoCount > 0
    ? Math.round(
        history
          .filter((h) => h.type === "seo" && h.score != null)
          .reduce((sum, h) => sum + (h.score || 0), 0) /
          Math.max(1, history.filter((h) => h.type === "seo" && h.score != null).length)
      )
    : 0;

  return (
    <div style={{ animation: "fadeSlideIn 0.5s ease-out" }}>
      {/* Stat cards */}
      <div className="dashboard-grid">
        <StatCard
          icon={
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
              <polyline points="16 7 22 7 22 13" />
            </svg>
          }
          value={totalAnalyses}
          label="Tổng phân tích"
          accent="linear-gradient(90deg, #8b5cf6, #6366f1)"
        />
        <StatCard
          icon={
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
            </svg>
          }
          value={seoCount}
          label="SEO Audit"
          accent="linear-gradient(90deg, #3b82f6, #2563eb)"
        />
        <StatCard
          icon={
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
              <path d="M3.6 9h16.8" />
            </svg>
          }
          value={serpCount}
          label="SERP Live"
          accent="linear-gradient(90deg, #a855f7, #7c3aed)"
        />
        <StatCard
          icon={
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 20V10" /><path d="M18 20V4" /><path d="M6 20v-4" />
            </svg>
          }
          value={avgScore > 0 ? `${avgScore}/100` : "—"}
          label="Điểm SEO trung bình"
          accent="linear-gradient(90deg, #10b981, #059669)"
        />
      </div>

      {/* Quick actions */}
      <div className="dash-actions">
        <button className="dash-action-btn" onClick={() => onNavigate("seo")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
          </svg>
          Kiểm tra SEO mới
        </button>
        <button className="dash-action-btn" onClick={() => onNavigate("serp")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
            <path d="M3.6 9h16.8" />
          </svg>
          SERP trực tiếp
        </button>
        <button className="dash-action-btn" onClick={() => onNavigate("competitor")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
          </svg>
          So sánh đối thủ
        </button>
        <button className="dash-action-btn" onClick={() => onNavigate("planner")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
          </svg>
          Viết nội dung
        </button>
      </div>

      {/* History */}
      <div className="dash-history">
        <div className="dash-history-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
          </svg>
          Lịch sử phân tích
          {history.length > 0 && (
            <button
              className="export-btn"
              onClick={handleClear}
              style={{ marginLeft: "auto" }}
            >
              Xóa tất cả
            </button>
          )}
        </div>

        {history.length === 0 ? (
          <div className="dash-empty">
            <div className="dash-empty-icon">📊</div>
            <div className="dash-empty-text">Chưa có phân tích nào</div>
            <div className="dash-empty-sub">
              Bắt đầu bằng cách chạy SEO Audit hoặc SERP Live
            </div>
          </div>
        ) : (
          <div className="dash-history-list">
            {history.slice(0, 15).map((entry) => {
              const typeInfo = TYPE_LABELS[entry.type] || { label: entry.type, cls: "" };
              return (
                <div key={entry.id} className="dash-history-item">
                  <span className={`history-type-badge ${typeInfo.cls}`}>
                    {typeInfo.label}
                  </span>
                  <span className="history-keyword">{entry.keyword}</span>
                  <span className="history-time">{timeAgo(entry.timestamp)}</span>
                  {entry.score != null && (
                    <span
                      className="history-score"
                      style={{
                        color:
                          entry.score >= 80 ? "#6ee7b7" :
                          entry.score >= 50 ? "#fcd34d" : "#fca5a5",
                      }}
                    >
                      {entry.score}
                    </span>
                  )}
                  <button
                    className="export-btn"
                    onClick={(e) => { e.stopPropagation(); handleDelete(entry.id); }}
                    title="Xóa"
                    style={{ padding: "0.2rem 0.4rem" }}
                  >
                    ✕
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
