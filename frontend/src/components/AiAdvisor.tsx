import React, { useState, useEffect, useCallback } from "react";
import { API_BASE } from "../lib/apiConfig";
import { authFetch } from "../lib/auth";
import "./DashboardOverview.css"; // Reuse dashboard grids/charts styling
import { AdvisorRoadmapTree } from "./AdvisorRoadmapTree";


import type {
  ManagedSite,
  PendingRecommendationItem,
  RecommendationOutcomeUpdatePayload,
  OutcomeTrackingContext,
  AdvisorResponse
} from "../types/advisor";


export function AiAdvisor() {
  // Site resolution & Form states
  const [sites, setSites] = useState<ManagedSite[]>([]);
  const [activeSite, setActiveSite] = useState<ManagedSite | null>(null);
  const [selectedSiteUrl, setSelectedSiteUrl] = useState("");
  const [targetKeyword, setTargetKeyword] = useState("");
  const [days, setDays] = useState(30);

  // Toggle checks
  const [includeGsc, setIncludeGsc] = useState(true);
  const [includeGa4, setIncludeGa4] = useState(true);
  const [includeSerp, setIncludeSerp] = useState(true);
  const [includeRankTracking, setIncludeRankTracking] = useState(true);
  const [includeTechnical, setIncludeTechnical] = useState(true);
  const [includeCwv, setIncludeCwv] = useState(true);
  const [includeSchema, setIncludeSchema] = useState(true);
  const [includeUsageHistory, setIncludeUsageHistory] = useState(true);

  // Analysis result & Loading states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AdvisorResponse | null>(null);

  // Export report states — Phase 9
  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Roadmap collapsed streams state hook — Phase 10
  const [collapsedStreams, setCollapsedStreams] = useState<Record<string, boolean>>({});



  // SEO memory collapsible sections toggle states
  const [showRecurringOpportunities, setShowRecurringOpportunities] = useState(false);
  const [showPendingRecommendations, setShowPendingRecommendations] = useState(false);
  const [showInProgressRecommendations, setShowInProgressRecommendations] = useState(false);
  const [showRepeatedRecommendations, setShowRepeatedRecommendations] = useState(false);

  // Status updating form states
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [updatingStatus, setUpdatingStatus] = useState("pending");
  const [updatingNote, setUpdatingNote] = useState("");
  const [clicksDelta, setClicksDelta] = useState("");
  const [impressionsDelta, setImpressionsDelta] = useState("");
  const [ctrDelta, setCtrDelta] = useState("");
  const [positionDelta, setPositionDelta] = useState("");
  const [updatingOutcome, setUpdatingOutcome] = useState("");
  const [ctrBefore, setCtrBefore] = useState("");
  const [ctrAfter, setCtrAfter] = useState("");
  const [positionBefore, setPositionBefore] = useState("");
  const [positionAfter, setPositionAfter] = useState("");
  const [updatingLoading, setUpdatingLoading] = useState(false);
  const [updatingError, setUpdatingError] = useState<string | null>(null);

  // Outcome tracking list states
  const [completedRecs, setCompletedRecs] = useState<PendingRecommendationItem[]>([]);
  const [failedRecs, setFailedRecs] = useState<PendingRecommendationItem[]>([]);
  const [showCompletedRecs, setShowCompletedRecs] = useState(false);
  const [showFailedRecs, setShowFailedRecs] = useState(false);

  // Fetch managed sites list & Active site prefill
  const loadSites = useCallback(async () => {
    try {
      const res = await authFetch(`${API_BASE}/sites/list`);
      if (res.ok) {
        const data = await res.json();
        const siteList = data.sites || [];
        setSites(siteList);

        // Fetch active site
        const activeRes = await authFetch(`${API_BASE}/sites/active`);
        if (activeRes.ok) {
          const activeData = await activeRes.json();
          if (activeData && activeData.url) {
            setActiveSite(activeData);
            setSelectedSiteUrl(activeData.url);
          } else if (siteList.length > 0) {
            setSelectedSiteUrl(siteList[0].url);
          }
        }
      }
    } catch {
      setError("Không thể tải danh sách website từ hệ thống.");
    }
  }, []);

  const fetchOutcomes = useCallback(async (siteUrl: string) => {
    try {
      const compRes = await authFetch(`${API_BASE}/dataset/recommendations?site_url=${encodeURIComponent(siteUrl)}&status=completed`);
      if (compRes.ok) {
        const compData = await compRes.json();
        setCompletedRecs(compData.items || []);
      }
      const failRes = await authFetch(`${API_BASE}/dataset/recommendations?site_url=${encodeURIComponent(siteUrl)}&status=failed`);
      if (failRes.ok) {
        const failData = await failRes.json();
        setFailedRecs(failData.items || []);
      }
    } catch (err) {
      console.error("Lỗi khi tải danh sách khuyến nghị đã hoàn thành/thất bại:", err);
    }
  }, []);

  useEffect(() => {
    loadSites();
  }, [loadSites]);

  useEffect(() => {
    if (result && result.site_url) {
      fetchOutcomes(result.site_url);
    } else {
      setCompletedRecs([]);
      setFailedRecs([]);
    }
  }, [result?.site_url, fetchOutcomes]);

  // Handle Analysis submit
  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await authFetch(`${API_BASE}/advisor/analyze`, {
        method: "POST",
        body: JSON.stringify({
          site_url: selectedSiteUrl || undefined,
          target_keyword: targetKeyword.trim() || undefined,
          days,
          include_gsc: includeGsc,
          include_ga4: includeGa4,
          include_serp: includeSerp,
          include_rank_tracking: includeRankTracking,
          include_technical: includeTechnical,
          include_cwv: includeCwv,
          include_schema: includeSchema,
          include_usage_history: includeUsageHistory,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? `Lỗi hệ thống (HTTP ${res.status})`);
      }

      const data = await res.json();
      setResult(data);

      // Auto-expand memory details sections if they contain items
      if (data.recurring_opportunities && data.recurring_opportunities.length > 0) {
        setShowRecurringOpportunities(true);
      } else {
        setShowRecurringOpportunities(false);
      }
      if (data.pending_recommendations && data.pending_recommendations.length > 0) {
        setShowPendingRecommendations(true);
      } else {
        setShowPendingRecommendations(false);
      }
      if (data.in_progress_recommendations && data.in_progress_recommendations.length > 0) {
        setShowInProgressRecommendations(true);
      } else {
        setShowInProgressRecommendations(false);
      }
      if (data.repeated_recommendations && data.repeated_recommendations.length > 0) {
        setShowRepeatedRecommendations(true);
      } else {
        setShowRepeatedRecommendations(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Có lỗi xảy ra trong quá trình phân tích.");
    } finally {
      setLoading(false);
    }
  };

  const handleExportReport = async (format: "json" | "markdown" | "html") => {
    if (!result) return;
    setExportLoading(true);
    setExportError(null);
    try {
      const res = await authFetch(`${API_BASE}/advisor/export`, {
        method: "POST",
        body: JSON.stringify({
          format,
          advisor_result: result,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? `Không thể xuất báo cáo (HTTP ${res.status})`);
      }

      const blob = await res.blob();
      
      // Read filename from Content-Disposition header if available
      let filename = "";
      const contentDisposition = res.headers.get("content-disposition");
      if (contentDisposition) {
        const match = contentDisposition.match(/filename=["']?([^"']+)["']?/);
        if (match && match[1]) {
          filename = match[1];
        }
      }

      // Fallback filename if not provided in header
      if (!filename) {
        const domain = result.site_url 
          ? result.site_url.replace(/^(https?:\/\/)?(www\.)?/, "").replace(/[^a-zA-Z0-9\-]/g, "-").replace(/-+/g, "-").replace(/-$/, "")
          : "site";
        const dateStr = new Date().toISOString().split("T")[0];
        const ext = format === "markdown" ? "md" : format;
        filename = `advisor-report-${domain || "site"}-${dateStr}.${ext}`;
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setExportError(err instanceof Error ? err.message : "Có lỗi xảy ra khi tải file báo cáo.");
    } finally {
      setExportLoading(false);
    }
  };

  const startUpdating = (rec: PendingRecommendationItem) => {

    setUpdatingId(rec.id);
    setUpdatingStatus(rec.status);
    setUpdatingNote(rec.execution_note || "");
    setUpdatingOutcome(rec.outcome || "");
    const delta = rec.measured_delta_json || {};
    setClicksDelta(delta.clicks_diff !== undefined ? String(delta.clicks_diff) : "");
    setImpressionsDelta(delta.impressions_diff !== undefined ? String(delta.impressions_diff) : "");
    setCtrDelta(delta.ctr_diff !== undefined ? String(delta.ctr_diff) : "");
    setPositionDelta(delta.position_diff !== undefined ? String(delta.position_diff) : "");
    setCtrBefore(delta.ctr_before !== undefined ? String(delta.ctr_before) : "");
    setCtrAfter(delta.ctr_after !== undefined ? String(delta.ctr_after) : "");
    setPositionBefore(delta.position_before !== undefined ? String(delta.position_before) : "");
    setPositionAfter(delta.position_after !== undefined ? String(delta.position_after) : "");
    setUpdatingError(null);
  };

  const handleUpdateStatus = async (id: number) => {
    setUpdatingLoading(true);
    setUpdatingError(null);

    const deltas: Record<string, number> = {};
    if (clicksDelta) deltas.clicks_diff = parseInt(clicksDelta, 10);
    if (impressionsDelta) deltas.impressions_diff = parseInt(impressionsDelta, 10);
    if (ctrDelta) deltas.ctr_diff = parseFloat(ctrDelta);
    if (positionDelta) deltas.position_diff = parseFloat(positionDelta);
    if (ctrBefore) deltas.ctr_before = parseFloat(ctrBefore);
    if (ctrAfter) deltas.ctr_after = parseFloat(ctrAfter);
    if (positionBefore) deltas.position_before = parseFloat(positionBefore);
    if (positionAfter) deltas.position_after = parseFloat(positionAfter);

    const measured_delta_json = Object.keys(deltas).length > 0 ? deltas : null;

    try {
      const payload: RecommendationOutcomeUpdatePayload = {
        status: updatingStatus,
        outcome: updatingOutcome || (updatingStatus === "completed" ? "Thành công" : (updatingStatus === "failed" ? "Thất bại" : "Đang thực hiện")),
        measured_delta_json,
        execution_note: updatingNote || null,
      };

      const res = await authFetch(`${API_BASE}/dataset/recommendations/${id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? `Lỗi cập nhật (HTTP ${res.status})`);
      }

      const updatedItem = await res.json();

      setResult((prev) => {
        if (!prev) return null;

        let newPending = prev.pending_recommendations || [];
        let newInProgress = prev.in_progress_recommendations || [];

        // 1. Remove from lists
        newPending = newPending.filter((r) => r.id !== id);
        newInProgress = newInProgress.filter((r) => r.id !== id);
        
        // Remove from completedRecs and failedRecs local state
        setCompletedRecs((prevComp) => prevComp.filter((r) => r.id !== id));
        setFailedRecs((prevFail) => prevFail.filter((r) => r.id !== id));

        // 2. Add to list
        const itemToMove: PendingRecommendationItem = {
          id: updatedItem.id,
          recommendation_type: updatedItem.recommendation_type,
          recommendation_text: updatedItem.recommendation_text,
          priority: updatedItem.priority,
          impact: updatedItem.impact,
          status: updatedItem.status,
          page_url: updatedItem.page_url,
          keyword: updatedItem.keyword,
          created_at: updatedItem.created_at,
          reviewed_at: updatedItem.reviewed_at,
          execution_note: updatedItem.execution_note,
          measured_delta_json: updatedItem.measured_delta_json,
          outcome: updatedItem.outcome
        };

        if (updatedItem.status === "pending") {
          newPending = [itemToMove, ...newPending];
        } else if (updatedItem.status === "in_progress") {
          newInProgress = [itemToMove, ...newInProgress];
        } else if (updatedItem.status === "completed") {
          setCompletedRecs((prevComp) => [itemToMove, ...prevComp]);
        } else if (updatedItem.status === "failed") {
          setFailedRecs((prevFail) => [itemToMove, ...prevFail]);
        }

        // 3. Update tracker counts
        const newTrackingContext: OutcomeTrackingContext = prev.outcome_tracking_context ? { ...prev.outcome_tracking_context } : {
          total_outcomes: 0,
          pending_count: 0,
          in_progress_count: 0,
          completed_count: 0,
          failed_count: 0,
          completed_with_delta_count: 0,
          recent_completed_recommendations: [],
          recent_failed_recommendations: []
        };

        const wasPending = (prev.pending_recommendations || []).some(r => r.id === id);
        const wasInProgress = (prev.in_progress_recommendations || []).some(r => r.id === id);
        const wasCompleted = completedRecs.some(r => r.id === id);
        const wasFailed = failedRecs.some(r => r.id === id);

        if (wasPending) {
          newTrackingContext.pending_count = Math.max(0, (newTrackingContext.pending_count || 0) - 1);
        } else if (wasInProgress) {
          newTrackingContext.in_progress_count = Math.max(0, (newTrackingContext.in_progress_count || 0) - 1);
        } else if (wasCompleted) {
          newTrackingContext.completed_count = Math.max(0, (newTrackingContext.completed_count || 0) - 1);
          const oldItem = completedRecs.find(r => r.id === id);
          if (oldItem && oldItem.measured_delta_json && Object.keys(oldItem.measured_delta_json).length > 0) {
            newTrackingContext.completed_with_delta_count = Math.max(0, (newTrackingContext.completed_with_delta_count || 0) - 1);
          }
        } else if (wasFailed) {
          newTrackingContext.failed_count = Math.max(0, (newTrackingContext.failed_count || 0) - 1);
        }

        if (updatedItem.status === "pending") {
          newTrackingContext.pending_count = (newTrackingContext.pending_count || 0) + 1;
        } else if (updatedItem.status === "in_progress") {
          newTrackingContext.in_progress_count = (newTrackingContext.in_progress_count || 0) + 1;
        } else if (updatedItem.status === "completed") {
          newTrackingContext.completed_count = (newTrackingContext.completed_count || 0) + 1;
          const hasDelta = updatedItem.measured_delta_json && Object.keys(updatedItem.measured_delta_json).length > 0;
          if (hasDelta) {
            newTrackingContext.completed_with_delta_count = (newTrackingContext.completed_with_delta_count || 0) + 1;
          }
        } else if (updatedItem.status === "failed") {
          newTrackingContext.failed_count = (newTrackingContext.failed_count || 0) + 1;
        }

        let pendingCount = prev.memory_context?.pending_recommendations_count ?? 0;
        if (wasPending && updatedItem.status !== "pending") {
          pendingCount = Math.max(0, pendingCount - 1);
        } else if (!wasPending && updatedItem.status === "pending") {
          pendingCount = pendingCount + 1;
        }

        const newContext = prev.memory_context ? {
          ...prev.memory_context,
          pending_recommendations_count: pendingCount,
        } : null;

        return {
          ...prev,
          pending_recommendations: newPending,
          in_progress_recommendations: newInProgress,
          memory_context: newContext,
          outcome_tracking_context: newTrackingContext
        };
      });

      // Clear edit panel state
      setUpdatingId(null);
      setUpdatingStatus("pending");
      setUpdatingNote("");
      setClicksDelta("");
      setImpressionsDelta("");
      setCtrDelta("");
      setPositionDelta("");
      setUpdatingOutcome("");
      setCtrBefore("");
      setCtrAfter("");
      setPositionBefore("");
      setPositionAfter("");
    } catch (err) {
      setUpdatingError(err instanceof Error ? err.message : "Không thể cập nhật trạng thái khuyến nghị.");
    } finally {
      setUpdatingLoading(false);
    }
  };

  // Helper styles & icons
  const statusBadge = (status: string) => {
    const s = (status || "").toLowerCase();
    if (s === "pending") return <span className="issue-badge badge-warning" style={{ padding: "2px 8px", background: "rgba(245, 158, 11, 0.15)", color: "#fbbf24", border: "1px solid rgba(245, 158, 11, 0.3)" }}>Chờ xử lý</span>;
    if (s === "in_progress") return <span className="issue-badge badge-warning" style={{ padding: "2px 8px", background: "rgba(6, 182, 212, 0.15)", color: "#67e8f9", border: "1px solid rgba(6, 182, 212, 0.3)" }}>Đang thực hiện</span>;
    if (s === "completed") return <span className="issue-badge badge-suggestion" style={{ padding: "2px 8px", background: "rgba(16, 185, 129, 0.15)", color: "#34d399", border: "1px solid rgba(16, 185, 129, 0.3)" }}>Hoàn thành</span>;
    if (s === "failed") return <span className="issue-badge badge-critical" style={{ padding: "2px 8px", background: "rgba(239, 68, 68, 0.15)", color: "#f87171", border: "1px solid rgba(239, 68, 68, 0.3)" }}>Thất bại</span>;
    return <span className="issue-badge" style={{ padding: "2px 8px", background: "rgba(255,255,255,0.1)", color: "var(--text)" }}>{status}</span>;
  };

  const renderRecommendationItem = (rec: PendingRecommendationItem, borderLeftColor: string) => {
    return (
      <div className="geo-faq-item" style={{ borderLeft: `2px solid ${borderLeftColor}`, margin: 0 }} key={rec.id}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
          <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
            <span className="rt-tag-badge" style={{ background: "rgba(255,255,255,0.05)", color: "var(--text-h)" }}>{rec.recommendation_type}</span>
            {rec.status && statusBadge(rec.status)}
            {rec.priority && priorityLabel(rec.priority as string)}
          </div>
          {rec.created_at && (
            <span style={{ fontSize: "11px", color: "var(--text-dim)" }}>
              Đề xuất: {new Date(rec.created_at).toLocaleDateString("vi-VN")}
            </span>
          )}
        </div>
        
        <p style={{ fontSize: "13px", color: "var(--text-h)", margin: "8px 0 4px 0", fontWeight: "600" }}>
          {rec.recommendation_text}
        </p>
        
        {rec.page_url && (
          <p style={{ fontSize: "11px", color: "#3b82f6", margin: "2px 0" }}>
            🔗 <strong>Trang đích:</strong> <a href={rec.page_url} target="_blank" rel="noreferrer" style={{ color: "#60a5fa" }}>{rec.page_url}</a>
          </p>
        )}
        {rec.keyword && (
          <p style={{ fontSize: "11px", color: "#10b981", margin: "2px 0" }}>
            🔑 <strong>Từ khóa mục tiêu:</strong> '{rec.keyword}'
          </p>
        )}
        {rec.impact && (
          <p style={{ fontSize: "11px", color: "var(--text-dim)", margin: "2px 0" }}>
            ⚡ <strong>Tác động dự kiến:</strong> {rec.impact}
          </p>
        )}
        {rec.execution_note && (
          <p style={{ fontSize: "11px", color: "#e9d5ff", margin: "4px 0" }}>
            📝 <strong>Ghi chú thực thi:</strong> {rec.execution_note}
          </p>
        )}
        {rec.outcome && (
          <p style={{ fontSize: "11px", color: "#67e8f9", margin: "4px 0" }}>
            🎯 <strong>Kết quả:</strong> {rec.outcome}
          </p>
        )}
        
        {rec.measured_delta_json && Object.keys(rec.measured_delta_json).length > 0 && (
          <div style={{ marginTop: "6px", padding: "6px 10px", background: "rgba(255,255,255,0.02)", borderRadius: "4px", fontSize: "11px", border: "1px solid rgba(255,255,255,0.05)" }}>
            <span style={{ color: "#34d399", fontWeight: "bold" }}>📈 Số liệu đo lường KPI:</span>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "6px", marginTop: "4px" }}>
              {rec.measured_delta_json.ctr_before !== undefined && <span>CTR trước: <strong>{rec.measured_delta_json.ctr_before}%</strong></span>}
              {rec.measured_delta_json.ctr_after !== undefined && <span>CTR sau: <strong>{rec.measured_delta_json.ctr_after}%</strong></span>}
              {rec.measured_delta_json.position_before !== undefined && <span>Vị trí trước: <strong>#{rec.measured_delta_json.position_before}</strong></span>}
              {rec.measured_delta_json.position_after !== undefined && <span>Vị trí sau: <strong>#{rec.measured_delta_json.position_after}</strong></span>}
              {rec.measured_delta_json.clicks_diff !== undefined && <span>Clicks: <strong>{rec.measured_delta_json.clicks_diff > 0 ? `+${rec.measured_delta_json.clicks_diff}` : rec.measured_delta_json.clicks_diff}</strong></span>}
              {rec.measured_delta_json.impressions_diff !== undefined && <span>Impressions: <strong>{rec.measured_delta_json.impressions_diff > 0 ? `+${rec.measured_delta_json.impressions_diff}` : rec.measured_delta_json.impressions_diff}</strong></span>}
            </div>
          </div>
        )}

        {updatingId === rec.id ? (
          <div style={{ marginTop: "12px", padding: "12px", background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)", borderRadius: "8px" }}>
            <h4 style={{ fontSize: "12px", margin: "0 0 10px 0", color: "#a78bfa" }}>Cập nhật trạng thái khuyến nghị</h4>
            
            <div className="geo-schema-form" style={{ display: "grid", gridTemplateColumns: "1fr", gap: "8px" }}>
              <div className="input-group">
                <label className="input-label" style={{ fontSize: "11px" }}>Trạng thái</label>
                <select
                  className="text-input"
                  value={updatingStatus}
                  onChange={(e) => setUpdatingStatus(e.target.value)}
                  style={{ height: "32px", fontSize: "12px", background: "var(--surface)", color: "var(--text)" }}
                >
                  <option value="pending">Chờ xử lý (Pending)</option>
                  <option value="in_progress">Đang thực hiện (In Progress)</option>
                  <option value="completed">Hoàn thành (Completed)</option>
                  <option value="failed">Thất bại (Failed)</option>
                </select>
              </div>

              <div className="input-group">
                <label className="input-label" style={{ fontSize: "11px" }}>Ghi chú thực thi</label>
                <textarea
                  className="text-input"
                  value={updatingNote}
                  onChange={(e) => setUpdatingNote(e.target.value)}
                  placeholder="Ví dụ: Đang tối ưu lại thẻ tiêu đề theo từ khóa lặp lại..."
                  style={{ height: "60px", fontSize: "12px", padding: "6px" }}
                />
              </div>

              <div className="input-group">
                <label className="input-label" style={{ fontSize: "11px" }}>Kết quả (Outcome)</label>
                <input
                  type="text"
                  className="text-input"
                  value={updatingOutcome}
                  onChange={(e) => setUpdatingOutcome(e.target.value)}
                  placeholder="Ví dụ: Đạt mục tiêu, tăng CTR nhẹ..."
                  style={{ height: "32px", fontSize: "12px" }}
                />
              </div>

              {updatingStatus === "completed" && (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "8px", marginTop: "4px" }}>
                  <div className="input-group">
                    <label className="input-label" style={{ fontSize: "10px" }}>CTR trước (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      className="text-input"
                      placeholder="Ví dụ: 1.2"
                      value={ctrBefore}
                      onChange={(e) => setCtrBefore(e.target.value)}
                      style={{ height: "30px", fontSize: "12px" }}
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label" style={{ fontSize: "10px" }}>CTR sau (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      className="text-input"
                      placeholder="Ví dụ: 2.1"
                      value={ctrAfter}
                      onChange={(e) => setCtrAfter(e.target.value)}
                      style={{ height: "30px", fontSize: "12px" }}
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label" style={{ fontSize: "10px" }}>Vị trí trước</label>
                    <input
                      type="number"
                      step="0.1"
                      className="text-input"
                      placeholder="Ví dụ: 8.5"
                      value={positionBefore}
                      onChange={(e) => setPositionBefore(e.target.value)}
                      style={{ height: "30px", fontSize: "12px" }}
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label" style={{ fontSize: "10px" }}>Vị trí sau</label>
                    <input
                      type="number"
                      step="0.1"
                      className="text-input"
                      placeholder="Ví dụ: 5.2"
                      value={positionAfter}
                      onChange={(e) => setPositionAfter(e.target.value)}
                      style={{ height: "30px", fontSize: "12px" }}
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label" style={{ fontSize: "10px" }}>Clicks thay đổi</label>
                    <input
                      type="number"
                      className="text-input"
                      placeholder="+15"
                      value={clicksDelta}
                      onChange={(e) => setClicksDelta(e.target.value)}
                      style={{ height: "30px", fontSize: "12px" }}
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label" style={{ fontSize: "10px" }}>Impressions thay đổi</label>
                    <input
                      type="number"
                      className="text-input"
                      placeholder="+150"
                      value={impressionsDelta}
                      onChange={(e) => setImpressionsDelta(e.target.value)}
                      style={{ height: "30px", fontSize: "12px" }}
                    />
                  </div>
                </div>
              )}
            </div>

            {updatingError && (
              <div style={{ color: "#ef4444", fontSize: "11px", marginTop: "8px" }}>❌ {updatingError}</div>
            )}

            <div style={{ display: "flex", gap: "8px", marginTop: "12px", justifyContent: "flex-end" }}>
              <button
                type="button"
                onClick={() => setUpdatingId(null)}
                className="rt-btn"
                style={{ padding: "4px 12px", fontSize: "11px", background: "rgba(255,255,255,0.05)", border: "1px solid var(--border)", color: "var(--text)" }}
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={() => handleUpdateStatus(rec.id)}
                disabled={updatingLoading}
                className="rt-btn rt-btn-add"
                style={{ padding: "4px 12px", fontSize: "11px" }}
              >
                {updatingLoading ? "Đang lưu..." : "Lưu"}
              </button>
            </div>
          </div>
        ) : (
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "8px" }}>
            <button
              type="button"
              onClick={() => startUpdating(rec)}
              className="rt-btn"
              style={{ padding: "4px 12px", fontSize: "11px", background: "rgba(139, 92, 246, 0.1)", border: "1px solid rgba(139, 92, 246, 0.3)", color: "#c4b5fd" }}
            >
              Cập nhật tiến độ
            </button>
          </div>
        )}
      </div>
    );
  };

  // Helper styles & icons
  const severityBadge = (sev: "critical" | "warning" | "info") => {
    if (sev === "critical") return <span className="issue-badge badge-critical">Nghiêm trọng</span>;
    if (sev === "warning") return <span className="issue-badge badge-warning">Cảnh báo</span>;
    return <span className="issue-badge badge-suggestion">Gợi ý</span>;
  };

  const priorityLabel = (pri: "high" | "medium" | "low" | string) => {
    const p = (pri || "").toLowerCase();
    if (p === "high") return <span className="issue-badge badge-critical" style={{ padding: "2px 6px" }}>Ưu tiên cao</span>;
    if (p === "medium") return <span className="issue-badge badge-warning" style={{ padding: "2px 6px" }}>Trung bình</span>;
    return <span className="issue-badge badge-suggestion" style={{ padding: "2px 6px" }}>Thấp</span>;
  };

  const sourceStatusLabel = (status: string) => {
    const s = (status || "").toLowerCase();
    if (s === "ok" || s === "gsc_real" || s === "live_ga4" || s === "partial_live_ga4") {
      return <span style={{ color: "#10b981", fontWeight: "bold" }}>● Hoạt động</span>;
    }
    if (s === "disabled") {
      return <span style={{ color: "#94a3b8", fontWeight: "bold" }}>○ Bị tắt</span>;
    }
    if (s === "missing_credentials") {
      return <span style={{ color: "#f59e0b", fontWeight: "bold" }}>⚠ Thiếu cấu hình</span>;
    }
    return <span style={{ color: "#ef4444", fontWeight: "bold" }}>✕ Lỗi/Không có dữ liệu</span>;
  };

  return (
    <div className="geo-optimizer" style={{ paddingBottom: "3rem" }}>
      <div className="hint-box">
        💡 <strong>AI Cố vấn website:</strong> Hợp nhất toàn bộ dữ liệu Marketing (GSC, GA4, Technical SEO, rank tracker, v.v.), tính toán deterministic insights trước, sau đó dùng AI của Groq LLaMA 3.3 để xây dựng kế hoạch bứt phá traffic.
      </div>

      {/* Inputs Form */}
      <form className="audit-form" style={{ marginTop: "1rem" }} onSubmit={handleAnalyze}>
        <div className="geo-schema-form" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "12px" }}>
          
          <div className="input-group">
            <label className="input-label" htmlFor="site-select">Chọn Website phân tích</label>
            <select
              id="site-select"
              className="text-input"
              value={selectedSiteUrl}
              onChange={(e) => setSelectedSiteUrl(e.target.value)}
              style={{ background: "var(--surface)", color: "var(--text)" }}
            >
              {activeSite && <option value={activeSite.url}>{activeSite.name} (Active - {activeSite.url})</option>}
              {sites
                .filter((s) => !activeSite || s.url !== activeSite.url)
                .map((site) => (
                  <option key={site.id} value={site.url}>
                    {site.name} ({site.url})
                  </option>
                ))}
              <option value="">-- Dùng cấu hình mặc định trong .env --</option>
            </select>
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="kw-input">Từ khóa mục tiêu (SEO Target)</label>
            <input
              id="kw-input"
              className="text-input"
              type="text"
              placeholder="Ví dụ: dịch vụ seo bình phước (Cần thiết cho SERP)"
              value={targetKeyword}
              onChange={(e) => setTargetKeyword(e.target.value)}
              style={{ paddingLeft: "12px" }}
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="days-select">Khoảng thời gian</label>
            <select
              id="days-select"
              className="text-input"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              style={{ background: "var(--surface)", color: "var(--text)" }}
            >
              <option value={30}>30 ngày qua</option>
              <option value={60}>60 ngày qua</option>
              <option value={90}>90 ngày qua</option>
            </select>
          </div>

        </div>

        {/* Checkbox triggers */}
        <div style={{ marginTop: "1rem" }}>
          <label className="input-label" style={{ marginBottom: "6px" }}>Nguồn dữ liệu đưa vào cố vấn</label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "16px", padding: "10px", background: "rgba(255,255,255,0.03)", borderRadius: "8px", border: "1px solid var(--border)" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeGsc} onChange={(e) => setIncludeGsc(e.target.checked)} />
              Google Search Console
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeGa4} onChange={(e) => setIncludeGa4(e.target.checked)} />
              Google Analytics 4
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeSerp} onChange={(e) => setIncludeSerp(e.target.checked)} />
              SERP Live
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeRankTracking} onChange={(e) => setIncludeRankTracking(e.target.checked)} />
              Rank Tracker Local
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeTechnical} onChange={(e) => setIncludeTechnical(e.target.checked)} />
              Technical SEO
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeCwv} onChange={(e) => setIncludeCwv(e.target.checked)} />
              Core Web Vitals
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeSchema} onChange={(e) => setIncludeSchema(e.target.checked)} />
              Schema Validation
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
              <input type="checkbox" checked={includeUsageHistory} onChange={(e) => setIncludeUsageHistory(e.target.checked)} />
              Lịch sử sử dụng
            </label>
          </div>
        </div>

        <div style={{ marginTop: "1rem", display: "flex", gap: "8px" }}>
          <button
            type="submit"
            className="rt-btn rt-btn-add"
            style={{ width: "fit-content", padding: "8px 24px", display: "flex", alignItems: "center", gap: "8px" }}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="btn-spinner" aria-label="Loading" />
                Đang chẩn đoán website...
              </>
            ) : (
              <>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
                Phân tích &amp; Cố vấn AI
              </>
            )}
          </button>
        </div>
      </form>

      {/* Error display */}
      {error && (
        <div className="mock-warning-banner" role="alert" style={{ borderColor: "#ef4444", marginTop: "1rem" }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span><strong>Lỗi phân tích:</strong> {error}</span>
        </div>
      )}

      {/* Results Workspace */}
      {result && (
        <div style={{ marginTop: "1.5rem" }} className="result-wrapper">

          {/* Export Report Actions — Phase 9 */}
          <div className="section-block" style={{ padding: "16px 20px", background: "rgba(255,255,255,0.02)", borderRadius: "12px", border: "1px solid var(--border)", marginBottom: "1rem" }}>
            <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "12px" }}>
              <div style={{ fontSize: "14px", fontWeight: "600", color: "var(--text-h)" }}>
                📥 Xuất báo cáo chẩn đoán SEO AI:
              </div>
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  type="button"
                  className="rt-btn"
                  onClick={() => handleExportReport("json")}
                  disabled={exportLoading}
                  style={{ padding: "6px 14px", fontSize: "12px", background: "rgba(139, 92, 246, 0.1)", border: "1px solid rgba(139, 92, 246, 0.3)", color: "#c4b5fd", cursor: "pointer" }}
                >
                  Xuất JSON
                </button>
                <button
                  type="button"
                  className="rt-btn"
                  onClick={() => handleExportReport("markdown")}
                  disabled={exportLoading}
                  style={{ padding: "6px 14px", fontSize: "12px", background: "rgba(6, 182, 212, 0.1)", border: "1px solid rgba(6, 182, 212, 0.3)", color: "#67e8f9", cursor: "pointer" }}
                >
                  Xuất Markdown
                </button>
                <button
                  type="button"
                  className="rt-btn"
                  onClick={() => handleExportReport("html")}
                  disabled={exportLoading}
                  style={{ padding: "6px 14px", fontSize: "12px", background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.3)", color: "#34d399", cursor: "pointer" }}
                >
                  Xuất HTML
                </button>
              </div>
            </div>
            {exportLoading && (
              <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "var(--text-dim)", marginTop: "10px" }}>
                <span className="btn-spinner" style={{ width: "12px", height: "12px", borderWidth: "2px" }} />
                Đang khởi tạo và tải file báo cáo...
              </div>
            )}
            {exportError && (
              <div style={{ color: "#ef4444", fontSize: "12px", marginTop: "10px" }}>
                ❌ Lỗi xuất báo cáo: {exportError}
              </div>
            )}
          </div>
          
          {/* Executive Summary Card */}

          <div className="section-block" style={{ padding: "20px", background: "rgba(255,255,255,0.02)", borderRadius: "12px", border: "1px solid var(--border)" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "8px", margin: "0 0 10px 0", color: "#8b5cf6", fontSize: "17px", fontWeight: "700" }}>
              💎 Tóm tắt điều hành (Executive Summary)
              <span style={{ fontSize: "10px", background: "rgba(139,92,246,0.15)", color: "#c4b5fd", padding: "2px 8px", borderRadius: "99px", marginLeft: "auto", border: "1px solid rgba(139,92,246,0.2)" }}>
                AI: {result.ai_provider}
              </span>
            </h3>
            <p style={{ fontSize: "14px", lineHeight: "1.6", color: "var(--text-h)", margin: 0 }}>
              {result.summary}
            </p>
          </div>

          {/* Bộ nhớ lịch sử SEO */}
          <div className="section-block" style={{ marginTop: "1.5rem" }}>
            <h3 className="section-title" style={{ display: "flex", alignItems: "center", gap: "6px", color: "#c084fc" }}>
              🧠 Bộ nhớ lịch sử SEO (SEO Memory)
            </h3>
            
            {/* 1 Summary Row with Counters */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "12px", marginTop: "12px" }}>
              <div style={{ background: "rgba(139, 92, 246, 0.05)", padding: "12px 16px", borderRadius: "10px", border: "1px solid rgba(139, 92, 246, 0.15)" }}>
                <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "4px" }}>Cơ hội từ khóa đã lưu</div>
                <div style={{ fontSize: "20px", fontWeight: "bold", color: "#c4b5fd" }}>
                  {result.memory_context?.keyword_memory_records ?? 0} <span style={{ fontSize: "12px", fontWeight: "normal", color: "var(--text-dim)" }}>bản ghi</span>
                </div>
              </div>
              <div style={{ background: "rgba(6, 182, 212, 0.05)", padding: "12px 16px", borderRadius: "10px", border: "1px solid rgba(6, 182, 212, 0.15)" }}>
                <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "4px" }}>Tổng số đề xuất lịch sử</div>
                <div style={{ fontSize: "20px", fontWeight: "bold", color: "#67e8f9" }}>
                  {result.memory_context?.recommendation_outcomes ?? 0} <span style={{ fontSize: "12px", fontWeight: "normal", color: "var(--text-dim)" }}>đề xuất</span>
                </div>
              </div>
              <div style={{ background: "rgba(245, 158, 11, 0.05)", padding: "12px 16px", borderRadius: "10px", border: "1px solid rgba(245, 158, 11, 0.15)" }}>
                <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "4px" }}>Đề xuất đang tồn đọng</div>
                <div style={{ fontSize: "20px", fontWeight: "bold", color: "#fcd34d" }}>
                  {result.memory_context?.pending_recommendations_count ?? 0} <span style={{ fontSize: "12px", fontWeight: "normal", color: "var(--text-dim)" }}>chờ xử lý</span>
                </div>
              </div>
            </div>

            {/* Info Banner for new_vs_recurring_summary */}
            {result.new_vs_recurring_summary && (
              <div className="mock-warning-banner" style={{ 
                marginTop: "12px", 
                borderColor: "rgba(139, 92, 246, 0.3)", 
                background: "rgba(139, 92, 246, 0.05)", 
                color: "#e9d5ff",
                display: "flex",
                alignItems: "flex-start",
                gap: "10px",
                padding: "12px"
              }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#c084fc" strokeWidth="2.5" style={{ flexShrink: 0, marginTop: "2px" }}>
                  <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
                  <path d="M12 16v-4" />
                  <path d="M12 8h.01" />
                </svg>
                <div style={{ fontSize: "13px", lineHeight: "1.5" }}>
                  <strong>Phân tích bộ nhớ:</strong> {result.new_vs_recurring_summary}
                </div>
              </div>
            )}

            {/* Collapsible Details Sections */}
            <div style={{ marginTop: "1rem", display: "flex", flexDirection: "column", gap: "10px" }}>
              
              {/* Section A: Cơ hội lặp lại */}
              <div style={{ border: "1px solid var(--border)", borderRadius: "8px", overflow: "hidden", background: "rgba(255,255,255,0.01)" }}>
                <button 
                  type="button" 
                  onClick={() => setShowRecurringOpportunities(!showRecurringOpportunities)}
                  style={{ 
                    width: "100%", 
                    display: "flex", 
                    justifyContent: "space-between", 
                    alignItems: "center", 
                    padding: "12px 16px", 
                    background: "rgba(255,255,255,0.02)", 
                    border: "none", 
                    cursor: "pointer", 
                    color: "var(--text-h)",
                    fontWeight: "600",
                    fontSize: "14px",
                    textAlign: "left"
                  }}
                >
                  <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    🔄 Cơ hội từ khóa lặp lại nhiều lần 
                    <span className="issue-badge badge-suggestion" style={{ background: "rgba(192, 132, 252, 0.15)", color: "#c084fc" }}>
                      {result.recurring_opportunities?.length ?? 0}
                    </span>
                  </span>
                  <span>{showRecurringOpportunities ? "▲" : "▼"}</span>
                </button>
                
                {showRecurringOpportunities && (
                  <div style={{ padding: "16px", borderTop: "1px solid var(--border)", background: "rgba(0,0,0,0.1)" }}>
                    {!result.recurring_opportunities || result.recurring_opportunities.length === 0 ? (
                      <p style={{ color: "var(--text-dim)", fontSize: "13px", margin: 0, fontStyle: "italic" }}>
                        Chưa có dữ liệu lịch sử đủ để phát hiện cơ hội lặp lại.
                      </p>
                    ) : (
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "10px" }}>
                        {result.recurring_opportunities.map((opp, index) => (
                          <div key={index} className="geo-faq-item" style={{ borderLeft: "2px solid #c084fc", margin: 0 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
                              <strong style={{ color: "var(--text-h)", fontSize: "13px" }}>{opp.keyword}</strong>
                              <span className="rt-tag-badge" style={{ background: "rgba(192,132,252,0.15)", color: "#c084fc", flexShrink: 0 }}>
                                Lặp {opp.occurrences} lần
                              </span>
                            </div>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "12px", marginTop: "8px", fontSize: "11px", color: "var(--text-dim)" }}>
                              <span>Phân loại: <strong>{opp.opportunity_type}</strong></span>
                              {opp.impressions !== undefined && <span>Hiển thị: <strong>{opp.impressions.toLocaleString()}</strong></span>}
                              {opp.clicks !== undefined && <span>Clicks: <strong>{opp.clicks}</strong></span>}
                              {opp.ctr !== undefined && <span>CTR: <strong>{opp.ctr}%</strong></span>}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Section B: Khuyến nghị đang tồn đọng */}
              <div style={{ border: "1px solid var(--border)", borderRadius: "8px", overflow: "hidden", background: "rgba(255,255,255,0.01)" }}>
                <button 
                  type="button" 
                  onClick={() => setShowPendingRecommendations(!showPendingRecommendations)}
                  style={{ 
                    width: "100%", 
                    display: "flex", 
                    justifyContent: "space-between", 
                    alignItems: "center", 
                    padding: "12px 16px", 
                    background: "rgba(255,255,255,0.02)", 
                    border: "none", 
                    cursor: "pointer", 
                    color: "var(--text-h)",
                    fontWeight: "600",
                    fontSize: "14px",
                    textAlign: "left"
                  }}
                >
                  <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    ⏳ Khuyến nghị tồn đọng (Chờ xử lý)
                    <span className="issue-badge badge-critical" style={{ background: "rgba(239, 68, 68, 0.15)", color: "#ef4444" }}>
                      {result.pending_recommendations?.length ?? 0}
                    </span>
                  </span>
                  <span>{showPendingRecommendations ? "▲" : "▼"}</span>
                </button>
                
                {showPendingRecommendations && (
                  <div style={{ padding: "16px", borderTop: "1px solid var(--border)", background: "rgba(0,0,0,0.1)" }}>
                    {!result.pending_recommendations || result.pending_recommendations.length === 0 ? (
                      <p style={{ color: "var(--text-dim)", fontSize: "13px", margin: 0, fontStyle: "italic" }}>
                        Chưa có khuyến nghị tồn đọng nào được ghi nhận.
                      </p>
                    ) : (
                      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                        {result.pending_recommendations.map((rec) => renderRecommendationItem(rec, "#ef4444"))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Section C: Khuyến nghị đang thực hiện */}
              <div style={{ border: "1px solid var(--border)", borderRadius: "8px", overflow: "hidden", background: "rgba(255,255,255,0.01)" }}>
                <button 
                  type="button" 
                  onClick={() => setShowInProgressRecommendations(!showInProgressRecommendations)}
                  style={{ 
                    width: "100%", 
                    display: "flex", 
                    justifyContent: "space-between", 
                    alignItems: "center", 
                    padding: "12px 16px", 
                    background: "rgba(255,255,255,0.02)", 
                    border: "none", 
                    cursor: "pointer", 
                    color: "var(--text-h)",
                    fontWeight: "600",
                    fontSize: "14px",
                    textAlign: "left"
                  }}
                >
                  <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    ⚙️ Khuyến nghị đang thực hiện (In Progress)
                    <span className="issue-badge badge-warning" style={{ background: "rgba(6, 182, 212, 0.15)", color: "#06b6d4" }}>
                      {result.in_progress_recommendations?.length ?? 0}
                    </span>
                  </span>
                  <span>{showInProgressRecommendations ? "▲" : "▼"}</span>
                </button>
                
                {showInProgressRecommendations && (
                  <div style={{ padding: "16px", borderTop: "1px solid var(--border)", background: "rgba(0,0,0,0.1)" }}>
                    {!result.in_progress_recommendations || result.in_progress_recommendations.length === 0 ? (
                      <p style={{ color: "var(--text-dim)", fontSize: "13px", margin: 0, fontStyle: "italic" }}>
                        Không có khuyến nghị nào đang thực hiện.
                      </p>
                    ) : (
                      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                        {result.in_progress_recommendations.map((rec) => renderRecommendationItem(rec, "#06b6d4"))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Section D: Khuyến nghị lặp lại */}
              <div style={{ border: "1px solid var(--border)", borderRadius: "8px", overflow: "hidden", background: "rgba(255,255,255,0.01)" }}>
                <button 
                  type="button" 
                  onClick={() => setShowRepeatedRecommendations(!showRepeatedRecommendations)}
                  style={{ 
                    width: "100%", 
                    display: "flex", 
                    justifyContent: "space-between", 
                    alignItems: "center", 
                    padding: "12px 16px", 
                    background: "rgba(255,255,255,0.02)", 
                    border: "none", 
                    cursor: "pointer", 
                    color: "var(--text-h)",
                    fontWeight: "600",
                    fontSize: "14px",
                    textAlign: "left"
                  }}
                >
                  <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    🔄 Khuyến nghị lặp lại (Xuất hiện nhiều lần)
                    <span className="issue-badge badge-warning" style={{ background: "rgba(245, 158, 11, 0.15)", color: "#f59e0b" }}>
                      {result.repeated_recommendations?.length ?? 0}
                    </span>
                  </span>
                  <span>{showRepeatedRecommendations ? "▲" : "▼"}</span>
                </button>
                
                {showRepeatedRecommendations && (
                  <div style={{ padding: "16px", borderTop: "1px solid var(--border)", background: "rgba(0,0,0,0.1)" }}>
                    {!result.repeated_recommendations || result.repeated_recommendations.length === 0 ? (
                      <p style={{ color: "var(--text-dim)", fontSize: "13px", margin: 0, fontStyle: "italic" }}>
                        Chưa ghi nhận khuyến nghị lặp lại trong lịch sử.
                      </p>
                    ) : (
                      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                        {result.repeated_recommendations.map((rec, index) => (
                          <div key={index} className="geo-faq-item" style={{ borderLeft: "2px solid #f59e0b", margin: 0 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
                              <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                                <span className="rt-tag-badge" style={{ background: "rgba(245, 158, 11, 0.15)", color: "#fbbf24" }}>{rec.recommendation_type}</span>
                                {rec.priority && priorityLabel(rec.priority as string)}
                              </div>
                              <span className="rt-tag-badge" style={{ background: "rgba(245,158,11,0.15)", color: "#f59e0b", fontWeight: "bold" }}>
                                Đã thấy {rec.occurrences} lần
                              </span>
                            </div>
                            <p style={{ fontSize: "13px", color: "var(--text-h)", margin: "8px 0 4px 0" }}>
                              {rec.recommendation_text}
                            </p>
                            {rec.last_seen && (
                              <p style={{ fontSize: "11px", color: "var(--text-dim)", margin: 0 }}>
                                📅 Lần cuối ghi nhận: {new Date(rec.last_seen).toLocaleDateString("vi-VN")}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

            </div>
          </div>

          {/* Tiến độ xử lý khuyến nghị */}
          {result.outcome_tracking_context && (
            <div className="section-block" style={{ marginTop: "1.5rem" }}>
              <h3 className="section-title" style={{ display: "flex", alignItems: "center", gap: "6px", color: "#06b6d4" }}>
                🎯 Tiến độ xử lý khuyến nghị (Execution Tracker)
              </h3>
              
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", marginTop: "12px" }}>
                <div style={{ background: "rgba(245, 158, 11, 0.05)", padding: "12px 16px", borderRadius: "10px", border: "1px solid rgba(245, 158, 11, 0.15)" }}>
                  <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "4px" }}>Chờ xử lý (Pending)</div>
                  <div style={{ fontSize: "20px", fontWeight: "bold", color: "#fbbf24" }}>
                    {result.outcome_tracking_context.pending_count ?? 0} <span style={{ fontSize: "12px", fontWeight: "normal", color: "var(--text-dim)" }}>đề xuất</span>
                  </div>
                </div>
                <div style={{ background: "rgba(6, 182, 212, 0.05)", padding: "12px 16px", borderRadius: "10px", border: "1px solid rgba(6, 182, 212, 0.15)" }}>
                  <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "4px" }}>Đang thực hiện (In Progress)</div>
                  <div style={{ fontSize: "20px", fontWeight: "bold", color: "#67e8f9" }}>
                    {result.outcome_tracking_context.in_progress_count ?? 0} <span style={{ fontSize: "12px", fontWeight: "normal", color: "var(--text-dim)" }}>đề xuất</span>
                  </div>
                </div>
                <div style={{ background: "rgba(16, 185, 129, 0.05)", padding: "12px 16px", borderRadius: "10px", border: "1px solid rgba(16, 185, 129, 0.15)" }}>
                  <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "4px" }}>Đã hoàn thành (Completed)</div>
                  <div style={{ fontSize: "20px", fontWeight: "bold", color: "#34d399" }}>
                    {result.outcome_tracking_context.completed_count ?? 0} <span style={{ fontSize: "12px", fontWeight: "normal", color: "var(--text-dim)" }}>đề xuất</span>
                  </div>
                  {result.outcome_tracking_context.completed_with_delta_count > 0 && (
                    <div style={{ fontSize: "10px", color: "#a7f3d0", marginTop: "2px" }}>
                      ({result.outcome_tracking_context.completed_with_delta_count} có đo lường KPI delta)
                    </div>
                  )}
                </div>
                <div style={{ background: "rgba(220, 38, 38, 0.05)", padding: "12px 16px", borderRadius: "10px", border: "1px solid rgba(220, 38, 38, 0.15)" }}>
                  <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "4px" }}>Thất bại (Failed)</div>
                  <div style={{ fontSize: "20px", fontWeight: "bold", color: "#fca5a5" }}>
                    {result.outcome_tracking_context.failed_count ?? 0} <span style={{ fontSize: "12px", fontWeight: "normal", color: "var(--text-dim)" }}>đề xuất</span>
                  </div>
                </div>
              </div>

              {/* Summaries from advisor */}
              {(result.effective_recommendation_summary || result.completed_recommendations_summary || result.failed_recommendations_summary) && (
                <div style={{ marginTop: "1rem", display: "flex", flexDirection: "column", gap: "8px" }}>
                  {result.effective_recommendation_summary && (
                    <div className="mock-warning-banner" style={{ borderColor: "rgba(16, 185, 129, 0.3)", background: "rgba(16, 185, 129, 0.03)", color: "#a7f3d0", display: "flex", gap: "8px", padding: "12px" }}>
                      <span style={{ fontSize: "16px" }}>📈</span>
                      <div style={{ fontSize: "13px", lineHeight: "1.5" }}>
                        <strong>Đánh giá hiệu quả:</strong> {result.effective_recommendation_summary}
                      </div>
                    </div>
                  )}
                  {result.completed_recommendations_summary && (
                    <div className="mock-warning-banner" style={{ borderColor: "rgba(59, 130, 246, 0.3)", background: "rgba(59, 130, 246, 0.03)", color: "#93c5fd", display: "flex", gap: "8px", padding: "12px" }}>
                      <span style={{ fontSize: "16px" }}>✅</span>
                      <div style={{ fontSize: "13px", lineHeight: "1.5" }}>
                        <strong>Thực thi hoàn thành:</strong> {result.completed_recommendations_summary}
                      </div>
                    </div>
                  )}
                  {result.failed_recommendations_summary && (
                    <div className="mock-warning-banner" style={{ borderColor: "rgba(239, 68, 68, 0.3)", background: "rgba(239, 68, 68, 0.03)", color: "#fca5a5", display: "flex", gap: "8px", padding: "12px" }}>
                      <span style={{ fontSize: "16px" }}>⚠️</span>
                      <div style={{ fontSize: "13px", lineHeight: "1.5" }}>
                        <strong>Khuyến nghị thất bại:</strong> {result.failed_recommendations_summary}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Collapsible Details for Completed/Failed outcomes */}
              <div style={{ marginTop: "1.5rem", display: "flex", flexDirection: "column", gap: "10px" }}>
                
                {/* Collapsible: Khuyến nghị đã hoàn thành */}
                <div style={{ border: "1px solid var(--border)", borderRadius: "8px", overflow: "hidden", background: "rgba(255,255,255,0.01)" }}>
                  <button 
                    type="button" 
                    onClick={() => setShowCompletedRecs(!showCompletedRecs)}
                    style={{ 
                      width: "100%", 
                      display: "flex", 
                      justifyContent: "space-between", 
                      alignItems: "center", 
                      padding: "12px 16px", 
                      background: "rgba(255,255,255,0.02)", 
                      border: "none", 
                      cursor: "pointer", 
                      color: "var(--text-h)",
                      fontWeight: "600",
                      fontSize: "14px",
                      textAlign: "left"
                    }}
                  >
                    <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      ✅ Khuyến nghị đã hoàn thành (Completed)
                      <span className="issue-badge badge-suggestion" style={{ background: "rgba(16, 185, 129, 0.15)", color: "#10b981" }}>
                        {completedRecs.length}
                      </span>
                    </span>
                    <span>{showCompletedRecs ? "▲" : "▼"}</span>
                  </button>

                  {showCompletedRecs && (
                    <div style={{ padding: "16px", borderTop: "1px solid var(--border)", background: "rgba(0,0,0,0.1)" }}>
                      {completedRecs.length === 0 ? (
                        <p style={{ color: "var(--text-dim)", fontSize: "13px", margin: 0, fontStyle: "italic" }}>
                          Không có khuyến nghị đã hoàn thành nào được ghi nhận.
                        </p>
                      ) : (
                        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                          {completedRecs.map((rec) => renderRecommendationItem(rec, "#10b981"))}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Collapsible: Khuyến nghị thất bại */}
                <div style={{ border: "1px solid var(--border)", borderRadius: "8px", overflow: "hidden", background: "rgba(255,255,255,0.01)" }}>
                  <button 
                    type="button" 
                    onClick={() => setShowFailedRecs(!showFailedRecs)}
                    style={{ 
                      width: "100%", 
                      display: "flex", 
                      justifyContent: "space-between", 
                      alignItems: "center", 
                      padding: "12px 16px", 
                      background: "rgba(255,255,255,0.02)", 
                      border: "none", 
                      cursor: "pointer", 
                      color: "var(--text-h)",
                      fontWeight: "600",
                      fontSize: "14px",
                      textAlign: "left"
                    }}
                  >
                    <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      ❌ Khuyến nghị thất bại (Failed)
                      <span className="issue-badge badge-critical" style={{ background: "rgba(239, 68, 68, 0.15)", color: "#ef4444" }}>
                        {failedRecs.length}
                      </span>
                    </span>
                    <span>{showFailedRecs ? "▲" : "▼"}</span>
                  </button>

                  {showFailedRecs && (
                    <div style={{ padding: "16px", borderTop: "1px solid var(--border)", background: "rgba(0,0,0,0.1)" }}>
                      {failedRecs.length === 0 ? (
                        <p style={{ color: "var(--text-dim)", fontSize: "13px", margin: 0, fontStyle: "italic" }}>
                          Không có khuyến nghị thất bại nào được ghi nhận.
                        </p>
                      ) : (
                        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                          {failedRecs.map((rec) => renderRecommendationItem(rec, "#ef4444"))}
                        </div>
                      )}
                    </div>
                  )}
                </div>

              </div>
            </div>
          )}

          {/* 3 Largest Issues */}
          {result.top_issues && result.top_issues.length > 0 && (
            <div className="section-block" style={{ marginTop: "1rem" }}>
              <h3 className="section-title critical-title" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                🔴 Các vấn đề cần ưu tiên xử lý hàng đầu
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "10px" }}>
                {result.top_issues.slice(0, 5).map((issue, idx) => (
                  <div key={idx} className="geo-faq-item" style={{ borderLeft: "3px solid #ef4444" }}>
                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                      {severityBadge(issue.severity)}
                      <span className="rt-tag-badge">{issue.category}</span>
                    </div>
                    <p style={{ fontSize: "14px", color: "var(--text-h)", fontWeight: "600", margin: "8px 0 4px 0" }}>
                      {issue.message}
                    </p>
                    <p style={{ fontSize: "12px", color: "#10b981", margin: 0 }}>
                      👉 <strong>Khắc phục:</strong> {issue.fix}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Wins Table */}
          {result.quick_wins && result.quick_wins.length > 0 && (
            <div className="section-block" style={{ marginTop: "1.5rem" }}>
              <h3 className="section-title" style={{ display: "flex", alignItems: "center", gap: "6px", color: "#06b6d4" }}>
                🚀 Cơ hội thăng hạng nhanh (Quick Wins)
              </h3>
              <div className="top-pages-table" style={{ marginTop: "10px" }}>
                <table>
                  <thead>
                    <tr>
                      <th>Từ khóa cơ hội</th>
                      <th>Vị trí hiện tại</th>
                      <th>Lượt hiển thị GSC</th>
                      <th>Khuyến nghị hành động</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.quick_wins.map((qw, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: "700", color: "#e2e8f0" }}>{qw.keyword}</td>
                        <td style={{ color: "#3b82f6", fontWeight: "bold" }}>#{qw.current_position}</td>
                        <td>{qw.impressions.toLocaleString()}</td>
                        <td style={{ fontSize: "12px", color: "var(--text-dim)" }}>{qw.action}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Technical Blockers & Core Web Vitals */}
          {result.technical_blockers && result.technical_blockers.length > 0 && (
            <div className="section-block" style={{ marginTop: "1.5rem" }}>
              <h3 className="section-title warning-title" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                ⚡ Rào cản kỹ thuật &amp; Core Web Vitals
              </h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "10px", marginTop: "10px" }}>
                {result.technical_blockers.slice(0, 6).map((blocker, idx) => (
                  <div key={idx} className="geo-faq-item" style={{ borderLeft: "3px solid #f59e0b" }}>
                    <span className="rt-tag-badge" style={{ background: "rgba(245,158,11,0.15)", color: "#f59e0b" }}>{blocker.category}</span>
                    <p style={{ fontSize: "13px", color: "var(--text-h)", fontWeight: "600", margin: "6px 0" }}>{blocker.message}</p>
                    <p style={{ fontSize: "12px", color: "#10b981", margin: 0 }}>👉 {blocker.fix}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Content Opportunities */}
          {result.content_opportunities && result.content_opportunities.length > 0 && (
            <div className="section-block" style={{ marginTop: "1.5rem" }}>
              <h3 className="section-title" style={{ display: "flex", alignItems: "center", gap: "6px", color: "#ec4899" }}>
                ✍️ Cơ hội mở rộng nội dung (Content Gaps)
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "10px" }}>
                {result.content_opportunities.map((opp, idx) => (
                  <div key={idx} className="geo-faq-item" style={{ borderLeft: "3px solid #ec4899" }}>
                    <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                      <span className="rt-tag-badge" style={{ background: "rgba(236,72,153,0.15)", color: "#ec4899" }}>{opp.search_intent}</span>
                    </div>
                    <p style={{ fontSize: "13px", color: "var(--text-h)", margin: "4px 0 0 0" }}>{opp.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Visual Roadmap Tree — Phase 10 */}
          {result.roadmap_tree && (
            <AdvisorRoadmapTree
              roadmapTree={result.roadmap_tree}
              roadmapSummary={result.roadmap_summary}
              collapsedStreams={collapsedStreams}
              setCollapsedStreams={setCollapsedStreams}
              priorityLabel={priorityLabel}
            />
          )}


          {/* Action Plans 7d & 30d */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "16px", marginTop: "1.5rem" }}>

            
            {/* 7 Days Plan */}
            <div className="section-block" style={{ margin: 0 }}>
              <h3 className="section-title" style={{ color: "#8b5cf6" }}>📅 Kế hoạch hành động 7 ngày tới</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "10px" }}>
                {result.action_plan_7d.map((plan, i) => (
                  <div key={i} className="geo-faq-item" style={{ borderLeft: "2px solid #8b5cf6", background: "rgba(255,255,255,0.01)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "6px" }}>
                      <strong style={{ color: "#c4b5fd", fontSize: "13px" }}>{plan.day || `Giai đoạn ${i+1}`}</strong>
                      <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                        {plan.pending_before_count !== undefined && plan.pending_before_count > 0 && (
                          <span className="issue-badge badge-critical" style={{ padding: "2px 6px", fontSize: "10px" }}>Tồn đọng ({plan.pending_before_count})</span>
                        )}
                        {plan.is_recurring && (
                          <span className="issue-badge" style={{ padding: "2px 6px", fontSize: "10px", background: "rgba(139,92,246,0.15)", color: "#c4b5fd", border: "1px solid rgba(139,92,246,0.3)" }}>Lặp lại</span>
                        )}
                        {priorityLabel(plan.priority)}
                      </div>
                    </div>
                    <p style={{ fontSize: "13px", color: "var(--text-h)", margin: "6px 0" }}>{plan.task}</p>
                    {plan.history_note && (
                      <p style={{ fontSize: "11px", color: "#fcd34d", margin: "4px 0", fontStyle: "italic" }}>
                        ⚠️ {plan.history_note}
                      </p>
                    )}
                    {plan.pattern_note && (
                      <p style={{ fontSize: "11px", color: "#a78bfa", margin: "4px 0", fontStyle: "italic" }}>
                        💡 {plan.pattern_note}
                      </p>
                    )}
                    <p style={{ fontSize: "11px", color: "var(--text-dim)", margin: 0 }}>
                      ⚡ <strong>Tác động:</strong> {plan.impact}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* 30 Days Plan */}
            <div className="section-block" style={{ margin: 0 }}>
              <h3 className="section-title" style={{ color: "#06b6d4" }}>📅 Chiến lược tăng trưởng 30 ngày</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "10px" }}>
                {result.action_plan_30d.map((plan, i) => (
                  <div key={i} className="geo-faq-item" style={{ borderLeft: "2px solid #06b6d4", background: "rgba(255,255,255,0.01)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "6px" }}>
                      <strong style={{ color: "#94a3b8", fontSize: "13px" }}>{plan.week || `Tuần ${i+1}`}</strong>
                      <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                        {plan.pending_before_count !== undefined && plan.pending_before_count > 0 && (
                          <span className="issue-badge badge-critical" style={{ padding: "2px 6px", fontSize: "10px" }}>Tồn đọng ({plan.pending_before_count})</span>
                        )}
                        {plan.is_recurring && (
                          <span className="issue-badge" style={{ padding: "2px 6px", fontSize: "10px", background: "rgba(139,92,246,0.15)", color: "#c4b5fd", border: "1px solid rgba(139,92,246,0.3)" }}>Lặp lại</span>
                        )}
                        {priorityLabel(plan.priority)}
                      </div>
                    </div>
                    <p style={{ fontSize: "13px", color: "var(--text-h)", margin: "6px 0" }}>{plan.task}</p>
                    {plan.history_note && (
                      <p style={{ fontSize: "11px", color: "#fcd34d", margin: "4px 0", fontStyle: "italic" }}>
                        ⚠️ {plan.history_note}
                      </p>
                    )}
                    {plan.pattern_note && (
                      <p style={{ fontSize: "11px", color: "#a78bfa", margin: "4px 0", fontStyle: "italic" }}>
                        💡 {plan.pattern_note}
                      </p>
                    )}
                    <p style={{ fontSize: "11px", color: "var(--text-dim)", margin: 0 }}>
                      ⚡ <strong>Tác động:</strong> {plan.impact}
                    </p>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Sources and Data Coverage Status */}
          <div className="section-block" style={{ marginTop: "1.5rem" }}>
            <h3 className="section-title" style={{ fontSize: "15px" }}>📊 Bản đồ phủ dữ liệu &amp; Mức độ tin cậy</h3>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px", background: "rgba(255,255,255,0.02)", borderRadius: "8px", border: "1px solid var(--border)", margin: "10px 0" }}>
              <span style={{ fontSize: "13px" }}>Website chẩn đoán: <strong>{result.site_url}</strong></span>
              <span style={{ fontSize: "13px" }}>
                Độ tin cậy cố vấn:{" "}
                <strong style={{ color: result.confidence === "high" ? "#10b981" : result.confidence === "medium" ? "#3b82f6" : "#ef4444" }}>
                  {result.confidence.toUpperCase()} ({result.confidence_score}%)
                </strong>
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "8px" }}>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Google Search Console</span>
                {sourceStatusLabel(result.source_status.gsc)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Google Analytics 4</span>
                {sourceStatusLabel(result.source_status.ga4)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>SERP Live</span>
                {sourceStatusLabel(result.source_status.serp)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Technical SEO</span>
                {sourceStatusLabel(result.source_status.technical)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Core Web Vitals</span>
                {sourceStatusLabel(result.source_status.cwv)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Schema.org validation</span>
                {sourceStatusLabel(result.source_status.schema)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Link hỏng</span>
                {sourceStatusLabel(result.source_status.broken)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Thứ hạng theo dõi</span>
                {sourceStatusLabel(result.source_status.rank_tracking)}
              </div>
              <div style={{ background: "var(--surface2)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>Lịch sử hệ thống</span>
                {sourceStatusLabel(result.source_status.usage)}
              </div>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
export default AiAdvisor;
