import { useState, useEffect, useRef } from "react";
import { API_BASE } from "../lib/apiConfig";
import "./CoreWebVitals.css";

// ─── Types ─────────────────────────────────────────────────────────────────────

interface MetricData {
  value: number;
  unit: string;
  rating: string; // "good" | "needs_improvement" | "poor"
}

interface LighthouseScores {
  performance: number;
  seo: number;
  accessibility: number;
  best_practices: number;
}

interface Opportunity {
  name: string;
  description: string;
  savings_ms: number;
  score: number;
}

interface CWVResult {
  url: string;
  strategy: string;
  metrics: {
    lcp: MetricData;
    inp: MetricData;
    cls: MetricData;
  };
  lighthouse_scores: LighthouseScores;
  opportunities: Opportunity[];
  overall_status: string; // "good" | "needs_improvement" | "poor"
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

/** Map rating string to CSS class */
function ratingClass(rating: string): string {
  if (rating === "good") return "good";
  if (rating === "needs_improvement") return "warning";
  return "poor";
}

/** Map rating string to Vietnamese label */
function ratingLabel(rating: string): string {
  if (rating === "good") return "Tốt";
  if (rating === "needs_improvement") return "Cần cải thiện";
  return "Kém";
}

/** Map rating to hex color */
function ratingColor(rating: string): string {
  if (rating === "good") return "#7c3aed";
  if (rating === "needs_improvement") return "#eab308";
  return "#ef4444";
}

/** Score (0-100) to color */
function scoreColor(score: number): string {
  if (score >= 90) return "#7c3aed";
  if (score >= 50) return "#eab308";
  return "#ef4444";
}

/** Format metric value for display */
function formatMetric(value: number, unit: string): string {
  if (unit === "ms") return `${Math.round(value)}`;
  // CLS has no unit
  return value.toFixed(3);
}

// ─── Animated Gauge Component ──────────────────────────────────────────────────

const GAUGE_RADIUS = 50;
const GAUGE_CIRCUMFERENCE = 2 * Math.PI * GAUGE_RADIUS;

/** Compute fill ratio for each metric type.
 *  LCP: good < 2500ms, poor > 4000ms
 *  INP: good < 200ms,  poor > 500ms
 *  CLS: good < 0.1,    poor > 0.25
 */
function metricToRatio(name: string, value: number): number {
  let max: number;
  if (name === "lcp") max = 5000;
  else if (name === "inp") max = 600;
  else max = 0.4; // CLS
  const ratio = 1 - Math.min(value / max, 1);
  return Math.max(ratio, 0.03); // minimum visible arc
}

function MetricGauge({ name, metric }: { name: string; metric: MetricData }) {
  const circleRef = useRef<SVGCircleElement>(null);
  const color = ratingColor(metric.rating);
  const ratio = metricToRatio(name, metric.value);

  useEffect(() => {
    const el = circleRef.current;
    if (!el) return;
    const offset = GAUGE_CIRCUMFERENCE - ratio * GAUGE_CIRCUMFERENCE;
    // Start from full offset (hidden) then animate
    el.style.strokeDashoffset = String(GAUGE_CIRCUMFERENCE);
    requestAnimationFrame(() => {
      el.style.transition = "stroke-dashoffset 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)";
      el.style.strokeDashoffset = String(offset);
    });
  }, [ratio]);

  const displayVal = formatMetric(metric.value, metric.unit);
  const unitLabel = metric.unit === "ms" ? "ms" : metric.unit || "";

  return (
    <div className="cwv-gauge">
      <svg viewBox="0 0 130 130">
        {/* Track */}
        <circle className="cwv-gauge-track" cx="65" cy="65" r={GAUGE_RADIUS} />
        {/* Fill */}
        <circle
          ref={circleRef}
          className="cwv-gauge-fill"
          cx="65" cy="65" r={GAUGE_RADIUS}
          stroke={color}
          strokeDasharray={GAUGE_CIRCUMFERENCE}
          strokeDashoffset={GAUGE_CIRCUMFERENCE}
          transform="rotate(-90 65 65)"
          style={{ filter: `drop-shadow(0 0 6px ${color}80)` }}
        />
        {/* Value text */}
        <text className="cwv-gauge-value" x="65" y="62" textAnchor="middle" dominantBaseline="middle">
          {displayVal}
        </text>
        <text className="cwv-gauge-unit" x="65" y="80" textAnchor="middle">
          {unitLabel}
        </text>
      </svg>
    </div>
  );
}

// ─── Main Component ────────────────────────────────────────────────────────────

export function CoreWebVitals() {
  const [url, setUrl] = useState("");
  const [strategy, setStrategy] = useState<"mobile" | "desktop">("mobile");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CWVResult | null>(null);
  const [error, setError] = useState("");

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const r = await fetch(`${API_BASE}/seo-tools/core-web-vitals`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          url: url.trim(), 
          strategy,
          api_key: localStorage.getItem("pagespeed_api_key") || undefined 
        }),
      });
      const d = await r.json();
      if (!r.ok || d.error) {
        setError(d.error || d.detail || `HTTP ${r.status}`);
      } else {
        setResult(d);
      }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
    } catch (err: any) {
      setError(err.message || "Lỗi kết nối");
    }
    setLoading(false);
  };

  // Sort opportunities by savings descending
  const sortedOpps = result?.opportunities
    ? [...result.opportunities].sort((a, b) => b.savings_ms - a.savings_ms)
    : [];

  return (
    <div className="cwv-container">
      {/* ── Input Form ── */}
      <form className="audit-form" onSubmit={handleCheck}>
        <div className="hint-box">
          ⚡ <strong>Core Web Vitals:</strong> Kiểm tra LCP, INP, CLS và điểm Lighthouse từ Google PageSpeed Insights.
        </div>

        <div className="input-row">
          <div className="input-group" style={{ flex: 1 }}>
            <label className="input-label">URL trang web</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
                <path d="M3.6 9h16.8M3.6 15h16.8" />
              </svg>
              <input
                type="url" className="text-input" value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="https://example.com" required
              />
            </div>
          </div>

          {/* Strategy toggle */}
          <div className="input-group">
            <label className="input-label">Thiết bị</label>
            <div className="cwv-strategy-toggle">
              <button
                type="button"
                className={`cwv-strategy-btn ${strategy === "mobile" ? "active" : ""}`}
                onClick={() => setStrategy("mobile")}
              >
                📱 Mobile
              </button>
              <button
                type="button"
                className={`cwv-strategy-btn ${strategy === "desktop" ? "active" : ""}`}
                onClick={() => setStrategy("desktop")}
              >
                🖥️ Desktop
              </button>
            </div>
          </div>

          <button
            className={`analyze-btn`}
            type="submit" disabled={loading || !url.trim()}
            style={{ alignSelf: "flex-end" }}
          >
            {loading ? <span className="btn-spinner" /> : "⚡ Kiểm tra"}
          </button>
        </div>

        {error && <p className="error-msg">❌ {error}</p>}
      </form>

      {/* ── Results ── */}
      {result && (
        <div className="cwv-container">
          {/* Overall status */}
          <div className={`cwv-status-banner status-${ratingClass(result.overall_status)}`}>
            <div className="cwv-status-dot" style={{ background: ratingColor(result.overall_status) }} />
            {result.overall_status === "good"
              ? "✅ Trang web đạt chuẩn Core Web Vitals"
              : result.overall_status === "needs_improvement"
              ? "⚠️ Trang web cần cải thiện Core Web Vitals"
              : "❌ Trang web không đạt chuẩn Core Web Vitals"
            }
          </div>

          {/* ── 3 Main Metric Gauges ── */}
          <h3 className="cwv-section-title">📊 Chỉ số Core Web Vitals</h3>
          <div className="cwv-metrics-grid">
            {(["lcp", "inp", "cls"] as const).map(key => {
              const metric = result.metrics[key];
              if (!metric) return null;
              const labels: Record<string, string> = {
                lcp: "Largest Contentful Paint",
                inp: "Interaction to Next Paint",
                cls: "Cumulative Layout Shift",
              };
              return (
                <div className="cwv-metric-card" key={key}>
                  <span className="cwv-metric-name">{labels[key]}</span>
                  <MetricGauge name={key} metric={metric} />
                  <div className={`cwv-metric-status ${ratingClass(metric.rating)}`}>
                    <span className="cwv-metric-status-dot" />
                    {ratingLabel(metric.rating)}
                  </div>
                </div>
              );
            })}
          </div>

          {/* ── 4 Lighthouse Score Cards ── */}
          <h3 className="cwv-section-title">🏆 Lighthouse Scores</h3>
          <div className="cwv-scores-grid">
            {([
              { key: "performance", label: "Performance" },
              { key: "seo", label: "SEO" },
              { key: "accessibility", label: "Accessibility" },
              { key: "best_practices", label: "Best Practices" },
            ] as const).map(item => {
              const score = result.lighthouse_scores?.[item.key as keyof LighthouseScores];
              const s = typeof score === "number" ? Math.round(score) : 0;
              const color = scoreColor(s);
              return (
                <div className="cwv-score-card" key={item.key}>
                  <span className="cwv-score-label">{item.label}</span>
                  <span className="cwv-score-value" style={{ color }}>{s}</span>
                </div>
              );
            })}
          </div>

          {/* ── Opportunities Table ── */}
          {sortedOpps.length > 0 && (
            <div className="cwv-opportunities">
              <h3>💡 Cơ hội cải thiện ({sortedOpps.length})</h3>
              <table className="cwv-opps-table">
                <thead>
                  <tr>
                    <th>Tên</th>
                    <th>Mô tả</th>
                    <th>Tiết kiệm (ms)</th>
                    <th>Điểm</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedOpps.map((opp, i) => (
                    <tr key={i}>
                      <td className="opps-name">{opp.name}</td>
                      <td className="opps-desc">{opp.description}</td>
                      <td className="opps-savings">
                        {opp.savings_ms > 0 ? `−${Math.round(opp.savings_ms)}ms` : "—"}
                      </td>
                      <td className="opps-score" style={{ color: scoreColor(opp.score * 100) }}>
                        {(opp.score * 100).toFixed(0)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
