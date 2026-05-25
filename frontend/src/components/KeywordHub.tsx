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
// Response shape from POST /api/ai-keywords:
// { gsc_keywords, total_clicks, total_impressions, ai_analysis, summary,
//   recommended_keywords, quick_wins, keyword_clusters, content_strategy,
//   top_performing, data_source, ai_provider, error? }

interface GscKeyword {
  keyword: string;
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

interface AIKeywordsResponse {
  gsc_keywords: GscKeyword[];
  total_clicks: number;
  total_impressions: number;
  ai_analysis: string;
  summary: string;
  data_source: string;
  ai_provider: string;
  error?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  recommended_keywords: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  quick_wins: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  keyword_clusters: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  content_strategy: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  top_performing: any[];
}

function AIKeywordsPanel() {
  const [targetKeyword, setTargetKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AIKeywordsResponse | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/ai-keywords`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_keyword: targetKeyword.trim() || undefined,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `HTTP ${res.status}`);
      }
      const result: AIKeywordsResponse = await res.json();
      if (result.error) {
        setError(result.error);
      }
      setData(result);
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
            <label className="ws-label">Từ khóa mục tiêu (tùy chọn)</label>
            <input
              className="ws-input"
              placeholder="VD: mitsubishi bình phước — để trống để phân tích tổng thể"
              value={targetKeyword}
              onChange={(e) => setTargetKeyword(e.target.value)}
            />
          </div>
          <div className="ws-field ws-field-btn">
            <button type="submit" className="ws-submit" disabled={loading}>
              {loading ? <span className="btn-spinner" /> : "🔑 Phân tích từ khóa"}
            </button>
          </div>
        </div>
      </form>
      {error && !data && <div className="ws-error">❌ {error}</div>}
      {loading && (
        <div className="ws-loading">
          <span className="btn-spinner" style={{ width: 24, height: 24 }} />
          <p>Đang lấy dữ liệu GSC và phân tích bằng AI... (15-30s)</p>
        </div>
      )}
      {data && (
        <div className="ws-results">
          {/* Stat summary cards */}
          <div className="ws-stat-row">
            <div className="ws-stat-card">
              <div className="ws-stat-value">{data.gsc_keywords.length}</div>
              <div className="ws-stat-label">Từ khóa</div>
            </div>
            <div className="ws-stat-card">
              <div className="ws-stat-value">{data.total_clicks.toLocaleString()}</div>
              <div className="ws-stat-label">Lượt nhấp</div>
            </div>
            <div className="ws-stat-card">
              <div className="ws-stat-value">{data.total_impressions.toLocaleString()}</div>
              <div className="ws-stat-label">Hiển thị</div>
            </div>
            <div className="ws-stat-card">
              <div className="ws-stat-value" style={{ fontSize: '0.9rem' }}>{data.data_source === 'live_gsc' ? '🟢 GSC Live' : '⚠️ ' + data.data_source}</div>
              <div className="ws-stat-label">Nguồn dữ liệu</div>
            </div>
          </div>

          {/* AI Summary */}
          {data.summary && (
            <div className="ws-summary-box">
              <h4>📊 Tóm tắt phân tích</h4>
              <p>{data.summary}</p>
              {data.ai_provider !== 'none' && (
                <span className="ws-ai-badge">AI: {data.ai_provider}</span>
              )}
            </div>
          )}

          {/* GSC Keywords Table */}
          {data.gsc_keywords.length > 0 && (
            <>
              <h4 style={{ margin: '1rem 0 0.5rem', color: 'var(--text-h, #e2e8f0)', fontSize: '0.85rem' }}>
                🔍 Từ khóa GSC ({data.gsc_keywords.length})
              </h4>
              <table className="ws-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Từ khóa</th>
                    <th>Vị trí</th>
                    <th>Clicks</th>
                    <th>Impressions</th>
                    <th>CTR</th>
                  </tr>
                </thead>
                <tbody>
                  {data.gsc_keywords.slice(0, 50).map((kw, i) => (
                    <tr key={i}>
                      <td style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>{i + 1}</td>
                      <td><strong>{kw.keyword}</strong></td>
                      <td style={{ color: kw.position <= 3 ? '#10b981' : kw.position <= 10 ? '#3b82f6' : kw.position <= 20 ? '#f59e0b' : '#ef4444' }}>
                        {kw.position.toFixed(1)}
                      </td>
                      <td>{kw.clicks}</td>
                      <td>{kw.impressions.toLocaleString()}</td>
                      <td>{(kw.ctr * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}

          {/* Quick Wins */}
          {data.quick_wins.length > 0 && (
            <div className="ws-section-block">
              <h4>⚡ Quick Wins ({data.quick_wins.length})</h4>
              <div className="ws-card-grid">
                {data.quick_wins.map((qw, i) => (
                  <div key={i} className="ws-insight-card ws-insight-win">
                    <strong>{qw.keyword}</strong>
                    {qw.current_position && <span className="ws-pos-badge">Pos {qw.current_position}</span>}
                    <p>{qw.action}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Keywords */}
          {data.recommended_keywords.length > 0 && (
            <div className="ws-section-block">
              <h4>💡 Từ khóa đề xuất ({data.recommended_keywords.length})</h4>
              <div className="ws-card-grid">
                {data.recommended_keywords.map((rk, i) => (
                  <div key={i} className="ws-insight-card ws-insight-rec">
                    <strong>{rk.keyword}</strong>
                    <div className="ws-tag-row">
                      {rk.search_intent && <span className="ws-mini-tag">{rk.search_intent}</span>}
                      {rk.difficulty && <span className="ws-mini-tag">{rk.difficulty}</span>}
                      {rk.priority && <span className="ws-mini-tag ws-mini-tag-pri">{rk.priority}</span>}
                    </div>
                    {rk.reason && <p>{rk.reason}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Keyword Clusters */}
          {data.keyword_clusters.length > 0 && (
            <div className="ws-section-block">
              <h4>🏷️ Nhóm chủ đề ({data.keyword_clusters.length})</h4>
              <div className="ws-card-grid">
                {data.keyword_clusters.map((cl, i) => (
                  <div key={i} className="ws-insight-card ws-insight-cluster">
                    <strong>{cl.cluster_name}</strong>
                    <div className="ws-tag-row">
                      {cl.keywords?.slice(0, 5).map((k: string, j: number) => (
                        <span key={j} className="ws-mini-tag">{k}</span>
                      ))}
                    </div>
                    {cl.suggested_content && <p>{cl.suggested_content}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Content Strategy */}
          {data.content_strategy?.length > 0 && (
            <div className="ws-section-block">
              <h4>📝 Chiến lược nội dung</h4>
              <div className="ws-card-grid">
                {data.content_strategy.map((cs, i) => (
                  <div key={i} className="ws-insight-card">
                    <strong>{cs.title}</strong>
                    <div className="ws-tag-row">
                      {cs.content_type && <span className="ws-mini-tag">{cs.content_type}</span>}
                      {cs.priority && <span className="ws-mini-tag ws-mini-tag-pri">{cs.priority}</span>}
                    </div>
                    {cs.description && <p>{cs.description}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error from backend but still partial data */}
          {data.error && data.gsc_keywords.length === 0 && (
            <div className="ws-error" style={{ marginTop: '1rem' }}>⚠️ {data.error}</div>
          )}
        </div>
      )}
      {!data && !loading && !error && (
        <div className="ws-empty">
          <span className="ws-empty-icon">🔑</span>
          <p>Phân tích từ khóa từ Google Search Console kết hợp AI.</p>
          <p className="ws-empty-hint">Hệ thống sẽ lấy dữ liệu GSC thật, sau đó dùng AI đề xuất chiến lược từ khóa mới.</p>
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
