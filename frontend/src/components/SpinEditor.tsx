import { useState } from "react";
import { API_BASE } from "../lib/apiConfig";

interface DiffSegment {
  type: "same" | "removed" | "added";
  text: string;
}

interface SpinResult {
  original: string;
  rewritten: string;
  diff: DiffSegment[];
  uniqueness_percent: number;
  similarity_percent: number;
  original_words: number;
  rewritten_words: number;
  level: string;
  tone: string;
  preserved_keywords: string[];
  version?: number;
}

interface MultiResult {
  versions: SpinResult[];
  total_versions: number;
  best_uniqueness: number;
}

export function SpinEditor() {
  const [content, setContent] = useState("");
  const [level, setLevel] = useState<"light" | "medium" | "heavy">("medium");
  const [tone, setTone] = useState("neutral");
  const [keywords, setKeywords] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SpinResult | null>(null);
  const [multiResult, setMultiResult] = useState<MultiResult | null>(null);
  const [activeVersion, setActiveVersion] = useState(0);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState<"side" | "diff">("side");
  const [spinMode, setSpinMode] = useState<"single" | "multi" | "paragraph">("single");
  const [copied, setCopied] = useState(false);

  const handleSpin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || content.trim().length < 20) {
      setError("Nội dung cần ít nhất 20 ký tự");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    setMultiResult(null);

    const preserveKws = keywords.split(",").map(k => k.trim()).filter(Boolean);
    const body = {
      content: content.trim(),
      level,
      tone,
      preserve_keywords: preserveKws.length > 0 ? preserveKws : null,
    };

    try {
      if (spinMode === "multi") {
        const r = await fetch(`${API_BASE}/content/spin-multi`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...body, num_versions: 3 }),
        });
        const d = await r.json();
        if (d.error) { setError(d.error); }
        else { setMultiResult(d); setActiveVersion(0); }
      } else if (spinMode === "paragraph") {
        const r = await fetch(`${API_BASE}/content/spin-paragraphs`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const d = await r.json();
        if (d.error) { setError(d.error); }
        else if (d.full_rewritten) {
          // Map paragraph result to SpinResult format
          setResult({
            original: content.trim(),
            rewritten: d.full_rewritten,
            diff: [],
            uniqueness_percent: d.overall_uniqueness,
            similarity_percent: 100 - d.overall_uniqueness,
            original_words: content.trim().split(/\s+/).length,
            rewritten_words: d.full_rewritten.split(/\s+/).length,
            level, tone,
            preserved_keywords: preserveKws,
          });
        } else { setResult(d); }
      } else {
        const r = await fetch(`${API_BASE}/content/spin`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const d = await r.json();
        if (d.error) { setError(d.error); }
        else { setResult(d); }
      }
    } catch (e: any) {
      setError(e.message || "Lỗi kết nối");
    }
    setLoading(false);
  };

  const copyText = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const uniquenessColor = (pct: number) => {
    if (pct >= 70) return "#22c55e";
    if (pct >= 40) return "#f59e0b";
    return "#ef4444";
  };

  const levelLabels: Record<string, { label: string; desc: string; color: string }> = {
    light: { label: "Nhẹ", desc: "~30%", color: "#3b82f6" },
    medium: { label: "Vừa", desc: "~60%", color: "#f59e0b" },
    heavy: { label: "Mạnh", desc: "~90%", color: "#ef4444" },
  };

  const toneLabels: Record<string, { label: string; icon: string }> = {
    neutral: { label: "Trung lập", icon: "📝" },
    professional: { label: "Chuyên nghiệp", icon: "🏢" },
    friendly: { label: "Thân thiện", icon: "😊" },
    sales: { label: "Bán hàng", icon: "💰" },
  };

  const currentResult = multiResult
    ? multiResult.versions[activeVersion]
    : result;

  return (
    <div className="spin-editor">
      <form className="spin-form" onSubmit={handleSpin}>
        <div className="hint-box">
          ✍️ <strong>Spin Editor:</strong> Viết lại nội dung bằng AI —
          chọn giọng văn, mức độ, tạo nhiều phiên bản cùng lúc.
        </div>

        {/* Spin mode selector */}
        <div className="spin-mode-row">
          <span className="spin-level-label">Chế độ:</span>
          <div className="spin-level-btns">
            {([
              { id: "single", label: "1 bản", icon: "📄" },
              { id: "multi", label: "3 bản", icon: "📚" },
              { id: "paragraph", label: "Theo đoạn", icon: "📋" },
            ] as const).map(m => (
              <button key={m.id} type="button"
                className={`spin-level-btn ${spinMode === m.id ? "active" : ""}`}
                onClick={() => setSpinMode(m.id)}
                style={{ "--level-color": "#8b5cf6" } as any}>
                <span className="spin-level-name">{m.icon} {m.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Level selector */}
        <div className="spin-level-row">
          <span className="spin-level-label">Mức độ:</span>
          <div className="spin-level-btns">
            {(["light", "medium", "heavy"] as const).map(l => (
              <button key={l} type="button"
                className={`spin-level-btn ${level === l ? "active" : ""}`}
                onClick={() => setLevel(l)}
                style={{ "--level-color": levelLabels[l].color } as any}>
                <span className="spin-level-name">{levelLabels[l].label}</span>
                <span className="spin-level-desc">{levelLabels[l].desc}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tone selector */}
        <div className="spin-level-row">
          <span className="spin-level-label">Giọng văn:</span>
          <div className="spin-level-btns">
            {Object.entries(toneLabels).map(([id, t]) => (
              <button key={id} type="button"
                className={`spin-level-btn ${tone === id ? "active" : ""}`}
                onClick={() => setTone(id)}
                style={{ "--level-color": "#22d3ee" } as any}>
                <span className="spin-level-name">{t.icon} {t.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Keywords */}
        <div className="input-group" style={{ marginBottom: 12 }}>
          <label className="input-label">Giữ nguyên từ khóa SEO (dấu phẩy)</label>
          <div className="input-wrap">
            <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
            </svg>
            <input type="text" className="text-input"
              placeholder="mitsubishi bình phước, xpander, triton..."
              value={keywords} onChange={e => setKeywords(e.target.value)} />
          </div>
        </div>

        {/* Textarea */}
        <div className="spin-textarea-wrap">
          <textarea className="spin-textarea"
            placeholder={"Dán nội dung cần viết lại vào đây...\n\nVí dụ: Mitsubishi Xpander là dòng xe MPV 7 chỗ bán chạy nhất Việt Nam..."}
            value={content} onChange={e => setContent(e.target.value)} rows={8} />
          <span className="spin-word-count">{content.split(/\s+/).filter(Boolean).length} từ</span>
        </div>

        <div className="spin-submit-row">
          <button className="spin-submit-btn" type="submit"
            disabled={loading || content.trim().length < 20}>
            {loading ? (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="spin-icon">
                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /><path d="M3 3v5h5" />
                </svg>
                Đang viết lại...
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                </svg>
                {spinMode === "multi" ? "Tạo 3 phiên bản" : spinMode === "paragraph" ? "Spin từng đoạn" : "Viết lại"}
              </>
            )}
          </button>
        </div>

        {error && (
          <p className="error-msg" role="alert">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
            </svg>
            {error}
          </p>
        )}
      </form>

      {/* Multi-version tabs */}
      {multiResult && multiResult.versions.length > 0 && (
        <div className="spin-version-tabs">
          {multiResult.versions.map((v, i) => (
            <button key={i}
              className={`spin-version-tab ${activeVersion === i ? "active" : ""}`}
              onClick={() => setActiveVersion(i)}>
              Bản {v.version || i + 1}
              <span className="spin-version-score" style={{ color: uniquenessColor(v.uniqueness_percent) }}>
                {v.uniqueness_percent}%
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Results */}
      {currentResult && (
        <div className="spin-result">
          <div className="spin-stats">
            <div className="spin-stat">
              <span className="spin-stat-label">Độ khác biệt</span>
              <span className="spin-stat-value" style={{ color: uniquenessColor(currentResult.uniqueness_percent) }}>
                {currentResult.uniqueness_percent}%
              </span>
            </div>
            <div className="spin-stat">
              <span className="spin-stat-label">Mức độ</span>
              <span className="spin-stat-value" style={{ color: levelLabels[currentResult.level]?.color }}>
                {levelLabels[currentResult.level]?.label}
              </span>
            </div>
            <div className="spin-stat">
              <span className="spin-stat-label">Giọng văn</span>
              <span className="spin-stat-value" style={{ fontSize: 14 }}>
                {toneLabels[currentResult.tone || "neutral"]?.icon} {toneLabels[currentResult.tone || "neutral"]?.label}
              </span>
            </div>
            <div className="spin-stat">
              <span className="spin-stat-label">Từ gốc</span>
              <span className="spin-stat-value">{currentResult.original_words}</span>
            </div>
            <div className="spin-stat">
              <span className="spin-stat-label">Từ mới</span>
              <span className="spin-stat-value">{currentResult.rewritten_words}</span>
            </div>
          </div>

          {/* View mode toggle */}
          <div className="spin-view-toggle">
            <button className={`spin-view-btn ${viewMode === "side" ? "active" : ""}`}
              onClick={() => setViewMode("side")}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" /><line x1="12" y1="3" x2="12" y2="21" />
              </svg>
              So sánh
            </button>
            {currentResult.diff && currentResult.diff.length > 0 && (
              <button className={`spin-view-btn ${viewMode === "diff" ? "active" : ""}`}
                onClick={() => setViewMode("diff")}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 5v14M5 12h14" />
                </svg>
                Diff
              </button>
            )}
          </div>

          {/* Content */}
          {viewMode === "side" ? (
            <div className="spin-panels">
              <div className="spin-panel spin-panel-old">
                <div className="spin-panel-header"><span>📄 Bản gốc</span></div>
                <div className="spin-panel-body">{currentResult.original}</div>
              </div>
              <div className="spin-panel spin-panel-new">
                <div className="spin-panel-header">
                  <span>✨ Bản mới</span>
                  <button className="spin-copy-btn" onClick={() => copyText(currentResult.rewritten)}>
                    {copied ? "✅ Đã copy" : "📋 Copy"}
                  </button>
                </div>
                <div className="spin-panel-body">{currentResult.rewritten}</div>
              </div>
            </div>
          ) : (
            <div className="spin-diff-view">
              <div className="spin-panel-header">
                <span>📝 So sánh thay đổi</span>
                <button className="spin-copy-btn" onClick={() => copyText(currentResult.rewritten)}>
                  {copied ? "✅ Đã copy" : "📋 Copy bản mới"}
                </button>
              </div>
              <div className="spin-diff-body">
                {currentResult.diff.map((seg, i) => (
                  <span key={i} className={`spin-diff-${seg.type}`}>{seg.text} </span>
                ))}
              </div>
            </div>
          )}

          <div className="spin-actions">
            <button className="rt-btn rt-btn-sync" onClick={handleSpin}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /><path d="M3 3v5h5" />
              </svg>
              Spin lại
            </button>
            <button className="rt-btn rt-btn-add"
              onClick={() => { setContent(currentResult.rewritten); setResult(null); setMultiResult(null); }}>
              ↩ Dùng bản mới làm gốc
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
