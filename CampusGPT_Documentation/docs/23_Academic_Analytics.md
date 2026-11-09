# 23 — Academic Analytics

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P15**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
Internal and exam marks, assignment performance, attendance trends, SGPA/CGPA, strengths, weaknesses and risk indicators — computed from stored data only.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | Own analytics |
| FACULTY | Class-level and assigned-student analytics |
| ADMIN | Department and institution analytics |

## 3. Functional behaviour
- Trends over time, subject comparisons, assignment score distributions, attendance vs performance views.
- Risk indicators from transparent rules (for example attendance below threshold plus falling marks) with the rule shown.
- Predictions are shown only when sufficient data exists and are labelled as estimates with the method; otherwise 'insufficient data'.

## 4. Business rules
- No fabricated or unsupported predictions.
- Aggregates for small groups suppress identifying detail (minimum group size configurable).

## 5. Frontend responsibilities
- Chart cards (reference 4), drill-downs, empty states.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `analytics` module: SQL aggregations and pure calculation functions.

## 7. Database requirements (PROPOSED)
- Uses marks, attendance and assignment tables; optional materialised views (PROPOSED)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| GET | `/api/v1/analytics/me` | STUDENT | own |
| GET | `/api/v1/analytics/classes/{id}` | FACULTY | class |
| GET | `/api/v1/analytics/institution` | ADMIN | institution |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- Scope derived server-side.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- Date-range and group parameters validated.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Small-group suppression; no cross-student data to students.

## 14. Testing
- Calculation fixtures; permission tests; insufficient-data behaviour.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- P07, P09, marks data

## 16. Acceptance criteria
- Every number traces to stored records.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).
