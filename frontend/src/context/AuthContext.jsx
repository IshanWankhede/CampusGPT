import { createContext, useContext, useEffect, useMemo, useState } from "react";

const API_BASE = "/api/v1/auth";
const STORAGE_KEY = "campusgpt.auth";

const AuthContext = createContext(null);

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
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

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const urlAccessToken = urlParams.get("access_token");
    const urlRefreshToken = urlParams.get("refresh_token");

    if (urlAccessToken && urlRefreshToken) {
      const nextSession = { access_token: urlAccessToken, refresh_token: urlRefreshToken };
      request("/me", {
        headers: { Authorization: `Bearer ${urlAccessToken}` },
      })
        .then((user) => {
          saveSession({ ...nextSession, user });
          window.history.replaceState({}, document.title, "/app");
          window.location.href = "/app";
        })
        .catch(() => {
          setLoading(false);
        });
      return;
    }

    if (!session?.access_token) {
      setLoading(false);
      return;
    }

    request("/me", {
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
    const nextSession = await request("/login", {
      method: "POST",
      body: JSON.stringify({ email, password, college }),
    });
    const user = await request("/me", {
      headers: { Authorization: `Bearer ${nextSession.access_token}` },
    });
    saveSession({ ...nextSession, user });
    return user;
  };

  const register = async (fullName, email, password, role, college) => {
    return request("/register", {
      method: "POST",
      body: JSON.stringify({ full_name: fullName, email, password, role, college }),
    });
  };

  const sendOtp = (email, purpose, college) =>
    request("/send-otp", { method: "POST", body: JSON.stringify({ email, purpose, college }) });
  const verifyOtp = (email, otp, purpose) =>
    request("/verify-otp", { method: "POST", body: JSON.stringify({ email, otp, purpose }) });
  const forgotPassword = (email) =>
    request("/forgot-password", { method: "POST", body: JSON.stringify({ email }) });
  const resetPassword = (email, otp, newPassword) =>
    request("/reset-password", {
      method: "POST",
      body: JSON.stringify({ email, otp, new_password: newPassword }),
    });

  const logout = async () => {
    if (session?.access_token) {
      await request("/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${session.access_token}` },
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
