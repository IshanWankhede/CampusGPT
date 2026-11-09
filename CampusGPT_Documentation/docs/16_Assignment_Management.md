# 16 — Assignment Management

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P09**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
Faculty create assignments with instructions, files, deadlines, marks and rubrics; students submit PDF/document files and track status, timestamps, feedback and marks.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | View assignments and due dates; download references; submit and resubmit before the deadline; see status, history, feedback, marks |
| FACULTY | Create/edit assignments for assigned classes; view submissions; evaluate with rubric; give feedback and marks |
| ADMIN | Oversight and reports |

## 3. Functional behaviour
- Statuses: not submitted, submitted, late, evaluated, returned.
- Resubmission keeps history; the latest valid submission is evaluated.
- Deadlines use server time; late policy configurable (accept-late with flag vs block).
- Evaluation records rubric scores, total and feedback.

## 4. Business rules
- Only assigned faculty may create or evaluate for a class.
- Students can submit only to assignments of classes they are enrolled in.
- Marks visible to the student only after the faculty publishes them.

## 5. Frontend responsibilities
- Assignment list/detail, upload dialog with progress and validation messages, evaluation screen with rubric.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `assignments` module; file handling through a storage interface (PD-12).

## 7. Database requirements (PROPOSED)
- assignments(id, class_id, subject_id, faculty_id, title, instructions, due_at, max_marks, allow_late, published_at)
- assignment_files(id, assignment_id, file_id)
- rubric_criteria(id, assignment_id, label, max_marks)
- submissions(id, assignment_id, student_id, submitted_at, is_late, status, version)
- submission_files(id, submission_id, file_id)
- evaluations(id, submission_id, evaluator_id, total, feedback, published_at)
- evaluation_scores(id, evaluation_id, criterion_id, marks)
- stored_files(id, owner_id, path, sha256, size, mime, created_at)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/assignments` | FACULTY | create |
| GET | `/api/v1/assignments` | STUDENT, FACULTY | scoped list |
| POST | `/api/v1/assignments/{id}/submissions` | STUDENT | submit (multipart) |
| GET | `/api/v1/assignments/{id}/submissions` | FACULTY | list submissions |
| PUT | `/api/v1/submissions/{id}/evaluation` | FACULTY | evaluate |
| GET | `/api/v1/submissions/{id}/files/{file_id}` | STUDENT, FACULTY | download with authorisation |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- File downloads re-check authorisation on every request; paths are never public URLs.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- Extension, MIME and magic-byte check; size limit; filename sanitised and replaced by a generated name; virus-scan hook point documented.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Upload hardening, storage outside web root, checksum, no path traversal, rate limits on uploads.

## 14. Testing
- Late flag at the boundary; resubmission history; cross-class submission blocked; download IDOR test; malicious filename test.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- Documents/storage interface
- Academic structure
- Notifications for deadlines

## 16. Acceptance criteria
- Students cannot see others' submissions or unpublished marks.
- Upload validation rejects spoofed types.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).
