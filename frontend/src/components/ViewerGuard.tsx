/**
 * ViewerGuard — Show restricted view for non-admin users.
 *
 * Wraps children content. If user role is "viewer", shows a
 * "no data" placeholder instead of the actual content.
 */

import { getCurrentUser } from "../lib/auth";

interface ViewerGuardProps {
  children: React.ReactNode;
  /** Custom message for viewers */
  message?: string;
}

export function ViewerGuard({ children, message }: ViewerGuardProps) {
  const user = getCurrentUser();

  // Admin and editor can see everything
  if (user?.role === "admin" || user?.role === "editor") {
    return <>{children}</>;
  }

  // Viewer sees restricted placeholder
  return (
    <div className="viewer-guard">
      <div className="viewer-guard-icon">🔒</div>
      <h3 className="viewer-guard-title">Quyền truy cập hạn chế</h3>
      <p className="viewer-guard-msg">
        {message || "Bạn đang sử dụng tài khoản Viewer. Liên hệ admin để được nâng cấp quyền truy cập đầy đủ."}
      </p>
      <p className="viewer-guard-hint">
        Tài khoản: <strong>{user?.email}</strong> · Vai trò: <strong>{user?.role || "viewer"}</strong>
      </p>
    </div>
  );
}
