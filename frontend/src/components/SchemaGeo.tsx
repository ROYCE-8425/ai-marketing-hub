import { useState } from "react";
import { GeoOptimizer } from "./GeoOptimizer";
import { SchemaValidator } from "./SchemaValidator";

type SchemaTab = "analyze" | "generate" | "validate";

const TABS: { id: SchemaTab; label: string; icon: string }[] = [
  { id: "generate", label: "Tạo Schema", icon: "🏗️" },
  { id: "validate", label: "Kiểm tra Schema", icon: "✅" },
];

interface SchemaGeoProps {
  initialTab?: SchemaTab;
}

export function SchemaGeo({ initialTab }: SchemaGeoProps) {
  const [activeTab, setActiveTab] = useState<SchemaTab>(initialTab || "generate");

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
        {activeTab === "generate" && <GeoOptimizer />}
        {activeTab === "validate" && <SchemaValidator />}
      </div>
    </div>
  );
}
