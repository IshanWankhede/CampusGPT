# 22 — Document Ingestion and Retrieval Pipeline

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P14**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
Step-by-step pipeline from upload to cited answer, including OCR for scans, table extraction, chunking, embedding, retries and failure handling.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | Sees processing status for own uploads |
| FACULTY | Sees status and failures for class documents; can retry |
| ADMIN | Operates the pipeline |

## 3. Functional behaviour
- Stages: upload → validate → store → parse → OCR if needed → normalise → sections → tables → semantic chunking → metadata → embed → store vectors → ready.
- Jobs are rows in `document_processing_jobs`, claimed with `SELECT … FOR UPDATE SKIP LOCKED` by a worker process in the same codebase (no Redis, no external queue).
- Retries with backoff and a maximum; permanent failures surfaced with a reason.
- Retrieval: embed query → permission-filtered hybrid search → (optional rerank) → context assembly → generation → citations.

## 4. Business rules
- Each stage is idempotent and re-runnable.
- Parsing runs with CPU/memory/time limits.
- Ingestion never makes a document visible beyond its ACL.

## 5. Frontend responsibilities
- Status badges, retry action, failure message.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- Worker entrypoint (separate Compose service, same image) — a process type, not a microservice.

## 7. Database requirements (PROPOSED)
- document_processing_jobs (see doc 18)
- document_chunks (see doc 21)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/documents/{id}/reprocess` | FACULTY, ADMIN | retry processing |
| GET | `/api/v1/documents/{id}/processing` | owner, FACULTY, ADMIN | status |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- Same ACL as documents.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- Reject encrypted or corrupt files with a clear error; page and size limits.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Sandboxed parsing; no execution of macros; strip active content.

## 14. Testing
- Failure injection per stage; retry; idempotency; OCR sample; large-file limits.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- P11
- P14 libraries (PyMuPDF etc. via requirements-ai)

## 16. Acceptance criteria
- Every failure is visible and retryable.
- Pipeline is restartable without duplicates.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).

## 17. Complete pipeline checklist (all 20 stages)
1 file upload validation · 2 secure storage · 3 parsing of PDF, DOCX, PPTX and XLSX (delivery order PD-09) · 4 OCR when needed · 5 text normalisation · 6 table and section extraction · 7 semantic chunking · 8 metadata assignment · 9 embedding generation (provider and **vector dimension pending PD-11**) · 10 pgvector storage · 11 hybrid retrieval · 12 reranking (only if evaluation shows benefit) · 13 context assembly · 14 grounded generation · 15 source citations · 16 **feedback collection** (`message_feedback` ratings linked to the cited chunks; low-rated answers feed the evaluation set, never automatic changes) · 17 document reindexing (on new version, on model/dimension change, on parser upgrade) · 18 version management (a new version supersedes the previous for retrieval; old versions kept per retention rule) · 19 permission-aware retrieval (filters inside the SQL) · 20 deletion and reprocessing workflows (deleting a document/version removes chunks and embeddings; reprocessing is idempotent and retryable).
