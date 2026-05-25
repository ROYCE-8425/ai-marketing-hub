import { useState } from "react";
import { TechnicalSeo } from "./TechnicalSeo";
import { BacklinkAnalyzer } from "./BacklinkAnalyzer";
import { CoreWebVitals } from "./CoreWebVitals";
import { BrokenLinkChecker } from "./BrokenLinkChecker";
import { SchemaValidator } from "./SchemaValidator";
import { CroDashboard } from "./CroDashboard";
import { useSeoAudit } from "../hooks/useSeoAudit";

// ═══════════════════════════════════════════════════════════════════════
// SeoWorkspace — All tabs self-contained, including CRO
// CRO tab now has inline audit form → fetches data → renders CroDashboard
// ═══════════════════════════════════════════════════════════════════════

type SeoTab = "techseo" | "cro" | "backlinks" | "cwv" | "brokenlinks" | "schema";

const TABS: { id: SeoTab; label: string; icon: string }[] = [
  { id: "techseo", label: "Technical SEO", icon: "🔧" },
  { id: "cro", label: "CRO & Uy tín", icon: "📊" },
  { id: "backlinks", label: "Backlinks", icon: "🔗" },
  { id: "cwv", label: "Core Web Vitals", icon: "⚡" },
  { id: "brokenlinks", label: "Link hỏng", icon: "🔍" },
  { id: "schema", label: "Schema", icon: "📋" },
];

interface SeoWorkspaceProps {
  initialTab?: SeoTab;
}

// ── CRO Audit Panel — self-contained ──────────────────────────────────────────
function CroAuditPanel() {
  const [url, setUrl] = useState("");
  const [keyword, setKeyword] = useState("");
  const { data, loading, error, analyze } = useSeoAudit();

  const handleAudit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim() && keyword.trim()) {
      analyze({ url: url.trim(), primary_keyword: keyword.trim() });
    }
  };

  return (
    <div>
      <form className="ws-form" onSubmit={handleAudit}>
        <div className="ws-form-row">
          <div className="ws-field ws-field-grow">
            <label className="ws-label">URL trang cần phân tích</label>
            <input
              className="ws-input"
              placeholder="https://example.com/landing-page"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
          </div>
          <div className="ws-field ws-field-grow">
            <label className="ws-label">Từ khóa chính</label>
            <input
              className="ws-input"
              placeholder="VD: mua xe ô tô"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              required
            />
          </div>
          <div className="ws-field ws-field-btn">
            <button type="submit" className="ws-submit" disabled={loading || !url.trim() || !keyword.trim()}>
              {loading ? <span className="btn-spinner" /> : "📊 Phân tích CRO"}
            </button>
          </div>
        </div>
      </form>
      {error && <div className="ws-error">❌ {error}</div>}
      {loading && (
        <div className="ws-loading">
          <span className="btn-spinner" style={{ width: 24, height: 24 }} />
          <p>Đang phân tích CRO & tín hiệu uy tín... (15-30s)</p>
        </div>
      )}
      {data && <CroDashboard cro={data.cro_analysis} />}
      {!data && !loading && !error && (
        <div className="ws-empty">
          <span className="ws-empty-icon">📊</span>
          <p>Phân tích CRO, CTA, Above-the-Fold và Trust Signals cho landing page.</p>
          <p className="ws-empty-hint">Nhập URL và từ khóa chính để bắt đầu.</p>
        </div>
      )}
    </div>
  );
}

// ── Main Workspace ────────────────────────────────────────────────────────────
export function SeoWorkspace({ initialTab }: SeoWorkspaceProps) {
  const [activeTab, setActiveTab] = useState<SeoTab>(initialTab || "techseo");

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
        {activeTab === "techseo" && <TechnicalSeo />}
        {activeTab === "cro" && <CroAuditPanel />}
        {activeTab === "backlinks" && <BacklinkAnalyzer />}
        {activeTab === "cwv" && <CoreWebVitals />}
        {activeTab === "brokenlinks" && <BrokenLinkChecker />}
        {activeTab === "schema" && <SchemaValidator />}
      </div>
    </div>
  );
}
