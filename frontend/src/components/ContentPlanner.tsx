import { useState } from "react";
import type { PlanContentResponse, SectionResult } from "../types/content";
import { PolishPanel } from "./PolishPanel";
import "./ContentPlanner.css";

// ─── Section type → icon/label/color ────────────────────────────────────────────

const TYPE_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  intro:          { label: "Introduction", color: "#8b5cf6", icon: "→" },
  body_how_to:    { label: "How-To",       color: "#10b981", icon: "⚙" },
  body_comparison:{ label: "Comparison",    color: "#22d3ee", icon: "⟷" },
  body_explanation:{ label: "Explanation", color: "#f59e0b", icon: "◈" },
  body_list:      { label: "List",         color: "#f59e0b", icon: "≡" },
  faq:            { label: "FAQ",          color: "#22d3ee", icon: "?" },
  conclusion:     { label: "Conclusion",  color: "#ef4444", icon: "✓" },
};

function typeLabel(t: string) {
  return TYPE_CONFIG[t]?.label ?? t.replace(/_/g, " ");
}
function typeColor(t: string) {
  return TYPE_CONFIG[t]?.color ?? "var(--primary)";
}
function typeIcon(t: string) {
  return TYPE_CONFIG[t]?.icon ?? "◆";
}

// ─── Section badge ─────────────────────────────────────────────────────────────

function SectionTypeBadge({ type }: { type: string }) {
  return (
    <span
      className="section-type-badge"
      style={{ color: typeColor(type), borderColor: typeColor(type) + "40" }}
    >
      {typeIcon(type)} {typeLabel(type)}
    </span>
  );
}

// ─── Tree node ─────────────────────────────────────────────────────────────────

function TreeNode({ section, index }: { section: SectionResult; index: number }) {
  // isIntro / isConclusion / ctaColor reserved for future layout logic
  const _isIntro    = index === 0;
  const _isConclusion = index > 0 && (section.type === "conclusion" || index === 0);
  const _ctaColor = section.cta ? "var(--green)" : "transparent";
  void _isIntro; void _isConclusion; void _ctaColor; // suppress unused warnings

  return (
    <div className="tree-node">
      {/* Connector line */}
      {index > 0 && <div className="tree-connector" />}

      <div className="tree-card" style={{ borderLeftColor: typeColor(section.type) }}>
        {/* Header */}
        <div className="tree-card-header">
          <div className="tree-number">{section.section_number}</div>
          <div className="tree-heading">{section.heading}</div>
          <SectionTypeBadge type={section.type} />
        </div>

        {/* Meta row */}
        <div className="tree-meta-row">
          <span className="tree-meta-chip">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
            </svg>
            {section.word_target.toLocaleString()} words
          </span>

          {section.cta && (
            <span className="tree-meta-chip cta-chip" style={{ color: "var(--green)" }}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
              {section.cta.toUpperCase()} CTA
            </span>
          )}

          {section.featured_snippet && (
            <span className="tree-meta-chip snippet-chip">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              Featured Snippet
            </span>
          )}

          {section.mini_story && (
            <span className="tree-meta-chip story-chip">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>
              </svg>
              Mini-Story
            </span>
          )}
        </div>

        {/* Details */}
        <div className="tree-details">
          {section.strategic_angle && (
            <p className="tree-angle">
              <span className="tree-detail-label">Angle:</span> {section.strategic_angle}
            </p>
          )}
          {section.engagement_hook && (
            <p className="tree-hook">
              <span className="tree-detail-label">Hook:</span> {section.engagement_hook}
            </p>
          )}
          {section.knowledge_gaps.length > 0 && (
            <div className="tree-gaps">
              <span className="tree-detail-label">Gaps Addressed:</span>
              <div className="tree-gap-tags">
                {section.knowledge_gaps.map((g, i) => (
                  <span key={i} className="tree-gap-tag">{g}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Timeline track ────────────────────────────────────────────────────────────

function TimelineTrack({ sections }: { sections: SectionResult[] }) {
  return (
    <div className="timeline-track">
      <div className="timeline-bar">
        {sections.map((sec, i) => (
          <div
            key={i}
            className="timeline-segment"
            style={{
              flex: sec.word_target,
              background: typeColor(sec.type) + "30",
              borderColor: typeColor(sec.type),
            }}
            title={`${sec.heading} — ${sec.word_target} words`}
          />
        ))}
      </div>
      <div className="timeline-labels">
        {sections.map((sec, i) => (
          <span key={i} className="timeline-label" style={{ color: typeColor(sec.type) }}>
            {sec.section_number}
          </span>
        ))}
      </div>
    </div>
  );
}

// ─── Title Options ─────────────────────────────────────────────────────────────

function TitleOptions({ meta }: { meta: PlanContentResponse["meta"] }) {
  return (
    <div className="title-options-block">
      <h4 className="section-sub-title">Title Options</h4>
      <div className="title-options-list">
        {meta.title_options.map((title, i) => (
          <div key={i} className="title-option-item">
            <span className="title-num">{i + 1}</span>
            <span className="title-text">{title}</span>
          </div>
        ))}
      </div>
      <div className="meta-details-grid">
        <div className="meta-detail">
          <span className="meta-detail-label">Meta Title</span>
          <span className="meta-detail-value">{meta.meta_title}</span>
        </div>
        <div className="meta-detail">
          <span className="meta-detail-label">Slug</span>
          <span className="meta-detail-value mono">/blog/{meta.url_slug}</span>
        </div>
      </div>
    </div>
  );
}

// ─── Main ContentPlanner ────────────────────────────────────────────────────────

interface ContentPlannerPanelProps {
  plan: PlanContentResponse;
  /** Called when user wants to open the publish modal with final content. */
  onPublish?: (articleTitle: string, articleContent: string) => void;
}

export function ContentPlannerPanel({ plan, onPublish }: ContentPlannerPanelProps) {
  // AI Writer draft state — populated only via AI polish flow
  const [writerDraft, setWriterDraft] = useState("");

  const handlePolishAccept = (humanized: string) => {
    setWriterDraft(humanized);
  };

  const handlePolishPublish = (humanized: string) => {
    onPublish?.(
      plan.meta.title_options[0] || plan.topic,
      humanized
    );
  };

  // Warn if user tries to publish the outline skeleton directly
  const handleOutlinePublish = () => {
    const placeholders = plan.sections
      .map((s) => `[Write section ${s.section_number} here`)
      .join(", ");
    const confirmed = window.confirm(
      `⚠️ Publishing this outline will send placeholder content:\n"${placeholders}"\n\n` +
      `Use the AI Writer tab to generate full article sections before publishing. ` +
      `Are you sure you want to publish anyway?`
    );
    if (!confirmed) return;
    const outlineText = plan.sections
      .map((s) => `## ${s.heading}\n\n[Write section ${s.section_number} here — ${s.word_target} words]`)
      .join("\n\n");
    onPublish?.(
      plan.meta.title_options[0] || plan.topic,
      `# ${plan.topic}\n\n${outlineText}`
    );
  };

  return (
    <div className="result-panel">
      <div className="result-header">
        <div className="result-meta">
          <h2 className="result-title">AI Content Outline</h2>
          <p className="result-keyword">
            Topic: <strong>{plan.topic}</strong>
          </p>
          <p className="result-wordcount">
            {plan.sections.length} sections · {plan.total_word_target.toLocaleString()} target words
          </p>
        </div>
        <div className="header-stat">
          <span className="header-stat-num">{plan.sections.length}</span>
          <span className="header-stat-label">Sections</span>
        </div>
      </div>

      {/* Meta */}
      <TitleOptions meta={plan.meta} />

      {/* Timeline track */}
      <div className="section-block">
        <h3 className="section-title">Content Timeline</h3>
        <TimelineTrack sections={plan.sections} />
      </div>

      {/* Tree outline */}
      <div className="section-block">
        <h3 className="section-title">Section Outline</h3>
        <div className="tree-outline">
          {plan.sections.map((section, i) => (
            <TreeNode key={i} section={section} index={i} />
          ))}
        </div>
      </div>

      {/* CTA plan */}
      <div className="section-block">
        <h3 className="section-title">CTA &amp; Engagement Map</h3>
        <div className="engagement-grid">
          {Object.entries(plan.engagement_map.ctas).map(([type, section_num]) => (
            <div key={type} className="engagement-chip">
              <span className="engagement-label">{type.toUpperCase()}</span>
              <span className="engagement-section">Section {section_num}</span>
            </div>
          ))}
          {plan.engagement_map.mini_stories.map((s) => (
            <div key={`story-${s}`} className="engagement-chip story">
              <span className="engagement-label">STORY</span>
              <span className="engagement-section">Section {s}</span>
            </div>
          ))}
          {plan.engagement_map.featured_snippets.map((s) => (
            <div key={`snippet-${s}`} className="engagement-chip snippet">
              <span className="engagement-label">SNIPPET</span>
              <span className="engagement-section">Section {s}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Full outline (raw) */}
      <details className="outline-details">
        <summary className="outline-summary">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
          Full Markdown Outline
        </summary>
        <pre className="outline-pre">{plan.markdown_outline}</pre>
      </details>

      {/* ── AI Writer — Polish & Humanize Section ── */}
      <div className="section-block">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "14px" }}>
          <h3 className="section-title" style={{ margin: 0 }}>AI Writer</h3>
          {writerDraft && (
            <button
              type="button"
              onClick={handleOutlinePublish}
              style={{
                fontSize: "12px",
                padding: "5px 12px",
                background: "rgba(139,92,246,0.1)",
                border: "1px solid rgba(139,92,246,0.25)",
                borderRadius: "99px",
                color: "var(--primary)",
                cursor: "pointer",
              }}
            >
              Publish Outline as Draft
            </button>
          )}
        </div>

        {/* Polish panel: textarea + action bar + result */}
        <PolishPanel
          onAccept={handlePolishAccept}
          onPublish={handlePolishPublish}
        />
      </div>
    </div>
  );
}