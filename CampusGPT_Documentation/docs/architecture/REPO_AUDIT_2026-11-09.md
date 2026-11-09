# Technical Repository Audit Report — Live HEAD Baseline

**Audit Date:** 2026-11-09  
**Repository Branch / Commit:** `main` (clean working tree, commit `09e1aa7`)  
**Auditor:** Google Antigravity Agent  
**Execution Context:** Strictly read-only audit in compliance with `docs/prompts/master/02_Initial_Repository_Audit_Prompt.md` and `docs/architecture/00_Source_Reconciliation_and_Baseline.md`.

---

## 1. Executive Summary

A comprehensive, strictly read-only technical audit of the live CampusGPT repository HEAD was conducted on 2026-11-09. The codebase represents an early-stage modular monolith foundation containing an initial authentication subsystem, landing page, and authentication user flows. 

Every statement previously documented as **PO-RV (Previously Observed, Re-Verification Required)** has been verified directly against live source code. All 10 specific security and architectural defects (C1–C3, H1–H4, M1–M2) previously hypothesized have been **confirmed on the live codebase**. No academic ERP modules, real-time WebSocket communication, pgvector extension migrations, RAG retrieval pipelines, or automated test suites exist in the application code today.

---

## 2. Answers to Mandatory Audit Questions

| Audit Question | Verified Live Fact | Status / Evidence |
|---|---|---|
| **JavaScript vs. TypeScript?** | **JavaScript / JSX only** in production frontend. TypeScript is isolated to the prototype. | `frontend/package.json` contains no TypeScript compile dependencies. All source files in `frontend/src/` use `.js` and `.jsx`. `ui-prototype/` uses TypeScript (`.ts`, `.tsx`), but is strictly a prototype. |
| **Tailwind configured and used?** | **Yes, Tailwind CSS v4** is configured and active. | `tailwindcss` (^4.3.3) and `@tailwindcss/vite` (^4.3.3) in `frontend/package.json`. Configured via `plugins: [tailwindcss()]` in `frontend/vite.config.js` and `@import "tailwindcss";` in `frontend/src/index.css`. |
| **Multi-college implemented?** | **Partially in schema / auth**, but no data isolation. | `CollegeName` enum (`COEP`, `PICT`, `VIT`) defined in `backend/app/models/user.py`. `users.college` column exists. Domain validation in `auth/service.py`. No multi-tenant data isolation exists across any tables (blocked on PD-07). |
| **Resend used for OTP?** | **Yes.** | `resend==2.21.0` in `backend/requirements.txt`. Used in `backend/app/core/email.py` for verification and password reset emails. |
| **Compose auto-migration?** | **Yes (Defective M2).** | `docker-compose.yml` line 32 executes `alembic upgrade head && uvicorn ...`. `backend/Dockerfile` line 15 also executes `alembic upgrade head` on start. |
| **Credentials isolation?** | **Defective / Unsafe.** | Hardcoded credentials `campusgpt:campusgpt_dev` present in `docker-compose.yml`, `.env.example`, and default weak secret in `backend/app/core/config.py`. |

---

## 3. Project Structure

```
d:\Codes\Projects\CampusGPT\
├── .env.example                               # Sample environment variables with dev credentials
├── .gitignore                                 # Git ignore (ignores venv, node_modules, .env, ui-prototype/, prompts/)
├── docker-compose.yml                         # Container services: campusgpt_db (pgvector/pg16), backend, frontend
├── LICENSE                                    # MIT License
├── README.md                                  # Repository documentation (overview, features, tech stack)
├── backend/
│   ├── .dockerignore
│   ├── .env                                   # Local development env (git-ignored)
│   ├── alembic.ini                            # Alembic configuration
│   ├── Dockerfile                             # Python 3.11-slim container with PyTorch CPU & auto-migration CMD
│   ├── requirements.txt                       # Python dependencies (includes ML libraries, excludes pytest)
│   ├── alembic/
│   │   ├── env.py                             # Alembic runner (DEFECT M1: models not imported)
│   │   ├── script.py.mako
│   │   └── versions/                          # 5 linear revisions: 0001 -> 0002 -> 0003 -> 0004 -> 0005
│   └── app/
│       ├── create_admin.py                    # CLI admin bootstrapper
│       ├── main.py                            # FastAPI entry point, CORS, /health endpoint
│       ├── auth/                              # Authentication module (repository, router, schemas, service)
│       ├── core/                              # Config, dependencies (get_current_user, require_role), email
│       ├── database/                          # SQLAlchemy Base and session factory
│       └── models/                            # User and OtpVerification models
├── frontend/
│   ├── .dockerignore
│   ├── .gitignore
│   ├── Dockerfile, Dockerfile.dev             # Container build files
│   ├── eslint.config.js                       # ESLint flat config
│   ├── index.html
│   ├── nginx.conf
│   ├── package.json, package-lock.json        # React 19, Vite 8, Tailwind v4, Motion, GSAP, Lenis, OGL
│   ├── vite.config.js                         # Vite config with @tailwindcss/vite and /api proxy
│   └── src/
│       ├── App.jsx, main.jsx, index.css
│       ├── context/AuthContext.jsx            # Token storage in localStorage, URL param token extraction (H1)
│       ├── routes/AppRoutes.jsx               # React Router routes (/ , /auth, /auth/callback, /app, etc.)
│       └── features/
│           ├── auth/                          # Auth views (VerifyEmail, ForgotPassword, ResetPassword; AuthPage unreferenced)
│           ├── dashboard-placeholder/         # Minimal placeholder dashboard for /app
│           ├── landing/                       # LandingPage.jsx (unreferenced in AppRoutes)
│           └── prototype-visuals/             # Active LandingPage, AuthScreen, SmoothScroll, Strands, etc.
├── flowcharts/                                # Interactive HTML flowcharts for auth workflows
├── CampusGPT_Documentation/                   # 40 core specification documents, ADRs, work packages, prompts
└── ui-prototype/                              # Google AI Studio generated prototype (TypeScript, mockData, Bun)
```

---

## 4. Detailed Component Audit

### 4.1 Frontend (`frontend/`)

* **Technology & Tooling:** React 19.2.8, Vite 8.2.0, Tailwind CSS v4.3.3 (`@tailwindcss/vite`), JavaScript/JSX only.
* **Animation & Visual Libraries:** `motion` (12.43.0), `gsap` (3.15.0), `lenis` (1.3.26), `ogl` (1.0.11), `react-icons` (5.7.0).
* **Missing UI Libraries:** `lucide-react` is **not installed** (planned for new UI under D-03); `@react-three/fiber` / `three` is **not installed** (deferred to Phase 12).
* **Routing (`frontend/src/routes/AppRoutes.jsx`):**
  * `/` -> [`features/prototype-visuals/LandingPage.jsx`](file:///d:/Codes/Projects/CampusGPT/frontend/src/features/prototype-visuals/LandingPage.jsx) (**IMPLEMENTED**)
  * `/auth` -> [`features/prototype-visuals/AuthScreen.jsx`](file:///d:/Codes/Projects/CampusGPT/frontend/src/features/prototype-visuals/AuthScreen.jsx) (**IMPLEMENTED**)
  * `/auth/callback` -> [`features/prototype-visuals/AuthScreen.jsx`](file:///d:/Codes/Projects/CampusGPT/frontend/src/features/prototype-visuals/AuthScreen.jsx) (**IMPLEMENTED**)
  * `/auth/forgot-password` -> [`features/auth/ForgotPassword.jsx`](file:///d:/Codes/Projects/CampusGPT/frontend/src/features/auth/ForgotPassword.jsx) (**IMPLEMENTED**)
  * `/auth/reset-password` -> [`features/auth/ResetPassword.jsx`](file:///d:/Codes/Projects/CampusGPT/frontend/src/features/auth/ResetPassword.jsx) (**IMPLEMENTED**)
  * `/auth/verify-email` -> [`features/auth/VerifyEmail.jsx`](file:///d:/Codes/Projects/CampusGPT/frontend/src/features/auth/VerifyEmail.jsx) (**IMPLEMENTED BUT LIKELY ORPHANED**)
  * `/app` -> [`features/dashboard-placeholder/DashboardPlaceholder.jsx`](file:///d:/Codes/Projects/CampusGPT/frontend/src/features/dashboard-placeholder/DashboardPlaceholder.jsx) (**PLACEHOLDER ONLY**)
* **State Management & Session:** [`frontend/src/context/AuthContext.jsx`](file:///d:/Codes/Projects/CampusGPT/frontend/src/context/AuthContext.jsx)
  * Stores `{ access_token, refresh_token, user }` in `localStorage` under `campusgpt.auth`.
  * Defect H1 confirmed: lines 34–40 parse `access_token` and `refresh_token` directly from `window.location.search`.
  * Defect H4 confirmed: `refresh_token` is stored but never utilized for token refresh upon 401 expiration; `logout` makes a best-effort call to `/logout` but clears localStorage regardless.
* **Orphaned / Unreferenced Code:**
  * [`frontend/src/features/auth/AuthPage.jsx`](file:///d:/Codes/Projects/CampusGPT/frontend/src/features/auth/AuthPage.jsx) is not referenced by `AppRoutes.jsx` (preserved per D-07).
  * [`frontend/src/features/landing/LandingPage.jsx`](file:///d:/Codes/Projects/CampusGPT/frontend/src/features/landing/LandingPage.jsx) is not referenced by `AppRoutes.jsx` (preserved per D-07).

### 4.2 Backend (`backend/`)

* **Framework & Core:** FastAPI 0.141.1, Pydantic 2.13.4, SQLAlchemy 2.0.52, Alembic 1.19.1.
* **Dependencies:** `backend/requirements.txt` contains heavy ML dependencies: `torch==2.13.0`, `transformers==5.15.1`, `sentence-transformers==6.0.0`, `scikit-learn==1.9.0`, `scipy==1.17.1`, `pymupdf==1.28.2`, `pgvector==0.5.0`.
* **Testing Dependencies:** `pytest`, `pytest-asyncio`, and `httpx` (as test client) are **missing** from `requirements.txt` (`httpx` is only present as runtime dependency for OAuth).
* **Entry Point (`backend/app/main.py`):**
  * Configures CORS using `settings.CORS_ORIGINS`.
  * Includes only `auth_router` under prefix `/api/v1/auth`.
  * Provides `GET /health` returning status and environment.

### 4.3 Database and Migrations (`backend/alembic/`)

* **Database Engine:** PostgreSQL 16 via Docker (`pgvector/pgvector:pg16`).
* **ORM Architecture:** Declarative Base (`app/database/base.py`).
* **Models:**
  * `User` ([`backend/app/models/user.py`](file:///d:/Codes/Projects/CampusGPT/backend/app/models/user.py)): `users` table. Columns: `id`, `email`, `hashed_password`, `full_name`, `role`, `college`, `auth_provider`, `google_id`, `profile_picture`, `is_active`, `is_email_verified`, `created_at`, `updated_at`.
  * `OtpVerification` ([`backend/app/models/otp_verification.py`](file:///d:/Codes/Projects/CampusGPT/backend/app/models/otp_verification.py)): `otp_verifications` table. Columns: `id`, `user_id`, `email`, `otp_hash`, `purpose`, `expires_at`, `attempts`, `is_used`, `created_at`.
* **Alembic Revisions (`backend/alembic/versions/`):**
  1. `0001` (`0001_create_users.py`): Initial `users` table with `user_role` enum.
  2. `0002_add_email_verification` (`0002_add_email_verification.py`): Adds `is_email_verified` to `users`, creates `otp_verifications` table with `otp_purpose` enum.
  3. `0003` (`0003_allow_pending_email_otps.py`): Makes `otp_verifications.user_id` nullable, adds `otp_verifications.email` and composite indices.
  4. `0004` (`0004_add_college_and_auth_provider.py`): Adds `college_name` enum, `auth_provider` enum, and adds `college`, `auth_provider`, `google_id`, `profile_picture` to `users`.
  5. `0005` (`0005_alter_profile_picture_to_text.py`): Alters `profile_picture` from VARCHAR(255) to TEXT.
* **pgvector Extension Status:**
  * The `vector` PostgreSQL extension is **NOT** created in any migration.
  * The `pgvector` Python library is installed but not used by any model.
* **Alembic Registration Defect (M1):**
  * `backend/alembic/env.py` line 12 sets `target_metadata = Base.metadata`, but **neither `app.models.user` nor `app.models.otp_verification` is imported**. Running `alembic check` or autogenerate sees an empty schema.

---

## 5. API Endpoint Inventory

| HTTP Method | Route Path | Handler Function | Security / Auth | Status |
|---|---|---|---|---|
| `GET` | `/health` | `app.main::health_check` | Public | **IMPLEMENTED** |
| `POST` | `/api/v1/auth/register` | `auth.router::register` | Public (vulnerable C3) | **IMPLEMENTED BUT DEFECTIVE** |
| `POST` | `/api/v1/auth/login` | `auth.router::login` | Public (vulnerable C1) | **IMPLEMENTED BUT DEFECTIVE** |
| `GET` | `/api/v1/auth/google/login` | `auth.router::google_login` | Public | **IMPLEMENTED** |
| `GET` | `/api/v1/auth/google/callback` | `auth.router::google_callback` | Public (vulnerable H1) | **IMPLEMENTED BUT DEFECTIVE** |
| `POST` | `/api/v1/auth/refresh` | `auth.router::refresh` | Public / Refresh token | **IMPLEMENTED** |
| `POST` | `/api/v1/auth/logout` | `auth.router::logout` | `Depends(get_current_user)` | **IMPLEMENTED (NO-OP)** |
| `GET` | `/api/v1/auth/me` | `auth.router::me` | `Depends(get_current_user)` | **IMPLEMENTED** |
| `GET` | `/api/v1/auth/admin-test` | `auth.router::admin_test` | `Depends(require_role(ADMIN))` | **IMPLEMENTED (TEST ENDPOINT)** |
| `POST` | `/api/v1/auth/send-otp` | `auth.router::send_otp` | Public | **IMPLEMENTED** |
| `POST` | `/api/v1/auth/verify-otp` | `auth.router::verify_otp` | Public (vulnerable C2) | **IMPLEMENTED BUT DEFECTIVE** |
| `POST` | `/api/v1/auth/forgot-password`| `auth.router::forgot_password` | Public | **IMPLEMENTED** |
| `POST` | `/api/v1/auth/reset-password` | `auth.router::reset_password` | Public | **IMPLEMENTED** |

**Summary:** 1 health check endpoint + 12 auth endpoints = 13 total endpoints. No ERP, academic, timetable, attendance, document, or AI endpoints exist.

---

## 6. Detailed Verification of Baseline Defects

| Defect ID | Severity | Documented Hypothesis | Live Code Audit Finding | Verification Status |
|---|---|---|---|---|
| **C1** | **CRITICAL** | Google OAuth users with null password hashes can authenticate with any arbitrary password. | In `backend/app/auth/service.py` (`authenticate_user`, lines 111–112): `if user.hashed_password and not verify_password(password, user.hashed_password): return None`. When `user.hashed_password is None`, the check is bypassed completely and returns `user`. Any password succeeds. | **CONFIRMED** |
| **C2** | **CRITICAL** | 5 failed OTP attempts mark `is_used = True`, which `register_user` misinterprets as successful email verification. | In `backend/app/auth/service.py` (`verify_otp`, lines 164–175): after 5 failed guesses, `record.is_used = True` is committed to DB. In `backend/app/auth/repository.py` (`has_recent_used_email_otp`, lines 121–134): checks only `is_used == True` within expiry window. In `service.py` (`register_user`, line 86): allows registration if `has_recent_used_email_otp` is True. Anyone guessing wrongly 5 times is granted verification bypass. | **CONFIRMED** |
| **C3** | **CRITICAL** | Public registration endpoint permits arbitrary role self-assignment (`ADMIN` / `FACULTY`). | In `backend/app/auth/schemas.py` (`RegisterRequest`, line 14): `role: UserRole = UserRole.STUDENT`. The client can post `{"role": "ADMIN"}` or `{"role": "FACULTY"}` directly. In `service.py` (`register_user`, line 94): passed verbatim into `repository.create_user`. | **CONFIRMED** |
| **H1** | **HIGH** | Google OAuth callback exposes access and refresh tokens in GET redirect URL query parameters. | In `backend/app/auth/router.py` (`google_callback`, lines 186–187): `target_url = f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"`. In `frontend/src/context/AuthContext.jsx` (lines 34–40): tokens are parsed from `window.location.search`. Exposed in browser history, logs, and Referer headers. | **CONFIRMED** |
| **H2** | **HIGH** | Insecure default secrets and SQLite database fallback with no production startup guards. | In `backend/app/core/config.py` (lines 9–10): `DATABASE_URL: str = "sqlite:///./campusgpt.db"`, `JWT_SECRET_KEY: str = "development-only-change-me"`. No validation checks prevent booting with these values in non-dev environments. | **CONFIRMED** |
| **H3** | **HIGH** | Lack of IP/account-level rate limiting on auth endpoints; OTP attempt counter resets per generated code. | `backend/app/auth/router.py` has no rate-limiting middleware or decorators. In `service.py` (`create_and_send_otp`, line 141), each new OTP creates a fresh `OtpVerification` row with `attempts = 0`. An attacker can request a new OTP to reset the 5-attempt counter. | **CONFIRMED** |
| **H4** | **HIGH** | Refresh tokens are not rotated, tracked, or revocable; `/logout` endpoint is a no-op; frontend never refreshes tokens. | `refresh_token` is a stateless JWT with 7-day expiry; no database tracking or token family tracking exists. In `backend/app/auth/router.py` (lines 203–205): `logout` returns `204 No Content` without revoking tokens. `frontend/src/context/AuthContext.jsx` stores the refresh token but has no interceptor to call `/refresh` on 401. | **CONFIRMED** |
| **M1** | **MEDIUM** | Alembic `env.py` fails to import database models, blinding autogenerate and drift detection. | In `backend/alembic/env.py` (lines 6–12): imports `Base` but imports no model classes. `Base.metadata.tables` remains empty. Autogenerate proposes dropping all tables. | **CONFIRMED** |
| **M2** | **MEDIUM** | Automatic migrations run at container startup; default credentials hardcoded in Compose. | `docker-compose.yml` line 32 and `backend/Dockerfile` line 15 execute `alembic upgrade head` before `uvicorn`. `docker-compose.yml` hardcodes `campusgpt:campusgpt_dev` and publishes port `5433:5432` on all interfaces (`0.0.0.0`). | **CONFIRMED** |

---

## 7. Existing vs. Documented vs. Prototype Functionality

| Functional Domain | Live Codebase (`frontend/` & `backend/`) | Documented Scope (`CampusGPT_Documentation`) | Prototype Scope (`ui-prototype/`) |
|---|---|---|---|
| **Landing & Auth UI** | **Implemented** (React 19 JSX, LandingPage, AuthScreen, forgot/reset password) | Preserved as baseline (D-04) | Separate mockup with client role switcher |
| **Auth Backend** | **Implemented with defects C1–C3, H1–H4** | Remediated in Stage 0 (WP2, WP4–WP7) | Mock authenticated session |
| **Academic Core (Depts/Classes)** | **Not Implemented** | Full data dictionary & APIs (P05) | Mocked in `mockData.ts` & `AdminStructurePage.tsx` |
| **Attendance Management** | **Not Implemented** | Manual sessions, timetable linkage, calculation engine (P07 slice A) | Mock attendance cards & roster tables |
| **Face Recognition & Liveness** | **Not Implemented** | Required core capability behind provider abstraction (P07 slice B) | None |
| **Timetable Management** | **Not Implemented** | Conflict detection, faculty/student views, calendar export (P08) | Mock timeline view (`TimetableModule.tsx`) |
| **Assignment Lifecycle** | **Not Implemented** | Submissions, grading, deadline tracking (P09) | Mock submission cards (`StudentAssignmentsPage.tsx`) |
| **Notices & Push Alerts** | **Not Implemented** | Broadcast notices, targeting by dept/branch (P10) | Mock notice list |
| **Document Management** | **Not Implemented** | Secure multi-format storage & ingestion (P11) | Mock library UI (`DocumentsPage.tsx`, `LibraryPage.tsx`) |
| **CampusGPT AI Chat** | **Not Implemented** | Real-time WebSocket, permissions-aware tools, RAG (P12–P14) | Mock chat dialog (`CampusGptModal.tsx`, `ClaraModal.tsx`) |
| **Voice Interaction** | **Not Implemented** | Vapi Web SDK -> Vapi agent -> secured FastAPI tools (P22) | Mock UI orb with CSS pulse animations |
| **Role-Based Dashboards** | **Placeholder Only (`/app`)** | Dedicated Student, Faculty, and Admin dashboards (P05, P20, P21) | Fully interactive mock screens with TS data |
| **Testing Infrastructure** | **Not Implemented** | Pytest + HTTPX suite against dedicated `_test` DB (WP0, WP9) | None |
| **CI / CD Workflows** | **Not Implemented** | GitHub Actions pipeline for test, lint, and drift checks (WP10) | None |

---

## 8. Missing Modules & Infrastructure

1. **Test Infrastructure:**
   * No `backend/tests/` directory.
   * `pytest` not listed in `backend/requirements.txt`.
   * Running `pytest backend/` yields `collected 0 items`.
2. **CI/CD:**
   * No `.github/workflows/` directory in repository.
3. **Audit & Logging:**
   * No audit log table or logging configuration in backend.
4. **pgvector Integration:**
   * No Alembic migration creating the `vector` PostgreSQL extension.
5. **UI Reference Assets:**
   * `CampusGPT_Documentation/assets/references/` contains only `README.md`; the 5 original PNG reference mockups are absent.

---

## 9. Discrepancies Between Codebase and Baseline

1. **Root Directory Cleanliness:**
   * The repository root contains `flowcharts/` (4 HTML files) and `ui-prototype/`.
   * The historical `Architecture/` directory mentioned in documentation does not exist at root (architecture documents are maintained under `CampusGPT_Documentation/docs/architecture/`).
2. **Prototype Location:**
   * Documentation references `ui-reference/google-ai-studio/`, whereas the repository has placed the prototype in `ui-prototype/`. The root `.gitignore` specifically ignores `ui-prototype/`.
3. **Frontend Host Environment:**
   * `frontend/node_modules` exists on disk but lacks host-executable binaries in `.bin` (e.g. running `npm run lint` on the host fails because `eslint` is not found). Development is designed around the Dockerized dev environment.

---

## 10. Recommended Sequence

The findings from this technical audit confirm that the repository state is completely aligned with the assumptions of the Stage 0 Foundation Stabilisation plan. No ERP or AI features should be started until the critical defects and infrastructure gaps are resolved.

The recommended immediate sequence is:

1. **WP0 — Repository & Database Preflight (Stage 0):**
   * Establish read-only verification of existing database records.
   * Verify test database configuration (`campusgpt_test`).
   * Create minimal `pytest` harness and characterization tests for existing auth routes.
2. **WP1 — Alembic Model Registration & pgvector Migration:**
   * Register models in `backend/alembic/env.py`.
   * Add additive migration for `CREATE EXTENSION IF NOT EXISTS vector;`.
3. **WP2 — Critical Auth Fixes & Faculty Approval:**
   * Fix Google OAuth password bypass (C1).
   * Fix OTP 5-attempt verification bypass (C2).
   * Restrict public `/register` to role `STUDENT` only (C3).
   * Implement admin approval flow for faculty accounts.
4. **WP3 through WP11:**
   * Execute remaining foundation work packages in the mandatory sequence specified in `docs/foundation-stabilisation/Foundation_Execution_Order.md`.

