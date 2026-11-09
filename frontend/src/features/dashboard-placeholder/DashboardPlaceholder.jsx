import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function DashboardPlaceholder({ roleView }) {
  const { user, role, isPendingFaculty, pendingRoleRequest, logout, logoutAll } = useAuth();
  const navigate = useNavigate();
  const [signingOut, setSigningOut] = useState(false);

  const displayRole = (roleView || role || "user").toUpperCase();

  const handleSignOut = async () => {
    setSigningOut(true);
    try {
      await logout();
    } finally {
      navigate("/", { replace: true });
    }
  };

  const handleSignOutAll = async () => {
    setSigningOut(true);
    try {
      await logoutAll();
    } finally {
      navigate("/", { replace: true });
    }
  };

  return (
    <main className="placeholder-page">
      <div className="placeholder-card">
        <div className="brand-mark">⌁</div>
        <p className="eyebrow">CAMPUSGPT</p>
        <h1>Welcome, {user?.full_name || "Campus User"} 👋</h1>

        {/* Pending Faculty Notice Banner */}
        {isPendingFaculty && (
          <div
            role="status"
            className="mb-4 p-3.5 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-200 text-xs leading-relaxed text-left"
          >
            <div className="flex items-center gap-2 font-semibold text-amber-300 mb-1">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
              Faculty Account Pending Verification
            </div>
            <p>
              Your application for <strong>{pendingRoleRequest?.requested_role || "FACULTY"}</strong> role is
              currently undergoing administrator review. In the meantime, you have full access to student
              capabilities.
            </p>
          </div>
        )}

        <p>
          Your <strong>{displayRole}</strong> dashboard is under construction — check back soon.
        </p>

        <div className="flex flex-wrap gap-2.5 justify-center mt-6">
          <button
            type="button"
            className="primary-pill"
            disabled={signingOut}
            onClick={handleSignOut}
          >
            {signingOut ? "Signing out…" : "Sign out"}
          </button>
          <button
            type="button"
            className="px-4 py-2 text-xs text-neutral-400 hover:text-white border border-white/10 hover:border-white/25 rounded-full transition-colors"
            disabled={signingOut}
            onClick={handleSignOutAll}
          >
            Sign out all devices
          </button>
        </div>
      </div>
    </main>
  );
}
