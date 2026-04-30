import { useState, useRef, useCallback } from "react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const FORMAT_ICONS: Record<string, string> = {
  ".pdf": "📄", ".docx": "📝", ".doc": "📝", ".pptx": "📊",
  ".xlsx": "📈", ".xls": "📈", ".csv": "📋", ".html": "🌐",
  ".htm": "🌐", ".json": "🔧", ".xml": "📦", ".txt": "📃",
  ".md": "📑", ".epub": "📚", ".zip": "🗜️", ".jpg": "🖼️",
  ".jpeg": "🖼️", ".png": "🖼️", ".mp3": "🎵", ".wav": "🎵",
};

interface ConvertResult {
  markdown: string;
  filename?: string;
  url?: string;
  word_count: number;
  char_count: number;
  extension?: string;
  success: boolean;
  error?: string;
}

export default function FileConverter() {
  const [mode, setMode] = useState<"file" | "url">("file");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<ConvertResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [copied, setCopied] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) setSelectedFile(file);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setSelectedFile(file);
  };

  const convertFile = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      const resp = await fetch(`${API_BASE}/api/convert/file`, {
        method: "POST",
        body: formData,
      });
      if (!resp.ok) throw new Error(`Server error: ${resp.status}`);
      const data: ConvertResult = await resp.json();
      if (!data.success) throw new Error(data.error || "Conversion failed");
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Lỗi chuyển đổi file");
    } finally {
      setLoading(false);
    }
  };

  const convertUrl = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const resp = await fetch(`${API_BASE}/api/convert/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      if (!resp.ok) throw new Error(`Server error: ${resp.status}`);
      const data: ConvertResult = await resp.json();
      if (!data.success) throw new Error(data.error || "Conversion failed");
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Lỗi chuyển đổi URL");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!result?.markdown) return;
    navigator.clipboard.writeText(result.markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadMarkdown = () => {
    if (!result?.markdown) return;
    const name = result.filename
      ? result.filename.replace(/\.[^.]+$/, ".md")
      : "converted.md";
    const blob = new Blob([result.markdown], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="audit-form" style={{ maxWidth: 900 }}>
      <h2 style={{ marginBottom: 6, display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ fontSize: 28 }}>📎</span> File Converter
        <span style={{
          fontSize: 11, background: "linear-gradient(135deg, #8b5cf6, #06b6d4)",
          padding: "3px 10px", borderRadius: 12, fontWeight: 600, marginLeft: 8
        }}>MarkItDown</span>
      </h2>
      <p style={{ color: "var(--text-m)", fontSize: 13, marginBottom: 20 }}>
        Chuyển đổi PDF, Word, Excel, PowerPoint, HTML, ảnh → Markdown để phân tích SEO
      </p>

      {/* Mode Toggle */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        <button
          className={`submit-btn ${mode === "file" ? "" : "secondary"}`}
          onClick={() => { setMode("file"); setResult(null); setError(""); }}
          style={mode !== "file" ? {
            background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)"
          } : {}}
        >📁 Upload File</button>
        <button
          className={`submit-btn ${mode === "url" ? "" : "secondary"}`}
          onClick={() => { setMode("url"); setResult(null); setError(""); }}
          style={mode !== "url" ? {
            background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)"
          } : {}}
        >🌐 Từ URL</button>
      </div>

      {/* File Upload Mode */}
      {mode === "file" && (
        <>
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleFileDrop}
            onClick={() => fileRef.current?.click()}
            style={{
              border: `2px dashed ${dragOver ? "#8b5cf6" : "rgba(255,255,255,0.15)"}`,
              borderRadius: 16,
              padding: selectedFile ? "24px" : "48px 24px",
              textAlign: "center",
              cursor: "pointer",
              transition: "all 0.3s ease",
              background: dragOver
                ? "rgba(139,92,246,0.08)"
                : "rgba(255,255,255,0.02)",
              marginBottom: 16,
            }}
          >
            <input
              ref={fileRef}
              type="file"
              onChange={handleFileSelect}
              style={{ display: "none" }}
              accept=".pdf,.docx,.doc,.pptx,.xlsx,.xls,.csv,.html,.htm,.json,.xml,.txt,.md,.epub,.zip,.jpg,.jpeg,.png,.mp3,.wav"
            />
            {selectedFile ? (
              <div style={{ display: "flex", alignItems: "center", gap: 14, justifyContent: "center" }}>
                <span style={{ fontSize: 36 }}>
                  {FORMAT_ICONS[`.${selectedFile.name.split(".").pop()?.toLowerCase()}`] || "📄"}
                </span>
                <div style={{ textAlign: "left" }}>
                  <div style={{ fontWeight: 600, color: "var(--text-h)", fontSize: 15 }}>
                    {selectedFile.name}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-m)" }}>
                    {formatSize(selectedFile.size)} • Nhấn để đổi file
                  </div>
                </div>
              </div>
            ) : (
              <>
                <div style={{ fontSize: 48, marginBottom: 12 }}>
                  {dragOver ? "📥" : "📂"}
                </div>
                <div style={{ color: "var(--text-h)", fontWeight: 600, fontSize: 15, marginBottom: 6 }}>
                  Kéo thả file vào đây
                </div>
                <div style={{ color: "var(--text-m)", fontSize: 13 }}>
                  hoặc nhấn để chọn file • PDF, Word, Excel, PPT, HTML, ảnh...
                </div>
              </>
            )}
          </div>

          <button
            className="submit-btn"
            onClick={convertFile}
            disabled={!selectedFile || loading}
            style={{ width: "100%", opacity: !selectedFile ? 0.5 : 1 }}
          >
            {loading ? "⏳ Đang chuyển đổi..." : "🔄 Chuyển đổi sang Markdown"}
          </button>
        </>
      )}

      {/* URL Mode */}
      {mode === "url" && (
        <>
          <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/article"
              style={{
                flex: 1, padding: "12px 16px", borderRadius: 10,
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.1)",
                color: "var(--text-h)", fontSize: 14, outline: "none",
              }}
              onKeyDown={(e) => e.key === "Enter" && convertUrl()}
            />
          </div>
          <button
            className="submit-btn"
            onClick={convertUrl}
            disabled={!url.trim() || loading}
            style={{ width: "100%", opacity: !url.trim() ? 0.5 : 1 }}
          >
            {loading ? "⏳ Đang chuyển đổi..." : "🌐 Chuyển đổi URL sang Markdown"}
          </button>
        </>
      )}

      {/* Error */}
      {error && (
        <div style={{
          marginTop: 16, padding: "12px 16px", borderRadius: 10,
          background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
          color: "#f87171", fontSize: 13
        }}>
          ❌ {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="result-panel" style={{ marginTop: 20 }}>
          {/* Stats Bar */}
          <div style={{
            display: "flex", gap: 16, marginBottom: 16, flexWrap: "wrap"
          }}>
            <div style={{
              padding: "10px 16px", borderRadius: 10,
              background: "rgba(139,92,246,0.1)", border: "1px solid rgba(139,92,246,0.2)",
              fontSize: 13
            }}>
              📊 <strong>{result.word_count.toLocaleString()}</strong> từ
            </div>
            <div style={{
              padding: "10px 16px", borderRadius: 10,
              background: "rgba(6,182,212,0.1)", border: "1px solid rgba(6,182,212,0.2)",
              fontSize: 13
            }}>
              📝 <strong>{result.char_count.toLocaleString()}</strong> ký tự
            </div>
            {result.filename && (
              <div style={{
                padding: "10px 16px", borderRadius: 10,
                background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)",
                fontSize: 13
              }}>
                📎 {result.filename}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
            <button className="submit-btn" onClick={copyToClipboard} style={{ fontSize: 13, padding: "8px 16px" }}>
              {copied ? "✅ Đã copy!" : "📋 Copy Markdown"}
            </button>
            <button className="submit-btn" onClick={downloadMarkdown}
              style={{ fontSize: 13, padding: "8px 16px", background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)" }}
            >
              💾 Download .md
            </button>
          </div>

          {/* Markdown Preview */}
          <div style={{ position: "relative" }}>
            <div style={{
              fontSize: 11, color: "var(--text-m)", marginBottom: 6,
              textTransform: "uppercase", letterSpacing: 1
            }}>
              Markdown Output
            </div>
            <pre style={{
              background: "rgba(0,0,0,0.3)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 10, padding: 16,
              maxHeight: 500, overflow: "auto",
              fontSize: 12.5, lineHeight: 1.6,
              color: "var(--text-h)", whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}>
              {result.markdown || "(Không có nội dung)"}
            </pre>
          </div>
        </div>
      )}

      {/* Supported Formats */}
      <details style={{ marginTop: 24 }}>
        <summary style={{
          cursor: "pointer", color: "var(--text-m)", fontSize: 13,
          padding: "8px 0", userSelect: "none"
        }}>
          📋 Xem 20 định dạng được hỗ trợ
        </summary>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
          gap: 8, marginTop: 12, padding: 16,
          background: "rgba(255,255,255,0.02)", borderRadius: 12,
          border: "1px solid rgba(255,255,255,0.06)"
        }}>
          {Object.entries(FORMAT_ICONS).map(([ext, icon]) => (
            <div key={ext} style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "6px 10px", borderRadius: 8,
              background: "rgba(255,255,255,0.03)", fontSize: 13
            }}>
              <span>{icon}</span>
              <span style={{ color: "var(--text-h)", fontWeight: 500 }}>{ext}</span>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}
