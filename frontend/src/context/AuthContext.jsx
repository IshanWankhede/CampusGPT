import { createContext, useContext, useEffect, useMemo, useState, useCallback } from "react";
import {
  apiFetch,
  clearStoredSession,
  getStoredSession,
  saveStoredSession,
  subscribeSession,
} from "../services/api";
import { getRoleStatus } from "../utils/roleUtils";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => getStoredSession());
  const [loading, setLoading] = useState(() => {
    if (typeof window !== "undefined") {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get("code")) return true;
    }
    return Boolean(getStoredSession()?.access_token);
  });

  const saveSession = useCallback((nextSession) => {
    saveStoredSession(nextSession);
    setSession(nextSession);
  }, []);

  const clearSession = useCallback(() => {
    clearStoredSession();
    setSession(null);
  }, []);

  // Listen to background session updates (e.g. from token refresh or other tabs)
  useEffect(() => {
    const unsubscribe = subscribeSession(({ type, session: updatedSession }) => {
      if (type === "UPDATE") {
        setSession(updatedSession);
      } else if (type === "CLEAR") {
        setSession(null);
      }
    });
    return unsubscribe;
  }, []);

  // Handle OAuth code exchange or session initialization on mount
  useEffect(() => {
    let isMounted = true;
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");

    if (code) {
      // Immediate URL cleanup to avoid temporary code leakage in history/referrer
      window.history.replaceState({}, document.title, window.location.pathname);

      apiFetch("/auth/google/exchange", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({ code }),
      })
        .then((tokenData) => {
          if (!isMounted) return;
          saveSession(tokenData);
          setLoading(false);
          window.location.href = "/app";
        })
        .catch((error) => {
          if (!isMounted) return;
          setLoading(false);
          const encodedErr = encodeURIComponent(error.message || "Google sign-in failed.");
          window.location.href = `/auth?error=${encodedErr}`;
        });
      return () => {
        isMounted = false;
      };
    }

    const current = getStoredSession();
    if (!current?.access_token) {
      // Initialized to false; no action required
      return () => {
        isMounted = false;
      };
    }

    // Validate active session against /api/v1/auth/me
    apiFetch("/auth/me")
      .then((user) => {
        if (!isMounted) return;
        const merged = { ...current, user };
        saveSession(merged);
      })
      .catch(() => {
        if (!isMounted) return;
        clearSession();
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [saveSession, clearSession]);

  const login = useCallback(
    async (email, password, college) => {
      const nextSession = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password, college }),
      });
      const user = await apiFetch("/auth/me", {
        headers: { Authorization: `Bearer ${nextSession.access_token}` },
      });
      const fullSession = { ...nextSession, user };
      saveSession(fullSession);
      return user;
    },
    [saveSession]
  );

  const register = useCallback(
    async (fullName, email, password, role, college) => {
      return apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({ full_name: fullName, email, password, role, college }),
      });
    },
    []
  );

  const sendOtp = useCallback(async (email, purpose, college) => {
    return apiFetch("/auth/send-otp", {
      method: "POST",
      body: JSON.stringify({ email, purpose, college }),
    });
  }, []);

  const verifyOtp = useCallback(async (email, otp, purpose) => {
    return apiFetch("/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ email, otp, purpose }),
    });
  }, []);

  const forgotPassword = useCallback(async (email) => {
    return apiFetch("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  }, []);

  const resetPassword = useCallback(async (email, otp, newPassword) => {
    return apiFetch("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ email, otp, new_password: newPassword }),
    });
  }, []);

  const logout = useCallback(async () => {
    const currentRefresh = session?.refresh_token;
    if (session?.access_token || currentRefresh) {
      await apiFetch("/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: currentRefresh || null }),
      }).catch(() => {});
    }
    clearSession();
  }, [session, clearSession]);

  const logoutAll = useCallback(async () => {
    if (session?.access_token) {
      await apiFetch("/auth/logout-all", {
        method: "POST",
      }).catch(() => {});
    }
    clearSession();
  }, [session, clearSession]);

  const roleInfo = useMemo(() => getRoleStatus(session?.user), [session?.user]);

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
      // Role & permissions helpers
      role: roleInfo.role,
      isStudent: roleInfo.isStudent,
      isFaculty: roleInfo.isFaculty,
      isAdmin: roleInfo.isAdmin,
      isPendingFaculty: roleInfo.isPendingFaculty,
      pendingRoleRequest: roleInfo.pendingRoleRequest,
      canAccessFaculty: roleInfo.canAccessFaculty,
      canAccessAdmin: roleInfo.canAccessAdmin,
      canAccessStudent: roleInfo.canAccessStudent,
      defaultDashboardRoute: roleInfo.defaultDashboardRoute,
    }),
    [
      session,
      loading,
      login,
      register,
      sendOtp,
      verifyOtp,
      forgotPassword,
      resetPassword,
      logout,
      logoutAll,
      roleInfo,
    ]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
