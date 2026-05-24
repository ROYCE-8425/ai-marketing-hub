/**
 * Auth utilities — token management, authenticated fetch, user info.
 *
 * Stores access + refresh tokens in localStorage.
 * Provides authFetch() wrapper that auto-attaches Authorization header
 * and handles token refresh on 401.
 */

import { API_BASE } from "./apiConfig";

// ── Storage keys ────────────────────────────────────────────────────────────

const ACCESS_TOKEN_KEY = "amh_access_token";
const REFRESH_TOKEN_KEY = "amh_refresh_token";
const USER_KEY = "amh_user";

// ── Token storage ───────────────────────────────────────────────────────────

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

// ── User storage ────────────────────────────────────────────────────────────

export interface AuthUser {
  id: number;
  email: string;
  full_name: string;
  role: "admin" | "editor" | "viewer";
  is_active: boolean;
  created_at: string;
  last_login?: string | null;
}

export function setStoredUser(user: AuthUser): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

// ── Auth check ──────────────────────────────────────────────────────────────

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

// ── Decode JWT payload (without verification) ───────────────────────────────

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const payload = atob(parts[1].replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(payload);
  } catch {
    return null;
  }
}

export function getCurrentUser(): AuthUser | null {
  // Prefer stored user object (has full info)
  const stored = getStoredUser();
  if (stored) return stored;

  // Fallback: decode JWT
  const token = getAccessToken();
  if (!token) return null;

  const payload = decodeJwtPayload(token);
  if (!payload) return null;

  return {
    id: Number(payload.sub),
    email: payload.email as string,
    full_name: (payload.full_name as string) || (payload.email as string),
    role: (payload.role as "admin" | "editor" | "viewer") || "viewer",
    is_active: true,
    created_at: "",
  };
}

// ── Token refresh ───────────────────────────────────────────────────────────

let refreshPromise: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  // Deduplicate concurrent refresh attempts
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;

    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) {
        clearTokens();
        return false;
      }

      const data = await res.json();
      setTokens(data.access_token, data.refresh_token);
      if (data.user) setStoredUser(data.user);
      return true;
    } catch {
      clearTokens();
      return false;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

// ── Authenticated fetch wrapper ─────────────────────────────────────────────

export async function authFetch(
  url: string,
  options: RequestInit = {},
): Promise<Response> {
  const token = getAccessToken();

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Default Content-Type for JSON bodies
  if (options.body && typeof options.body === "string" && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  let res = await fetch(url, { ...options, headers });

  // If 401, try refreshing the token once
  if (res.status === 401 && token) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      const newToken = getAccessToken();
      if (newToken) {
        headers["Authorization"] = `Bearer ${newToken}`;
      }
      res = await fetch(url, { ...options, headers });
    }
  }

  return res;
}

// ── Logout ──────────────────────────────────────────────────────────────────

export async function logout(): Promise<void> {
  const refreshToken = getRefreshToken();
  if (refreshToken) {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } catch {
      // Ignore — clear tokens anyway
    }
  }
  clearTokens();
}
