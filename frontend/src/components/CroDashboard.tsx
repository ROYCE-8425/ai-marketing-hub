import type {
  CroAnalysis,
  SalesRiskAlert,
  CroChecklist,
  CtaAnalysis,
  AboveFoldAnalysis,
  TrustSignals,
} from "../types/seo";

// ─── Helpers ────────────────────────────────────────────────────────────────────

function ScorePill({ label, score }: { label: string; score: number }) {
  const color =
    score >= 80 ? "#10b981" : score >= 60 ? "#f59e0b" : "#ef4444";
  return (
    <div className="cro-pill">
      <span className="cro-pill-label">{label}</span>
      <span className="cro-pill-score" style={{ color }}>
        {score}
      </span>
    </div>
  );
}

function RiskAlertBadge({ alert }: { alert: SalesRiskAlert }) {
  const color = alert.severity === "high" ? "#ef4444" : "#f59e0b";
  const bg = alert.severity === "high"
    ? "rgba(239,68,68,0.1)"
    : "rgba(245,158,11,0.1)";
  const border = alert.severity === "high"
    ? "rgba(239,68,68,0.3)"
    : "rgba(245,158,11,0.3)";
  return (
    <div className="risk-alert-badge" style={{ background: bg, borderColor: border }}>
      <svg width="12" height="12" viewBox="0 0 24 24" fill={color} aria-hidden="true">
        <path d="M12 2L2 22h20L12 2zm0 15v2m0-4h.01" stroke={color} strokeWidth="2" fill="none" strokeLinecap="round" />
      </svg>
      <span style={{ color }}>{alert.message}</span>
    </div>
  );
}

function GlassCard({ children, title, accent }: { children: React.ReactNode; title: string; accent?: string }) {
  return (
    <div className="glass-card" style={{ "--accent": accent ?? "#8b5cf6" } as React.CSSProperties}>
      <h3 className="glass-card-title">{title}</h3>
      {children}
    </div>
  );
}

function CategoryMiniBar({ name, score }: { name: string; score: number }) {
  const color =
    score >= 80 ? "#10b981" : score >= 60 ? "#f59e0b" : "#ef4444";
  return (
    <div className="cro-mini-bar">
      <span className="cro-mini-bar-name">{name}</span>
      <div className="cro-mini-track">
        <div
          className="cro-mini-fill"
          style={{ width: `${score}%`, background: color }}
        />
      </div>
      <span className="cro-mini-score" style={{ color }}>{score}</span>
    </div>
  );
}

// ─── CTA Card ──────────────────────────────────────────────────────────────────

function CtaCard({ cta }: { cta: CtaAnalysis }) {
  const qualityColor =
    cta.avg_quality_score >= 70 ? "#10b981"
    : cta.avg_quality_score >= 50 ? "#f59e0b"
    : "#ef4444";

  return (
    <GlassCard title="Call-to-Action Analysis" accent="#22d3ee">
      <div className="cta-grid">
        <div className="cta-stat">
          <span className="cta-stat-num" style={{ color: qualityColor }}>
            {cta.total_ctas}
          </span>
          <span className="cta-stat-lbl">CTAs Found</span>
        </div>
        <div className="cta-stat">
          <span className="cta-stat-num" style={{ color: qualityColor }}>
            {cta.avg_quality_score}
          </span>
          <span className="cta-stat-lbl">Quality Score</span>
        </div>
        <div className="cta-stat">
          <span className="cta-stat-num">
            {cta.distribution.first_cta_position != null
              ? `${cta.distribution.first_cta_position.toFixed(0)}%`
              : "—"}
          </span>
          <span className="cta-stat-lbl">First CTA Position</span>
        </div>
        <div className="cta-stat">
          <span
            className="cta-stat-num"
            style={{
              color: cta.distribution.has_above_fold ? "#10b981" : "#ef4444",
            }}
          >
            {cta.distribution.has_above_fold ? "Yes" : "No"}
          </span>
          <span className="cta-stat-lbl">Above Fold</span>
        </div>
      </div>

      {cta.ctas_found.length > 0 && (
        <div className="cta-list">
          <p className="cta-list-title">CTAs Detected</p>
          {cta.ctas_found.map((c, i) => (
            <div key={i} className="cta-item">
              <span className="cta-item-text">"{c.text}"</span>
              <div className="cta-item-meta">
                <span className="cta-item-pos">{c.position_pct}%</span>
                <span
                  className="cta-item-score"
                  style={{
                    color:
                      c.quality_score >= 70 ? "#10b981"
                      : c.quality_score >= 50 ? "#f59e0b"
                      : "#ef4444",
                  }}
                >
                  {c.quality_score}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {cta.recommendations.slice(0, 2).map((r, i) => (
        <div key={i} className="cro-rec-badge">
          <span className="rec-priority">{r.priority.toUpperCase()}</span>
          <span>{r.recommendation}</span>
        </div>
      ))}
    </GlassCard>
  );
}

// ─── Above Fold Card ──────────────────────────────────────────────────────────

function AboveFoldCard({ atf }: { atf: AboveFoldAnalysis }) {
  const passColor = atf.passes_5_second_test ? "#10b981" : "#ef4444";

  return (
    <GlassCard title="Above the Fold — First Impression" accent="#a78bfa">
      <div className="atf-summary">
        <div
          className="atf-pass-badge"
          style={{
            background: atf.passes_5_second_test
              ? "rgba(16,185,129,0.12)"
              : "rgba(239,68,68,0.12)",
            borderColor: passColor,
          }}
        >
          <span style={{ color: passColor, fontWeight: 700 }}>
            {atf.passes_5_second_test ? "✓ Passes 5-Second Test" : "✗ Fails 5-Second Test"}
          </span>
        </div>
        <div className="atf-score-large" style={{ color: passColor }}>
          {atf.overall_score}
          <span className="atf-score-unit">/100</span>
        </div>
      </div>

      <div className="element-grid">
        {(
          [
            { key: "headline", label: "Headline" },
            { key: "value_prop", label: "Value Prop" },
            { key: "cta", label: "CTA" },
            { key: "trust", label: "Trust" },
          ] as const
        ).map(({ key, label }) => {
          const score = atf.element_scores[key];
          return (
            <div key={key} className="element-chip">
              <span className="element-chip-label">{label}</span>
              <span
                className="element-chip-score"
                style={{
                  color: score >= 70 ? "#10b981" : score >= 50 ? "#f59e0b" : "#ef4444",
                }}
              >
                {score}
              </span>
            </div>
          );
        })}
      </div>

      {atf.headline_text && (
        <div className="atf-hl-preview">
          <span className="atf-hl-label">Headline</span>
          <p className="atf-hl-text">"{atf.headline_text}"</p>
          <span className={`atf-hl-quality ${atf.headline_quality}`}>
            {atf.headline_quality}
          </span>
        </div>
      )}

      {atf.cta_text && (
        <div className="atf-cta-preview">
          <span className="atf-hl-label">First CTA</span>
          <p className="atf-hl-text" style={{ color: "#22d3ee" }}>
            "{atf.cta_text}"
          </p>
        </div>
      )}

      {atf.recommendations.length > 0 && (
        <div className="atf-recs">
          {atf.recommendations.slice(0, 2).map((r, i) => (
            <p key={i} className="atf-rec">→ {r}</p>
          ))}
        </div>
      )}
    </GlassCard>
  );
}

// ─── Trust Signals Card ────────────────────────────────────────────────────────

function TrustCard({ trust }: { trust: TrustSignals }) {
  const scoreColor =
    trust.overall_score >= 80 ? "#10b981"
    : trust.overall_score >= 60 ? "#f59e0b"
    : "#ef4444";

  return (
    <GlassCard title="Trust & Social Proof" accent="#10b981">
      <div className="trust-score-row">
        <div className="trust-score-circle" style={{ borderColor: scoreColor }}>
          <span style={{ color: scoreColor }}>{trust.overall_score}</span>
          <span className="trust-score-sub">/100</span>
        </div>
        <div className="trust-meta">
          <div className="trust-meta-item">
            <span className={`trust-dot ${trust.summary.testimonials_found > 0 ? "on" : "off"}`} />
            <span>{trust.summary.testimonials_found} testimonial(s)</span>
          </div>
          <div className="trust-meta-item">
            <span className={`trust-dot ${trust.summary.has_social_proof ? "on" : "off"}`} />
            <span>Social proof</span>
          </div>
          <div className="trust-meta-item">
            <span className={`trust-dot ${trust.summary.has_risk_reversal ? "on" : "off"}`} />
            <span>Risk reversal</span>
          </div>
        </div>
      </div>

      {trust.testimonials.length > 0 && (
        <div className="testimonial-list">
          <p className="section-label">Testimonials</p>
          {trust.testimonials.map((t, i) => (
            <div key={i} className="testimonial-item">
              <p className="testimonial-quote">"{t.quote}"</p>
              {t.attribution && (
                <span className="testimonial-attr">— {t.attribution}</span>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="trust-signal-chips">
        <div className="trust-chip-row">
          <span className="trust-chip-label">Free Trial</span>
          <span className={`trust-chip ${trust.risk_reversals.free_trial_found ? "on" : "off"}`}>
            {trust.risk_reversals.free_trial_found ? "✓" : "✗"}
          </span>
        </div>
        <div className="trust-chip-row">
          <span className="trust-chip-label">No Credit Card</span>
          <span className={`trust-chip ${trust.risk_reversals.no_credit_card_found ? "on" : "off"}`}>
            {trust.risk_reversals.no_credit_card_found ? "✓" : "✗"}
          </span>
        </div>
        <div className="trust-chip-row">
          <span className="trust-chip-label">Cancel Anytime</span>
          <span className={`trust-chip ${trust.risk_reversals.cancel_anytime_found ? "on" : "off"}`}>
            {trust.risk_reversals.cancel_anytime_found ? "✓" : "✗"}
          </span>
        </div>
        <div className="trust-chip-row">
          <span className="trust-chip-label">Guarantee</span>
          <span className={`trust-chip ${trust.risk_reversals.guarantee_found ? "on" : "off"}`}>
            {trust.risk_reversals.guarantee_found ? "✓" : "✗"}
          </span>
        </div>
      </div>

      {trust.weaknesses.length > 0 && (
        <div className="trust-weaknesses">
          <p className="section-label">Weaknesses</p>
          {trust.weaknesses.map((w, i) => (
            <p key={i} className="trust-weak">• {w}</p>
          ))}
        </div>
      )}
    </GlassCard>
  );
}

// ─── CRO Checklist Card ───────────────────────────────────────────────────────

function CroChecklistCard({ checklist }: { checklist: CroChecklist }) {
  return (
    <GlassCard title="CRO Checklist" accent="#f59e0b">
      <div className="check-summary">
        <span className="check-pass">{checklist.summary.passed} passed</span>
        <span className="check-sep">/</span>
        <span className="check-total">{checklist.summary.total_checks}</span>
        {checklist.critical_failures.length > 0 && (
          <span className="check-critical">
            {checklist.critical_failures.length} critical
          </span>
        )}
      </div>

      <div className="cro-category-list">
        {Object.entries(checklist.category_scores).map(([name, score]) => (
          <CategoryMiniBar
            key={name}
            name={name.replace(/_/g, " ")}
            score={score}
          />
        ))}
      </div>

      {checklist.critical_failures.length > 0 && (
        <div className="critical-list">
          <p className="section-label">Critical Failures</p>
          {checklist.critical_failures.map((f, i) => (
            <p key={i} className="critical-item">✗ {f}</p>
          ))}
        </div>
      )}

      {checklist.recommendations.slice(0, 3).map((r, i) => (
        <div key={i} className={`rec-badge priority-${r.priority}`}>
          <span className="rec-tag">{r.priority}</span>
          <span>{r.check}: {r.recommendation}</span>
        </div>
      ))}
    </GlassCard>
  );
}

// ─── Main Dashboard ────────────────────────────────────────────────────────────

export function CroDashboard({ cro }: { cro: CroAnalysis }) {
  return (
    <div className="cro-dashboard">
      {/* Sales risk alerts */}
      {cro.sales_risk_alerts.length > 0 && (
        <div className="risk-alerts-section">
          <p className="risk-section-label">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="#ef4444" aria-hidden="true">
              <path d="M12 2L2 22h20L12 2zm0 15v2m0-4h.01" stroke="#ef4444" strokeWidth="2" fill="none" strokeLinecap="round" />
            </svg>
            Sales Risk Alerts
          </p>
          <div className="risk-alerts-grid">
            {cro.sales_risk_alerts.map((alert, i) => (
              <RiskAlertBadge key={i} alert={alert} />
            ))}
          </div>
        </div>
      )}

      {/* CRO Overview pills */}
      <div className="cro-overview-row">
        <ScorePill label="CRO Score" score={cro.overall_cro_score} />
        <ScorePill
          label="CTA Effectiveness"
          score={cro.cta_analysis.overall_effectiveness}
        />
        <ScorePill
          label="Above Fold"
          score={cro.above_fold_analysis.overall_score}
        />
        <ScorePill
          label="Trust Score"
          score={cro.trust_signals.overall_score}
        />
      </div>

      {/* Grid of glassmorphism cards */}
      <div className="cro-grid">
        <CroChecklistCard checklist={cro.cro_checklist} />
        <CtaCard cta={cro.cta_analysis} />
        <AboveFoldCard atf={cro.above_fold_analysis} />
        <TrustCard trust={cro.trust_signals} />
      </div>
    </div>
  );
}
