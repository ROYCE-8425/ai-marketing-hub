/**
 * Analysis History — localStorage persistence
 *
 * Saves and retrieves analysis results so users can review past work.
 * Each entry stores: type, keyword/url, timestamp, score, and summary data.
 */

const STORAGE_KEY = "ai_marketing_hub_history";
const MAX_ENTRIES = 50;

export interface HistoryEntry {
  id: string;
  type: "seo" | "serp" | "competitor" | "content";
  keyword: string;
  url?: string;
  timestamp: string;
  score?: number;
  summary: string;
  data?: unknown; // Full response for re-display
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}

export function getHistory(): HistoryEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as HistoryEntry[];
  } catch {
    return [];
  }
}

export function addToHistory(entry: Omit<HistoryEntry, "id" | "timestamp">): void {
  try {
    const history = getHistory();
    history.unshift({
      ...entry,
      id: generateId(),
      timestamp: new Date().toISOString(),
    });
    // Keep only last MAX_ENTRIES
    if (history.length > MAX_ENTRIES) {
      history.length = MAX_ENTRIES;
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch {
    // Silently fail if localStorage is full
  }
}

export function clearHistory(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export function deleteHistoryEntry(id: string): void {
  const history = getHistory().filter((e) => e.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}

/**
 * Export history or analysis data as CSV
 */
export function exportToCsv(
  filename: string,
  headers: string[],
  rows: string[][]
): void {
  const csvContent = [
    headers.join(","),
    ...rows.map((row) =>
      row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")
    ),
  ].join("\n");

  const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${filename}_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Export SERP results to CSV
 */
export function exportSerpToCsv(keyword: string, results: Array<{ position: number; title: string; url: string; domain: string; snippet: string }>) {
  exportToCsv(
    `serp_${keyword.replace(/\s+/g, "_")}`,
    ["Position", "Title", "Domain", "URL", "Snippet"],
    results.map((r) => [String(r.position), r.title, r.domain, r.url, r.snippet])
  );
}

/**
 * Export SEO audit to CSV
 */
export function exportAuditToCsv(url: string, _score: number, issues: Array<{ category: string; message: string; severity: string }>) {
  exportToCsv(
    `seo_audit_${new URL(url).hostname}`,
    ["Category", "Severity", "Issue"],
    issues.map((i) => [i.category, i.severity, i.message])
  );
}
