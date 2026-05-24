/**
 * UserManagement — Admin panel for managing users.
 *
 * Table: Email, Họ tên, Vai trò, Trạng thái, Ngày tạo, Hành động
 * Role badges: Admin (purple), Editor (cyan), Viewer (gray)
 * Actions: Change role, Deactivate
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authFetch, getCurrentUser } from "../lib/auth";
import { API_BASE } from "../lib/apiConfig";

interface ManagedUser {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string | null;
}

export default function UserManagement() {
  const navigate = useNavigate();
  const currentUser = getCurrentUser();
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  // Redirect non-admins
  useEffect(() => {
    if (!currentUser || currentUser.role !== "admin") {
      navigate("/");
    }
  }, [currentUser, navigate]);

  // Fetch users
  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await authFetch(`${API_BASE}/auth/users`);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Lỗi ${res.status}`);
      }
      setUsers(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi tải danh sách");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Change role
  const handleRoleChange = async (userId: number, newRole: string) => {
    setActionLoading(userId);
    try {
      const res = await authFetch(`${API_BASE}/auth/users/${userId}/role`, {
        method: "PUT",
        body: JSON.stringify({ role: newRole }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Lỗi ${res.status}`);
      }
      await fetchUsers();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Lỗi thay đổi vai trò");
    } finally {
      setActionLoading(null);
    }
  };

  // Deactivate user
  const handleDeactivate = async (userId: number, email: string) => {
    if (!confirm(`Bạn có chắc muốn vô hiệu hóa tài khoản ${email}?`)) return;

    setActionLoading(userId);
    try {
      const res = await authFetch(`${API_BASE}/auth/users/${userId}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Lỗi ${res.status}`);
      }
      await fetchUsers();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Lỗi vô hiệu hóa");
    } finally {
      setActionLoading(null);
    }
  };

  // Role badge styles
  const roleBadge = (role: string) => {
    const map: Record<string, { bg: string; color: string; label: string }> = {
      admin: { bg: "rgba(22,163,74,0.15)", color: "#16a34a", label: "Admin" },
      editor: { bg: "rgba(6,182,212,0.15)", color: "#059669", label: "Editor" },
      viewer: { bg: "rgba(100,116,139,0.15)", color: "#94a3b8", label: "Viewer" },
    };
    const r = map[role] || map.viewer;
    return (
      <span style={{
        background: r.bg,
        color: r.color,
        padding: "3px 10px",
        borderRadius: "99px",
        fontSize: "12px",
        fontWeight: 600,
        border: `1px solid ${r.color}33`,
      }}>
        {r.label}
      </span>
    );
  };

  const formatDate = (iso: string) => {
    try {
      return new Date(iso).toLocaleDateString("vi-VN", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    } catch {
      return iso;
    }
  };

  if (!currentUser || currentUser.role !== "admin") return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "16px",
      }}>
        <h2 style={{
          fontSize: "18px",
          fontWeight: 700,
          color: "var(--text-h)",
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}>
          👥 Quản lý người dùng
        </h2>
        <button
          className="reset-btn"
          onClick={fetchUsers}
          disabled={loading}
        >
          🔄 Làm mới
        </button>
      </div>

      {error && (
        <div className="error-msg" role="alert">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{
          textAlign: "center",
          padding: "40px",
          color: "var(--text-dim)",
        }}>
          <span className="btn-spinner" style={{ width: "24px", height: "24px", borderWidth: "3px" }} />
          <p style={{ marginTop: "12px" }}>Đang tải...</p>
        </div>
      ) : (
        <div className="result-panel" style={{ padding: "0", overflow: "hidden" }}>
          <div style={{ overflowX: "auto" }}>
            <table className="serp-table" style={{ minWidth: "700px" }}>
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Họ tên</th>
                  <th>Vai trò</th>
                  <th>Trạng thái</th>
                  <th>Ngày tạo</th>
                  <th>Hành động</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} style={{ opacity: u.is_active ? 1 : 0.5 }}>
                    <td style={{ fontWeight: 500, color: "var(--text-h)" }}>{u.email}</td>
                    <td>{u.full_name}</td>
                    <td>{roleBadge(u.role)}</td>
                    <td>
                      <span style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px",
                        fontSize: "12px",
                        color: u.is_active ? "var(--green)" : "var(--red)",
                      }}>
                        <span style={{
                          width: "6px",
                          height: "6px",
                          borderRadius: "50%",
                          background: u.is_active ? "var(--green)" : "var(--red)",
                          boxShadow: u.is_active ? "0 0 6px var(--green)" : "0 0 6px var(--red)",
                        }} />
                        {u.is_active ? "Hoạt động" : "Vô hiệu"}
                      </span>
                    </td>
                    <td style={{ fontSize: "13px", color: "var(--text-dim)" }}>{formatDate(u.created_at)}</td>
                    <td>
                      {u.id !== currentUser.id && u.is_active ? (
                        <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                          <select
                            value={u.role}
                            onChange={(e) => handleRoleChange(u.id, e.target.value)}
                            disabled={actionLoading === u.id}
                            style={{
                              background: "var(--surface2)",
                              border: "1px solid var(--border)",
                              borderRadius: "6px",
                              color: "var(--text-h)",
                              padding: "4px 8px",
                              fontSize: "12px",
                              fontFamily: "'DM Sans', sans-serif",
                              cursor: "pointer",
                            }}
                          >
                            <option value="viewer">Viewer</option>
                            <option value="editor">Editor</option>
                            <option value="admin">Admin</option>
                          </select>
                          <button
                            onClick={() => handleDeactivate(u.id, u.email)}
                            disabled={actionLoading === u.id}
                            style={{
                              background: "rgba(239,68,68,0.1)",
                              border: "1px solid rgba(239,68,68,0.3)",
                              borderRadius: "6px",
                              color: "var(--red)",
                              padding: "4px 10px",
                              fontSize: "12px",
                              fontWeight: 600,
                              cursor: "pointer",
                              fontFamily: "'DM Sans', sans-serif",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {actionLoading === u.id ? "..." : "Vô hiệu hóa"}
                          </button>
                        </div>
                      ) : (
                        <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>
                          {u.id === currentUser.id ? "Bạn" : "—"}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
