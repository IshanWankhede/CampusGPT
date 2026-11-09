# 25 — Internships and Hackathons

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P17**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
Faculty/admin-posted internships and hackathons with eligibility, deadlines, stipends, external links, bookmarks, explanations and participation tracking.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | Browse, bookmark, check eligibility, track participation |
| FACULTY | Post opportunities for their scope |
| ADMIN | Manage all |

## 3. Functional behaviour
- Opportunity types INTERNSHIP and HACKATHON share one table with a type field.
- Eligibility reuses the placement rules engine.
- Deadline reminders via notifications.

## 4. Business rules
- External links are validated and opened with `rel=noopener`.
- Expired opportunities are archived automatically.

## 5. Frontend responsibilities
- Cards with filters, bookmarks, tracking list.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `opportunities` module sharing the criteria evaluator with placements.

## 7. Database requirements (PROPOSED)
- opportunities(id, type, title, org, criteria JSON, stipend, deadline, url, created_by)
- opportunity_bookmarks(student_id, opportunity_id)
- opportunity_participation(id, student_id, opportunity_id, status)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/opportunities` | STUDENT | list |
| POST | `/api/v1/opportunities` | FACULTY, ADMIN | create |
| POST | `/api/v1/opportunities/{id}/bookmark` | STUDENT | bookmark |
| PUT | `/api/v1/opportunities/{id}/participation` | STUDENT | track |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- Faculty may edit only their own postings.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- URL scheme allow-list (https).

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Link validation; no HTML in descriptions without sanitisation.

## 14. Testing
- Eligibility explanations; archive job; URL validation.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- P16 rules engine

## 16. Acceptance criteria
- Eligibility consistent with placements.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).
