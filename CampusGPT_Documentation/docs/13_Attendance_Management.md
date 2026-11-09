# 13 — Attendance Management

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P07**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
Faculty-controlled attendance sessions linked to timetable entries, verified by face recognition with liveness checks (a required core capability), supported by campus-geofence evidence, with real-time status, duplicate prevention, manual faculty override, attendance audit logs, student history, percentage and shortage calculations, and recovery planning.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | View overall and subject-wise attendance, history, calendar, status (present/absent/late), shortage and classes needed to recover; mark own attendance in an open session through face verification (manual fallback available through the faculty) |
| FACULTY | Start/stop sessions for assigned timetable entries, watch the live roster and face-verification outcomes in real time, manually mark or override with a recorded reason, view reports |
| ADMIN | Set attendance policies (threshold default 75%), geofence and biometric policy, oversight reports, audit review |

## 3. Functional behaviour
- A session is created by the assigned faculty from a **timetable entry** (class, subject, slot) and closed manually or by timeout.
- Students verify their presence through **face recognition plus liveness verification** during an open session; the outcome (PRESENT/LATE/REJECTED/NEEDS_REVIEW) and evidence summary are stored on a verification event linked to the attendance record. Face verification is a planned core product requirement, not an optional extra (see doc 14).
- **Duplicate attendance prevention:** one record per (session, student), enforced by a database unique constraint and by server-side checks (including repeated or concurrent attempts).
- **Geofence** (campus boundary) is recorded as supporting evidence; GPS is never treated as definitive proof of physical presence.
- **Real-time status:** the faculty roster updates live over the WebSocket channel (see `docs/architecture/WebSocket_Protocol.md`); the student sees their own verification result immediately.
- **Manual fallback and override:** when verification fails, is unavailable, the student has not consented, or a device lacks a camera, faculty can mark attendance manually; every override stores reason, actor, time and the previous value.
- Statuses PRESENT, ABSENT, LATE; attendance percentage = present-equivalent ÷ conducted sessions per subject; overall = across subjects (late weighting configurable).
- **Shortage calculation:** for threshold T (default 75%), present p, conducted c: classes the student can still miss = floor(p/T − c) when positive; classes needed to recover = ceil((T·c − p)/(1 − T)) when below threshold; the UI shows the formula inputs.
- Notifications when a subject falls below threshold (P10).
- Student attendance history, calendar view and subject-wise breakdown.
- Every session, verification event, override and policy change is written to the attendance audit log.

## 4. Business rules
- Default threshold 75%, configurable per policy.
- Faculty can only open sessions for entries assigned to them.
- Corrections and overrides after the fact require a reason and create an audit record; the original value is retained.
- Blink detection is one liveness signal, never the complete liveness solution; liveness must also address photo and replay spoofing (doc 14).
- Biometric processing requires explicit informed consent; students without consent use the manual fallback without penalty.
- Faculty see verification outcomes and scores summaries, **not** raw images or templates.
- The face-recognition provider is an unresolved decision (PD-10); implementation is provider-agnostic behind an interface. No production enablement of biometrics before PD-10 and the privacy/legal review are completed.

## 5. Frontend responsibilities
- Student: attendance cards, subject table, calendar, history, shortage and recovery widget, verification capture screen (camera permission, liveness prompts, clear success/failure/fallback states), consent and enrolment screens (doc 14).
- Faculty: live session screen with real-time roster and verification status, manual marking and override dialog (reason required), reports.
- Admin: policy (threshold, geofence, biometric policy, retention) and report screens.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `attendance` module: session service, record service, calculation service (pure functions with unit tests), report service, audit writer.
- `biometrics` module: consent, enrolment, verification and liveness orchestration behind a `BiometricProvider` interface; development uses a clearly-labelled mock provider that must never be described as real verification.
- WebSocket publisher for live roster updates (PD-25 for multi-worker fan-out).
- Calculation logic is server-side only and shared by the dashboard, reports and AI tools.

## 7. Database requirements (PROPOSED)
- attendance_policies(id, scope, threshold_pct, late_weight, geofence_id, verification_required, fallback_allowed)
- attendance_sessions(id, class_id, subject_id, faculty_id, timetable_entry_id, started_at, ended_at, status, verification_mode)
- attendance_records(id, session_id, student_id, status, source[face|manual|override], marked_at, verification_event_id, UNIQUE(session_id, student_id))
- attendance_overrides(id, record_id, old_status, new_status, reason, actor_id, created_at)
- verification_events(id, session_id, student_id, provider, match_score, liveness_result, geofence_result, outcome, created_at)
- geofences(id, name, polygon JSON, active)
- (biometric tables: face_consents, face_templates, liveness_challenges — see doc 14)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/attendance/sessions` | FACULTY | start session from a timetable entry |
| POST | `/api/v1/attendance/sessions/{id}/close` | FACULTY | stop session |
| POST | `/api/v1/attendance/sessions/{id}/verify` | STUDENT | submit face + liveness verification for this session |
| PUT | `/api/v1/attendance/sessions/{id}/records/{student_id}` | FACULTY | manual mark or override (reason required) |
| GET | `/api/v1/attendance/me` | STUDENT | own summary and subject-wise |
| GET | `/api/v1/attendance/me/shortage` | STUDENT | classes that can be missed / needed to recover |
| GET | `/api/v1/attendance/reports` | FACULTY, ADMIN | scoped reports |
| WS | `/api/v1/ws/attendance/{session_id}` | FACULTY (session owner) | live roster and verification events |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- Faculty must be assigned to the subject and class.
- Student endpoints derive identity from the token; a student can verify only for a session of their enrolled class that is open.
- Faculty cannot read raw biometric data; admins cannot read templates.
- WebSocket connections authenticate on connect and re-check session ownership.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- Status enum; one record per (session, student); session must be open; student must be enrolled in the class and (for face mode) have valid consent and enrolment, otherwise the manual fallback path is signalled.
- Image size/type limits; liveness challenge freshness and single use.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Server-side time for all timestamps.
- Audit every mark, verification, override and policy change.
- Rate limit verification attempts per student and per session.
- Biometric data handling per doc 14 (encryption, retention, deletion, access restrictions).

## 14. Testing
- Duplicate mark rejected (including concurrent requests).
- Percentage and shortage calculations against hand-computed fixtures including the boundary at exactly 75%.
- Faculty cannot open sessions for others' classes; student cannot verify for a class they are not enrolled in.
- Student cannot read another student's attendance.
- Manual fallback path works when verification is unavailable or consent is missing.
- Override requires a reason and preserves the previous value.
- Live roster WebSocket authenticates, authorises and delivers events only to the session owner.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- P05 shell and academic structure
- P08 timetable (session linking; build order: P08 before P07)
- Biometric provider decision PD-10 for the production face slice
- WebSocket decision PD-25 for multi-worker live updates

## 16. Acceptance criteria
- Calculations match fixtures.
- All mutations and overrides audited.
- No cross-student leakage.
- Face verification and liveness implemented behind the provider interface with consent, fallback and audit; no claim of production biometric readiness until PD-10 and the privacy/legal review are complete.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).

## 17. Delivery slices inside phase P07
1. **Slice A — core attendance:** sessions from timetable entries, manual marking, calculations, history, shortage, audit, real-time roster.
2. **Slice B — face verification and liveness:** consent, enrolment, verification and liveness orchestration, geofence evidence, fallback and override flows — built behind `BiometricProvider`. Slice B is part of the required scope of P07; only its **production enablement** waits for PD-10 (provider and biometric policies) and the privacy/legal review.
