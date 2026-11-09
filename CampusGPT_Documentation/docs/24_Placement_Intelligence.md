# 24 — Placement Intelligence

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P16**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
Company and job discovery, eligibility checking with explanations, application tracking, interview rounds, offers, statistics and recommendations; fourth-year full workspace, earlier years readiness.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | Browse, check eligibility, apply/track, see readiness |
| FACULTY | Placement coordinators manage listings per designation |
| ADMIN | Manage companies, opportunities, statistics |

## 3. Functional behaviour
- Eligibility rules: CGPA, backlogs, branch, year, skills; the result lists each rule as met/unmet with the student's value.
- Application pipeline with rounds and outcomes; offers recorded.
- Readiness score from transparent inputs (skills vs target role, courses done).

## 4. Business rules
- Explanations must name the failing rule.
- Statistics aggregate only; no individual disclosure to other students.

## 5. Frontend responsibilities
- Opportunity list, eligibility panel, pipeline board, statistics.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `placements` module with a rules engine of declarative criteria.

## 7. Database requirements (PROPOSED)
- companies(id, name, sector, website)
- placement_opportunities(id, company_id, title, criteria JSON, deadline, created_by)
- placement_applications(id, opportunity_id, student_id, status, updated_at)
- interview_rounds(id, application_id, round_no, kind, scheduled_at, outcome)
- offers(id, application_id, ctc, role, accepted_at)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/placements/opportunities` | STUDENT | list with eligibility |
| GET | `/api/v1/placements/opportunities/{id}/eligibility` | STUDENT | explained result |
| POST | `/api/v1/placements/opportunities/{id}/apply` | STUDENT | apply |
| POST | `/api/v1/admin/placements/opportunities` | ADMIN, coordinator | create |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- Designation `placement coordinator` (PD-14) scoped to the institution.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- Criteria schema validated; deadlines enforced server-side.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Salary and offer data restricted to the owner and authorised staff.

## 14. Testing
- Eligibility matrix with boundary values; explanation content; privacy of offers.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- P06 profile, marks
- P10 notifications

## 16. Acceptance criteria
- Eligibility is deterministic and explained.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).
