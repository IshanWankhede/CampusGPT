# 26 — Course Recommendation System

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P18**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
Recommend learning courses from academic weaknesses, interests and target-role skills, with explanations and feedback; development demonstration uses 10–12 sample courses.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | Get recommendations, track progress, give feedback |
| FACULTY | View aggregate course engagement |
| ADMIN | Manage the course catalogue |

## 3. Functional behaviour
- Inputs: weak subjects (analytics), declared interests, skill gaps for target roles, prerequisites and difficulty.
- Output: ranked list with a plain-language reason for each.
- Feedback (not relevant / done) adjusts future ranking.

## 4. Business rules
- Recommendations are explainable; no opaque scores shown as facts.
- Only the student's own data is used for their recommendations.

## 5. Frontend responsibilities
- Recommendation cards with reasons, progress bars, course detail.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `courses` module: rule-based scorer first; embedding similarity optional after P14.

## 7. Database requirements (PROPOSED)
- courses(id, title, category, difficulty, duration_hours, prerequisites JSON, resources JSON)
- course_skills(course_id, skill)
- course_progress(id, student_id, course_id, progress_pct, score, completed_at)
- recommendation_feedback(id, student_id, course_id, signal, created_at)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/courses/recommendations` | STUDENT | personalised, with reasons |
| PUT | `/api/v1/courses/{id}/progress` | STUDENT | update progress |
| POST | `/api/v1/admin/courses` | ADMIN | manage catalogue |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- Student scope from token.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- Progress 0–100; prerequisites exist.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- No sharing of individual progress with other students.

## 14. Testing
- Deterministic ranking fixtures; reasons present; feedback effect.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- P15 analytics
- P06 profile

## 16. Acceptance criteria
- Every recommendation has a reason.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).
