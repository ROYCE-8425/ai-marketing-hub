import { useState, useEffect } from "react";
import { API_BASE } from "../lib/apiConfig";

interface AbTest {
  id: number;
  name: string;
  test_type: string;
  url: string;
  keyword: string;
  variant_a: string;
  variant_b: string;
  winner: string;
  score_a: number;
  score_b: number;
  ai_analysis: string;
  status: string;
  created_at: string;
}

interface EvalResult {
  winner: string;
  score_a: number;
  score_b: number;
  analysis: string;
  criteria: Record<string, { a: number; b: number; note: string }>;
}

const TYPE_LABELS: Record<string, { label: string; icon: string }> = {
  title: { label: "Title Tag", icon: "🏷️" },
  description: { label: "Meta Description", icon: "📝" },
  heading: { label: "Heading", icon: "📑" },
  content: { label: "Nội dung", icon: "📄" },
};

export function AbTesting() {
  const [tests, setTests] = useState<AbTest[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "", test_type: "title", variant_a: "", variant_b: "", url: "", keyword: "",
  });
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState<number | null>(null);
  const [evalResult, setEvalResult] = useState<EvalResult | null>(null);
  const [selectedTest, setSelectedTest] = useState<number | null>(null);

  const fetchTests = async () => {
    try {
      const r = await fetch(`${API_BASE}/ab-test/list`);
      const d = await r.json();
      setTests(d.tests || []);
    } catch { /* ignore */ }
  };

  useEffect(() => { fetchTests(); }, []);

  const handleCreate = async () => {
    if (!form.name.trim() || !form.variant_a.trim() || !form.variant_b.trim()) return;
    setLoading(true);
    await fetch(`${API_BASE}/ab-test/create`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setForm({ name: "", test_type: "title", variant_a: "", variant_b: "", url: "", keyword: "" });
    setShowForm(false);
    await fetchTests();
    setLoading(false);
  };

  const handleEvaluate = async (id: number) => {
    setEvaluating(id);
    setEvalResult(null);
    setSelectedTest(id);
    try {
      const r = await fetch(`${API_BASE}/ab-test/evaluate`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      const d = await r.json();
      if (d.error) { alert(d.error); }
      else { setEvalResult(d); await fetchTests(); }
    } catch { /* ignore */ }
    setEvaluating(null);
  };

  const handleDelete = async (id: number) => {
    await fetch(`${API_BASE}/ab-test/delete`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    if (selectedTest === id) { setSelectedTest(null); setEvalResult(null); }
    await fetchTests();
  };

  const winnerColor = (w: string) => w === "A" ? "#3b82f6" : "#22c55e";

  return (
    <div className="geo-optimizer">
      <div className="hint-box">🧪 <strong>SEO A/B Testing:</strong> So sánh 2 phiên bản title/description/content — AI đánh giá bản nào tốt hơn.</div>

      <div className="geo-actions" style={{ marginTop: 16 }}>
        <button className="rt-btn rt-btn-add" onClick={() => setShowForm(!showForm)}>➕ Tạo A/B Test</button>
      </div>

      {/* Create form */}
      {showForm && (
        <div className="rt-import-panel" style={{ marginTop: 12 }}>
          <div className="geo-schema-form">
            <div className="input-group">
              <label className="input-label">Tên test *</label>
              <input className="text-input" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="VD: Test title trang chủ" style={{ paddingLeft: 12 }} />
            </div>
            <div className="input-group">
              <label className="input-label">Loại test</label>
              <select className="text-input" value={form.test_type} onChange={e => setForm({ ...form, test_type: e.target.value })} style={{ paddingLeft: 12 }}>
                {Object.entries(TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v.icon} {v.label}</option>)}
              </select>
            </div>
            <div className="input-group">
              <label className="input-label">URL trang</label>
              <input className="text-input" value={form.url} onChange={e => setForm({ ...form, url: e.target.value })} placeholder="https://..." style={{ paddingLeft: 12 }} />
            </div>
            <div className="input-group">
              <label className="input-label">Từ khóa mục tiêu</label>
              <input className="text-input" value={form.keyword} onChange={e => setForm({ ...form, keyword: e.target.value })} placeholder="mitsubishi bình phước" style={{ paddingLeft: 12 }} />
            </div>
            <div className="input-group" style={{ gridColumn: "1 / -1" }}>
              <label className="input-label" style={{ color: "#3b82f6" }}>🅰️ Phiên bản A *</label>
              <textarea className="spin-textarea" rows={3} value={form.variant_a} onChange={e => setForm({ ...form, variant_a: e.target.value })}
                placeholder="Nhập phiên bản A..." />
            </div>
            <div className="input-group" style={{ gridColumn: "1 / -1" }}>
              <label className="input-label" style={{ color: "#22c55e" }}>🅱️ Phiên bản B *</label>
              <textarea className="spin-textarea" rows={3} value={form.variant_b} onChange={e => setForm({ ...form, variant_b: e.target.value })}
                placeholder="Nhập phiên bản B..." />
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <button className="rt-btn rt-btn-add" onClick={handleCreate} disabled={loading || !form.name.trim() || !form.variant_a.trim() || !form.variant_b.trim()}>
              🧪 Tạo Test
            </button>
            <button className="rt-btn" onClick={() => setShowForm(false)} style={{ background: "var(--surface2)", color: "var(--text)" }}>Hủy</button>
          </div>
        </div>
      )}

      {/* Tests list */}
      {tests.length > 0 && (
        <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 10 }}>
          {tests.map(test => {
            const meta = TYPE_LABELS[test.test_type] || TYPE_LABELS.title;
            const isEvaluated = test.status === "evaluated";
            return (
              <div key={test.id} className="geo-faq-item" style={{ borderLeftColor: isEvaluated ? winnerColor(test.winner) : "var(--border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ fontWeight: 700, color: "var(--text-h)", display: "flex", alignItems: "center", gap: 8 }}>
                      {meta.icon} {test.name}
                      <span style={{ fontSize: 10, background: "var(--surface2)", padding: "2px 8px", borderRadius: 4, color: "var(--text-dim)" }}>{meta.label}</span>
                      {isEvaluated && (
                        <span style={{ fontSize: 11, background: winnerColor(test.winner), color: "#fff", padding: "2px 8px", borderRadius: 4, fontWeight: 700 }}>
                          Winner: {test.winner}
                        </span>
                      )}
                    </div>
                    {test.keyword && <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 2 }}>🔑 {test.keyword}</div>}
                  </div>
                  {isEvaluated && (
                    <div style={{ display: "flex", gap: 12, textAlign: "center" }}>
                      <div>
                        <div style={{ fontSize: 20, fontWeight: 800, color: test.winner === "A" ? "#3b82f6" : "var(--text-dim)" }}>{test.score_a}</div>
                        <div style={{ fontSize: 10, color: "var(--text-dim)" }}>🅰️</div>
                      </div>
                      <div style={{ color: "var(--text-dim)", alignSelf: "center" }}>vs</div>
                      <div>
                        <div style={{ fontSize: 20, fontWeight: 800, color: test.winner === "B" ? "#22c55e" : "var(--text-dim)" }}>{test.score_b}</div>
                        <div style={{ fontSize: 10, color: "var(--text-dim)" }}>🅱️</div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Variants preview */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 10 }}>
                  <div style={{ padding: "8px 12px", background: "rgba(59,130,246,0.06)", borderRadius: 6, fontSize: 12, border: "1px solid rgba(59,130,246,0.15)" }}>
                    <span style={{ fontWeight: 700, color: "#3b82f6", fontSize: 10 }}>🅰️ Phiên bản A</span>
                    <p style={{ margin: "4px 0 0", color: "var(--text)" }}>{test.variant_a.slice(0, 150)}{test.variant_a.length > 150 ? "..." : ""}</p>
                  </div>
                  <div style={{ padding: "8px 12px", background: "rgba(34,197,94,0.06)", borderRadius: 6, fontSize: 12, border: "1px solid rgba(34,197,94,0.15)" }}>
                    <span style={{ fontWeight: 700, color: "#22c55e", fontSize: 10 }}>🅱️ Phiên bản B</span>
                    <p style={{ margin: "4px 0 0", color: "var(--text)" }}>{test.variant_b.slice(0, 150)}{test.variant_b.length > 150 ? "..." : ""}</p>
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
                  {!isEvaluated && (
                    <button className="rt-btn rt-btn-sync" onClick={() => handleEvaluate(test.id)} disabled={evaluating === test.id}>
                      {evaluating === test.id ? "⏳ AI đang đánh giá..." : "🤖 AI Đánh giá"}
                    </button>
                  )}
                  {isEvaluated && (
                    <button className="rt-btn" style={{ fontSize: 11, background: "rgba(139,92,246,0.12)", color: "#8b5cf6", border: "1px solid rgba(139,92,246,0.2)" }}
                      onClick={() => { setSelectedTest(test.id); try { setEvalResult(JSON.parse(test.ai_analysis)); } catch { /* */ } }}>
                      📊 Xem chi tiết
                    </button>
                  )}
                  <button className="rt-del-btn" onClick={() => handleDelete(test.id)} title="Xóa" style={{ marginLeft: "auto" }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12" /></svg>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Eval result detail */}
      {evalResult && selectedTest && (
        <div className="geo-recs" style={{ marginTop: 16 }}>
          <h3 className="section-title">🏆 Kết quả AI — Winner: <span style={{ color: winnerColor(evalResult.winner) }}>{evalResult.winner}</span></h3>
          <p style={{ color: "var(--text)", lineHeight: 1.7, fontSize: 13, marginTop: 8 }}>{evalResult.analysis}</p>
          {evalResult.criteria && (
            <div className="geo-bars" style={{ marginTop: 14 }}>
              {Object.entries(evalResult.criteria).map(([key, val]) => (
                <div key={key} className="geo-bar-item">
                  <div className="geo-bar-label">
                    <span style={{ textTransform: "uppercase", fontSize: 11 }}>{key}</span>
                    <span style={{ fontSize: 12 }}>
                      <span style={{ color: "#3b82f6", fontWeight: 700 }}>A:{val.a}</span>
                      {" vs "}
                      <span style={{ color: "#22c55e", fontWeight: 700 }}>B:{val.b}</span>
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: 4, height: 6 }}>
                    <div style={{ flex: val.a, background: "#3b82f6", borderRadius: 3 }} />
                    <div style={{ flex: val.b, background: "#22c55e", borderRadius: 3 }} />
                  </div>
                  {val.note && <p style={{ fontSize: 11, color: "var(--text-dim)", margin: "4px 0 0" }}>{val.note}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tests.length === 0 && !showForm && (
        <div className="rt-empty" style={{ marginTop: 20 }}>
          <p>Chưa có A/B test nào. Nhấn <strong>➕ Tạo A/B Test</strong> để bắt đầu.</p>
        </div>
      )}
    </div>
  );
}
