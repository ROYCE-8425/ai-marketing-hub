import { useState } from "react";
import { usePolish } from "../hooks/usePolish";
import type { PolishSuccess } from "../hooks/usePolish";
import "./ContentPlanner.css";

interface PolishPanelProps {
  /** Callback when the humanized content is accepted — updates the draft. */
  onAccept: (humanized: string) => void;
  /** Callback to open the publish modal with humanized content. */
  onPublish: (humanized: string) => void;
}

export function PolishPanel({ onAccept, onPublish }: PolishPanelProps) {
  const [draft, setDraft] = useState("");
  const { loading, error, result, polish, reset } = usePolish();

  const hasResult = result !== null && result.success;
  const polishResult = result as PolishSuccess | null;

  const handlePolish = async () => {
    if (!draft.trim()) return;
    await polish(draft);
  };

  const handleAccept = () => {
    if (!polishResult) return;
    onAccept(polishResult.humanized_content);
    setDraft(polishResult.humanized_content);
    reset();
  };

  const handleCopy = () => {
    if (!polishResult) return;
    navigator.clipboard.writeText(polishResult.humanized_content).catch(() => {
      /* clipboard unavailable in some environments */
    });
  };

  const handlePublish = () => {
    if (!polishResult) return;
    onPublish(polishResult.humanized_content);
  };

  const handleDismiss = () => {
    reset();
  };

  return (
    <>
      {/* ── Draft Textarea ── */}
      <div className="writer-draft-area">
        <label className="writer-draft-label" htmlFor="writer-draft">
          AI Draft Content
        </label>
        <textarea
          id="writer-draft"
          className={`writer-draft-textarea${hasResult ? " polished" : ""}`}
          placeholder={
            "Paste your AI-generated article draft here...\n\n" +
            "Example content with AI telltale signs:\n" +
            "It is important to note that in today's digital landscape,\n" +
            "podcast hosting platforms have become increasingly essential.\n" +
            "Let's dive into the key factors that define success."
          }
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
      </div>

      {/* ── Action Bar ── */}
      <div className="polish-action-bar">
        <span className="polish-action-hint">
          Remove AI watermarks &amp; scores — no external API required.
        </span>

        <button
          type="button"
          className="polish-btn"
          disabled={loading || !draft.trim()}
          onClick={handlePolish}
          title="Polish & Humanize AI content"
        >
          {loading ? (
            <span className="btn-spinner" aria-label="Polishing" />
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          )}
          Polish &amp; Humanize
        </button>
      </div>

      {/* ── Loading state ── */}
      {loading && (
        <div className="polish-loading-row" role="status" aria-live="polite">
          <span className="btn-spinner" aria-hidden="true" />
          Running anti-detection scrub &amp; readability analysis…
        </div>
      )}

      {/* ── Error state ── */}
      {error && !loading && (
        <div className="polish-error-row" role="alert">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          {error}
        </div>
      )}

      {/* ── Result card ── */}
      {hasResult && polishResult && (
        <div className="polish-result-card" role="region" aria-label="Polish results">
          <div className="polish-result-header">
            <div className="polish-success-icon" aria-hidden="true">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <div>
              <p className="polish-result-title">Humanized Successfully</p>
              <p className="polish-result-subtitle">
                {polishResult.ai_watermarks_removed > 0
                  ? `Removed ${polishResult.ai_watermarks_removed} AI sign${polishResult.ai_watermarks_removed !== 1 ? "s" : ""}`
                  : "No AI watermarks detected — content is clean"}
              </p>
            </div>
          </div>

          {/* Metrics */}
          <div className="polish-metrics-row">
            {polishResult.ai_watermarks_removed > 0 && (
              <span className="polish-metric-chip signs">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
                </svg>
                {polishResult.ai_watermarks_removed} AI signs removed
              </span>
            )}

            <span className="polish-metric-chip readability">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
              </svg>
              Readability: {polishResult.readability_grade}
            </span>

            <span className="polish-metric-chip flesch">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
              </svg>
              Flesch Ease: {polishResult.flesch_reading_ease}
            </span>

            <span className="polish-metric-chip engagement">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              Engagement: {polishResult.engagement_score}/100
            </span>
          </div>

          {/* Scrub stats detail */}
          {polishResult.scrub_stats.ai_phrases_replaced > 0 && (
            <p style={{ fontSize: "11px", color: "var(--text-dim)", marginBottom: "10px" }}>
              Scrubbed: {polishResult.scrub_stats.ai_phrases_replaced} AI phrases,{" "}
              {polishResult.scrub_stats.unicode_removed} invisible chars,{" "}
              {polishResult.scrub_stats.format_control_removed} format-control chars
            </p>
          )}

          {/* Actions */}
          <div className="polish-actions">
            <button type="button" className="polish-action-btn btn-copy" onClick={handleCopy}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              Copy to Clipboard
            </button>
            <button type="button" className="polish-action-btn btn-publish" onClick={handlePublish}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
              </svg>
              Publish to WordPress
            </button>
            <button type="button" className="polish-action-btn btn-dismiss" onClick={handleDismiss}>
              Dismiss
            </button>
            <button type="button" className="polish-action-btn btn-copy" onClick={handleAccept}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Replace Draft
            </button>
          </div>
        </div>
      )}
    </>
  );
}
