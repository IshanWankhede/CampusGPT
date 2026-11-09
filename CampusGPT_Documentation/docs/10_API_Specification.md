# 10 — API Specification

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Conventions
- Base path `/api/v1`; health at `/health`. JSON bodies; UTF-8; ISO-8601 UTC timestamps.
- Auth: `Authorization: Bearer <access_token>`.
- Pagination: `?page=1&page_size=20` (max 100); list responses `{"items": [...], "page": 1, "page_size": 20, "total": 123}`.
- IDs are UUIDs (verify against existing models).
- **Errors.** Existing auth routes return FastAPI's default `{"detail": "..."}` (REQUIRES VERIFICATION; the frontend reads it). New modules use the envelope below. Whether old routes migrate to it is decided in WP7 so the frontend client handles both.

```json
{ "error": { "code": "forbidden", "message": "You do not have access to this resource.", "request_id": "…", "details": null } }
```

| HTTP | Code | When |
|---|---|---|
| 400 | bad_request | malformed request, unrecognised email domain |
| 401 | unauthenticated | missing/invalid/expired token |
| 403 | forbidden | authenticated but not allowed |
| 404 | not_found | missing **or** not visible to the caller |
| 409 | conflict | duplicates, state conflicts |
| 422 | validation_error | schema validation |
| 429 | rate_limited | with `Retry-After` |
| 503 | unavailable | email/LLM provider down |

## 2. Existing endpoints (audit-reported)
| Method | Path | Auth | Status |
|---|---|---|---|
| GET | `/health` | none | IMPLEMENTED (PO-RV) |
| POST | `/api/v1/auth/register` | none (verified email required) | IMPLEMENTED & HARDENED (WP2: C2/C3 closed, creates STUDENT + pending role request, rejects ADMIN with 422) |
| POST | `/api/v1/auth/login` | none | IMPLEMENTED & HARDENED (WP2: C1 closed, timing equalized dummy hash comparison) |
| POST | `/api/v1/auth/refresh` | refresh token | PARTIALLY IMPLEMENTED (PO-RV) (no rotation) |
| POST | `/api/v1/auth/logout` | access | no-op |
| GET | `/api/v1/auth/me` | access | IMPLEMENTED (WP2: exposes pending_role_request) |
| GET | `/api/v1/auth/admin-test` | ADMIN | placeholder |
| POST | `/api/v1/auth/send-otp` | none | IMPLEMENTED & HARDENED (WP2: mandatory domain check, user-enum defense, 503 on provider error) |
| POST | `/api/v1/auth/verify-otp` | none | IMPLEMENTED & HARDENED (WP2: C2 closed, sets verified_at only on success) |
| POST | `/api/v1/auth/forgot-password` | none | IMPLEMENTED & HARDENED (WP2: user-enum defense) |
| POST | `/api/v1/auth/reset-password` | none | IMPLEMENTED (PO-RV) |
| GET | `/api/v1/auth/google/login` | none | IMPLEMENTED (PO-RV) |
| GET | `/api/v1/auth/google/callback` | none | IMPLEMENTED & HARDENED (WP2: requires verified local account before linking) |

## 3. Proposed foundation endpoints
| Method | Path | Work package | Notes |
|---|---|---|---|
| POST | `/api/v1/auth/google/exchange` | WP4 | body `{ "code": "…" }` → token response |
| POST | `/api/v1/auth/logout` | WP6 | body carries refresh token; revokes it |
| POST | `/api/v1/auth/logout-all` | WP6 | revoke every session |
| GET | `/api/v1/admin/role-requests` | WP2 | ADMIN (IMPLEMENTED) |
| POST | `/api/v1/admin/role-requests/{id}/approve` | WP2 | ADMIN (IMPLEMENTED) |
| POST | `/api/v1/admin/role-requests/{id}/reject` | WP2 | ADMIN (IMPLEMENTED) |

Changed behaviour (same paths): `/register` ignores privileged roles; `/send-otp` always validates domain and may return 503; limited endpoints return 429.

## 4. Proposed module endpoints
### Student Dashboard and Profile (P05–P06)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/students/me` | STUDENT | own profile |
| PATCH | `/api/v1/students/me` | STUDENT | edit editable fields only |
| GET | `/api/v1/students/me/dashboard` | STUDENT | aggregated dashboard |
| GET | `/api/v1/students/{id}` | FACULTY, ADMIN | scoped profile view |
| PUT | `/api/v1/admin/students/{id}/verified-fields` | ADMIN | set verified fields |

### Attendance Management (P07)

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

### Face Recognition and Liveness (P07 (slice B))

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/biometrics/consent` | STUDENT | grant or withdraw consent |
| POST | `/api/v1/biometrics/enrol` | STUDENT | enrol (requires valid consent) |
| DELETE | `/api/v1/biometrics/me` | STUDENT | delete own template |
| POST | `/api/v1/attendance/sessions/{id}/verify` | STUDENT | verify during an open session |
| GET | `/api/v1/admin/biometric-policy` | ADMIN | read policy |
| PUT | `/api/v1/admin/biometric-policy` | ADMIN | update policy (audited) |

### Timetable Management (P08)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/timetable/me` | STUDENT, FACULTY | own timetable for a date range |
| POST | `/api/v1/admin/timetable/entries` | ADMIN | create entry (conflict-checked) |
| POST | `/api/v1/timetable/entries/{id}/changes` | FACULTY, ADMIN | cancel or modify an occurrence |
| GET | `/api/v1/calendar` | any | academic calendar |

### Assignment Management (P09)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/assignments` | FACULTY | create |
| GET | `/api/v1/assignments` | STUDENT, FACULTY | scoped list |
| POST | `/api/v1/assignments/{id}/submissions` | STUDENT | submit (multipart) |
| GET | `/api/v1/assignments/{id}/submissions` | FACULTY | list submissions |
| PUT | `/api/v1/submissions/{id}/evaluation` | FACULTY | evaluate |
| GET | `/api/v1/submissions/{id}/files/{file_id}` | STUDENT, FACULTY | download with authorisation |

### Notices and Notifications (P10)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/notices` | FACULTY, ADMIN | create |
| GET | `/api/v1/notices` | any | visible notices (paged, searchable) |
| POST | `/api/v1/notices/{id}/read` | any | mark read |
| POST | `/api/v1/notices/{id}/ack` | STUDENT | acknowledge |
| GET | `/api/v1/notifications` | any | list own |
| POST | `/api/v1/notifications/{id}/read` | any | mark read |

### Document Management (P11)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/documents` | FACULTY, ADMIN, STUDENT | upload (multipart) |
| GET | `/api/v1/documents` | any | authorised list with filters |
| GET | `/api/v1/documents/{id}/download` | any | authorised download |
| POST | `/api/v1/documents/{id}/versions` | owner, FACULTY | new version |
| DELETE | `/api/v1/documents/{id}` | owner, ADMIN | delete (propagates) |

### CampusGPT AI Assistant (P12)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| WS | `/api/v1/ws/chat` | any (authenticated on connect) | streaming chat channel |
| POST | `/api/v1/ai/conversations` | any | create |
| GET | `/api/v1/ai/conversations` | any | list own |
| GET | `/api/v1/ai/conversations/{id}/messages` | owner | history |
| POST | `/api/v1/ai/messages/{id}/feedback` | any | rate |
| DELETE | `/api/v1/ai/conversations/{id}` | owner | delete |

### Intent Detection and Routing (P13)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/ai/route-debug` | ADMIN (dev only) | inspect classification without executing tools |

### RAG Architecture (P14)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/rag/search` | any | permission-filtered retrieval (also used internally) |

### Document Ingestion and Retrieval Pipeline (P14)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/documents/{id}/reprocess` | FACULTY, ADMIN | retry processing |
| GET | `/api/v1/documents/{id}/processing` | owner, FACULTY, ADMIN | status |

### Academic Analytics (P15)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/analytics/me` | STUDENT | own |
| GET | `/api/v1/analytics/classes/{id}` | FACULTY | class |
| GET | `/api/v1/analytics/institution` | ADMIN | institution |

### Placement Intelligence (P16)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/placements/opportunities` | STUDENT | list with eligibility |
| GET | `/api/v1/placements/opportunities/{id}/eligibility` | STUDENT | explained result |
| POST | `/api/v1/placements/opportunities/{id}/apply` | STUDENT | apply |
| POST | `/api/v1/admin/placements/opportunities` | ADMIN, coordinator | create |

### Internships and Hackathons (P17)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/opportunities` | STUDENT | list |
| POST | `/api/v1/opportunities` | FACULTY, ADMIN | create |
| POST | `/api/v1/opportunities/{id}/bookmark` | STUDENT | bookmark |
| PUT | `/api/v1/opportunities/{id}/participation` | STUDENT | track |

### Course Recommendation System (P18)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/courses/recommendations` | STUDENT | personalised, with reasons |
| PUT | `/api/v1/courses/{id}/progress` | STUDENT | update progress |
| POST | `/api/v1/admin/courses` | ADMIN | manage catalogue |

### Visual Learning Workspace (P19)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/visual/boards` | any | create |
| GET | `/api/v1/visual/boards` | any | list own |
| PUT | `/api/v1/visual/boards/{id}` | owner | save |
| POST | `/api/v1/visual/generate` | any | AI diagram from prompt, schema-validated |

### Voice Interaction (Vapi) (P22)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/voice/sessions` | any | create a short-lived voice session bound to the caller |
| POST | `/api/v1/voice/sessions/{id}/end` | owner | end and invalidate |
| POST | `/api/v1/voice/tools/{tool_name}` | Vapi (server-authenticated + voice-session bound) | tool invocation endpoint used by Vapi custom Function Tools |
| POST | `/api/v1/voice/events` | Vapi (server-authenticated) | call lifecycle events for session and usage tracking |

### Faculty Dashboard (P20)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/faculty/me/dashboard` | FACULTY | aggregated |
| GET | `/api/v1/faculty/me/classes` | FACULTY | assigned classes |

### Admin Dashboard (P21)

| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/admin/users` | ADMIN | list/search |
| GET | `/api/v1/admin/audit-logs` | ADMIN | read-only |
| POST | `/api/v1/admin/imports/students` | ADMIN | CSV dry-run then commit |


## 5. Versioning and deprecation
Breaking changes require a new prefix or a documented deprecation window; the OpenAPI document is generated by FastAPI and served only in development (WP3).

## 6. Real-time and voice interfaces
| Interface | Path | Notes |
|---|---|---|
| WebSocket chat | `/api/v1/ws/chat` | authenticated on connect by a first `auth` message; protocol in `docs/architecture/WebSocket_Protocol.md` |
| WebSocket live attendance | `/api/v1/ws/attendance/{session_id}` | session owner only |
| Voice sessions | `POST /api/v1/voice/sessions`, `POST /api/v1/voice/sessions/{id}/end` | bearer token required |
| Vapi tool endpoints | `POST /api/v1/voice/tools/{tool_name}`, `POST /api/v1/voice/events` | Vapi server authentication **and** voice-session binding required (doc 37) |
| Biometrics | `/api/v1/biometrics/*`, `/api/v1/attendance/sessions/{id}/verify` | consent required (doc 14) |
All paths are PROPOSED. WebSocket is the only real-time transport; SSE is not part of the design.
