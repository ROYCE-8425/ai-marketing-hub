/**
 * AuthPage — Login / Register with dark glassmorphism design.
 *
 * Center-card layout (no sidebar). Vietnamese UI text.
 * Toggle between "Đăng nhập" and "Đăng ký" tabs.
 */

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE } from "../lib/apiConfig";
import { setTokens, setStoredUser } from "../lib/auth";
import type { AuthUser } from "../lib/auth";
import "./AuthPage.css";

type AuthTab = "login" | "register";

// Google Client ID from env or hardcoded for now
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

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

  // ── Google Sign-In ──────────────────────────────────────────────────────

  const handleGoogleCallback = useCallback(async (response: { credential: string }) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/auth/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credential: response.credential }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `Lỗi ${res.status}`);
      handleAuthSuccess(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi đăng nhập Google");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return;

    // Load Google Identity Services script
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => {
      // @ts-expect-error -- Google GSI global
      window.google?.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleCallback,
      });
      // Render button into container
      const container = document.getElementById("google-signin-btn");
      if (container) {
        // @ts-expect-error -- Google GSI global
        window.google?.accounts.id.renderButton(container, {
          theme: "outline",
          size: "large",
          width: 320,
          text: "signin_with",
          locale: "vi",
        });
      }
    };
    document.head.appendChild(script);

    return () => {
      // Cleanup
      try { document.head.removeChild(script); } catch { /* ignore */ }
    };
  }, [handleGoogleCallback, tab]);

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
          <>
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

          {/* Google Sign-In divider + button */}
          <div className="auth-divider">
            <span className="auth-divider-line" />
            <span className="auth-divider-text">hoặc</span>
            <span className="auth-divider-line" />
          </div>
          {GOOGLE_CLIENT_ID ? (
            <div className="google-signin-wrapper">
              <div id="google-signin-btn" />
            </div>
          ) : (
            <button
              type="button"
              className="google-btn"
              onClick={() => setError("Chưa cấu hình Google Client ID. Liên hệ admin.")}
            >
              <svg width="18" height="18" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
              </svg>
              Đăng nhập với Google
            </button>
          )}
          </>
        )}

        {/* Register form */}
        {tab === "register" && (
          <>
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

          {/* Google Sign-In for register tab */}
          <div className="auth-divider">
            <span className="auth-divider-line" />
            <span className="auth-divider-text">hoặc</span>
            <span className="auth-divider-line" />
          </div>
          {GOOGLE_CLIENT_ID ? (
            <div className="google-signin-wrapper">
              <div id="google-signin-btn" />
            </div>
          ) : (
            <button
              type="button"
              className="google-btn"
              onClick={() => setError("Chưa cấu hình Google Client ID. Liên hệ admin.")}
            >
              <svg width="18" height="18" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
              </svg>
              Đăng ký với Google
            </button>
          )}
          </>
        )}
      </div>
    </div>
  );
}
