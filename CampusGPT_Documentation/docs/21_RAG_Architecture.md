# 21 — RAG Architecture

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P14**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
PostgreSQL + pgvector retrieval-augmented generation that respects document permissions and produces cited, grounded answers.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | Retrieve from authorised and personal documents |
| FACULTY | Retrieve from own and class documents |
| ADMIN | Manage index, view processing health |

## 3. Functional behaviour
- Chunks carry document, version, subject, unit/topic, page/section, audience metadata.
- Hybrid retrieval: vector similarity plus PostgreSQL full-text search, merged; reranking only if evaluation shows benefit.
- Permission filtering is part of the SQL (join against the same ACL used by document download).
- Context assembly respects a token budget and preserves source ids for citations.
- Grounded generation instructions: answer only from context, cite, say 'not found' otherwise.

## 4. Business rules
- No ChromaDB, no Redis, no separate vector database.
- Re-index on new version; delete chunks when a document or version is deleted.
- Evaluation set maintained: retrieval hit-rate and groundedness checks.

## 5. Frontend responsibilities
- Citation chips linking to document preview and page.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `rag` module: chunker, embedder interface, retriever, context builder, evaluation scripts.

## 7. Database requirements (PROPOSED)
- document_chunks(id, document_id, version_id, ordinal, text, page, section, metadata JSON, embedding vector(N), tsv tsvector)
- embedding_models(id, name, dimension, active)
- retrieval_evaluations(id, query, expected_chunk_ids, result_ids, hit, created_at)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/rag/search` | any | permission-filtered retrieval (also used internally) |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- Retriever signature requires the caller; there is no code path without a permission filter.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- Embedding dimension equals column dimension; chunk size bounds.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Prompt injection: retrieved text is delimited and treated as data; filters use parameterised queries; no cross-user chunks.

## 14. Testing
- Permission-filter tests with two users and overlapping content; deletion propagation; versioning; golden retrieval set.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- WP1 pgvector extension
- P11
- PD-11
- AI dependencies installed from `requirements-ai.txt`

## 16. Acceptance criteria
- Unauthorised chunks are never returned.
- Retrieval evaluation meets the agreed threshold.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).
