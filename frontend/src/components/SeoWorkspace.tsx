import { useState } from "react";
import { TechnicalSeo } from "./TechnicalSeo";
import { BacklinkAnalyzer } from "./BacklinkAnalyzer";
import { CoreWebVitals } from "./CoreWebVitals";
import { BrokenLinkChecker } from "./BrokenLinkChecker";
import { SchemaValidator } from "./SchemaValidator";

// Note: CroDashboard requires `cro` prop from audit data.
// In workspace mode, we show a placeholder until user runs SEO Audit on main page.

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
        {activeTab === "cro" && (
          <div className="workspace-placeholder">
            <div>
              <p style={{fontSize: "16px", fontWeight: 600, marginBottom: "8px"}}>📊 CRO & Uy tín</p>
              <p>Chạy <strong>Kiểm tra SEO</strong> trước để xem phân tích CRO.</p>
              <p style={{fontSize: "12px", color: "var(--text-muted)", marginTop: "4px"}}>CRO data được tạo tự động khi bạn audit một URL.</p>
            </div>
          </div>
        )}
        {activeTab === "backlinks" && <BacklinkAnalyzer />}
        {activeTab === "cwv" && <CoreWebVitals />}
        {activeTab === "brokenlinks" && <BrokenLinkChecker />}
        {activeTab === "schema" && <SchemaValidator />}
      </div>
    </div>
  );
}
