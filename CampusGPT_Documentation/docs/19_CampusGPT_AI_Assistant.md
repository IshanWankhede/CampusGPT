# 19 — CampusGPT AI Assistant

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P12**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
A ChatGPT-style workspace whose answers are grounded in authorised institutional data and documents; it states when information is unavailable, cites sources, and streams over WebSocket.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | Ask about own attendance, timetable, assignments, marks, notes; get explanations |
| FACULTY | Ask about assigned classes and own documents within scope |
| ADMIN | Ask scoped institutional questions; configure AI settings |

## 3. Functional behaviour
- Conversation sidebar (new, recent, search, rename, delete), message input, attachments, streaming responses, stop generation, regenerate, copy, feedback, suggested questions, citations and document references.
- Real-time transport is **WebSocket** (`/api/v1/ws/chat`): authenticated on connect, typed JSON events for generation status, token deltas, sources, errors and stop; reconnection with backoff (`docs/architecture/WebSocket_Protocol.md`).
- Per request: authenticate → classify intent → call permitted tools / retrieve documents with the caller's permissions → assemble context → generate → attach sources.
- When no authorised source supports an answer, the assistant says so and does not guess.
- Voice interaction is provided through Vapi (doc 37) and always passes through the same backend tools.

## 4. Business rules
- The model never receives data the caller may not see.
- The model never generates SQL; data is fetched by fixed, parameterised, permission-checked tools.
- User text and document text are untrusted and cannot change system rules (prompt-injection defence).
- Conversation history belongs to the user; admins cannot read it without an explicit audited process.
- The LLM and embedding providers are configurable and still pending (PD-11); nothing here names a chosen provider.

## 5. Frontend responsibilities
- Chat workspace per reference 2; WebSocket client with reconnect, stop and error handling; streaming renderer; citation chips; accessible keyboard controls; Lucide icons; AI orb via React Three Fiber only if it adds value (decided in P12 ADR).

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `ai` module: orchestrator, tool registry, prompt builder, provider adapter (PD-11), conversation service, WebSocket endpoint with per-user connection limits.

## 7. Database requirements (PROPOSED)
- conversations(id, user_id, title, created_at, updated_at, deleted_at)
- messages(id, conversation_id, role, content, model, tokens, created_at)
- message_sources(id, message_id, source_type, source_id, chunk_id, score)
- message_feedback(id, message_id, rating, comment, created_at)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| WS | `/api/v1/ws/chat` | any (authenticated on connect) | streaming chat channel |
| POST | `/api/v1/ai/conversations` | any | create |
| GET | `/api/v1/ai/conversations` | any | list own |
| GET | `/api/v1/ai/conversations/{id}/messages` | owner | history |
| POST | `/api/v1/ai/messages/{id}/feedback` | any | rate |
| DELETE | `/api/v1/ai/conversations/{id}` | owner | delete |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- Conversation access limited to owner; every tool call receives the caller identity and re-checks scope; the WebSocket re-validates the token on connect and when it is refreshed.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- Message length caps; attachment validation; per-user rate limits and token budgets; WebSocket message-size and frame-rate limits.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Prompt-injection tests; output sanitisation; no secrets in prompts; provider API key only on the server; logging excludes message bodies by default; origin checks on WebSocket upgrade.

## 14. Testing
- Cross-user leak tests through the assistant; tool-permission tests; adversarial prompts in documents; 'no source' behaviour; WebSocket auth failure, stop generation, reconnect and cleanup.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- P11 documents
- P13 routing
- P14 RAG
- PD-11 provider decision
- PD-18 WebSocket parameters, PD-25 scaling

## 16. Acceptance criteria
- Answers cite authorised sources or say none found.
- No cross-user data in any test.
- WebSocket protocol implemented as documented, with tests for authentication, stop, errors and reconnection.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).
