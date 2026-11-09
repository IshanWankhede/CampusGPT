# 18 — Document Management

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P11**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
Institutional and personal academic document library (PDF, DOCX; PPTX and XLSX per PD-09) organised by department, branch, year, semester, subject, unit and topic, with versions, access control and processing status; documents become RAG sources.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | Browse authorised documents; upload personal documents; preview/download |
| FACULTY | Upload and version documents for assigned subjects; set audience |
| ADMIN | Manage all documents, retention and deletion |

## 3. Functional behaviour
- Upload → validate → store → register metadata → queue processing (extract/index, P14).
- Processing status shown per document (pending, processing, indexed, failed with reason).
- Version management: a new version supersedes the previous for retrieval; older versions kept per retention rule.
- Deletion propagates to chunks and embeddings.

## 4. Business rules
- Personal uploads are visible only to the owner (and not to faculty unless shared).
- Institutional documents follow audience rules (department/subject/role).
- Retention and deletion rules are explicit and logged.

## 5. Frontend responsibilities
- Library with folders by hierarchy (reference 5), preview, upload, version history, processing badges.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `documents` module with a storage interface and an ACL service reused by RAG.

## 7. Database requirements (PROPOSED)
- documents(id, owner_id, title, kind, department_id, branch_id, year_id, semester_id, subject_id, unit, topic, visibility, current_version_id)
- document_versions(id, document_id, file_id, version_no, sha256, size, mime, created_at)
- document_acl(id, document_id, principal_type, principal_id, permission)
- document_processing_jobs(id, version_id, status, attempts, error, started_at, finished_at)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/documents` | FACULTY, ADMIN, STUDENT | upload (multipart) |
| GET | `/api/v1/documents` | any | authorised list with filters |
| GET | `/api/v1/documents/{id}/download` | any | authorised download |
| POST | `/api/v1/documents/{id}/versions` | owner, FACULTY | new version |
| DELETE | `/api/v1/documents/{id}` | owner, ADMIN | delete (propagates) |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- One ACL function used by listing, download and retrieval so RAG cannot bypass it.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- Type allow-list, magic-byte check, size cap, decompression-bomb limits for Office formats, filename sanitisation.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Parsers run with resource limits; documents are untrusted input (prompt-injection risk handled in doc 21).

## 14. Testing
- IDOR on download; personal document isolation; version supersede; deletion removes chunks; malformed file handled.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- Storage backend (PD-12)
- P14 for indexing

## 16. Acceptance criteria
- ACL enforced in one place.
- Processing state visible and retryable.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).
