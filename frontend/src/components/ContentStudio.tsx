import { useState } from "react";
import { SpinEditor } from "./SpinEditor";

// ContentPlannerPanel requires `plan` prop from App.tsx state.
// In workspace mode, show placeholder for planner tab.

type ContentTab = "planner" | "spin";

const TABS: { id: ContentTab; label: string; icon: string }[] = [
  { id: "planner", label: "Lập kế hoạch & Viết bài", icon: "✍️" },
  { id: "spin", label: "Spin & Viết lại", icon: "🔄" },
];

interface ContentStudioProps {
  initialTab?: ContentTab;
}

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
        {activeTab === "planner" && (
          <div className="workspace-placeholder">
            <div>
              <p style={{fontSize: "16px", fontWeight: 600, marginBottom: "8px"}}>✍️ Lập kế hoạch & Viết bài AI</p>
              <p>Sử dụng trang <strong>Kiểm tra SEO</strong> để tạo kế hoạch nội dung.</p>
              <p style={{fontSize: "12px", color: "var(--text-muted)", marginTop: "4px"}}>Nhập từ khóa và đối tượng đọc → AI sẽ tạo outline → viết bài → polish → publish.</p>
            </div>
          </div>
        )}
        {activeTab === "spin" && <SpinEditor />}
      </div>
    </div>
  );
}
