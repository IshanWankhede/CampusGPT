import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LandingPage } from "../features/prototype-visuals/LandingPage";
import { AuthScreen as AuthPage } from "../features/prototype-visuals/AuthScreen";
import DashboardPlaceholder from "../features/dashboard-placeholder/DashboardPlaceholder";
import VerifyEmail from "../features/auth/VerifyEmail";
import ForgotPassword from "../features/auth/ForgotPassword";
import ResetPassword from "../features/auth/ResetPassword";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <div className="loading-screen">Loading CampusGPT…</div>;
  return isAuthenticated ? children : <Navigate to="/auth" replace />;
}

function PublicRoutes() {
  const navigate = useNavigate();
  return <Routes>
    <Route path="/" element={<LandingPage onGetStarted={() => navigate("/auth")} onSignIn={() => navigate("/auth")} />} />
    <Route path="/auth" element={<AuthPage onBackToLanding={() => navigate("/")} />} />
    <Route path="/auth/callback" element={<AuthPage onBackToLanding={() => navigate("/")} />} />
    <Route path="/auth/verify-email" element={<VerifyEmail />} />
    <Route path="/auth/forgot-password" element={<ForgotPassword />} />
    <Route path="/auth/reset-password" element={<ResetPassword />} />
    <Route path="/app" element={<ProtectedRoute><DashboardPlaceholder /></ProtectedRoute>} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>;
}

export default function AppRoutes() {
  return <PublicRoutes />;
}
