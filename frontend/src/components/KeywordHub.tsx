import { useState } from "react";
import { RankTracker } from "./RankTracker";

// Note: SerpResultsPanel, CompetitorRadarPanel, CampaignTrackerPanel require
// data props that come from App.tsx state. In workspace mode we show placeholders
// for those, and keep RankTracker (self-contained) as-is.

type KeywordTab = "research" | "serp" | "competitor" | "campaign" | "tracker";

const TABS: { id: KeywordTab; label: string; icon: string }[] = [
  { id: "tracker", label: "Theo dõi keyword", icon: "📈" },
  { id: "research", label: "AI Keywords", icon: "🔑" },
  { id: "serp", label: "SERP trực tiếp", icon: "🌐" },
  { id: "competitor", label: "Phân tích đối thủ", icon: "👥" },
  { id: "campaign", label: "Chiến dịch", icon: "🎯" },
];

interface KeywordHubProps {
  initialTab?: KeywordTab;
}

export function KeywordHub({ initialTab }: KeywordHubProps) {
  const [activeTab, setActiveTab] = useState<KeywordTab>(initialTab || "tracker");

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
        {activeTab === "tracker" && <RankTracker />}
        {activeTab === "research" && (
          <div className="workspace-placeholder">
            <div>
              <p style={{fontSize: "16px", fontWeight: 600, marginBottom: "8px"}}>🔑 AI Keywords</p>
              <p>Sử dụng trang <strong>Kiểm tra SEO</strong> để phân tích từ khóa AI.</p>
              <p style={{fontSize: "12px", color: "var(--text-muted)", marginTop: "4px"}}>Dữ liệu AI Keywords được tạo khi bạn audit URL với từ khóa.</p>
            </div>
          </div>
        )}
        {activeTab === "serp" && (
          <div className="workspace-placeholder">
            <div>
              <p style={{fontSize: "16px", fontWeight: 600, marginBottom: "8px"}}>🌐 SERP trực tiếp</p>
              <p>Sử dụng trang <strong>Kiểm tra SEO</strong> để xem kết quả SERP.</p>
              <p style={{fontSize: "12px", color: "var(--text-muted)", marginTop: "4px"}}>SERP data được lấy tự động khi bạn audit URL.</p>
            </div>
          </div>
        )}
        {activeTab === "competitor" && (
          <div className="workspace-placeholder">
            <div>
              <p style={{fontSize: "16px", fontWeight: 600, marginBottom: "8px"}}>👥 Phân tích đối thủ</p>
              <p>Sử dụng trang <strong>Kiểm tra SEO</strong> để so sánh với đối thủ.</p>
              <p style={{fontSize: "12px", color: "var(--text-muted)", marginTop: "4px"}}>Nhập URL đối thủ để bắt đầu phân tích gap.</p>
            </div>
          </div>
        )}
        {activeTab === "campaign" && (
          <div className="workspace-placeholder">
            <div>
              <p style={{fontSize: "16px", fontWeight: 600, marginBottom: "8px"}}>🎯 Chiến dịch</p>
              <p>Sử dụng trang <strong>Kiểm tra SEO</strong> để theo dõi chiến dịch.</p>
              <p style={{fontSize: "12px", color: "var(--text-muted)", marginTop: "4px"}}>Dữ liệu chiến dịch được tạo từ kết quả audit.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
