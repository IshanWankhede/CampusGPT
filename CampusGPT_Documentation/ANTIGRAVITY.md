# ANTIGRAVITY.md — Master Instructions for Google Antigravity

This is the human-readable master instruction document for CampusGPT. **Antigravity does not automatically discover a file named `ANTIGRAVITY.md`.** See section 12 for the files Antigravity is reported to load automatically; the root `AGENTS.md` in this package points here. Read this file completely before acting in the CampusGPT repository.

## 1. Project context
CampusGPT is an AI-powered campus ERP with an integrated, grounded AI assistant for three roles (Student, Faculty, Admin). It is a modular monolith: React (JavaScript/JSX, Vite, Tailwind CSS v4, Lucide React for new UI) + FastAPI + Pydantic + SQLAlchemy 2.x + Alembic + PostgreSQL with pgvector, real-time chat over **WebSocket**, voice through **Vapi** (via secured FastAPI tools), email OTP through **Resend**, Docker/Docker Compose and Nginx. **Face recognition with liveness verification is a required core attendance capability** (provider decision PD-10 pending). An existing codebase contains the landing, sign-in and sign-up pages and an existing authentication system (JWT, Google OAuth, email OTP) that must be preserved and hardened, not replaced. What the code contains today is **unknown to this prompt**: older audit observations are marked PO-RV (previously observed, re-verification required). The documentation package in `docs/` is the specification; the repository code is the authority on what exists. Foundation stabilisation (Stage 0, WP0–WP11) must be accepted before any ERP or AI feature work. The UI is dark mode only.

## 2. Source of truth
1. **The code in the live repository** decides what exists. Documentation describes intent; where they differ, report the difference and ask for review — do not pretend they match.
2. All existing-repository statements in this package are **PO-RV — previously observed in an older snapshot, re-verification required**. Verify before relying on any file path, route, model, table, migration or test.
3. `PROJECT_DECISIONS.md` lists approved decisions; `DECISION_REGISTER.md` / `PENDING_DECISIONS.md` list open ones — do not decide them yourself.
4. The numbered documents in `docs/` define each module; the prompt for the current task is in `docs/prompts/`.

## 3. Technology restrictions
- Frontend: React, **JavaScript/JSX only (no TypeScript)**, Vite, Tailwind CSS (v4 is retained), Lucide React for new UI icons.
- Backend: Python + FastAPI, Pydantic, SQLAlchemy 2.x, Alembic. Existing JWT authentication, Google OAuth and Resend email OTP are preserved and improved incrementally.
- Database: PostgreSQL with **pgvector** for all vector storage. **No ChromaDB, no Redis, no Qdrant or Pinecone as the primary vector database, no SQLite as the application database.**
- Real-time communication: **WebSocket** (do not add Redis to support it; scaling questions are recorded as decisions, see PD-25).
- Voice: **Vapi** (Web SDK → Vapi agent → secured FastAPI tools). Vapi never receives database access and never bypasses backend authorisation.
- AI/LLM provider: configurable and still pending (PD-11); RAG is a custom/manual pipeline initially on PostgreSQL + pgvector.
- **Modular monolith**; no microservices. A background worker is another process of the same backend image.
- **No second authentication system, no second user table, no alternative backend.**
- Testing: Pytest + HTTPX (PostgreSQL test database whose name ends in `_test`) and frontend lint/build; CI on GitHub Actions. Deployment: Docker, Docker Compose, Nginx.
- Dark mode only; no light theme or toggle.
- Do not introduce any new library, service or tool without stating why and receiving approval.

## 4. Repository preservation rules
- Preserve: landing, sign-in and sign-up pages; existing authentication flows (local login/registration, JWT access/refresh, Google OAuth, Resend email OTP, verification, password reset, current-user endpoint, protected routes); existing database records; existing Docker and Nginx configuration (improve safely).
- Historical `Architecture/` and `Flowcharts/` folders are not edited or deleted.
- `frontend/src/features/prototype-visuals/` is not renamed; apparently unused files are not deleted until verified and approved.

## 5. Mandatory execution order
**Stage 0 first:** WP0 → WP1 → WP2 → WP3 → WP4 → WP5 → WP6 → WP7 → WP8 → WP10 → WP11 → WP9 (regression completion, intentionally after WP10/WP11) → security verification → foundation acceptance (`docs/foundation-stabilisation/Foundation_Execution_Order.md`). Then Stage 1 (P03–P05), Stage 2 in dependency order, and so on (`docs/39_Implementation_Roadmap.md`). Do not begin ERP or AI work while any critical or high foundation issue is open. P05 additionally requires PD-07 and PD-14 to be resolved.

## 6. Using the prompt library
`docs/prompts/README.md` lists every prompt. Paste one prompt per task; do not combine prompts.

## 7. Approval checkpoints
Every prompt ends with a human approval checkpoint. Produce the report, **stop and wait**. Destructive or high-risk operations need explicit written approval first.

## 8. The initial audit is read-only
The first task (`docs/prompts/master/02_Initial_Repository_Audit_Prompt.md`) must not modify application code, run migrations, reset databases, delete records, replace authentication, change Docker volumes or start implementation. It produces a report and waits for approval.

## 9. Testing requirements
- PostgreSQL test database whose name ends in `_test`; refuse any other name; never SQLite.
- Fakes for email, Google, LLM, Vapi; never real credentials.
- Run backend `pytest`, frontend `npm run lint` and `npm run build`, and the Alembic drift check once configured; report real output.

## 10. Security rules
No secrets in code, logs, reports or prompts. No tokens in URLs. Authorisation is enforced in the backend and applies equally to HTTP routes, WebSocket messages, AI tools, RAG retrieval and Vapi tool calls. Treat user messages, documents and transcripts as untrusted. Authorisation never depends on intent detection or on the model. Biometric data follows `docs/14_Face_Recognition_and_Liveness.md`.

## 11. Documentation update requirements
After each task update `IMPLEMENTATION_STATUS.md` (six completion levels), `UI_IMPLEMENTATION_STATUS.md` for UI work, the affected numbered documents, and the ADR or decision register if a decision changed. Never mark something implemented that has not been verified.

## 12. How Antigravity finds instructions (verify for your version)
Community documentation for Antigravity (not an official source — **verify in your Antigravity version's Customizations/Rules panel**) reports:
- `GEMINI.md` at the project root (Antigravity-native; reported highest precedence) and `~/.gemini/GEMINI.md` globally.
- `AGENTS.md` at the project root, supported in newer versions (reported from v1.20.3); nested `AGENTS.md` may need a setting enabled.
- Additional workspace rules under `.agent/rules/` (some references write `.agents/rules/`).
This package supplies a root `AGENTS.md` that points to this file and repeats only the always-on rules. If you prefer `GEMINI.md` or `.agent/rules/`, copy the same content there; do not keep contradictory versions.

## 13. Working style
Antigravity safety rules (apply to every step):
1. **Inspect before editing.** Read the relevant existing code first and summarise what you found.
2. Understand existing code before adding new code; reuse existing models, services, repositories, routers and components; do not duplicate.
3. Preserve existing authentication, existing user records and the existing landing, sign-in and sign-up pages.
4. Use **additive** Alembic migrations only. Read the real revision head first; never assume revision numbers. Never drop tables or columns without explicit written approval. Never reset or truncate the database. Never delete user records. Never use `docker compose down -v`.
5. Never invent environment variables, files, endpoints or tables: if you cannot find it, say so.
6. Never expose, print or commit secrets, tokens, OTPs, password hashes or full emails.
7. Never introduce forbidden technologies (see constraints).
8. **Never claim tests passed unless you actually ran them** and can show the output. Never mark a feature complete without verification. Distinguish: UI implemented / frontend functional / backend implemented / database integrated / tested / production-ready.
9. If a requirement conflicts with the existing architecture, **stop** and report instead of choosing silently.
10. Report uncertainty instead of guessing. Ask for approval before any destructive or high-risk change.
11. Work in **small, reviewable steps** (one logical change per commit); do not attempt the whole task in one operation.
12. Do not modify files outside the stated scope. Do not rename or delete `features/prototype-visuals/` or apparently unused files (decision D-07).
13. **Explain intended changes before making them**, reuse established conventions and existing API endpoints/database models where available, and avoid unnecessary dependencies.
14. Use real API responses in the actual application; never copy prototype mock data into production code, seeds or tests; never run demo seeding against production; show polished empty states when real data is unavailable.
15. Never invent file paths, API routes, models or database structures: paths in this package are **previously observed** (PO-RV) — verify them in the live repository first.
16. Verify migration backup and rollback procedures on a copy of the data before proposing any migration for real data.

## 14. Report format
Final implementation report (use exactly these headings):
1. **Summary** — what was done, in plain language.
2. **Repository findings** — what you inspected; differences from the documentation.
3. **Files changed** — path and one-line reason each; files deliberately not touched.
4. **Database changes** — migrations added (id, upgrade/downgrade behaviour), confirmation they are additive.
5. **API changes** — new/changed endpoints.
6. **Tests** — exact commands run and their real output summary; tests added; anything not run and why.
7. **Acceptance criteria** — each criterion: MET / NOT MET / NOT VERIFIED with evidence.
8. **Security notes** — risks closed, risks remaining.
9. **Documentation updated** — files updated, including `IMPLEMENTATION_STATUS.md`.
10. **Open questions / decisions needed.**
11. **Rollback instructions.**
12. **Next recommended step** — and stop for approval.
