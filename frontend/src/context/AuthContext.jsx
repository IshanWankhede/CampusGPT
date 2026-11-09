import { createContext, useContext, useEffect, useMemo, useState } from "react";

const API_BASE = "/api/v1/auth";
const STORAGE_KEY = "campusgpt.auth";

const AuthContext = createContext(null);

let refreshPromise = null;

async function executeRefresh(refreshToken) {
  if (!refreshPromise) {
    refreshPromise = fetch(`${API_BASE}/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
      .then(async (res) => {
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          throw new Error(data.detail || "Session refresh failed");
        }
        return data;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

async function request(path, options = {}, onSessionUpdate = null, onSessionClear = null) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (
    response.status === 401 &&
    !options._retry &&
    !path.startsWith("/login") &&
    !path.startsWith("/refresh") &&
    !path.startsWith("/register") &&
    !path.startsWith("/logout")
  ) {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY)) || null;
      if (stored?.refresh_token) {
        const nextSession = await executeRefresh(stored.refresh_token);
        const merged = { ...stored, ...nextSession };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
        if (onSessionUpdate) onSessionUpdate(merged);

        return request(
          path,
          {
            ...options,
            _retry: true,
            headers: {
              ...(options.headers || {}),
              Authorization: `Bearer ${nextSession.access_token}`,
            },
          },
          onSessionUpdate,
          onSessionClear,
        );
      }
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      if (onSessionClear) onSessionClear();
    }
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((item) => item.msg).join(", ")
      : payload.detail || "Authentication request failed";
    throw new Error(detail);
  }
  return payload;
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(Boolean(session));

  const authRequest = (path, options) =>
    request(path, options, setSession, () => setSession(null));

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");

    if (code) {
      window.history.replaceState({}, document.title, window.location.pathname);

      authRequest("/google/exchange", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({ code }),
      })
        .then((tokenData) => {
          saveSession(tokenData);
          window.location.href = "/app";
        })
        .catch((error) => {
          setLoading(false);
          window.location.href = `/auth?error=${encodeURIComponent(error.message)}`;
        });
      return;
    }

    if (!session?.access_token) {
      setLoading(false);
      return;
    }

    authRequest("/me", {
      headers: { Authorization: `Bearer ${session.access_token}` },
    })
      .then((user) => setSession((current) => ({ ...current, user })))
      .catch(() => {
        localStorage.removeItem(STORAGE_KEY);
        setSession(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const saveSession = (nextSession) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
    setSession(nextSession);
  };

  const login = async (email, password, college) => {
    const nextSession = await authRequest("/login", {
      method: "POST",
      body: JSON.stringify({ email, password, college }),
    });
    const user = await authRequest("/me", {
      headers: { Authorization: `Bearer ${nextSession.access_token}` },
    });
    saveSession({ ...nextSession, user });
    return user;
  };

  const register = async (fullName, email, password, role, college) => {
    return authRequest("/register", {
      method: "POST",
      body: JSON.stringify({ full_name: fullName, email, password, role, college }),
    });
  };

  const sendOtp = (email, purpose, college) =>
    authRequest("/send-otp", { method: "POST", body: JSON.stringify({ email, purpose, college }) });
  const verifyOtp = (email, otp, purpose) =>
    authRequest("/verify-otp", { method: "POST", body: JSON.stringify({ email, otp, purpose }) });
  const forgotPassword = (email) =>
    authRequest("/forgot-password", { method: "POST", body: JSON.stringify({ email }) });
  const resetPassword = (email, otp, newPassword) =>
    authRequest("/reset-password", {
      method: "POST",
      body: JSON.stringify({ email, otp, new_password: newPassword }),
    });

  const logout = async () => {
    const currentRefresh = session?.refresh_token;
    if (session?.access_token || currentRefresh) {
      await fetch(`${API_BASE}/logout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {}),
        },
        body: JSON.stringify({ refresh_token: currentRefresh || null }),
      }).catch(() => {});
    }
    localStorage.removeItem(STORAGE_KEY);
    setSession(null);
  };

  const logoutAll = async () => {
    if (session?.access_token) {
      await fetch(`${API_BASE}/logout-all`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
      }).catch(() => {});
    }
    localStorage.removeItem(STORAGE_KEY);
    setSession(null);
  };

  const value = useMemo(
    () => ({
      user: session?.user || null,
      accessToken: session?.access_token || null,
      isAuthenticated: Boolean(session?.access_token && session?.user),
      loading,
      login,
      register,
      sendOtp,
      verifyOtp,
      forgotPassword,
      resetPassword,
      logout,
      logoutAll,
    }),
    [session, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
