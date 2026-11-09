# 00 — Source Reconciliation and Baseline

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

This document records how the three mandatory inputs were combined, where they disagreed, and how each disagreement was resolved. Nothing here changes the original product vision; it only fixes the order of work and corrects facts.

## 1. Inputs

| # | Input | Role in this package |
|---|---|---|
| S1 | Original CampusGPT Master Prompt (22 parts) | Product vision, 17 modules, RBAC, UI direction, data environments, 25-phase roadmap, working rules |
| S2 | Repository audit (10 sections) | Source of truth for what exists today and what is defective |
| S3 | Foundation Stabilisation Remediation Plan (12 fixes + work packages) | Security, database and infrastructure remediation, testing strategy, sequence |
| S4 | Definitive Master Documentation Instruction | Package structure, fixed stack, WP0–WP11, prompt library, 40 documents |

Precedence when sources disagree: **repository audit (what exists) > user decisions recorded in `PROJECT_DECISIONS.md` > S4 > S3 > S1** for implementation order; **S1 > S4** for product scope (nothing in S1 is dropped).

## 2. Conflicts and how they were resolved

| ID | Conflict | Resolution |
|---|---|---|
| X1 | S1 Part 17 lists 41 documentation topics; S4 lists 40 files | All 40 S4 files are produced. The S1 topic list is mapped onto them in `docs/architecture/01_Traceability_Matrix.md`; no S1 topic is dropped (S1's "Docker and deployment" and "Monitoring" map to docs 30 and 31, "Existing project integration" to doc 38, and so on). |
| X2 | S1 Module 7 supports PDF, DOCX, PPTX, XLSX; S4 §7.9 names PDF and DOCX only | Preserve all four formats as requirements. Implementation order: PDF and DOCX first, PPTX and XLSX after (PENDING_DECISIONS PD-09). |
| X3 | S1 expects violet/indigo/teal dark palette; audit found existing landing/auth pages are monochrome black/white | Existing pages are preserved untouched (user decision). The new application shell follows the S1 palette. Palette bridge is PENDING (PD-16). |
| X4 | S1 asks for Framer Motion, GSAP, React Three Fiber; audit found `motion` (renamed Framer Motion), `gsap`, `lenis`, `ogl` installed; R3F absent | Keep installed libraries. Add R3F only when the AI orb is built (Phase 12/22), with an ADR note. |
| X5 | Multi-college support exists in code but is absent from S1 | Retained (user decision). Data-isolation design is PENDING (PD-07). New tables must not block either outcome. |
| X6 | S3 numbered migrations `0006`–`0011`; S4 forbids assuming revision numbers | All migration numbers in this package are **illustrative**. Antigravity must read the real Alembic head first and use the next revision id. |
| X7 | S3 proposed 30-minute vs 15-minute access token; S4 says "initially 15 minutes" and also lists it as pending | 15 minutes is a **provisional default** (PD-03). Existing value in code is 30 minutes. |
| X8 | S3 said unused AI/ML dependencies can move to an optional requirements file; S4 says do not remove dependencies until usage is inspected | Audit grep found no imports in the snapshot, but WP8 prompt requires Antigravity to re-verify imports on HEAD before moving anything. |
| X9 | S4 CI scope includes "backend linting"; the repository has no linter | A linter must be chosen (proposal: Ruff). PENDING (PD-08). CI lint step is gated on that decision. |
| X10 | S1 and old `README.md` / `Architecture/PHASES.md` use different phase numberings (25 phases vs 11 phases) | The 25-phase roadmap (S1) with Stage 0 prepended is authoritative. Old `Architecture/*.md` are historical and are not edited or deleted. |
| X11 | S1 Part 16 proposes `docs/`, `ui-reference/`, `database/development-seed/`; repo has `Architecture/`, `Flowcharts/`, and `.gitignore` ignores `Prototype/` | Keep existing folders. Add `docs/` from this package. Add `ui-reference/` to `.gitignore` only when it is created (and note Git-ignore does not hide it from Antigravity). |
| X12 | S1 names five reference images; none were supplied to the generator | Images are not invented. `assets/references/README.md` states where the five images must be placed. |
| X13 | S4 asks to preserve "original ADRs" and "original Google AI Studio prompts"; S1 contains neither as ready text (only the strategy) | They are authored here from S1's stated requirements and labelled "authored from S1; no earlier text existed". |
| X14 | S1 asks for streaming responses; the old README mentions "WebSocket / Server-Sent Events"; the first package draft recommended SSE | **Resolved by the owner's final instruction:** WebSocket is the intended real-time approach everywhere (PD-18 direction confirmed; protocol parameters pending; multi-worker scaling PD-25). SSE is not documented as an alternative. |
| X15 | The first package draft described face recognition as optional/conditional | **Corrected:** face recognition with liveness is a required core attendance capability (doc 13, doc 14). Only the provider (PD-10) and production enablement are pending. |
| X16 | The first package draft described browser-native speech as the main voice direction | **Corrected:** Vapi is the intended voice integration (doc 37, PD-19 direction confirmed; deployment details pending). Vapi never bypasses the FastAPI backend. |
| X17 | The first package presented audit findings as "audit-reported" facts | **Corrected:** they are PO-RV (previously observed in an older snapshot, re-verification required). |
| X18 | The first package's `README.md` would collide with a project's own README on copy | **Corrected:** see the integration/merge rules in `README.md` (now named for safe copying) and `docs/00_Package_Integration_Guide.md`. |

## 3. Requirement extraction summary

S1 requirement groups and where each is documented:

- 17 modules (Part 5) → docs 02, 03, 13–27, 37 and phases P04–P22.
- RBAC (Part 6) → docs 11, 12, 28.
- Visual identity and prototype strategy (Parts 7–8) → docs 33–36 and the AI Studio prompt.
- Three data environments (Part 9–10) → doc 32.
- Backend, database, API, security (Parts 11–14) → docs 05, 07, 08, 09, 10, 28.
- Workflow and structure (Parts 15–16) → docs 38, 39, `ANTIGRAVITY.md`.
- 25-phase roadmap (Part 18) → doc 39 and `docs/prompts/phases/`.
- Working rules (Part 19) → `ANTIGRAVITY.md` safety rules, repeated in every prompt.

## Repository baseline — PO-RV (previously observed in an older snapshot; re-verification required)

| Area | Previously observed finding (older snapshot) | Previously observed status — re-verification required |
|---|---|---|
| Layout | `Architecture/` (7 old planning .md), `Flowcharts/` (4 HTML), `backend/`, `frontend/`, `docker-compose.yml`, `.env.example`, `README.md` | IMPLEMENTED (PO-RV) |
| Backend | FastAPI app `backend/app/main.py`; single feature module `auth/` (router, service, repository, schemas); `core/` (config, dependencies, email); `database/` (base, session); `models/` (user, otp_verification); `create_admin.py` CLI | IMPLEMENTED (PO-RV) |
| Database | PostgreSQL 16 + pgvector image in compose; tables `users`, `otp_verifications`; Alembic revisions `0001`, `0002_add_email_verification`, `0003`, `0004`, `0005` (linear) | IMPLEMENTED (PO-RV) |
| Auth | JWT access + refresh (HS256), bcrypt via passlib, email OTP via Resend, Google OAuth via direct `httpx` calls, college-domain restriction | IMPLEMENTED BUT DEFECTIVE (PO-RV) |
| RBAC | `UserRole` ADMIN/FACULTY/STUDENT; `get_current_user`, `require_role` (used only by `/auth/admin-test`) | PARTIALLY IMPLEMENTED (PO-RV) |
| Multi-college | `CollegeName` enum COEP/PICT/VIT, `users.college`, `COLLEGE_DOMAIN_MAP` | IMPLEMENTED (PO-RV) (outside original master prompt; isolation design PENDING APPROVAL) |
| Frontend | React 19, Vite 8, Tailwind v4, `react-router-dom` 7, `motion`, `gsap`, `lenis`, `ogl`, `react-icons`; JavaScript/JSX only | IMPLEMENTED (PO-RV) |
| Frontend routes | `/`, `/auth`, `/auth/callback`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/verify-email` (possibly orphaned), `/app` (placeholder) | PARTIALLY IMPLEMENTED (PO-RV) |
| Lucide React / React Three Fiber | Not installed | NOT IMPLEMENTED |
| ERP modules, RAG, AI chat, analytics, voice, seed data | Absent | NOT IMPLEMENTED |
| Tests / CI / logging / audit log | Absent (README mentions GitHub Actions; no workflow exists) | NOT IMPLEMENTED |
| pgvector extension migration | Not in migrations (enabled manually per old PHASES.md); Python `pgvector` package unused | NOT IMPLEMENTED |
| Alembic `env.py` model registration | Models are not imported, so autogenerate sees empty metadata | IMPLEMENTED BUT DEFECTIVE (PO-RV) |
| Docker | Dev-oriented compose only; `alembic upgrade head` runs in API start command and Dockerfile CMD; backend runs as root; DB port published on all host interfaces | IMPLEMENTED BUT DEFECTIVE (PO-RV) |

### Existing HTTP API (previously observed — PO-RV)

`GET /health`; under `/api/v1/auth`: `POST /register`, `POST /login`, `POST /refresh`, `POST /logout` (no-op), `GET /me`, `GET /admin-test`, `POST /send-otp`, `POST /verify-otp`, `POST /forgot-password`, `POST /reset-password`, `GET /google/login`, `GET /google/callback`.

### Defects found by the older audit (PO-RV — confirm each on the live code first; do not treat as confirmed)

| ID | Defect | Where | Remediation |
|---|---|---|---|
| C1 | Google-created users (null password hash) can log in with any password | `auth/service.py::authenticate_user` | WP2 |
| C2 | Five wrong OTP guesses set `is_used`, which registration treats as "email verified" | `service.verify_otp`, `repository.has_recent_used_email_otp` | WP2 |
| C3 | Public `/register` accepts `role` = ADMIN/FACULTY | `auth/schemas.py::RegisterRequest`, `service.register_user` | WP2 |
| H1 | Google callback puts access and refresh tokens in the redirect URL | `router.google_callback`, `AuthContext.jsx` | WP4 |
| H2 | Public default JWT secret and SQLite default; no production guard | `core/config.py::Settings` | WP3 |
| H3 | No login/OTP rate limiting; OTP guess counter resets per new code | `auth/router.py` | WP5 |
| H4 | Refresh tokens not rotated or revocable; `/logout` is a no-op; frontend never refreshes | `auth/service.py`, `AuthContext.jsx` | WP6, WP7 |
| M1 | `alembic/env.py` does not import models | `alembic/env.py` | WP1 |
| M2 | Auto-migration at API start; dev credentials hardcoded in four places | compose, Dockerfile, `.env.example`, README | WP3, WP8 |


## 4. Facts the generator could not establish

- Live repository HEAD (only a snapshot was audited).
- Whether any real user accounts exist, and how many are non-student (needs WP0 preflight queries).
- Whether the live database already has the `vector` extension.
- Real production email domains for COEP, PICT and VIT.
- Hosting target, domain name and HTTPS plan.
- LLM provider, embedding model and dimension, file-storage backend.
- Whether `frontend/src/features/auth/AuthPage.jsx`, `features/landing/LandingPage.jsx` and the `/auth/verify-email` route are truly unreferenced (imports found none; runtime not checked).
