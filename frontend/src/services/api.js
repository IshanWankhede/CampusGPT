/**
 * Centralized API client for CampusGPT.
 *
 * Provides:
 * - Single-flight token refresh with cross-tab Web Locks API synchronization
 * - In-memory promise lock fallback for environments without navigator.locks
 * - Post-lock storage re-reading to prevent redundant refresh calls across tabs
 * - Automatic 401 retry interceptor (maximum 1 retry)
 * - Safe exclusion of the refresh endpoint from recursive retry
 * - Normalized JSON error parsing for strings and Pydantic validation arrays
 * - Session state listeners for cross-component synchronisation
 */

const STORAGE_KEY = "campusgpt.auth";
const REFRESH_LOCK_NAME = "campusgpt_refresh_lock";

let inMemoryRefreshPromise = null;
const sessionListeners = new Set();

/**
 * Register a listener invoked when session is updated or cleared.
 * Returns an unregister function.
 */
export function subscribeSession(listener) {
  sessionListeners.add(listener);
  return () => sessionListeners.delete(listener);
}

function notifySessionUpdated(session) {
  sessionListeners.forEach((fn) => {
    try {
      fn({ type: "UPDATE", session });
    } catch {
      // Ignore listener error
    }
  });
}

function notifySessionCleared(reason) {
  sessionListeners.forEach((fn) => {
    try {
      fn({ type: "CLEAR", reason });
    } catch {
      // Ignore listener error
    }
  });
}

export function getStoredSession() {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveStoredSession(session) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  } catch {
    // Ignore storage write errors (e.g. private mode quota)
  }
}

export function clearStoredSession() {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignore storage removal errors
  }
}

/**
 * Low-level call to POST /api/v1/auth/refresh.
 * Never catches 401 itself to prevent recursive loops.
 */
async function callRefreshEndpoint(refreshToken) {
  const response = await fetch("/api/v1/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((d) => d.msg || JSON.stringify(d)).join(", ")
      : payload.detail || "Refresh token expired or revoked";
    const error = new Error(detail);
    error.status = response.status;
    error.data = payload;
    throw error;
  }

  return payload;
}

/**
 * Coordinates single-flight refresh across multiple browser tabs and threads.
 *
 * 1. Uses navigator.locks (Web Locks API) where available.
 * 2. Re-reads localStorage after acquiring the lock; if another tab already
 *    rotated the token, adopts that new token without calling the backend.
 * 3. Falls back to in-memory promise lock where Web Locks is unsupported.
 */
export async function executeRefresh(providedRefreshToken) {
  // Case A: Web Locks API is supported
  if (typeof navigator !== "undefined" && navigator.locks && typeof navigator.locks.request === "function") {
    return navigator.locks.request(REFRESH_LOCK_NAME, async () => {
      // Re-read storage after obtaining the lock
      const freshStored = getStoredSession();
      if (freshStored?.refresh_token && providedRefreshToken && freshStored.refresh_token !== providedRefreshToken) {
        // Another tab already completed rotation; return the latest stored session
        return freshStored;
      }

      const activeRefreshToken = freshStored?.refresh_token || providedRefreshToken;
      if (!activeRefreshToken) {
        throw new Error("No refresh token available for session renewal");
      }

      const tokenResponse = await callRefreshEndpoint(activeRefreshToken);
      const merged = { ...freshStored, ...tokenResponse };
      saveStoredSession(merged);
      notifySessionUpdated(merged);
      return merged;
    });
  }

  // Case B: In-memory fallback
  if (!inMemoryRefreshPromise) {
    inMemoryRefreshPromise = (async () => {
      try {
        const freshStored = getStoredSession();
        const activeRefreshToken = freshStored?.refresh_token || providedRefreshToken;
        if (!activeRefreshToken) {
          throw new Error("No refresh token available for session renewal");
        }
        const tokenResponse = await callRefreshEndpoint(activeRefreshToken);
        const merged = { ...freshStored, ...tokenResponse };
        saveStoredSession(merged);
        notifySessionUpdated(merged);
        return merged;
      } finally {
        inMemoryRefreshPromise = null;
      }
    })();
  }
  return inMemoryRefreshPromise;
}

/**
 * Centralized fetch client.
 *
 * - Prepends base URL `/api/v1` for relative paths
 * - Injects `Authorization: Bearer <access_token>`
 * - Automatically retries once on 401 using executeRefresh
 * - Clears session and notifies listeners if refresh fails
 * - Preserves Google OAuth credentials: "include" and Origin headers
 */
export async function apiFetch(path, options = {}) {
  const url = path.startsWith("http")
    ? path
    : path.startsWith("/api/v1")
      ? path
      : `/api/v1${path.startsWith("/") ? "" : "/"}${path}`;

  const isRefreshEndpoint = url.endsWith("/auth/refresh");
  const isAuthLoginOrPublic =
    url.endsWith("/auth/login") ||
    url.endsWith("/auth/register") ||
    url.endsWith("/auth/send-otp") ||
    url.endsWith("/auth/verify-otp") ||
    url.endsWith("/auth/forgot-password") ||
    url.endsWith("/auth/reset-password") ||
    url.endsWith("/auth/google/exchange");

  const stored = getStoredSession();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  // Attach token if authenticated and not already supplied
  if (stored?.access_token && !headers.Authorization && !headers.authorization) {
    headers.Authorization = `Bearer ${stored.access_token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle 401: single-flight refresh & retry at most once
  if (
    response.status === 401 &&
    !options._retry &&
    !isRefreshEndpoint &&
    !isAuthLoginOrPublic
  ) {
    const currentSession = getStoredSession();
    if (currentSession?.refresh_token) {
      try {
        const refreshedSession = await executeRefresh(currentSession.refresh_token);

        // Retry the original request exactly once
        return apiFetch(path, {
          ...options,
          _retry: true,
          headers: {
            ...(options.headers || {}),
            Authorization: `Bearer ${refreshedSession.access_token}`,
          },
        });
      } catch (refreshErr) {
        // Terminal failure: token compromised, expired, or revoked
        clearStoredSession();
        notifySessionCleared(refreshErr.message || "Session expired");
        if (typeof window !== "undefined") {
          const errMsg = encodeURIComponent("Your session has expired. Please sign in again.");
          window.location.href = `/auth?error=${errMsg}`;
        }
        throw refreshErr;
      }
    } else {
      clearStoredSession();
      notifySessionCleared("Authentication required");
      if (typeof window !== "undefined") {
        window.location.href = "/auth";
      }
    }
  }

  // Parse JSON response body
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((item) => item.msg || JSON.stringify(item)).join(", ")
      : payload.detail || payload.message || `Request failed with status ${response.status}`;
    const error = new Error(detail);
    error.status = response.status;
    error.data = payload;
    throw error;
  }

  return payload;
}

