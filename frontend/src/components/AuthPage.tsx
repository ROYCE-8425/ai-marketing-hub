/**
 * AuthPage — Login / Register with dark glassmorphism design.
 *
 * Center-card layout (no sidebar). Vietnamese UI text.
 * Toggle between "Đăng nhập" and "Đăng ký" tabs.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE } from "../lib/apiConfig";
import { setTokens, setStoredUser } from "../lib/auth";
import type { AuthUser } from "../lib/auth";
import "./AuthPage.css";

type AuthTab = "login" | "register";

export default function AuthPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState<AuthTab>("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Login fields
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Register fields
  const [regName, setRegName] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regConfirm, setRegConfirm] = useState("");

  const switchTab = (t: AuthTab) => {
    setTab(t);
    setError(null);
    setSuccess(null);
  };

  const handleAuthSuccess = (data: {
    access_token: string;
    refresh_token: string;
    user: AuthUser;
  }) => {
    setTokens(data.access_token, data.refresh_token);
    setStoredUser(data.user);
    navigate("/");
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginEmail.trim() || !loginPassword.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: loginEmail.trim().toLowerCase(),
          password: loginPassword,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || `Lỗi ${res.status}`);
      }

      handleAuthSuccess(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi kết nối máy chủ");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!regName.trim() || !regEmail.trim() || !regPassword || !regConfirm) return;

    if (regPassword !== regConfirm) {
      setError("Mật khẩu xác nhận không khớp");
      return;
    }
    if (regPassword.length < 6) {
      setError("Mật khẩu phải có ít nhất 6 ký tự");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: regEmail.trim().toLowerCase(),
          full_name: regName.trim(),
          password: regPassword,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || `Lỗi ${res.status}`);
      }

      handleAuthSuccess(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi kết nối máy chủ");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* Animated background blobs */}
      <div className="auth-blob auth-blob-1" />
      <div className="auth-blob auth-blob-2" />
      <div className="auth-blob auth-blob-3" />

      <div className="auth-card">
        {/* Brand */}
        <div className="auth-brand">
          <div className="auth-logo">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="url(#auth-lg)" strokeWidth="2.5">
              <defs>
                <linearGradient id="auth-lg" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#8b5cf6" />
                  <stop offset="100%" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
              <circle cx="12" cy="12" r="10" />
              <path d="M8 12l3 3 5-6" />
            </svg>
          </div>
          <h1 className="auth-app-name">AI Marketing Hub</h1>
          <p className="auth-app-desc">Nền tảng SEO & Marketing thông minh</p>
        </div>

        {/* Tabs */}
        <div className="auth-tabs">
          <button
            className={`auth-tab ${tab === "login" ? "auth-tab-active" : ""}`}
            onClick={() => switchTab("login")}
            type="button"
          >
            Đăng nhập
          </button>
          <button
            className={`auth-tab ${tab === "register" ? "auth-tab-active" : ""}`}
            onClick={() => switchTab("register")}
            type="button"
          >
            Đăng ký
          </button>
        </div>

        {/* Error / Success */}
        {error && (
          <div className="auth-error">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
            </svg>
            {error}
          </div>
        )}
        {success && (
          <div className="auth-success">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
            </svg>
            {success}
          </div>
        )}

        {/* Login form */}
        {tab === "login" && (
          <form className="auth-form" onSubmit={handleLogin} noValidate key="login">
            <div className="auth-field">
              <label className="auth-label" htmlFor="login-email">Email</label>
              <input
                id="login-email"
                className="auth-input"
                type="email"
                placeholder="email@example.com"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>
            <div className="auth-field">
              <label className="auth-label" htmlFor="login-password">Mật khẩu</label>
              <input
                id="login-password"
                className="auth-input"
                type="password"
                placeholder="••••••••"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>
            <button
              type="submit"
              className="auth-submit"
              disabled={loading || !loginEmail.trim() || !loginPassword.trim()}
            >
              {loading ? (
                <span className="btn-spinner" aria-label="Loading" />
              ) : (
                "Đăng nhập"
              )}
            </button>
            <div className="auth-footer">
              <button type="button" className="auth-footer-link" onClick={() => alert("Tính năng đặt lại mật khẩu sẽ được cập nhật sớm!")}>
                Quên mật khẩu?
              </button>
            </div>
          </form>
        )}

        {/* Register form */}
        {tab === "register" && (
          <form className="auth-form" onSubmit={handleRegister} noValidate key="register">
            <div className="auth-field">
              <label className="auth-label" htmlFor="reg-name">Họ tên</label>
              <input
                id="reg-name"
                className="auth-input"
                type="text"
                placeholder="Nguyễn Văn A"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                autoComplete="name"
                required
              />
            </div>
            <div className="auth-field">
              <label className="auth-label" htmlFor="reg-email">Email</label>
              <input
                id="reg-email"
                className="auth-input"
                type="email"
                placeholder="email@example.com"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>
            <div className="auth-field">
              <label className="auth-label" htmlFor="reg-password">Mật khẩu</label>
              <input
                id="reg-password"
                className="auth-input"
                type="password"
                placeholder="Tối thiểu 6 ký tự"
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
                autoComplete="new-password"
                minLength={6}
                required
              />
            </div>
            <div className="auth-field">
              <label className="auth-label" htmlFor="reg-confirm">Xác nhận mật khẩu</label>
              <input
                id="reg-confirm"
                className="auth-input"
                type="password"
                placeholder="Nhập lại mật khẩu"
                value={regConfirm}
                onChange={(e) => setRegConfirm(e.target.value)}
                autoComplete="new-password"
                required
              />
            </div>
            <button
              type="submit"
              className="auth-submit"
              disabled={loading || !regName.trim() || !regEmail.trim() || !regPassword || !regConfirm}
            >
              {loading ? (
                <span className="btn-spinner" aria-label="Loading" />
              ) : (
                "Đăng ký"
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
