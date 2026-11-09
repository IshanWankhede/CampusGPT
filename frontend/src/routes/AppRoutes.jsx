import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LandingPage } from "../features/prototype-visuals/LandingPage";
import { AuthScreen as AuthPage } from "../features/prototype-visuals/AuthScreen";
import DashboardPlaceholder from "../features/dashboard-placeholder/DashboardPlaceholder";
import VerifyEmail from "../features/auth/VerifyEmail";
import ForgotPassword from "../features/auth/ForgotPassword";
import ResetPassword from "../features/auth/ResetPassword";
import RoleRoute from "../components/RoleRoute";
import { useTransitionNavigate } from "../features/prototype-visuals/PageTransitionProvider";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen min-h-[100dvh] bg-black text-white flex items-center justify-center font-sans-ui">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-white/20 border-t-white animate-spin" />
          <p className="text-xs text-neutral-400">Loading CampusGPT…</p>
        </div>
      </div>
    );
  }
  return isAuthenticated ? children : <Navigate to="/auth" replace />;
}

function DefaultDashboardRedirect() {
  const { defaultDashboardRoute } = useAuth();
  return <Navigate to={defaultDashboardRoute || "/app/student"} replace />;
}

export default function AppRoutes() {
  // Use transition-aware navigation so stairs play BEFORE the page changes
  const transitionTo = useTransitionNavigate();

  return (
    <Routes>
      {/* Public Pages */}
      <Route
        path="/"
        element={
          <LandingPage
            onGetStarted={() => transitionTo("/auth")}
            onSignIn={() => transitionTo("/auth")}
          />
        }
      />
      <Route path="/auth" element={<AuthPage onBackToLanding={() => transitionTo("/")} />} />
      <Route path="/auth/callback" element={<AuthPage onBackToLanding={() => transitionTo("/")} />} />
      <Route path="/auth/verify-email" element={<VerifyEmail />} />
      <Route path="/auth/forgot-password" element={<ForgotPassword />} />
      <Route path="/auth/reset-password" element={<ResetPassword />} />

      {/* Dynamic Role-Based App Route */}
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <DefaultDashboardRedirect />
          </ProtectedRoute>
        }
      />

      {/* Role-Specific Protected Dashboards */}
      <Route
        path="/app/student"
        element={
          <RoleRoute allowedRoles={["STUDENT"]}>
            <DashboardPlaceholder roleView="student" />
          </RoleRoute>
        }
      />
      <Route
        path="/app/faculty"
        element={
          <RoleRoute requireFacultyAccess>
            <DashboardPlaceholder roleView="faculty" />
          </RoleRoute>
        }
      />
      <Route
        path="/app/admin"
        element={
          <RoleRoute allowedRoles={["ADMIN"]}>
            <DashboardPlaceholder roleView="admin" />
          </RoleRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
