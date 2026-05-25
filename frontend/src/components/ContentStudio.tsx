import { useState } from "react";
import { SpinEditor } from "./SpinEditor";
import { ContentPlannerPanel } from "./ContentPlanner";
import { API_BASE } from "../lib/apiConfig";
import type { PlanContentResponse } from "../types/content";

// ═══════════════════════════════════════════════════════════════════════
// ContentStudio — Self-contained content workflow workspace
// Tabs: Plan & Write (self-fetch) | Spin & Viết lại (existing)
// ═══════════════════════════════════════════════════════════════════════

type ContentTab = "planner" | "spin";

const TABS: { id: ContentTab; label: string; icon: string }[] = [
  { id: "planner", label: "Lập kế hoạch & Viết bài", icon: "✍️" },
  { id: "spin", label: "Spin & Viết lại", icon: "🔄" },
];

interface ContentStudioProps {
  initialTab?: ContentTab;
}

// ── ContentPlannerWrapper — self-contained plan form ──────────────────────────
function ContentPlannerWrapper() {
  const [keyword, setKeyword] = useState("");
  const [audience, setAudience] = useState("");
  const [gaps, setGaps] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [plan, setPlan] = useState<PlanContentResponse | null>(null);

  const handlePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim() || !audience.trim()) return;
    setLoading(true);
    setError(null);
    setPlan(null);
    try {
      const gapList = gaps.split("\n").map(g => g.trim()).filter(Boolean);
      const res = await fetch(`${API_BASE}/plan-content`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          primary_keyword: keyword.trim(),
          target_audience: audience.trim(),
          competitor_gaps: gapList.length > 0 ? gapList : undefined,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `HTTP ${res.status}`);
      }
      setPlan(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  };

  // If plan is loaded, show the full planner with write/polish/publish
  if (plan) {
    return (
      <div>
        <div style={{ marginBottom: 16 }}>
          <button
            className="ws-back-btn"
            onClick={() => setPlan(null)}
          >
            ← Tạo kế hoạch mới
          </button>
        </div>
        <ContentPlannerPanel plan={plan} />
      </div>
    );
  }

  return (
    <div>
      <form className="ws-form" onSubmit={handlePlan}>
        <div className="ws-form-row">
          <div className="ws-field ws-field-grow">
            <label className="ws-label">Từ khóa chính</label>
            <input
              className="ws-input"
              placeholder="VD: cách chọn xe ô tô phù hợp"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              required
            />
          </div>
          <div className="ws-field ws-field-grow">
            <label className="ws-label">Đối tượng đọc</label>
            <input
              className="ws-input"
              placeholder="VD: người mua xe lần đầu tại Việt Nam"
              value={audience}
              onChange={(e) => setAudience(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="ws-field" style={{ marginTop: 12 }}>
          <label className="ws-label">Gap từ đối thủ (tùy chọn, mỗi dòng 1 gap)</label>
          <textarea
            className="ws-input ws-textarea"
            placeholder={"VD: Thiếu phần so sánh giá\nThiếu FAQ\nKhông có case study"}
            value={gaps}
            onChange={(e) => setGaps(e.target.value)}
            rows={3}
          />
        </div>
        <button type="submit" className="ws-submit" disabled={loading || !keyword.trim() || !audience.trim()} style={{ marginTop: 12 }}>
          {loading ? <span className="btn-spinner" /> : "✍️ Tạo kế hoạch bài viết"}
        </button>
      </form>
      {error && <div className="ws-error">❌ {error}</div>}
      {loading && (
        <div className="ws-loading">
          <span className="btn-spinner" style={{ width: 24, height: 24 }} />
          <p>Đang tạo kế hoạch bài viết... (10-20s)</p>
        </div>
      )}
      {!loading && !error && (
        <div className="ws-empty">
          <span className="ws-empty-icon">✍️</span>
          <p>Tạo kế hoạch nội dung bằng AI từ từ khóa và đối tượng đọc.</p>
          <p className="ws-empty-hint">Sau khi tạo xong, bạn có thể viết bài → polish → publish ngay trong đây.</p>
        </div>
      )}
    </div>
  );
}

// ── Main Workspace ────────────────────────────────────────────────────────────
export function ContentStudio({ initialTab }: ContentStudioProps) {
  const [activeTab, setActiveTab] = useState<ContentTab>(initialTab || "planner");

  return (
    <div className="workspace-container">
      <div className="workspace-tabs">
        {TABS.map(tab => (
          <button
            key={tab.id}
            className={`workspace-tab ${activeTab === tab.id ? "workspace-tab-active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="workspace-tab-icon">{tab.icon}</span>
            <span className="workspace-tab-label">{tab.label}</span>
          </button>
        ))}
      </div>
      <div className="workspace-content">
        {activeTab === "planner" && <ContentPlannerWrapper />}
        {activeTab === "spin" && <SpinEditor />}
      </div>
    </div>
  );
}
