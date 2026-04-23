import { useDeepAnalyze } from "../hooks/useSerpLive";
import type { SerpLiveResponse, SerpResult, DeepAnalyzeResponse } from "../hooks/useSerpLive";
import { exportSerpToCsv } from "../lib/history";
import "./SerpResultsPanel.css";

// ─── Feature label mapping ─────────────────────────────────────────────────────

const FEATURE_LABELS: Record<string, string> = {
  featured_snippet: "Nổi bật",
  people_also_ask: "Câu hỏi liên quan",
  knowledge_panel: "Bảng tri thức",
  video_carousel: "Video",
  image_pack: "Hình ảnh",
  local_pack: "Địa điểm",
  shopping_results: "Mua sắm",
  top_stories: "Tin nổi bật",
  related_searches: "Liên quan",
};

// ─── Sub-components ────────────────────────────────────────────────────────────

function PositionBadge({ pos }: { pos: number }) {
  const cls = pos === 1 ? "serp-pos-1" : pos === 2 ? "serp-pos-2" : pos === 3 ? "serp-pos-3" : "serp-pos-default";
  return <span className={`serp-pos ${cls}`}>{pos}</span>;
}

function SerpFeatureBadges({ features }: { features: string[] }) {
  if (!features.length) return null;
  return (
    <div className="serp-features-row">
      {features.map((f) => (
        <span key={f} className="serp-feature-badge">
          <span className="serp-feature-dot" />
          {FEATURE_LABELS[f] || f.replace(/_/g, " ")}
        </span>
      ))}
    </div>
  );
}

function RankingTable({ results, onRowClick }: { results: SerpResult[]; onRowClick?: (url: string) => void }) {
  return (
    <table className="serp-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Trang web</th>
          <th>Mô tả</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {results.map((r) => (
          <tr
            key={r.position}
            className="serp-row"
            onClick={() => onRowClick ? onRowClick(r.url) : window.open(r.url, "_blank")}
          >
            <td>
              <PositionBadge pos={r.position} />
            </td>
            <td>
              <div className="serp-title-cell">
                <span className="serp-title">{r.title}</span>
                <span className="serp-domain">{r.domain}</span>
                {r.breadcrumb && <span className="serp-breadcrumb">{r.breadcrumb}</span>}
              </div>
            </td>
            <td>
              <span className="serp-snippet">{r.snippet}</span>
            </td>
            <td>
              <svg className="serp-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ─── Deep Analyze Panel ────────────────────────────────────────────────────────

function WordCountBars({ pages, maxCount }: { pages: DeepAnalyzeResponse["pages"]; maxCount: number }) {
  const sorted = [...pages]
    .filter((p) => p.word_count > 0)
    .sort((a, b) => b.word_count - a.word_count);

  const m = maxCount || Math.max(...sorted.map((p) => p.word_count), 1);

  return (
    <div className="wc-bar-list">
      {sorted.map((p, i) => {
        const pct = Math.min((p.word_count / m) * 100, 100);
        const hue = p.word_count > m * 0.75 ? 142 : p.word_count > m * 0.5 ? 217 : 38;
        let domain = "";
        try {
          domain = new URL(p.url).hostname.replace("www.", "");
        } catch {
          domain = p.url.slice(0, 30);
        }
        return (
          <div key={i} className="wc-bar-row">
            <span className="wc-bar-pos">#{i + 1}</span>
            <span className="wc-bar-domain" title={domain}>{domain}</span>
            <div className="wc-bar-track">
              <div
                className="wc-bar-fill"
                style={{
                  width: `${pct}%`,
                  background: `hsl(${hue}, 70%, 55%)`,
                }}
              />
            </div>
            <span className="wc-bar-count">{p.word_count.toLocaleString()}</span>
          </div>
        );
      })}
    </div>
  );
}

function DeepAnalyzePanel({
  keyword,
  urls,
}: {
  keyword: string;
  urls: string[];
}) {
  const { data, loading, error, analyze } = useDeepAnalyze();

  const handleDeep = () => {
    if (urls.length > 0) {
      analyze(keyword, urls.slice(0, 10));
    }
  };

  return (
    <div className="deep-analyze-section">
      <div className="deep-analyze-header">
        <h3>🔬 Phân tích nội dung đối thủ</h3>
        <button
          className="deep-analyze-btn"
          onClick={handleDeep}
          disabled={loading || urls.length === 0}
        >
          {loading ? (
            <span className="btn-spinner" aria-label="Analyzing" />
          ) : (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
                <polyline points="16 7 22 7 22 13" />
              </svg>
              Phân tích sâu ({urls.length} trang)
            </>
          )}
        </button>
      </div>

      {error && <p className="error-msg">{error}</p>}

      {data && (
        <>
          <WordCountBars pages={data.pages} maxCount={data.statistics.max || 0} />

          <div className="deep-stats-row">
            {data.statistics.min != null && (
              <div className="deep-stat-card">
                <div className="deep-stat-label">Tối thiểu</div>
                <div className="deep-stat-value">{data.statistics.min.toLocaleString()}</div>
              </div>
            )}
            {data.statistics.mean != null && (
              <div className="deep-stat-card">
                <div className="deep-stat-label">Trung bình</div>
                <div className="deep-stat-value">{data.statistics.mean.toLocaleString()}</div>
              </div>
            )}
            {data.statistics.median != null && (
              <div className="deep-stat-card">
                <div className="deep-stat-label">Trung vị</div>
                <div className="deep-stat-value">{data.statistics.median.toLocaleString()}</div>
              </div>
            )}
            {data.statistics.max != null && (
              <div className="deep-stat-card">
                <div className="deep-stat-label">Tối đa</div>
                <div className="deep-stat-value">{data.statistics.max.toLocaleString()}</div>
              </div>
            )}
            {data.statistics.percentile_75 != null && (
              <div className="deep-stat-card">
                <div className="deep-stat-label">P75</div>
                <div className="deep-stat-value">{data.statistics.percentile_75.toLocaleString()}</div>
              </div>
            )}
          </div>

          {data.recommendation.recommended_optimal != null && (
            <div className="deep-stats-row" style={{ marginTop: "0.5rem" }}>
              <div className="deep-stat-card" style={{ borderColor: "rgba(139,92,246,0.3)", borderWidth: "1px", borderStyle: "solid" }}>
                <div className="deep-stat-label">Đề xuất tối thiểu</div>
                <div className="deep-stat-value">{data.recommendation.recommended_min?.toLocaleString()}</div>
              </div>
              <div className="deep-stat-card" style={{ borderColor: "rgba(16,185,129,0.4)", borderWidth: "1px", borderStyle: "solid" }}>
                <div className="deep-stat-label">✨ Mục tiêu tối ưu</div>
                <div className="deep-stat-value" style={{ color: "#6ee7b7" }}>
                  {data.recommendation.recommended_optimal?.toLocaleString()}
                </div>
              </div>
              <div className="deep-stat-card">
                <div className="deep-stat-label">Giới hạn trên</div>
                <div className="deep-stat-value">{data.recommendation.recommended_max?.toLocaleString()}</div>
              </div>
            </div>
          )}

          {data.recommendation.message && (
            <div className={`deep-recommendation status-${data.recommendation.your_status || "good"}`}>
              <div className="deep-rec-title">
                {data.recommendation.your_status === "optimal" ? "✅ " : data.recommendation.your_status === "too_short" ? "⚠️ " : "💡 "}
                Đánh giá
              </div>
              <div className="deep-rec-msg">{data.recommendation.message}</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ─── Main Panel ────────────────────────────────────────────────────────────────

export function SerpResultsPanel({ data }: { data: SerpLiveResponse }) {
  const urls = data.organic_results.map((r) => r.url);

  return (
    <div className="serp-panel">
      {/* Meta bar */}
      <div className="serp-meta-bar">
        <span className="serp-meta-pill">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
          </svg>
          {data.keyword}
        </span>
        {data.location && (
          <span className="serp-meta-pill">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
            {data.location}
          </span>
        )}
        <span className="serp-meta-pill">
          {data.results_count} kết quả
        </span>
        {/* Export CSV button */}
        <button
          className="export-btn"
          onClick={(e) => { e.stopPropagation(); exportSerpToCsv(data.keyword, data.organic_results); }}
          title="Xuất CSV"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          CSV
        </button>
        {data.total_results > 0 && (
          <span className="serp-meta-pill">
            ~{data.total_results.toLocaleString()} tổng
          </span>
        )}
        {data.search_volume != null && (
          <span className="serp-meta-pill">
            Vol: {data.search_volume.toLocaleString()}
          </span>
        )}
        <span className={`serp-source-badge ${
          data.source === "dataforseo_live" ? "src-dataforseo" :
          data.source === "mock_serp" ? "src-scraper" : "src-dataforseo"
        }`}>
          {data.source === "dataforseo_live" ? "✅ DataForSEO" :
           data.source === "duckduckgo_live" ? "🔍 Dữ liệu thật" :
           data.source === "duckduckgo_search" ? "🔍 Dữ liệu thật" :
           data.source === "google_scrape" ? "🔍 Google Live" :
           data.source === "mock_serp" ? "⚠️ Dữ liệu mẫu" : data.source}
        </span>
      </div>

      {/* Warning note (mock data / network error) */}
      {(data.note || data.error) && (
        <div style={{
          padding: "0.6rem 1rem",
          background: "rgba(245,158,11,0.08)",
          border: "1px solid rgba(245,158,11,0.2)",
          borderRadius: "0.6rem",
          color: "#fcd34d",
          fontSize: "0.82rem",
        }}>
          {data.note || data.error}
        </div>
      )}

      {/* SERP Features */}
      <SerpFeatureBadges features={data.serp_features} />

      {/* Ranking table */}
      {data.organic_results.length > 0 ? (
        <RankingTable results={data.organic_results} />
      ) : (
        <p style={{ color: "rgba(255,255,255,0.4)", textAlign: "center", padding: "2rem" }}>
          Không tìm thấy kết quả. Vui lòng thử lại.
        </p>
      )}

      {/* Deep analyze */}
      {urls.length > 0 && (
        <DeepAnalyzePanel keyword={data.keyword} urls={urls} />
      )}
    </div>
  );
}
