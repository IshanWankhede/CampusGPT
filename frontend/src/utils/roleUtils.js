/**
 * Role evaluation utilities for CampusGPT.
 *
 * Backend role enums (UserRole):
 * - "STUDENT"
 * - "FACULTY"
 * - "ADMIN"
 *
 * Role request status (RoleRequestStatus):
 * - "PENDING"
 * - "APPROVED"
 * - "REJECTED"
 */

export function getRoleStatus(user) {
  const role = (user?.role || "").toUpperCase();
  const pendingReq = user?.pending_role_request;
  const pendingStatus = (pendingReq?.status || "").toUpperCase();
  const requestedRole = (pendingReq?.requested_role || "").toUpperCase();

  const isStudent = role === "STUDENT";
  const isFaculty = role === "FACULTY";
  const isAdmin = role === "ADMIN";

  // Per WP2 Defect C3: Faculty registrants start as STUDENT with a PENDING role request
  const isPendingFaculty = isStudent && pendingStatus === "PENDING" && requestedRole === "FACULTY";

  // Correction 1:
  // - FACULTY users can access faculty routes.
  // - STUDENT users can access faculty routes ONLY when pending_role_request.status === "pending".
  // - All other students must be redirected to /app/student.
  // - Never grant faculty access to every student.
  const canAccessFaculty = isFaculty || isPendingFaculty;

  // Admin access strictly requires ADMIN role
  const canAccessAdmin = isAdmin;

  // Student routes accessible to all students (including pending faculty)
  const canAccessStudent = isStudent;

  // Primary home dashboard based on role and pending status
  let defaultDashboardRoute = "/app/student";
  if (isAdmin) {
    defaultDashboardRoute = "/app/admin";
  } else if (isFaculty || isPendingFaculty) {
    defaultDashboardRoute = "/app/faculty";
  }

  return {
    role,
    isStudent,
    isFaculty,
    isAdmin,
    isPendingFaculty,
    pendingRoleRequest: pendingReq,
    canAccessFaculty,
    canAccessAdmin,
    canAccessStudent,
    defaultDashboardRoute,
  };
}

