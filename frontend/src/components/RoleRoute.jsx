import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getRoleStatus } from "../utils/roleUtils";

/**
 * Route guard component enforcing role-based access.
 *
 * Props:
 * - allowedRoles: Array<string> e.g. ["STUDENT", "ADMIN"]
 * - requireFacultyAccess: boolean (enforces: FACULTY or pending faculty STUDENT)
 * - children: React node to render when authorized
 */
export default function RoleRoute({
  allowedRoles,
  requireFacultyAccess = false,
  children,
}) {
  const { user, isAuthenticated, loading } = useAuth();

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

  if (!isAuthenticated || !user) {
    return <Navigate to="/auth" replace />;
  }

  const roleStatus = getRoleStatus(user);

  // Mandatory correction 1:
  // - FACULTY users can access faculty routes.
  // - STUDENT users can access faculty routes ONLY when pending_role_request.status === "pending".
  // - All other students must be redirected to /app/student.
  if (requireFacultyAccess) {
    if (!roleStatus.canAccessFaculty) {
      return <Navigate to="/app/student" replace />;
    }
    return children;
  }

  // Generic allowedRoles check
  if (allowedRoles && allowedRoles.length > 0) {
    const normalizedAllowed = allowedRoles.map((r) => r.toUpperCase());
    const hasAllowedRole = normalizedAllowed.includes(roleStatus.role);

    if (!hasAllowedRole) {
      // Redirect to user's authorized home dashboard
      return <Navigate to={roleStatus.defaultDashboardRoute} replace />;
    }
  }

  return children;
}

