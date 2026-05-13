/**
 * Centralized localization mapping for SEO Audit & CRO modules.
 *
 * Convention:
 *   - Card titles / Section titles: Vietnamese first, English in parentheses
 *     e.g. "Tối ưu từ khóa (Keyword Optimization)"
 *   - Pure UI labels (buttons, badges, stat labels): Vietnamese only
 *   - Core terminology (CTA, SEO, CRO, H1, Meta): keep English
 *
 * DO NOT scatter hardcoded Vietnamese text across components.
 * Import from this file instead.
 */

// ─── SEO Audit — category_scores keys → display labels ──────────────────────

export const SEO_CATEGORY_LABELS: Record<string, string> = {
  content: "Nội dung (Content)",
  keyword_optimization: "Tối ưu từ khóa (Keyword Optimization)",
  meta_elements: "Thành phần meta (Meta Elements)",
  structure: "Cấu trúc (Structure)",
  links: "Liên kết (Links)",
  readability: "Độ dễ đọc (Readability)",
};

// ─── CRO Checklist — category_scores keys → display labels ──────────────────

export const CRO_CATEGORY_LABELS: Record<string, string> = {
  headline: "Tiêu đề (Headline)",
  value_proposition: "Giá trị cốt lõi (Value Proposition)",
  social_proof: "Bằng chứng xã hội (Social Proof)",
  ctas: "Kêu gọi hành động (CTAs)",
  objection_handling: "Xử lý phản đối (Objection Handling)",
  risk_reversal: "Cam kết giảm rủi ro (Risk Reversal)",
  urgency: "Tính khẩn cấp (Urgency)",
  structure: "Cấu trúc trang (Page Structure)",
};

// ─── Above-the-Fold element labels ──────────────────────────────────────────

export const ATF_ELEMENT_LABELS: Record<string, string> = {
  headline: "Tiêu đề",
  value_prop: "Giá trị cốt lõi",
  cta: "CTA",
  trust: "Uy tín",
};

// ─── Generic label helper ───────────────────────────────────────────────────

/**
 * Resolve a category key to its localized label.
 * Falls back to capitalised key with underscores replaced by spaces.
 */
export function localizeCategory(
  key: string,
  map: Record<string, string>,
): string {
  if (map[key]) return map[key];
  // Fallback: capitalise first letter, replace underscores
  const fallback = key.replace(/_/g, " ");
  return fallback.charAt(0).toUpperCase() + fallback.slice(1);
}
