import React from "react";
import type { RoadmapTree } from "../types/advisor";

interface AdvisorRoadmapTreeProps {
  roadmapTree: RoadmapTree;
  roadmapSummary?: string | null;
  collapsedStreams: Record<string, boolean>;
  setCollapsedStreams: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
  priorityLabel: (pri: string) => React.ReactNode;
}

export function AdvisorRoadmapTree({
  roadmapTree,
  roadmapSummary,
  collapsedStreams,
  setCollapsedStreams,
  priorityLabel
}: AdvisorRoadmapTreeProps) {
  const streamPriorityBadge = (prio: string) => {
    if (prio === "high") return <span className="issue-badge badge-critical">Ưu tiên cao</span>;
    if (prio === "medium") return <span className="issue-badge badge-warning">Trung bình</span>;
    return <span className="issue-badge badge-suggestion">Thấp</span>;
  };

  return (
    <div className="section-block" style={{ marginTop: "1.5rem" }}>
      <h3 className="section-title" style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--primary)" }}>
        🗺️ Cây lộ trình hành động trực quan (Action Roadmap)
      </h3>
      
      {roadmapSummary && (
        <div className="mock-warning-banner" style={{ 
          marginTop: "10px", 
          borderColor: "rgba(139, 92, 246, 0.3)", 
          background: "rgba(139, 92, 246, 0.05)", 
          color: "#e9d5ff",
          padding: "12px",
          fontSize: "13px",
          lineHeight: "1.5",
          display: "flex",
          alignItems: "flex-start",
          gap: "10px"
        }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#c084fc" strokeWidth="2.5" style={{ flexShrink: 0, marginTop: "2px" }}>
            <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
            <path d="M12 16v-4" />
            <path d="M12 8h.01" />
          </svg>
          <div style={{ fontSize: "13px", lineHeight: "1.5" }}>
            <strong>Tóm tắt lộ trình:</strong> {roadmapSummary}
          </div>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "1rem" }}>
        {roadmapTree.streams.map((stream) => {
          const isCollapsed = collapsedStreams[stream.id] ?? false;

          return (
            <div 
              key={stream.id} 
              style={{ 
                background: "rgba(255, 255, 255, 0.01)", 
                border: "1px solid var(--border)", 
                borderRadius: "12px", 
                overflow: "hidden" 
              }}
            >
              {/* Stream Header */}
              <div 
                onClick={() => setCollapsedStreams(prev => ({ ...prev, [stream.id]: !isCollapsed }))}
                style={{ 
                  padding: "14px 18px", 
                  background: "rgba(255, 255, 255, 0.02)", 
                  display: "flex", 
                  justifyContent: "space-between", 
                  alignItems: "center", 
                  cursor: "pointer",
                  userSelect: "none"
                }}
              >
                <div style={{ paddingRight: "12px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                    <h4 style={{ margin: 0, fontSize: "15px", color: "var(--text-h)", fontWeight: "700" }}>
                      {stream.title}
                    </h4>
                    {streamPriorityBadge(stream.priority)}
                    <span style={{ fontSize: "11px", color: "var(--text-dim)" }}>
                      (Điểm lực: {stream.max_score})
                    </span>
                  </div>
                  <p style={{ margin: "4px 0 0 0", fontSize: "12px", color: "var(--text-dim)", lineHeight: "1.4" }}>
                    {stream.description}
                  </p>
                </div>
                <div style={{ fontSize: "12px", color: "var(--text-dim)", flexShrink: 0 }}>
                  {isCollapsed ? "▼ Mở rộng" : "▲ Thu gọn"}
                </div>
              </div>

              {/* Stream Children Tasks Timeline */}
              {!isCollapsed && (
                <div style={{ padding: "18px", background: "rgba(0,0,0,0.15)", borderTop: "1px solid var(--border)" }}>
                  <div style={{ 
                    position: "relative", 
                    paddingLeft: "20px", 
                    borderLeft: "2px solid rgba(139, 92, 246, 0.2)",
                    marginLeft: "10px"
                  }}>
                    {stream.children.map((task, idx) => {
                      return (
                        <div 
                          key={task.id} 
                          style={{ 
                            position: "relative", 
                            marginBottom: idx === stream.children.length - 1 ? 0 : "20px" 
                          }}
                        >
                          {/* Timeline Node Bullet */}
                          <div style={{ 
                            position: "absolute", 
                            left: "-27px", 
                            top: "6px", 
                            width: "12px", 
                            height: "12px", 
                            borderRadius: "50%", 
                            background: task.priority === "high" ? "#ef4444" : (task.priority === "medium" ? "#06b6d4" : "#8b5cf6"),
                            border: "3px solid #090514",
                            boxShadow: task.priority === "high" ? "0 0 8px #ef4444" : "0 0 8px #06b6d4"
                          }} />

                          {/* Task Card Body */}
                          <div style={{ 
                            background: "rgba(255, 255, 255, 0.02)", 
                            border: "1px solid var(--border)", 
                            borderRadius: "8px", 
                            padding: "14px" 
                          }}>
                            {/* Task Meta Row */}
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px", marginBottom: "8px" }}>
                              <span style={{ 
                                fontSize: "11px", 
                                fontWeight: "700", 
                                color: "var(--cyan)", 
                                background: "rgba(6, 182, 212, 0.1)", 
                                padding: "2px 8px", 
                                borderRadius: "4px" 
                              }}>
                                {task.phase === "7d" ? `[7 Ngày] ${task.day || "Kế hoạch"}` : `[30 Ngày] ${task.week || "Kế hoạch"}`}
                              </span>
                              
                              <div style={{ display: "flex", gap: "4px", alignItems: "center", flexWrap: "wrap" }}>
                                {task.is_recurring && (
                                  <span className="issue-badge" style={{ background: "rgba(139, 92, 246, 0.15)", color: "#c4b5fd", border: "1px solid rgba(139, 92, 246, 0.2)", padding: "1px 5px", fontSize: "10px" }}>🔁 Lặp lại</span>
                                )}
                                {task.pending_before_count > 0 && (
                                  <span className="issue-badge badge-critical" style={{ padding: "1px 5px", fontSize: "10px" }}>⏳ Tồn đọng ({task.pending_before_count} lần)</span>
                                )}
                                {task.pattern_related && (
                                  <span className="issue-badge" style={{ background: "rgba(245, 158, 11, 0.15)", color: "#fcd34d", border: "1px solid rgba(245, 158, 11, 0.2)", padding: "1px 5px", fontSize: "10px" }}>💡 Mẫu: {task.pattern_label}</span>
                                )}
                                {task.has_measured_delta_before && (
                                  <span className="issue-badge badge-suggestion" style={{ padding: "1px 5px", fontSize: "10px" }}>📈 Đã có hiệu quả</span>
                                )}
                                {priorityLabel(task.priority)}
                              </div>
                            </div>

                            {/* Task Text */}
                            <p style={{ margin: "6px 0", fontSize: "13px", fontWeight: "600", color: "var(--text-h)" }}>
                              {task.task}
                            </p>

                            {/* Stream Group Reason explanation */}
                            <div style={{ fontSize: "11px", color: "var(--text-dim)", fontStyle: "italic", marginBottom: "6px" }}>
                              🎯 {task.stream_reason}
                            </div>

                            {/* Priority Reasons Bullet list */}
                            {task.priority_reasons && task.priority_reasons.length > 0 && (
                              <div style={{ 
                                marginTop: "8px", 
                                padding: "8px 12px", 
                                background: "rgba(0,0,0,0.1)", 
                                borderRadius: "6px", 
                                border: "1px solid rgba(255, 255, 255, 0.03)" 
                              }}>
                                <div style={{ fontSize: "11px", fontWeight: "700", color: "#a78bfa", marginBottom: "4px" }}>
                                  🔍 Cơ sở xếp thứ tự ưu tiên:
                                </div>
                                <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "11px", color: "var(--text-dim)", lineHeight: "1.4" }}>
                                  {task.priority_reasons.map((reason, rIdx) => (
                                    <li key={rIdx}>{reason}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Historical Context Notes */}
                            {(task.history_note || task.pattern_note || task.outcome_note) && (
                              <div style={{ display: "flex", flexDirection: "column", gap: "4px", marginTop: "8px", borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: "8px" }}>
                                {task.history_note && (
                                  <p style={{ fontSize: "11px", color: "#fcd34d", margin: 0 }}>
                                    ⚠️ <strong>Lịch sử:</strong> {task.history_note}
                                  </p>
                                )}
                                {task.pattern_note && (
                                  <p style={{ fontSize: "11px", color: "#c084fc", margin: 0 }}>
                                    💡 <strong>Mẫu lặp:</strong> {task.pattern_note}
                                  </p>
                                )}
                                {task.outcome_note && (
                                  <p style={{ fontSize: "11px", color: "#34d399", margin: 0 }}>
                                    📈 <strong>Số liệu cũ:</strong> {task.outcome_note}
                                  </p>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
