# AGENTS.md — CampusGPT agent rules (pointer)

This file is the entry point for coding agents that load `AGENTS.md` automatically. The full, authoritative instructions are in **`ANTIGRAVITY.md`** (read it first) and the prompt library in `docs/prompts/`. This file only repeats the always-on rules; if anything here ever disagrees with `ANTIGRAVITY.md`, stop and ask.

## Always-on rules
1. **Inspect before editing.** The code is the source of truth. Anything about the existing repository in the docs is *previously observed — re-verify*; never invent file paths, routes, models, tables or environment variables.
2. **Start with the read-only audit** (`docs/prompts/master/02_Initial_Repository_Audit_Prompt.md`): no code changes, no migrations, no database resets, no deletions, no Docker volume changes. Report, then wait for approval.
3. **Foundation first:** Stage 0 (WP0–WP11, in `docs/foundation-stabilisation/Foundation_Execution_Order.md`) before any ERP or AI feature work. One prompt at a time; stop at each approval checkpoint.
4. **Stack is fixed:** React JavaScript/JSX (no TypeScript), Vite, Tailwind CSS, Lucide React; FastAPI, Pydantic, SQLAlchemy 2.x, Alembic; PostgreSQL + pgvector; WebSocket for real-time; Vapi for voice through secured FastAPI tools; Docker/Compose/Nginx. **No Redis, ChromaDB, Qdrant/Pinecone, SQLite as app DB, microservices, second auth system or second user table.**
5. **Preserve** the existing authentication, user records, landing/sign-in/sign-up pages, historical `Architecture/` and `Flowcharts/`, and `frontend/src/features/prototype-visuals/`.
6. **Database safety:** additive Alembic migrations only; never drop, truncate, reset or delete data; back up and rehearse rollback on a copy first.
7. **Security:** authorisation in the backend for routes, WebSocket messages, AI tools, RAG and Vapi tool calls; never trust frontend roles; no secrets or tokens in code, logs or URLs.
8. **Face recognition attendance with liveness is a required feature**; the provider is pending (PD-10) — never claim a provider or present simulation as real verification.
9. **Honesty:** never claim a feature is done or a test passed unless it was implemented and actually run; report real output.
10. Dark mode only. Prototype mock data never enters production; seed data never runs in production.
