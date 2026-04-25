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
  preserved_keywords: string[];
  error?: string;
}

export function SpinEditor() {
  const [content, setContent] = useState("");
  const [level, setLevel] = useState<"light" | "medium" | "heavy">("medium");
  const [keywords, setKeywords] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SpinResult | null>(null);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState<"side" | "diff">("side");
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
    try {
      const preserveKws = keywords.split(",").map(k => k.trim()).filter(Boolean);
      const r = await fetch(`${API_BASE}/content/spin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: content.trim(), level, preserve_keywords: preserveKws.length > 0 ? preserveKws : null }),
      });
      const d = await r.json();
      if (d.error) { setError(d.error); }
      else { setResult(d); }
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
    light: { label: "Nhẹ", desc: "~30% thay đổi", color: "#3b82f6" },
    medium: { label: "Vừa", desc: "~60% thay đổi", color: "#f59e0b" },
    heavy: { label: "Mạnh", desc: "~90% thay đổi", color: "#ef4444" },
  };

  return (
    <div className="spin-editor">
      {/* Input form */}
      <form className="spin-form" onSubmit={handleSpin}>
        <div className="hint-box">
          ✍️ <strong>Spin Editor:</strong> Viết lại nội dung bằng AI —
          giữ nguyên ý nghĩa nhưng thay đổi câu chữ để tránh trùng lặp.
          Giữ nguyên từ khóa SEO quan trọng.
        </div>

        {/* Level selector */}
        <div className="spin-level-row">
          <span className="spin-level-label">Mức độ viết lại:</span>
          <div className="spin-level-btns">
            {(["light", "medium", "heavy"] as const).map(l => (
              <button
                key={l}
                type="button"
                className={`spin-level-btn ${level === l ? "active" : ""}`}
                onClick={() => setLevel(l)}
                style={{ "--level-color": levelLabels[l].color } as any}
              >
                <span className="spin-level-name">{levelLabels[l].label}</span>
                <span className="spin-level-desc">{levelLabels[l].desc}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Keywords to preserve */}
        <div className="input-group" style={{ marginBottom: 12 }}>
          <label className="input-label">Giữ nguyên từ khóa SEO (phân cách bằng dấu phẩy)</label>
          <div className="input-wrap">
            <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
            </svg>
            <input
              type="text"
              className="text-input"
              placeholder="mitsubishi bình phước, xpander, triton..."
              value={keywords}
              onChange={e => setKeywords(e.target.value)}
            />
          </div>
        </div>

        {/* Content textarea */}
        <div className="spin-textarea-wrap">
          <textarea
            className="spin-textarea"
            placeholder="Dán nội dung cần viết lại vào đây...&#10;&#10;Ví dụ: Mitsubishi Xpander là dòng xe MPV 7 chỗ bán chạy nhất Việt Nam..."
            value={content}
            onChange={e => setContent(e.target.value)}
            rows={8}
          />
          <span className="spin-word-count">{content.split(/\s+/).filter(Boolean).length} từ</span>
        </div>

        <div className="spin-submit-row">
          <button className="spin-submit-btn" type="submit" disabled={loading || content.trim().length < 20}>
            {loading ? (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="spin-icon">
                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                  <path d="M3 3v5h5" />
                </svg>
                Đang viết lại...
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                </svg>
                Viết lại nội dung
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

      {/* Results */}
      {result && (
        <div className="spin-result">
          {/* Stats bar */}
          <div className="spin-stats">
            <div className="spin-stat">
              <span className="spin-stat-label">Độ khác biệt</span>
              <span className="spin-stat-value" style={{ color: uniquenessColor(result.uniqueness_percent) }}>
                {result.uniqueness_percent}%
              </span>
            </div>
            <div className="spin-stat">
              <span className="spin-stat-label">Mức độ</span>
              <span className="spin-stat-value" style={{ color: levelLabels[result.level]?.color }}>
                {levelLabels[result.level]?.label}
              </span>
            </div>
            <div className="spin-stat">
              <span className="spin-stat-label">Từ gốc</span>
              <span className="spin-stat-value">{result.original_words}</span>
            </div>
            <div className="spin-stat">
              <span className="spin-stat-label">Từ mới</span>
              <span className="spin-stat-value">{result.rewritten_words}</span>
            </div>
            {result.preserved_keywords.length > 0 && (
              <div className="spin-stat">
                <span className="spin-stat-label">Giữ keyword</span>
                <span className="spin-stat-value">{result.preserved_keywords.length}</span>
              </div>
            )}
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
            <button className={`spin-view-btn ${viewMode === "diff" ? "active" : ""}`}
              onClick={() => setViewMode("diff")}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 5v14M5 12h14" />
              </svg>
              Diff
            </button>
          </div>

          {/* Content panels */}
          {viewMode === "side" ? (
            <div className="spin-panels">
              <div className="spin-panel spin-panel-old">
                <div className="spin-panel-header">
                  <span>📄 Bản gốc</span>
                </div>
                <div className="spin-panel-body">{result.original}</div>
              </div>
              <div className="spin-panel spin-panel-new">
                <div className="spin-panel-header">
                  <span>✨ Bản mới</span>
                  <button className="spin-copy-btn" onClick={() => copyText(result.rewritten)}>
                    {copied ? "✅ Đã copy" : "📋 Copy"}
                  </button>
                </div>
                <div className="spin-panel-body">{result.rewritten}</div>
              </div>
            </div>
          ) : (
            <div className="spin-diff-view">
              <div className="spin-panel-header">
                <span>📝 So sánh thay đổi</span>
                <button className="spin-copy-btn" onClick={() => copyText(result.rewritten)}>
                  {copied ? "✅ Đã copy" : "📋 Copy bản mới"}
                </button>
              </div>
              <div className="spin-diff-body">
                {result.diff.map((seg, i) => (
                  <span key={i} className={`spin-diff-${seg.type}`}>
                    {seg.text}{" "}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="spin-actions">
            <button className="rt-btn rt-btn-sync" onClick={handleSpin}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              Spin lại
            </button>
            <button className="rt-btn rt-btn-add" onClick={() => { setContent(result.rewritten); setResult(null); }}>
              ↩ Dùng bản mới làm gốc
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
