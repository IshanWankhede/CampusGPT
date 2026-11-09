# PROJECT_DECISIONS

Approved (or provisionally approved) architectural and product decisions. Unresolved items live in `PENDING_DECISIONS.md`. Detailed rationale is in `docs/architecture/adr/`.

| ID | Decision | Source | Status |
|---|---|---|---|
| D-01 | Frontend uses JavaScript/JSX; TypeScript is not introduced. | S1, S4 §3 | ACCEPTED |
| D-02 | Tailwind CSS v4 is retained. | User decision 1 | ACCEPTED |
| D-03 | New application UI uses Lucide React icons; existing auth pages are not rewritten to use it. | User decision 1 | ACCEPTED |
| D-04 | Existing landing, sign-in and sign-up pages are preserved and not redesigned. | User decision 4, S4 §4 | ACCEPTED |
| D-05 | Multi-college support stays for now; architectural implications (data isolation) are evaluated before more tenant-aware tables are built. | User decision 2 | ACCEPTED (evaluation open: PD-07) |
| D-06 | Faculty accounts need administrator approval; students can never assign themselves privileged roles; public registration creates STUDENT only. | User decision 3, S4 WP2 | ACCEPTED |
| D-07 | `frontend/src/features/prototype-visuals/` is not renamed and apparently unused files are not deleted until references are verified; cleanup comes later. | User decision 5 | ACCEPTED |
| D-08 | AI/ML dependencies (torch, transformers, sentence-transformers and similar) are deferred to the RAG phase; they are moved, not deleted, after usage is re-verified. | User decision 6, S4 WP8 | ACCEPTED |
| D-09 | Foundation stabilisation (Stage 0) completes before any ERP or AI feature work. | S4 §5–6 | ACCEPTED |
| D-10 | PostgreSQL is the only database; pgvector provides vector search; no ChromaDB; no Redis; modular monolith, no microservices. | S1, S4 §3 | ACCEPTED |
| D-11 | The existing authentication system (JWT, Google OAuth, email OTP) is preserved and improved incrementally; no second user system or auth system. | S1, S4 §3 | ACCEPTED |
| D-12 | Migrations run through a dedicated one-shot migration service, not at API start; production migrations are an explicit, backed-up step. | S3 fix 10, S4 WP8 | ACCEPTED |
| D-13 | Minimum JWT secret length is 32 characters; production rejects default, weak or dev secrets. | S4 WP3 | ACCEPTED |
| D-14 | OAuth tokens never appear in redirect URLs; Google login uses a one-time hashed authorisation code exchanged by POST, plus a state/nonce cookie. | S3 fix 4, S4 WP4 | ACCEPTED (parameters provisional) |
| D-15 | Rate limiting is database-backed (`auth_attempts`), with no Redis and no in-memory limiter. | S3 fix 6, S4 WP5 | ACCEPTED (thresholds provisional) |
| D-16 | Refresh tokens are stored server-side (hashed or by `jti`), rotated on use, reuse-detected by token family, and revoked on logout, password reset and deactivation. | S3 fix 7, S4 WP6 | ACCEPTED |
| D-17 | Test database name must end with `_test`; destructive test setup refuses any other name; PostgreSQL (not SQLite) is used for integration tests. | S3 fix 12, S4 WP9 | ACCEPTED (exact name: PD-05) |
| D-18 | Testing stack: Pytest + HTTPX + frontend lint/build; CI on GitHub Actions. | S4 §3 | ACCEPTED |
| D-19 | Dark mode only for the entire application; no light-mode toggle. | S1 Part 7 | ACCEPTED |
| D-20 | Three data environments (AI Studio mock data, dev seed data, production data) are never mixed. | S1 Part 9 | ACCEPTED |
| D-21 | Access token lifetime starts at 15 minutes (currently 30 in code). | S3, S4 WP6 | PROVISIONAL (PD-03) |
| D-22 | localStorage is kept as an interim token store; HttpOnly/Secure/SameSite cookies with CSRF protection are the evaluated production target. | S3, S4 WP6 | PROVISIONAL (PD-04, PD-23) |
| D-23 | The deliverable archive is named exactly `CampusGPT_Final_Corrected_Documentation.zip` (the earlier archive is superseded). | Final correction instruction | ACCEPTED |
| D-24 | Face recognition with liveness verification is a **required** core attendance capability (not optional). The provider and biometric policies remain pending (PD-10) and production enablement waits for PD-10 and a privacy/legal review. | Final correction instruction §3A | ACCEPTED (provider PENDING) |
| D-25 | WebSocket is the intended real-time communication approach for chat and live attendance; SSE is not an alternative primary architecture; Redis is not added to support it. | Final correction instruction §3C | ACCEPTED (parameters PD-18, scaling PD-25) |
| D-26 | Vapi is the intended voice integration: React → Vapi Web SDK → Vapi agent → secured FastAPI tools → PostgreSQL/pgvector. Vapi never receives database access and never bypasses backend authorisation. | Final correction instruction §3B | ACCEPTED (deployment details PD-19) |
| D-27 | Email OTP uses Resend; AI/LLM provider is configurable and pending; RAG is a custom/manual pipeline initially on PostgreSQL + pgvector. | Final correction instruction §2 | ACCEPTED (providers PD-11, PD-22) |
| D-28 | Qdrant, Pinecone, SQLite as an application database, a second auth system, a second user table, and an alternative backend are prohibited recommendations. | Final correction instruction §2 | ACCEPTED |
| D-29 | Statements about the existing repository are PO-RV (previously observed, re-verification required) until a current audit confirms them; the codebase is the source of truth for what exists. | Final correction instruction §9 | ACCEPTED |
| D-30 | PD-07 (multi-college isolation) and PD-14 (designations/permissions) must be resolved **before** P05; they are not deferred to integration. | Final correction instruction §8 | ACCEPTED |

## Explicit exclusions

TypeScript, ChromaDB, Redis, microservices, a replacement authentication system, a second user table, SQLite as a test or production database, and a light theme are **not** part of CampusGPT. Any proposal to add them requires an ADR and explicit approval.
