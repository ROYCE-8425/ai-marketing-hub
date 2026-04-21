import type { OpportunitiesResponse } from "../types/phase5";
import "./CampaignTracker.css";

// ─── Intent badge colors ───────────────────────────────────────────────────────

const INTENT_COLOR: Record<string, string> = {
  informational: "#8b5cf6",
  navigational: "#22d3ee",
  transactional: "#10b981",
  commercial_investigation: "#f59e0b",
};

function IntentBadge({ intent }: { intent: string }) {
  const color = INTENT_COLOR[intent] ?? "var(--text)";
  return (
    <span
      className="intent-badge"
      style={{ color, borderColor: color + "40", background: color + "15" }}
    >
      {intent.replace(/_/g, " ")}
    </span>
  );
}

// ─── Verdict banner ───────────────────────────────────────────────────────────

function VerdictBanner({ data }: { data: OpportunitiesResponse }) {
  const { low_hanging_fruit, effort_level, verdict } = data;
  const isGood = low_hanging_fruit;
  const bg = isGood ? "rgba(16,185,129,0.12)" : "rgba(239,68,68,0.12)";
  const border = isGood ? "#10b981" : "#ef4444";
  const icon = isGood ? (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  ) : (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5">
      <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
  const label = isGood ? "Low-Hanging Fruit" : "High Effort";

  return (
    <div className="verdict-banner" style={{ background: bg, borderColor: border }}>
      <div className="verdict-left">
        {icon}
        <span className="verdict-label">{label}</span>
        <span className="verdict-effort">Effort: {effort_level}</span>
      </div>
      <p className="verdict-text">{verdict}</p>
    </div>
  );
}

// ─── Score gauge ───────────────────────────────────────────────────────────────

function ScoreGauge({ score, label }: { score: number; label: string }) {
  const color = score >= 70 ? "#10b981" : score >= 45 ? "#f59e0b" : "#ef4444";
  const r = 36;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  return (
    <div className="score-gauge">
      <svg width="90" height="90" viewBox="0 0 90 90">
        <circle cx="45" cy="45" r={r} fill="none" stroke="var(--border)" strokeWidth="8" />
        <circle
          cx="45" cy="45" r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={`${dash} ${circ}`}
          strokeDashoffset={circ / 4}
          strokeLinecap="round"
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
      </svg>
      <div className="gauge-inner">
        <span className="gauge-score" style={{ color }}>{Math.round(score)}</span>
        <span className="gauge-label">{label}</span>
      </div>
    </div>
  );
}

// ─── Score breakdown bars ─────────────────────────────────────────────────────

function ScoreBarRow({ label, value }: { label: string; value: number }) {
  const color = value >= 70 ? "#10b981" : value >= 45 ? "#f59e0b" : "#ef4444";
  return (
    <div className="score-bar-row">
      <span className="sb-label">{label}</span>
      <div className="sb-track">
        <div className="sb-fill" style={{ width: `${value}%`, background: color }} />
      </div>
      <span className="sb-value" style={{ color }}>{Math.round(value)}</span>
    </div>
  );
}

// ─── Category scores ───────────────────────────────────────────────────────────

function CategoryScoresCard({ cats }: {
  cats: OpportunitiesResponse["landing_page"]["category_scores"]
}) {
  const entries: [string, number][] = [
    ["Above Fold", cats.above_fold],
    ["CTAs", cats.ctas],
    ["Trust Signals", cats.trust_signals],
    ["Structure", cats.structure],
    ["SEO", cats.seo],
  ];
  return (
    <div className="cat-scores-card">
      <h4 className="card-sub-title">Landing Page Scores</h4>
      {entries.map(([label, val]) => (
        <ScoreBarRow key={label} label={label} value={val} />
      ))}
    </div>
  );
}

// ─── Intent recommendation pills ──────────────────────────────────────────────

function InsightList({ title, items, color }: {
  title: string; items: string[]; color: string;
}) {
  if (!items.length) return null;
  return (
    <div className="insight-section">
      <h4 className="card-sub-title" style={{ color }}>{title}</h4>
      <ul className="insight-list">
        {items.map((item, i) => (
          <li key={i} className="insight-item">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
              stroke={color} strokeWidth="2.5" aria-hidden="true">
              <polyline points="9 18 15 12 9 6" />
            </svg>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

// ─── Traffic projection card ─────────────────────────────────────────────────

function TrafficCard({ tp }: {
  tp: NonNullable<OpportunitiesResponse["traffic_projection"]>;
}) {
  const gain = tp.percent_increase >= 0
    ? `+${tp.percent_increase}%`
    : `${tp.percent_increase}%`;
  const gainColor = tp.percent_increase >= 0 ? "#10b981" : "#ef4444";

  return (
    <div className="traffic-card">
      <h4 className="card-sub-title">Traffic Projection</h4>
      <div className="traffic-grid">
        <div className="traffic-stat">
          <span className="traffic-now">
            {tp.current_clicks.toLocaleString()}<span className="traffic-unit">/mo</span>
          </span>
          <span className="traffic-label">Current Clicks</span>
        </div>
        <div className="traffic-arrow">→</div>
        <div className="traffic-stat">
          <span className="traffic-target" style={{ color: "#10b981" }}>
            {tp.potential_clicks.toLocaleString()}<span className="traffic-unit">/mo</span>
          </span>
          <span className="traffic-label">Target Clicks (Pos #{tp.target_position})</span>
        </div>
        <div className="traffic-stat">
          <span className="traffic-gain" style={{ color: gainColor }}>{gain}</span>
          <span className="traffic-label">Est. Gain</span>
        </div>
      </div>
    </div>
  );
}

// ─── Priority badge ────────────────────────────────────────────────────────────

const PRIORITY_COLOR: Record<string, string> = {
  CRITICAL: "#ef4444",
  HIGH: "#f97316",
  MEDIUM: "#f59e0b",
  LOW: "#22d3ee",
  SKIP: "#4a5578",
};

function PriorityBadge({ priority }: { priority: string }) {
  const color = PRIORITY_COLOR[priority] ?? "var(--text)";
  return (
    <span
      className="priority-badge"
      style={{ color, borderColor: color + "40", background: color + "15" }}
    >
      {priority}
    </span>
  );
}

// ─── Main CampaignTracker panel ────────────────────────────────────────────────

export function CampaignTrackerPanel({ data }: { data: OpportunitiesResponse }) {
  const { intent_analysis, landing_page, opportunity_score, traffic_projection,
    insight_adjustments, action_items } = data;

  return (
    <div className="result-panel">
      {/* Header */}
      <div className="result-header">
        <div className="result-meta">
          <h2 className="result-title">Campaign Tracker</h2>
          <p className="result-keyword">
            Keyword: <strong>{intent_analysis.keyword}</strong>
          </p>
          <p className="result-url">{data.url}</p>
          <div className="header-tags">
            <IntentBadge intent={intent_analysis.primary_intent} />
            <PriorityBadge priority={opportunity_score.priority} />
          </div>
        </div>
        <div className="header-dual-gauges">
          <ScoreGauge score={opportunity_score.final_score} label="Opportunity" />
          <ScoreGauge score={landing_page.overall_score} label="LP Score" />
        </div>
      </div>

      {/* Verdict */}
      <VerdictBanner data={data} />

      {/* Key stats row */}
      <div className="opp-stats-row">
        <div className="opp-stat-chip">
          <span className="osc-label">Primary Factor</span>
          <span className="osc-value">{opportunity_score.primary_factor.replace(/_/g, " ")}</span>
        </div>
        <div className="opp-stat-chip">
          <span className="osc-label">LP Word Count</span>
          <span className="osc-value">{landing_page.word_count.toLocaleString()}</span>
        </div>
        <div className="opp-stat-chip">
          <span className="osc-label">CTAs Found</span>
          <span className="osc-value">{landing_page.cta_count}</span>
        </div>
        <div className="opp-stat-chip">
          <span className="osc-label">Publishing Ready</span>
          <span
            className="osc-value"
            style={{ color: landing_page.publishing_ready ? "#10b981" : "#ef4444" }}
          >
            {landing_page.publishing_ready ? "Yes" : "No"}
          </span>
        </div>
      </div>

      {/* Score breakdown + categories side-by-side */}
      <div className="scores-split">
        <div className="section-block">
          <h3 className="section-title">Opportunity Score Breakdown</h3>
          {Object.entries(opportunity_score.score_breakdown).map(([key, val]) => (
            <ScoreBarRow
              key={key}
              label={key.replace(/_/g, " ")}
              value={val}
            />
          ))}
          <div className="score-explanation">
            <p>{opportunity_score.score_explanation}</p>
          </div>
        </div>

        <CategoryScoresCard cats={landing_page.category_scores} />
      </div>

      {/* Intent analysis */}
      <div className="section-block">
        <h3 className="section-title">Search Intent Analysis</h3>
        <div className="intent-conf-grid">
          {Object.entries(intent_analysis.confidence).map(([intent, pct]) => {
            const color = INTENT_COLOR[intent] ?? "var(--text)";
            return (
              <div key={intent} className="intent-conf-bar">
                <span className="icb-label">{intent.replace(/_/g, " ")}</span>
                <div className="icb-track">
                  <div
                    className="icb-fill"
                    style={{ width: `${pct}%`, background: color }}
                  />
                </div>
                <span className="icb-pct" style={{ color }}>{Math.round(pct)}%</span>
              </div>
            );
          })}
        </div>
        {intent_analysis.secondary_intent && (
          <p className="intent-secondary">
            Secondary intent: <strong>{intent_analysis.secondary_intent.replace(/_/g, " ")}</strong>
          </p>
        )}
        {intent_analysis.recommendations.length > 0 && (
          <InsightList
            title="Content Intent Recommendations"
            items={intent_analysis.recommendations.slice(0, 4)}
            color="#8b5cf6"
          />
        )}
      </div>

      {/* Traffic projection */}
      {traffic_projection && (
        <TrafficCard tp={traffic_projection} />
      )}

      {/* Insight adjustments */}
      {insight_adjustments.length > 0 && (
        <div className="section-block">
          <h3 className="section-title">Intent-Driven Insight Adjustments</h3>
          <ul className="insight-list">
            {insight_adjustments.map((adj, i) => (
              <li key={i} className="insight-item">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
                  stroke="#22d3ee" strokeWidth="2.5" aria-hidden="true">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                {adj}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Critical issues */}
      {landing_page.critical_issues.length > 0 && (
        <div className="section-block">
          <h3 className="section-title critical-title">Critical Issues</h3>
          <div className="issues-list">
            {landing_page.critical_issues.map((t, i) => (
              <span key={i} className="issue-badge badge-critical">{t}</span>
            ))}
          </div>
        </div>
      )}

      {/* Action items */}
      <div className="section-block">
        <h3 className="section-title">Next Action Items</h3>
        <div className="action-grid">
          {action_items.map((item, i) => (
            <div key={i} className="action-item">
              <span className="action-num">{i + 1}</span>
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
