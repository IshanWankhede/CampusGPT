# 15 — Timetable Management

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P08**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
Daily, weekly and semester timetables with subject, faculty, classroom and time; modifications, cancellations and notifications; lecture notes, homework and reminders; academic calendar.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | View own timetable, notes, homework, reminders, calendar |
| FACULTY | View assigned timetable; add lecture notes and homework; request changes or cancel a class |
| ADMIN | Create and manage institutional timetables, classrooms, calendar |

## 3. Functional behaviour
- Entries have day, start/end, subject, class/section, faculty, room.
- Conflict detection: same faculty, room or class in overlapping slots is rejected.
- Cancellations and changes create `timetable_changes` and notify affected students.
- Google Calendar integration is deferred (PD-20).

## 4. Business rules
- Only admins edit the master timetable; faculty changes are requests or limited cancellations within policy.
- Times are stored in the institution's timezone with explicit zone handling.

## 5. Frontend responsibilities
- Timeline/timetable views inspired by reference 3; week grid; today list; admin editor.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `timetable` module with conflict-check service.

## 7. Database requirements (PROPOSED)
- classrooms(id, name, capacity)
- timetable_entries(id, class_id, subject_id, faculty_id, classroom_id, weekday, start_time, end_time, valid_from, valid_to)
- timetable_changes(id, entry_id, date, kind[cancel|reschedule|room], detail, created_by)
- academic_calendar_events(id, title, date_from, date_to, kind)
- lecture_notes(id, entry_id, date, note, homework, created_by)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/timetable/me` | STUDENT, FACULTY | own timetable for a date range |
| POST | `/api/v1/admin/timetable/entries` | ADMIN | create entry (conflict-checked) |
| POST | `/api/v1/timetable/entries/{id}/changes` | FACULTY, ADMIN | cancel or modify an occurrence |
| GET | `/api/v1/calendar` | any | academic calendar |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- Students see entries of their enrolled classes only.
- Faculty see entries assigned to them.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- end > start; weekday range; overlap check inside a transaction.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Audit master-timetable edits.

## 14. Testing
- Overlap detection for faculty, room and class.
- Cancellation notification created.
- Timezone boundary cases.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- Academic structure
- Notifications (P10) for alerts

## 16. Acceptance criteria
- No double-booking possible through the API.
- Students see only their classes.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).
