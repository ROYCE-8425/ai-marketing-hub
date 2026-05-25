/**
 * UserMenu — Dropdown in the topbar showing user info + actions.
 *
 * - Avatar (initial letter circle) + name
 * - Dropdown: Hồ sơ, Cài đặt, Quản lý người dùng (admin), Đăng xuất
 */

import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getCurrentUser, logout } from "../lib/auth";
import type { AuthUser } from "../lib/auth";

export default function UserMenu() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const user: AuthUser | null = getCurrentUser();

  // Close on outside click — must be called before any early return
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  if (!user) return null;

  const initial = (user.full_name || user.email)[0].toUpperCase();

  // Role label & color
  const roleMap: Record<string, { label: string; color: string }> = {
    admin: { label: "Admin", color: "#8b5cf6" },
    editor: { label: "Editor", color: "#06b6d4" },
    viewer: { label: "Viewer", color: "#64748b" },
  };
  const role = roleMap[user.role] || roleMap.viewer;

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="user-menu-wrap" ref={menuRef}>
      <button
        className="user-menu-trigger"
        onClick={() => setOpen(!open)}
        aria-label="Menu người dùng"
      >
        <div className="user-avatar" style={{ background: `linear-gradient(135deg, ${role.color}, ${role.color}88)` }}>
          {initial}
        </div>
        <span className="user-menu-name">{user.full_name || user.email}</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className={`user-menu-chevron ${open ? "user-menu-chevron-open" : ""}`}>
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>

      {open && (
        <div className="user-menu-dropdown">
          {/* User info header */}
          <div className="user-menu-header">
            <div className="user-menu-email">{user.email}</div>
            <span className="user-menu-role-badge" style={{ background: `${role.color}22`, color: role.color, borderColor: `${role.color}44` }}>
              {role.label}
            </span>
          </div>

          <div className="user-menu-divider" />

          {/* Menu items */}
          <button className="user-menu-item" onClick={() => { setOpen(false); alert("Tính năng Hồ sơ sẽ được cập nhật sớm!"); }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            Hồ sơ
          </button>

          <button className="user-menu-item" onClick={() => { setOpen(false); alert("Tính năng Cài đặt sẽ được cập nhật sớm!"); }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
            </svg>
            Cài đặt
          </button>

          {user.role === "admin" && (
            <button className="user-menu-item" onClick={() => { setOpen(false); navigate("/admin/users"); }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
              Quản lý người dùng
            </button>
          )}

          <div className="user-menu-divider" />

          <button className="user-menu-item user-menu-item-danger" onClick={handleLogout}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Đăng xuất
          </button>
        </div>
      )}
    </div>
  );
}
