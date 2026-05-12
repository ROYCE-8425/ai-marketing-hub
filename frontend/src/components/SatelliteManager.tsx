import { useState, useEffect, useCallback } from "react";
import { API_BASE } from "../lib/apiConfig";
import "./SatelliteManager.css";

interface SatSite {
  id: string;
  name: string;
  url: string;
  platform: string;
  blog_id: string;
  total_posts: number;
  status: string;
  created_at: string;
}

interface SatPost {
  id: string;
  site_id: string;
  site_name: string;
  platform: string;
  title: string;
  post_url: string;
  backlink_url: string;
  backlink_keyword: string;
  status: string;
  error: string;
  posted_at: string;
  indexed: boolean;
}

interface SpinVersion {
  version: number;
  content_text: string;
  content_html: string;
  uniqueness_percent: number;
  word_count: number;
}

type TabId = "sites" | "spinpost" | "history";

export function SatelliteManager() {
  const [tab, setTab] = useState<TabId>("sites");
  const [sites, setSites] = useState<SatSite[]>([]);
  const [posts, setPosts] = useState<SatPost[]>([]);
  const [loading, setLoading] = useState(false);

  // Add site form
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSite, setNewSite] = useState({
    name: "", url: "", platform: "blogger", blog_id: "",
    wp_username: "", wp_app_password: "",
  });

  // Spin & Post form
  const [spinForm, setSpinForm] = useState({
    content: "", title: "", spin_level: "medium", spin_tone: "neutral",
    backlink_url: "https://binhphuocmitsubishi.com/",
    backlink_keyword: "mitsubishi bình phước",
    preserve_keywords: "",
  });
  const [selectedSites, setSelectedSites] = useState<string[]>([]);
  const [spinLoading, setSpinLoading] = useState(false);
  const [spinResults, setSpinResults] = useState<any>(null);

  // Preview
  const [previewVersions, setPreviewVersions] = useState<SpinVersion[]>([]);
  const [activePreview, setActivePreview] = useState(0);

  // ── Fetch Data ──────────────────────────────────────────────────────────

  const fetchSites = useCallback(async () => {
    try {
      const r = await fetch(`${API_BASE}/satellite/sites`);
      if (r.ok) {
        const d = await r.json();
        setSites(d.sites || []);
      }
    } catch { /* silent */ }
  }, []);

  const fetchPosts = useCallback(async () => {
    try {
      const r = await fetch(`${API_BASE}/satellite/posts?limit=50`);
      if (r.ok) {
        const d = await r.json();
        setPosts(d.posts || []);
      }
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    fetchSites();
    fetchPosts();
  }, [fetchSites, fetchPosts]);

  // ── Site CRUD ───────────────────────────────────────────────────────────

  const handleAddSite = async () => {
    if (!newSite.name || !newSite.url) return;
    setLoading(true);
    try {
      const r = await fetch(`${API_BASE}/satellite/sites`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSite),
      });
      if (r.ok) {
        setShowAddForm(false);
        setNewSite({ name: "", url: "", platform: "blogger", blog_id: "", wp_username: "", wp_app_password: "" });
        await fetchSites();
      }
    } catch { /* silent */ }
    setLoading(false);
  };

  const handleDeleteSite = async (id: string) => {
    if (!confirm("Xóa satellite site này?")) return;
    await fetch(`${API_BASE}/satellite/sites/${id}`, { method: "DELETE" });
    await fetchSites();
  };

  // ── Spin & Post ─────────────────────────────────────────────────────────

  const handleSpinAndPost = async () => {
    if (!spinForm.content.trim()) return;
    setSpinLoading(true);
    setSpinResults(null);
    try {
      const preserveArr = spinForm.preserve_keywords
        ? spinForm.preserve_keywords.split(",").map(k => k.trim()).filter(Boolean)
        : [];

      const r = await fetch(`${API_BASE}/satellite/spin-and-post`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: spinForm.content,
          title: spinForm.title,
          site_ids: selectedSites.length > 0 ? selectedSites : [],
          spin_level: spinForm.spin_level,
          spin_tone: spinForm.spin_tone,
          backlink_url: spinForm.backlink_url,
          backlink_keyword: spinForm.backlink_keyword,
          preserve_keywords: preserveArr.length > 0 ? preserveArr : null,
        }),
      });
      const d = await r.json();
      setSpinResults(d);
      if (!d.error) {
        await fetchPosts();
        await fetchSites();
      }
    } catch (e: any) {
      setSpinResults({ error: e.message });
    }
    setSpinLoading(false);
  };

  const handlePreviewSpin = async () => {
    if (!spinForm.content.trim()) return;
    setSpinLoading(true);
    setPreviewVersions([]);
    try {
      const r = await fetch(`${API_BASE.replace('/api', '/api')}/spin/multi`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: spinForm.content,
          level: spinForm.spin_level,
          tone: spinForm.spin_tone,
          num_versions: 3,
        }),
      });
      if (r.ok) {
        const d = await r.json();
        if (d.versions) {
          setPreviewVersions(d.versions.map((v: any, i: number) => ({
            version: i + 1,
            content_text: v.rewritten,
            content_html: "",
            uniqueness_percent: v.uniqueness_percent,
            word_count: v.rewritten_words,
          })));
          setActivePreview(0);
        }
      }
    } catch { /* silent */ }
    setSpinLoading(false);
  };

  // ── Stats ───────────────────────────────────────────────────────────────

  const totalPosts = posts.length;
  const publishedPosts = posts.filter(p => p.status === "published").length;
  const activeSites = sites.filter(s => s.status === "active").length;

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="satellite-manager">
      {/* Stats */}
      <div className="sat-stats">
        <div className="sat-stat">
          <div className="sat-stat-value">{activeSites}</div>
          <div className="sat-stat-label">Site vệ tinh</div>
        </div>
        <div className="sat-stat">
          <div className="sat-stat-value">{publishedPosts}</div>
          <div className="sat-stat-label">Bài đã đăng</div>
        </div>
        <div className="sat-stat">
          <div className="sat-stat-value">{totalPosts > 0 ? Math.round(publishedPosts / totalPosts * 100) : 0}%</div>
          <div className="sat-stat-label">Tỷ lệ thành công</div>
        </div>
        <div className="sat-stat">
          <div className="sat-stat-value">{posts.filter(p => p.indexed).length}</div>
          <div className="sat-stat-label">Đã index</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="sat-tabs">
        <button className={`sat-tab ${tab === "sites" ? "active" : ""}`} onClick={() => setTab("sites")}>
          🌐 Sites <span className="sat-badge">{sites.length}</span>
        </button>
        <button className={`sat-tab ${tab === "spinpost" ? "active" : ""}`} onClick={() => setTab("spinpost")}>
          🔄 Spin & Post
        </button>
        <button className={`sat-tab ${tab === "history" ? "active" : ""}`} onClick={() => setTab("history")}>
          📋 Lịch sử <span className="sat-badge">{posts.length}</span>
        </button>
      </div>

      {/* ── Tab: Sites ─────────────────────────────────────────────────── */}
      {tab === "sites" && (
        <div className="sat-card">
          <div className="sat-card-header">
            <div className="sat-card-title">🌐 Satellite Sites</div>
            <button className="sat-btn sat-btn-primary" onClick={() => setShowAddForm(!showAddForm)}>
              {showAddForm ? "✕ Đóng" : "➕ Thêm site"}
            </button>
          </div>

          {/* Add Form */}
          {showAddForm && (
            <div className="sat-add-form">
              <div className="sat-form-group">
                <label>Tên site</label>
                <input placeholder="Blog SEO 01" value={newSite.name}
                  onChange={e => setNewSite({ ...newSite, name: e.target.value })} />
              </div>
              <div className="sat-form-group">
                <label>URL</label>
                <input placeholder="https://blog01.blogspot.com" value={newSite.url}
                  onChange={e => setNewSite({ ...newSite, url: e.target.value })} />
              </div>
              <div className="sat-form-group">
                <label>Platform</label>
                <select value={newSite.platform}
                  onChange={e => setNewSite({ ...newSite, platform: e.target.value })}>
                  <option value="blogger">Blogger</option>
                  <option value="wordpress">WordPress</option>
                </select>
              </div>
              {newSite.platform === "blogger" && (
                <div className="sat-form-group">
                  <label>Blog ID</label>
                  <input placeholder="1234567890" value={newSite.blog_id}
                    onChange={e => setNewSite({ ...newSite, blog_id: e.target.value })} />
                </div>
              )}
              {newSite.platform === "wordpress" && (
                <>
                  <div className="sat-form-group">
                    <label>WP Username</label>
                    <input placeholder="admin" value={newSite.wp_username}
                      onChange={e => setNewSite({ ...newSite, wp_username: e.target.value })} />
                  </div>
                  <div className="sat-form-group">
                    <label>WP App Password</label>
                    <input type="password" placeholder="xxxx xxxx xxxx" value={newSite.wp_app_password}
                      onChange={e => setNewSite({ ...newSite, wp_app_password: e.target.value })} />
                  </div>
                </>
              )}
              <div className="sat-form-group full-width" style={{ display: "flex", gap: 8 }}>
                <button className="sat-btn sat-btn-primary" onClick={handleAddSite} disabled={loading}>
                  {loading ? "⏳ Đang thêm..." : "✅ Lưu site"}
                </button>
                <button className="sat-btn sat-btn-secondary" onClick={() => setShowAddForm(false)}>Hủy</button>
              </div>
            </div>
          )}

          {/* Sites Grid */}
          {sites.length === 0 ? (
            <div className="sat-empty">
              <div className="sat-empty-icon">🌐</div>
              <h3>Chưa có satellite site nào</h3>
              <p>Thêm blog Blogger hoặc WordPress để bắt đầu đăng bài tự động</p>
              <button className="sat-btn sat-btn-primary" onClick={() => setShowAddForm(true)}>
                ➕ Thêm site đầu tiên
              </button>
            </div>
          ) : (
            <div className="sat-site-grid">
              {sites.map(site => (
                <div key={site.id} className="sat-site-item">
                  <div className="sat-site-name">
                    <span className={`sat-platform-badge ${site.platform}`}>
                      {site.platform === "blogger" ? "🅱️ Blogger" : "🔵 WordPress"}
                    </span>
                    {site.name}
                  </div>
                  <div className="sat-site-url">{site.url}</div>
                  <div className="sat-site-meta">
                    <span>📝 {site.total_posts} bài</span>
                    <span>📅 {new Date(site.created_at).toLocaleDateString("vi-VN")}</span>
                  </div>
                  <div className="sat-site-actions">
                    <button onClick={() => window.open(site.url, "_blank")}>🔗 Mở</button>
                    <button className="delete-btn" onClick={() => handleDeleteSite(site.id)}>🗑️ Xóa</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Tab: Spin & Post ───────────────────────────────────────────── */}
      {tab === "spinpost" && (
        <div className="sat-card">
          <div className="sat-card-title" style={{ marginBottom: 16 }}>🔄 Spin nội dung & Đăng lên Satellite</div>

          <div className="sat-spin-panel">
            {/* Content input */}
            <div className="sat-form-group">
              <label>📝 Tiêu đề bài viết</label>
              <input className="sat-textarea" style={{ minHeight: "auto" }}
                placeholder="Tiêu đề bài viết (tuỳ chọn)"
                value={spinForm.title}
                onChange={e => setSpinForm({ ...spinForm, title: e.target.value })} />
            </div>

            <div className="sat-form-group">
              <label>📄 Nội dung gốc (sẽ được spin thành nhiều bản unique)</label>
              <textarea className="sat-textarea"
                placeholder="Dán nội dung bài viết gốc vào đây... AI sẽ viết lại thành nhiều bản khác nhau, mỗi bản đăng lên 1 satellite site."
                value={spinForm.content}
                onChange={e => setSpinForm({ ...spinForm, content: e.target.value })} />
            </div>

            {/* Options */}
            <div className="sat-options-row">
              <div className="sat-form-group">
                <label>⚡ Mức spin</label>
                <select value={spinForm.spin_level}
                  onChange={e => setSpinForm({ ...spinForm, spin_level: e.target.value })}>
                  <option value="light">Nhẹ (30%)</option>
                  <option value="medium">Trung bình (60%)</option>
                  <option value="heavy">Nặng (90%)</option>
                </select>
              </div>
              <div className="sat-form-group">
                <label>🎤 Giọng văn</label>
                <select value={spinForm.spin_tone}
                  onChange={e => setSpinForm({ ...spinForm, spin_tone: e.target.value })}>
                  <option value="neutral">Trung lập</option>
                  <option value="professional">Chuyên nghiệp</option>
                  <option value="friendly">Thân thiện</option>
                  <option value="sales">Bán hàng</option>
                </select>
              </div>
              <div className="sat-form-group">
                <label>🔗 URL backlink</label>
                <input value={spinForm.backlink_url}
                  onChange={e => setSpinForm({ ...spinForm, backlink_url: e.target.value })} />
              </div>
              <div className="sat-form-group">
                <label>🎯 Keyword backlink</label>
                <input value={spinForm.backlink_keyword}
                  onChange={e => setSpinForm({ ...spinForm, backlink_keyword: e.target.value })} />
              </div>
            </div>

            <div className="sat-form-group">
              <label>🔑 Từ khóa SEO giữ nguyên (phân cách bằng dấu phẩy)</label>
              <input placeholder="mitsubishi, xpander, bình phước"
                value={spinForm.preserve_keywords}
                onChange={e => setSpinForm({ ...spinForm, preserve_keywords: e.target.value })} />
            </div>

            {/* Site selection */}
            {sites.length > 0 && (
              <div className="sat-form-group">
                <label>🌐 Chọn site đăng (bỏ trống = tất cả)</label>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 }}>
                  {sites.map(site => (
                    <label key={site.id} style={{
                      display: "flex", alignItems: "center", gap: 4,
                      padding: "4px 10px", borderRadius: 8,
                      background: selectedSites.includes(site.id) ? "rgba(139,92,246,0.15)" : "rgba(255,255,255,0.04)",
                      border: `1px solid ${selectedSites.includes(site.id) ? "rgba(139,92,246,0.3)" : "rgba(255,255,255,0.08)"}`,
                      cursor: "pointer", fontSize: 12, color: "rgba(255,255,255,0.7)",
                    }}>
                      <input type="checkbox" checked={selectedSites.includes(site.id)}
                        onChange={e => {
                          if (e.target.checked) setSelectedSites([...selectedSites, site.id]);
                          else setSelectedSites(selectedSites.filter(id => id !== site.id));
                        }}
                        style={{ display: "none" }} />
                      {selectedSites.includes(site.id) ? "☑️" : "⬜"} {site.name}
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Preview */}
            {previewVersions.length > 0 && (
              <div>
                <div className="sat-version-tabs">
                  {previewVersions.map((v, i) => (
                    <button key={i}
                      className={`sat-version-tab ${activePreview === i ? "active" : ""}`}
                      onClick={() => setActivePreview(i)}>
                      V{v.version} · {v.uniqueness_percent}% unique
                    </button>
                  ))}
                </div>
                <div className="sat-preview">
                  {previewVersions[activePreview]?.content_text.split("\n").map((p, i) => (
                    <p key={i}>{p}</p>
                  ))}
                </div>
                <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", marginTop: 4 }}>
                  {previewVersions[activePreview]?.word_count} từ
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div style={{ display: "flex", gap: 8 }}>
              <button className="sat-btn sat-btn-secondary"
                onClick={handlePreviewSpin}
                disabled={spinLoading || !spinForm.content.trim()}>
                {spinLoading ? <><span className="sat-spinning">⏳</span> Đang spin...</> : "👁️ Xem trước spin"}
              </button>
              <button className="sat-btn sat-btn-primary"
                onClick={handleSpinAndPost}
                disabled={spinLoading || !spinForm.content.trim() || sites.length === 0}>
                {spinLoading ? <><span className="sat-spinning">🔄</span> Đang xử lý...</> : "🚀 Spin & Đăng ngay"}
              </button>
            </div>

            {sites.length === 0 && (
              <div style={{ color: "#f59e0b", fontSize: 13, padding: "8px 12px", background: "rgba(245,158,11,0.06)", borderRadius: 8, border: "1px solid rgba(245,158,11,0.15)" }}>
                ⚠️ Chưa có satellite site nào. Vui lòng thêm site ở tab "Sites" trước.
              </div>
            )}

            {/* Results */}
            {spinResults && (
              <div className="sat-results">
                {spinResults.error ? (
                  <div style={{ color: "#f87171", fontSize: 13 }}>❌ {spinResults.error}</div>
                ) : (
                  <>
                    <div style={{ fontSize: 13, color: "#4ade80", fontWeight: 600 }}>
                      ✅ Đã đăng: {spinResults.success}/{spinResults.total_sites} site
                    </div>
                    {spinResults.results?.map((r: any, i: number) => (
                      <div key={i} className={`sat-result-item ${r.success ? "success" : "failed"}`}>
                        <div className="sat-result-status">{r.success ? "✅" : "❌"}</div>
                        <div className="sat-result-info">
                          <h4>{r.site}</h4>
                          {r.success ? (
                            <p>Uniqueness: {r.uniqueness}% · <a href={r.post_url} target="_blank" rel="noopener" className="sat-result-link">Xem bài →</a></p>
                          ) : (
                            <p style={{ color: "#f87171" }}>{r.error}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Tab: History ───────────────────────────────────────────────── */}
      {tab === "history" && (
        <div className="sat-card">
          <div className="sat-card-header">
            <div className="sat-card-title">📋 Lịch sử bài đăng</div>
            <button className="sat-btn sat-btn-secondary" onClick={fetchPosts}>🔄 Refresh</button>
          </div>

          {posts.length === 0 ? (
            <div className="sat-empty">
              <div className="sat-empty-icon">📋</div>
              <h3>Chưa có bài nào được đăng</h3>
              <p>Spin & đăng bài đầu tiên ở tab "Spin & Post"</p>
            </div>
          ) : (
            <div className="sat-post-list">
              {posts.map(post => (
                <div key={post.id} className="sat-post-item">
                  <div className="sat-post-icon">
                    {post.status === "published" ? "✅" : "❌"}
                  </div>
                  <div className="sat-post-info">
                    <div className="sat-post-title">{post.title || "Untitled"}</div>
                    <div className="sat-post-meta">
                      <span>📍 {post.site_name}</span>
                      <span>📅 {new Date(post.posted_at).toLocaleString("vi-VN")}</span>
                      {post.backlink_keyword && <span>🔗 {post.backlink_keyword}</span>}
                    </div>
                  </div>
                  <span className={`sat-post-status ${post.status}`}>
                    {post.status === "published" ? "Đã đăng" : "Lỗi"}
                  </span>
                  {post.post_url && (
                    <a href={post.post_url} target="_blank" rel="noopener" className="sat-result-link">
                      Xem →
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
