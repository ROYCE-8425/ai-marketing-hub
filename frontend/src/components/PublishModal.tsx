import { useState } from "react";
import type { PublishResponse } from "../types/phase5";
import { API_BASE } from "../lib/apiConfig";
import "./PublishModal.css";

interface Props {
  articleTitle: string;
  articleContent: string;
  onClose: () => void;
}

export function PublishModal({ articleTitle, articleContent, onClose }: Props) {
  const placeholderPattern = /\[Write section \d+ here\]/i;
  const isPlaceholderContent = placeholderPattern.test(articleContent);

  const [form, setForm] = useState({
    wordpress_url: "",
    username: "",
    app_password: "",
    slug: "",
    excerpt: "",
    category: "",
    tags: "",
    // Force draft when publishing placeholder outline
    post_status: isPlaceholderContent ? "draft" : "draft",
  });
  const [result, setResult] = useState<PublishResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const set = (key: keyof typeof form) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setForm((prev) => ({ ...prev, [key]: e.target.value }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.wordpress_url || !form.username || !form.app_password) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/publish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          wordpress_url: form.wordpress_url,
          username: form.username,
          app_password: form.app_password,
          article_title: articleTitle,
          article_content: articleContent,
          slug: form.slug || undefined,
          excerpt: form.excerpt || undefined,
          category: form.category || undefined,
          tags: form.tags || undefined,
          post_status: form.post_status,
        }),
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.detail ?? `HTTP ${res.status}`);
      }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-label="Publish to WordPress">
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>

        {/* Header */}
        <div className="modal-header">
          <div className="modal-title-row">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" strokeWidth="2" aria-hidden="true">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
            </svg>
            <h2 className="modal-title">Publish to WordPress</h2>
          </div>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Article preview */}
        <div className="article-preview">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span className="ap-label">Article to publish</span>
            {isPlaceholderContent && (
              <span style={{
                fontSize: "10px",
                background: "rgba(245,158,11,0.15)",
                color: "#f59e0b",
                border: "1px solid rgba(245,158,11,0.3)",
                padding: "2px 7px",
                borderRadius: "99px",
                fontWeight: 600,
                letterSpacing: "0.05em",
              }}>
                DRAFT OUTLINE
              </span>
            )}
          </div>
          <span className="ap-title">{articleTitle}</span>
          <span className="ap-meta">
            {articleContent.split(/\s+/).length.toLocaleString()} words ·{" "}
            {articleContent.length.toLocaleString()} chars
            {isPlaceholderContent && " · Contains placeholder sections"}
          </span>
        </div>

        {result ? (
          /* ── Success state ── */
          <div className="publish-success">
            <div className="success-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <h3 className="success-title">{result.message}</h3>
            <div className="success-details">
              <div className="sd-row">
                <span className="sd-label">Post ID</span>
                <span className="sd-value mono">{result.post_id}</span>
              </div>
              <div className="sd-row">
                <span className="sd-label">Status</span>
                <span className="sd-value">{result.post_status}</span>
              </div>
              <div className="sd-row">
                <span className="sd-label">Slug</span>
                <span className="sd-value mono">/{result.slug}</span>
              </div>
              <div className="sd-row">
                <span className="sd-label">Words</span>
                <span className="sd-value">{result.word_count.toLocaleString()}</span>
              </div>
              {result.categories.length > 0 && (
                <div className="sd-row">
                  <span className="sd-label">Categories</span>
                  <span className="sd-value">{result.categories.join(", ")}</span>
                </div>
              )}
              {result.tags.length > 0 && (
                <div className="sd-row">
                  <span className="sd-label">Tags</span>
                  <span className="sd-value">{result.tags.join(", ")}</span>
                </div>
              )}
            </div>
            <div className="success-links">
              {result.edit_url && (
                <a href={result.edit_url} target="_blank" rel="noopener noreferrer" className="result-link edit">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                  </svg>
                  Edit in WordPress
                </a>
              )}
              {result.view_url && (
                <a href={result.view_url} target="_blank" rel="noopener noreferrer" className="result-link view">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
                  </svg>
                  View Live
                </a>
              )}
            </div>
            <button className="modal-close-btn" onClick={onClose}>Done</button>
          </div>
        ) : (
          /* ── Form state ── */
          <form className="publish-form" onSubmit={handleSubmit} noValidate>
            {/* WP Config */}
            <fieldset className="form-fieldset">
              <legend className="form-legend">WordPress Configuration</legend>
              <div className="form-group">
                <label htmlFor="wp-url" className="form-label">Site URL <span className="required">*</span></label>
                <input
                  id="wp-url"
                  type="url"
                  className="text-input"
                  placeholder="https://yoursite.com"
                  value={form.wordpress_url}
                  onChange={set("wordpress_url")}
                  required
                />
              </div>
              <div className="form-row-2">
                <div className="form-group">
                  <label htmlFor="wp-user" className="form-label">Username <span className="required">*</span></label>
                  <input
                    id="wp-user"
                    type="text"
                    className="text-input"
                    placeholder="admin"
                    value={form.username}
                    onChange={set("username")}
                    required
                    autoComplete="off"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="wp-pass" className="form-label">App Password <span className="required">*</span></label>
                  <input
                    id="wp-pass"
                    type="password"
                    className="text-input"
                    placeholder="xxxx xxxx xxxx xxxx"
                    value={form.app_password}
                    onChange={set("app_password")}
                    required
                    autoComplete="off"
                  />
                </div>
              </div>
            </fieldset>

            {/* Article options */}
            <fieldset className="form-fieldset">
              <legend className="form-legend">Article Options</legend>
              <div className="form-row-2">
                <div className="form-group">
                  <label htmlFor="pub-slug" className="form-label">URL Slug (optional)</label>
                  <input
                    id="pub-slug"
                    type="text"
                    className="text-input"
                    placeholder="auto-generated from title"
                    value={form.slug}
                    onChange={set("slug")}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="pub-status" className="form-label">Status</label>
                  <select
                    id="pub-status"
                    className="text-input"
                    value={isPlaceholderContent ? "draft" : form.post_status}
                    onChange={set("post_status")}
                    disabled={isPlaceholderContent}
                    title={isPlaceholderContent ? "Locked to Draft — article contains placeholder sections" : undefined}
                  >
                    <option value="draft">Draft</option>
                    {!isPlaceholderContent && <option value="publish">Publish Now</option>}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="pub-category" className="form-label">Category (optional)</label>
                <input
                  id="pub-category"
                  type="text"
                  className="text-input"
                  placeholder="Blog"
                  value={form.category}
                  onChange={set("category")}
                />
              </div>
              <div className="form-group">
                <label htmlFor="pub-tags" className="form-label">Tags (comma-separated, optional)</label>
                <input
                  id="pub-tags"
                  type="text"
                  className="text-input"
                  placeholder="podcast, hosting, guide"
                  value={form.tags}
                  onChange={set("tags")}
                />
              </div>
              <div className="form-group">
                <label htmlFor="pub-excerpt" className="form-label">Excerpt (optional)</label>
                <textarea
                  id="pub-excerpt"
                  className="text-input"
                  rows={3}
                  placeholder="Short description for the post..."
                  value={form.excerpt}
                  onChange={set("excerpt")}
                />
              </div>
            </fieldset>

            {isPlaceholderContent && (
              <div style={{
                background: "rgba(245,158,11,0.08)",
                border: "1px solid rgba(245,158,11,0.3)",
                borderRadius: "var(--radius-sm)",
                padding: "10px 14px",
                display: "flex",
                gap: "8px",
                alignItems: "flex-start",
                fontSize: "12.5px",
                color: "#f59e0b",
                lineHeight: 1.5,
              }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0, marginTop: "1px" }}>
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <span>
                  <strong>This article contains placeholder sections.</strong>{" "}
                  Publishing is locked to <strong>Draft</strong>.{" "}
                  No reader-ready content was generated — use the AI Writer tab to write real sections first.
                </span>
              </div>
            )}

            {error && (
              <p className="error-msg" role="alert">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                </svg>
                {error}
              </p>
            )}

            <div className="modal-actions">
              <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
              <button
                type="submit"
                className="publish-btn"
                disabled={
                  loading ||
                  !form.wordpress_url ||
                  !form.username ||
                  !form.app_password
                }
              >
                {loading ? (
                  <span className="btn-spinner" aria-label="Publishing…" />
                ) : (
                  <>
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M22 2L11 13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
                    </svg>
                    Publish Article
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
