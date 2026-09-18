import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LandingPage from "../features/landing/LandingPage";
import AuthPage from "../features/auth/AuthPage";
import DashboardPlaceholder from "../features/dashboard-placeholder/DashboardPlaceholder";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <div className="loading-screen">Loading CampusGPT…</div>;
  return isAuthenticated ? children : <Navigate to="/auth" replace />;
}

export default function AppRoutes() {
  return <Routes><Route path="/" element={<LandingPage />} /><Route path="/auth" element={<AuthPage />} /><Route path="/app" element={<ProtectedRoute><DashboardPlaceholder /></ProtectedRoute>} /><Route path="*" element={<Navigate to="/" replace />} /></Routes>;
}
