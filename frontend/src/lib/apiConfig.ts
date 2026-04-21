/**
 * Centralized API base URL configuration.
 * Reads VITE_API_BASE_URL from environment (set in .env.local).
 * Falls back to localhost for local development.
 *
 * NOTE: All backend routers use prefix="/api", so the base URL
 * must include the /api path segment.
 */
export const API_BASE: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, "") ??
  "http://localhost:8000/api";
