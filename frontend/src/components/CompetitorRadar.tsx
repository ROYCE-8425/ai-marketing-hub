import { useState } from "react";
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid,
} from "recharts";
import type {
  CompetitorGapResponse,
  CompetitorResult,
  GapItem,
} from "../types/content";
import "./CompetitorRadar.css";

// ─── Scoring helpers ────────────────────────────────────────────────────────────

function scoreCompetitor(c: CompetitorResult): number {
  const wGaps    = Math.max(0, 10 - c.gaps.length) * 5;
  const wContent = Math.min(c.word_count / 50, 100);
  const wStruct  = Math.min(c.structure.length * 7, 100);
  return Math.round((wGaps + wContent + wStruct) / 3);
}

function gapPriorityColor(p: string): string {
  if (p === "high")   return "var(--red)";
  if (p === "medium") return "var(--amber)";
  return "var(--text-dim)";
}

// ─── Radar Tab ─────────────────────────────────────────────────────────────────

const CHART_METRICS = [
  { key: "content_score", label: "Content Depth" },
  { key: "structure_score", label: "Structure" },
  { key: "freshness_score", label: "Freshness" },
  { key: "gaps_score", label: "Completeness" },
];

function scoreMetrics(c: CompetitorResult) {
  return {
    url:         c.title || c.url,
    content_score:   Math.min(Math.round(c.word_count / 50), 100),
    structure_score: Math.min(c.structure.length * 8, 100),
    freshness_score: c.outdated_items.length === 0 ? 85 : 30,
    gaps_score:      Math.max(0, 100 - c.gaps.length * 15),
  };
}

function CompetitorRadar({ data }: { data: CompetitorGapResponse }) {
  const radarData = data.competitors.map(scoreMetrics);

  return (
    <div className="radar-section">
      <h3 className="section-title">Competitor Radar Chart</h3>
      <p className="section-desc">Comparing content depth, structure, freshness &amp; gaps across competitors</p>
      <div className="radar-container">
        <ResponsiveContainer width="100%" height={320}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="var(--border)" />
            <PolarAngleAxis
              dataKey="url"
              tick={{ fill: "var(--text)", fontSize: 11 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: "var(--text-dim)", fontSize: 10 }}
              stroke="var(--border)"
            />
            {CHART_METRICS.map((m) => (
              <Radar
                key={m.key}
                name={m.label}
                dataKey={m.key}
                stroke="#8b5cf6"
                fill="#8b5cf6"
                fillOpacity={0.15}
                strokeWidth={2}
              />
            ))}
            <Tooltip
              contentStyle={{
                background: "var(--surface2)",
                border: "1px solid var(--border)",
                borderRadius: 8,
                color: "var(--text-h)",
              }}
            />
            <Legend
              wrapperStyle={{ color: "var(--text)", fontSize: 12 }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ─── Bar Chart Tab ─────────────────────────────────────────────────────────────

function CompetitorBars({ data }: { data: CompetitorGapResponse }) {
  const barData = data.competitors.map((c) => ({
    name:   (c.title || c.url).slice(0, 20),
    "Word Count": c.word_count,
    "Gaps Found": c.gaps.length,
    "Structures": c.structure.length,
  }));

  return (
    <div className="radar-section">
      <h3 className="section-title">Content Metrics Comparison</h3>
      <p className="section-desc">Word count, gaps, and H2 structure count per competitor</p>
      <div className="radar-container">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={barData} barCategoryGap="30%">
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="name" tick={{ fill: "var(--text)", fontSize: 11 }} />
            <YAxis tick={{ fill: "var(--text-dim)", fontSize: 10 }} />
            <Tooltip
              contentStyle={{
                background: "var(--surface2)",
                border: "1px solid var(--border)",
                borderRadius: 8,
                color: "var(--text-h)",
              }}
            />
            <Legend wrapperStyle={{ color: "var(--text)", fontSize: 12 }} />
            <Bar dataKey="Word Count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Structures" fill="#22d3ee" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Gaps Found" fill="#ef4444" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ─── Gap Table ─────────────────────────────────────────────────────────────────

function GapTable({ gaps }: { gaps: GapItem[] }) {
  if (!gaps.length) return <p className="empty-state">No gaps found.</p>;

  return (
    <div className="gap-table-wrapper">
      <table className="gap-table">
        <thead>
          <tr>
            <th>Priority</th>
            <th>Type</th>
            <th>Location</th>
            <th>Opportunity</th>
          </tr>
        </thead>
        <tbody>
          {gaps.map((g, i) => (
            <tr key={i}>
              <td>
                <span
                  className="priority-badge"
                  style={{ color: gapPriorityColor(g.priority) }}
                >
                  {g.priority.toUpperCase()}
                </span>
              </td>
              <td className="type-cell">{g.type.replace(/_/g, " ")}</td>
              <td className="location-cell">{g.location}</td>
              <td className="opportunity-cell">{g.opportunity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Blueprint Block ──────────────────────────────────────────────────────────

function BlueprintBlock({ data }: { data: CompetitorGapResponse }) {
  const { blueprint } = data;

  return (
    <div className="blueprint-block">
      <h3 className="section-title">Beat-Them Blueprint</h3>

      <div className="blueprint-cards">
        <div className="bp-card bp-must-fill">
          <h4 className="bp-card-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            Must-Fill Gaps ({blueprint.must_fill_gaps.length})
          </h4>
          <ul className="bp-list">
            {blueprint.must_fill_gaps.slice(0, 6).map((g, i) => (
              <li key={i} className="bp-list-item">{g.opportunity}</li>
            ))}
            {blueprint.must_fill_gaps.length === 0 && (
              <li className="bp-list-empty">No universal gaps detected across competitors</li>
            )}
          </ul>
        </div>

        <div className="bp-card bp-structure">
          <h4 className="bp-card-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <line x1="8" y1="6" x2="21" y2="6" /><line x1="8" y1="12" x2="21" y2="12" />
              <line x1="8" y1="18" x2="21" y2="18" /><line x1="3" y1="6" x2="3.01" y2="6" />
              <line x1="3" y1="12" x2="3.01" y2="12" /><line x1="3" y1="18" x2="3.01" y2="18" />
            </svg>
            Google-Validated Structure ({blueprint.structure_to_match.length})
          </h4>
          <ul className="bp-list">
            {blueprint.structure_to_match.slice(0, 8).map((s, i) => (
              <li key={i} className="bp-structure-item">
                <span className="bp-check">✓</span>
                {s}
              </li>
            ))}
          </ul>
        </div>

        <div className="bp-card bp-outdated">
          <h4 className="bp-card-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            Outdated Info to Update ({blueprint.outdated_to_update.length})
          </h4>
          <ul className="bp-list">
            {blueprint.outdated_to_update.slice(0, 5).map((item, i) => (
              <li key={i} className="bp-list-item outdated-item">{item}</li>
            ))}
            {blueprint.outdated_to_update.length === 0 && (
              <li className="bp-list-empty">Content appears up-to-date</li>
            )}
          </ul>
        </div>
      </div>

      {blueprint.differentiation_opportunities.length > 0 && (
        <div className="differentiation-block">
          <h4 className="section-title" style={{ fontSize: "12px" }}>Differentiation Angles</h4>
          <div className="diff-tags">
            {blueprint.differentiation_opportunities.map((opp, i) => (
              <span key={i} className="diff-tag">{opp}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Main CompetitorRadarExport ─────────────────────────────────────────────────

export function CompetitorRadarPanel({ data }: { data: CompetitorGapResponse }) {
  const [activeSubTab, setActiveSubTab] = useState<"radar" | "bars" | "gaps">("radar");

  return (
    <div className="result-panel">
      <div className="result-header">
        <div className="result-meta">
          <h2 className="result-title">Competitor Radar</h2>
          <p className="result-keyword">
            Keyword: <strong>{data.primary_keyword || "—"}</strong>
          </p>
          <p className="result-wordcount">
            {data.competitors_analyzed} competitors analyzed · {data.total_gaps_found} gaps found
          </p>
        </div>
        <div className="header-stat">
          <span className="header-stat-num">{scoreCompetitor(data.competitors[0] ?? {
            gaps: [], word_count: 0, structure: [], url: "", title: "", strengths: [], outdated_items: [],
          } as CompetitorResult)}</span>
          <span className="header-stat-label">Top Score</span>
        </div>
      </div>

      {/* Sub-tabs */}
      <div className="sub-tab-bar">
        {(["radar", "bars", "gaps"] as const).map((t) => (
          <button
            key={t}
            className={`sub-tab-btn ${activeSubTab === t ? "sub-tab-active" : ""}`}
            onClick={() => setActiveSubTab(t)}
          >
            {t === "radar" ? "Radar" : t === "bars" ? "Bar Chart" : "Gap Table"}
          </button>
        ))}
      </div>

      {activeSubTab === "radar"   && <CompetitorRadar data={data} />}
      {activeSubTab === "bars"    && <CompetitorBars data={data} />}
      {activeSubTab === "gaps"    && (
        <div className="radar-section">
          <h3 className="section-title">All Gaps ({data.total_gaps_found})</h3>
          <GapTable gaps={data.competitors.flatMap((c) => c.gaps)} />
        </div>
      )}

      <BlueprintBlock data={data} />

      {data.scraping_errors.length > 0 && (
        <div className="scraping-errors">
          <h4 className="section-title" style={{ color: "var(--amber)" }}>Scraping Errors</h4>
          <ul className="error-list">
            {data.scraping_errors.map((e, i) => (
              <li key={i} className="error-item">{e}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
