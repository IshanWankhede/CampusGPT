# 34 — Screen Inventory and Navigation

Routes and component names for new screens are **PROPOSED**; existing screens are marked from the audit. The current `/app` placeholder is replaced in P05.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

| Area | Screen | Route | Component | API dependency | Status |
|---|---|---|---|---|---|
| Public | Landing | `/` | existing `prototype-visuals/LandingPage.jsx` | — | IMPLEMENTED (PO-RV) (preserve) |
| Public | Sign in / Sign up | `/auth` | existing `AuthScreen.jsx` | /auth/* | IMPLEMENTED (PO-RV) (preserve) |
| Public | Google callback | `/auth/callback` | existing screen + `AuthContext` effect | /auth/google/exchange (WP4) | PARTIALLY IMPLEMENTED (PO-RV) |
| Public | Forgot / reset password | `/auth/forgot-password, /auth/reset-password` | existing | /auth/* | IMPLEMENTED (PO-RV) (preserve) |
| Public | Verify email | `/auth/verify-email` | existing (possibly orphaned, PD-21) | /auth/verify-otp | REQUIRES VERIFICATION |
| Student | Dashboard | `/app/student` | DashboardPage | /students/me/dashboard | NOT IMPLEMENTED (placeholder `/app`) |
| Student | Profile | `/app/student/profile` | ProfilePage | /students/me | NOT IMPLEMENTED |
| Student | Attendance | `/app/student/attendance` | AttendancePage | /attendance/me | NOT IMPLEMENTED |
| Student | Timetable | `/app/student/timetable` | TimetablePage | /timetable/me | NOT IMPLEMENTED |
| Student | Assignments | `/app/student/assignments` | AssignmentListPage / DetailPage | /assignments | NOT IMPLEMENTED |
| Student | Notices and notifications | `/app/student/notices` | NoticeFeed | /notices, /notifications | NOT IMPLEMENTED |
| Student | Documents | `/app/student/documents` | DocumentLibrary | /documents | NOT IMPLEMENTED |
| Student | CampusGPT | `/app/student/chat` | ChatWorkspace | /ai/* | NOT IMPLEMENTED |
| Student | Voice mode | `/app/student/chat?mode=voice` | VoiceOverlay | /ai/* | NOT IMPLEMENTED |
| Student | Analytics | `/app/student/analytics` | AnalyticsPage | /analytics/me | NOT IMPLEMENTED |
| Student | Placements | `/app/student/placements` | PlacementWorkspace | /placements/* | NOT IMPLEMENTED |
| Student | Internships and hackathons | `/app/student/opportunities` | OpportunityList | /opportunities | NOT IMPLEMENTED |
| Student | Courses | `/app/student/courses` | CourseRecommendations | /courses/* | NOT IMPLEMENTED |
| Student | Visual workspace | `/app/student/visual` | VisualWorkspace | /visual/* | NOT IMPLEMENTED |
| Faculty | Dashboard | `/app/faculty` | FacultyDashboard | /faculty/me/dashboard | NOT IMPLEMENTED |
| Faculty | Classes and students | `/app/faculty/classes` | ClassList / ClassDetail | /faculty/me/classes | NOT IMPLEMENTED |
| Faculty | Live attendance | `/app/faculty/attendance` | LiveSession | /attendance/sessions | NOT IMPLEMENTED |
| Faculty | Assignments and evaluation | `/app/faculty/assignments` | AssignmentManager / Evaluator | /assignments, /submissions | NOT IMPLEMENTED |
| Faculty | Notices | `/app/faculty/notices` | NoticeComposer | /notices | NOT IMPLEMENTED |
| Faculty | Documents upload | `/app/faculty/documents` | DocumentManager | /documents | NOT IMPLEMENTED |
| Faculty | Class analytics | `/app/faculty/analytics` | ClassAnalytics | /analytics/classes/{id} | NOT IMPLEMENTED |
| Faculty | CampusGPT | `/app/faculty/chat` | ChatWorkspace | /ai/* | NOT IMPLEMENTED |
| Admin | Dashboard | `/app/admin` | AdminDashboard | /admin/* | NOT IMPLEMENTED |
| Admin | Role requests | `/app/admin/role-requests` | RoleRequestQueue | /admin/role-requests | NOT IMPLEMENTED (API in WP2) |
| Admin | Users, students, faculty | `/app/admin/users` | UserTable | /admin/users | NOT IMPLEMENTED |
| Admin | Academic structure | `/app/admin/structure` | StructureManager | /admin/* | NOT IMPLEMENTED |
| Admin | Timetable management | `/app/admin/timetable` | TimetableEditor | /admin/timetable/* | NOT IMPLEMENTED |
| Admin | Policies (attendance, geofence, biometrics) | `/app/admin/policies` | PolicyForms | /admin/policies | NOT IMPLEMENTED |
| Admin | Notices and documents oversight | `/app/admin/content` | ContentTables | /notices, /documents | NOT IMPLEMENTED |
| Admin | Placements, opportunities, courses | `/app/admin/careers` | CareerManagers | /admin/placements, /opportunities, /admin/courses | NOT IMPLEMENTED |
| Admin | Audit logs | `/app/admin/audit` | AuditViewer | /admin/audit-logs | NOT IMPLEMENTED |
| Admin | AI configuration and system analytics | `/app/admin/system` | SystemPage | /admin/* | NOT IMPLEMENTED |
| Admin | Data import | `/app/admin/import` | ImportWizard | /admin/imports/* | NOT IMPLEMENTED |
| Shared | Settings / profile menu | `/app/settings` | SettingsPage | /auth/me | NOT IMPLEMENTED |

## Navigation trees (PROPOSED)
- **Student:** Dashboard · Attendance · Timetable · Assignments · Notices · Documents · CampusGPT · Analytics · Placements · Opportunities · Courses · Visual workspace · Profile.
- **Faculty:** Dashboard · Classes · Attendance · Assignments · Notices · Documents · Analytics · CampusGPT · Profile (pending-faculty users see a "waiting for approval" screen only).
- **Admin:** Dashboard · Role requests · Users · Structure · Timetable · Policies · Content · Careers · Audit · System · Import.

## Routing rules
All `/app/*` routes sit behind `ProtectedRoute` and a `RoleRoute`. Unknown routes redirect to the role's dashboard. Direct navigation to another role's route shows a not-authorised screen; the backend is still the real gate.

## Additional screens (final correction — all PROPOSED, NOT IMPLEMENTED)
| Area | Screen | Route | Component | API dependency |
|---|---|---|---|---|
| Student | Biometric consent and enrolment | `/app/student/biometrics` | ConsentFlow / EnrolmentFlow | `/biometrics/*` |
| Student | Attendance verification (camera + liveness) | `/app/student/attendance/verify/:sessionId` | VerificationCapture | `/attendance/sessions/{id}/verify` |
| Student | Voice mode (Vapi) | `/app/student/chat?mode=voice` | VoiceOverlay | `/voice/sessions` + Vapi SDK |
| Faculty | Live attendance with verification monitor and manual override | `/app/faculty/attendance/:sessionId` | LiveSession + OverrideDialog | `WS /ws/attendance/{id}`, `/attendance/*` |
| Faculty | Attendance reports and audit | `/app/faculty/attendance/reports` | AttendanceReports | `/attendance/reports` |
| Admin | Biometric policy, geofence, retention | `/app/admin/policies` | PolicyForms | `/admin/biometric-policy` |
| Shared | Settings and profile (privacy, consent status, sessions) | `/app/settings` | SettingsPage | `/auth/me`, `/biometrics/consent` |
Student, faculty and admin dashboards, chat, timetable, assignments and documents are listed in the main table above.
