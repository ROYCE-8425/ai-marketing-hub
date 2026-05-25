import { useState } from "react";
import { RankTracker } from "./RankTracker";
import { SerpResultsPanel } from "./SerpResultsPanel";
import { CompetitorRadarPanel } from "./CompetitorRadar";
import { CampaignTrackerPanel } from "./CampaignTracker";
import { useSerpLive } from "../hooks/useSerpLive";
import { API_BASE } from "../lib/apiConfig";
import type { CompetitorGapResponse } from "../types/content";
import type { OpportunitiesResponse } from "../types/phase5";

// ═══════════════════════════════════════════════════════════════════════
// KeywordHub — Self-contained workspace for keyword intelligence
// All tabs fetch their own data, no dependency on App.tsx state.
// ═══════════════════════════════════════════════════════════════════════

type KeywordTab = "tracker" | "research" | "serp" | "competitor" | "campaign";

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

// ── Tab: SERP Search ──────────────────────────────────────────────────────────
function SerpSearchPanel() {
  const [keyword, setKeyword] = useState("");
  const [location, setLocation] = useState("vn");
  const { data, loading, error, search } = useSerpLive();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (keyword.trim()) search(keyword.trim(), location);
  };

  return (
    <div>
      <form className="ws-form" onSubmit={handleSearch}>
        <div className="ws-form-row">
          <div className="ws-field ws-field-grow">
            <label className="ws-label">Từ khóa</label>
            <input
              className="ws-input"
              placeholder="Nhập từ khóa cần tra cứu SERP..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              required
            />
          </div>
          <div className="ws-field">
            <label className="ws-label">Quốc gia</label>
            <select className="ws-input" value={location} onChange={(e) => setLocation(e.target.value)}>
              <option value="vn">🇻🇳 Việt Nam</option>
              <option value="us">🇺🇸 Hoa Kỳ</option>
              <option value="gb">🇬🇧 Anh</option>
              <option value="au">🇦🇺 Úc</option>
            </select>
          </div>
          <div className="ws-field ws-field-btn">
            <button type="submit" className="ws-submit" disabled={loading || !keyword.trim()}>
              {loading ? <span className="btn-spinner" /> : "🔍 Tra cứu SERP"}
            </button>
          </div>
        </div>
      </form>
      {error && <div className="ws-error">❌ {error}</div>}
      {data && <SerpResultsPanel data={data} />}
      {!data && !loading && !error && (
        <div className="ws-empty">
          <span className="ws-empty-icon">🌐</span>
          <p>Nhập từ khóa để xem kết quả tìm kiếm Google thực tế.</p>
          <p className="ws-empty-hint">Hệ thống sẽ lấy top 10 kết quả và phân tích chi tiết.</p>
        </div>
      )}
    </div>
  );
}

// ── Tab: AI Keywords ──────────────────────────────────────────────────────────
interface AIKeywordResult {
  keyword: string;
  position?: number;
  clicks?: number;
  impressions?: number;
  ctr?: number;
  opportunity_score?: number;
  recommendation?: string;
}

function AIKeywordsPanel() {
  const [siteUrl, setSiteUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AIKeywordResult[] | null>(null);
  const [summary, setSummary] = useState("");

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!siteUrl.trim()) return;
    setLoading(true);
    setError(null);
    setResults(null);
    setSummary("");
    try {
      const res = await fetch(`${API_BASE}/ai-keywords`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ site_url: siteUrl.trim() }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `HTTP ${res.status}`);
      }
      const data = await res.json();
      setResults(data.keywords || data.results || []);
      setSummary(data.ai_analysis || data.summary || "");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form className="ws-form" onSubmit={handleAnalyze}>
        <div className="ws-form-row">
          <div className="ws-field ws-field-grow">
            <label className="ws-label">URL website</label>
            <input
              className="ws-input"
              placeholder="https://example.com"
              value={siteUrl}
              onChange={(e) => setSiteUrl(e.target.value)}
              required
            />
          </div>
          <div className="ws-field ws-field-btn">
            <button type="submit" className="ws-submit" disabled={loading || !siteUrl.trim()}>
              {loading ? <span className="btn-spinner" /> : "🔑 Phân tích từ khóa"}
            </button>
          </div>
        </div>
      </form>
      {error && <div className="ws-error">❌ {error}</div>}
      {loading && (
        <div className="ws-loading">
          <span className="btn-spinner" style={{ width: 24, height: 24 }} />
          <p>Đang phân tích từ khóa với AI... (có thể mất 15-30s)</p>
        </div>
      )}
      {results && results.length > 0 && (
        <div className="ws-results">
          {summary && (
            <div className="ws-summary-box">
              <h4>📊 Phân tích AI</h4>
              <p>{summary}</p>
            </div>
          )}
          <table className="ws-table">
            <thead>
              <tr>
                <th>Từ khóa</th>
                <th>Vị trí</th>
                <th>Clicks</th>
                <th>Impressions</th>
                <th>CTR</th>
                <th>Cơ hội</th>
              </tr>
            </thead>
            <tbody>
              {results.map((kw, i) => (
                <tr key={i}>
                  <td><strong>{kw.keyword}</strong></td>
                  <td>{kw.position != null ? kw.position.toFixed(1) : "—"}</td>
                  <td>{kw.clicks ?? "—"}</td>
                  <td>{kw.impressions ?? "—"}</td>
                  <td>{kw.ctr != null ? `${(kw.ctr * 100).toFixed(1)}%` : "—"}</td>
                  <td>
                    {kw.recommendation ? (
                      <span className="ws-rec-badge">{kw.recommendation}</span>
                    ) : kw.opportunity_score != null ? (
                      <span className="ws-opp-score">{kw.opportunity_score}</span>
                    ) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {results && results.length === 0 && (
        <div className="ws-empty">
          <p>Không tìm thấy dữ liệu từ khóa. Kiểm tra lại URL hoặc cấu hình GSC.</p>
        </div>
      )}
      {!results && !loading && !error && (
        <div className="ws-empty">
          <span className="ws-empty-icon">🔑</span>
          <p>Nhập URL website để phân tích từ khóa bằng AI.</p>
          <p className="ws-empty-hint">Cần cấu hình Google Search Console để lấy dữ liệu thực.</p>
        </div>
      )}
    </div>
  );
}

// ── Tab: Competitor Gap ───────────────────────────────────────────────────────
function CompetitorPanel() {
  const [myUrl, setMyUrl] = useState("");
  const [keyword, setKeyword] = useState("");
  const [compUrls, setCompUrls] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<CompetitorGapResponse | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    const urls = compUrls.split("\n").map(u => u.trim()).filter(Boolean);
    if (!myUrl.trim() || urls.length === 0) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/competitor-gap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          my_url: myUrl.trim(),
          competitor_urls: urls,
          primary_keyword: keyword.trim() || undefined,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `HTTP ${res.status}`);
      }
      setData(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form className="ws-form" onSubmit={handleAnalyze}>
        <div className="ws-form-row">
          <div className="ws-field ws-field-grow">
            <label className="ws-label">URL của bạn</label>
            <input
              className="ws-input"
              placeholder="https://yoursite.com/page"
              value={myUrl}
              onChange={(e) => setMyUrl(e.target.value)}
              required
            />
          </div>
          <div className="ws-field">
            <label className="ws-label">Từ khóa chính (tùy chọn)</label>
            <input
              className="ws-input"
              placeholder="VD: mua xe ô tô"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
            />
          </div>
        </div>
        <div className="ws-field" style={{ marginTop: 12 }}>
          <label className="ws-label">URL đối thủ (mỗi dòng 1 URL)</label>
          <textarea
            className="ws-input ws-textarea"
            placeholder={"https://competitor1.com/page\nhttps://competitor2.com/page"}
            value={compUrls}
            onChange={(e) => setCompUrls(e.target.value)}
            rows={3}
            required
          />
        </div>
        <button type="submit" className="ws-submit" disabled={loading || !myUrl.trim()} style={{ marginTop: 12 }}>
          {loading ? <span className="btn-spinner" /> : "👥 Phân tích đối thủ"}
        </button>
      </form>
      {error && <div className="ws-error">❌ {error}</div>}
      {loading && (
        <div className="ws-loading">
          <span className="btn-spinner" style={{ width: 24, height: 24 }} />
          <p>Đang cào và phân tích nội dung đối thủ... (30-60s)</p>
        </div>
      )}
      {data && <CompetitorRadarPanel data={data} />}
      {!data && !loading && !error && (
        <div className="ws-empty">
          <span className="ws-empty-icon">👥</span>
          <p>So sánh trang của bạn với đối thủ cạnh tranh.</p>
          <p className="ws-empty-hint">Nhập URL trang bạn và ít nhất 1 URL đối thủ để bắt đầu.</p>
        </div>
      )}
    </div>
  );
}

// ── Tab: Campaign / Opportunities ─────────────────────────────────────────────
function OpportunityPanel() {
  const [url, setUrl] = useState("");
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<OpportunitiesResponse | null>(null);

  const handleScore = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || !keyword.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const params = new URLSearchParams({ url: url.trim(), keyword: keyword.trim() });
      const res = await fetch(`${API_BASE}/opportunities?${params}`, {
        method: "POST",
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `HTTP ${res.status}`);
      }
      setData(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form className="ws-form" onSubmit={handleScore}>
        <div className="ws-form-row">
          <div className="ws-field ws-field-grow">
            <label className="ws-label">URL trang đích</label>
            <input
              className="ws-input"
              placeholder="https://yoursite.com/landing-page"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
          </div>
          <div className="ws-field ws-field-grow">
            <label className="ws-label">Từ khóa mục tiêu</label>
            <input
              className="ws-input"
              placeholder="VD: mua xe ô tô Bình Phước"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              required
            />
          </div>
          <div className="ws-field ws-field-btn">
            <button type="submit" className="ws-submit" disabled={loading || !url.trim() || !keyword.trim()}>
              {loading ? <span className="btn-spinner" /> : "🎯 Đánh giá cơ hội"}
            </button>
          </div>
        </div>
      </form>
      {error && <div className="ws-error">❌ {error}</div>}
      {loading && (
        <div className="ws-loading">
          <span className="btn-spinner" style={{ width: 24, height: 24 }} />
          <p>Đang phân tích cơ hội SEO... (20-40s)</p>
        </div>
      )}
      {data && <CampaignTrackerPanel data={data} />}
      {!data && !loading && !error && (
        <div className="ws-empty">
          <span className="ws-empty-icon">🎯</span>
          <p>Đánh giá cơ hội SEO cho một URL và từ khóa cụ thể.</p>
          <p className="ws-empty-hint">Hệ thống sẽ phân tích intent, landing page, traffic projection và đưa ra action items.</p>
        </div>
      )}
    </div>
  );
}

// ── Main Workspace ────────────────────────────────────────────────────────────
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
        {activeTab === "research" && <AIKeywordsPanel />}
        {activeTab === "serp" && <SerpSearchPanel />}
        {activeTab === "competitor" && <CompetitorPanel />}
        {activeTab === "campaign" && <OpportunityPanel />}
      </div>
    </div>
  );
}
