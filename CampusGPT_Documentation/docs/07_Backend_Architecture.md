# 07 — Backend Architecture

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Existing (PO-RV — previously observed in an older snapshot)
`backend/app/`: `main.py` (app, CORS, `/health`, mounts auth router), `core/` (`config.py` Settings, `dependencies.py` with `get_current_user` and `require_role`, `email.py` Resend), `database/` (`base.py`, `session.py`), `models/` (`User`, `OtpVerification`), `auth/` (`router.py`, `service.py`, `repository.py`, `schemas.py`), `create_admin.py`. SQLAlchemy 2.x with Pydantic v2; Alembic with five revisions.

## 2. Layering rule
`router` (HTTP, dependencies, response models) → `service` (business rules, authorisation, transactions) → `repository` (SQLAlchemy queries) → models. Schemas are separate for create/update/read to prevent mass assignment. Services never return ORM objects to routers outside their module.

## 3. Module template (PROPOSED)
```
app/<module>/
  router.py  service.py  repository.py  schemas.py  policies.py  tests in backend/tests/<module>/
```
`policies.py` holds permission functions (`can_view_attendance(user, student)`), shared by routes, services and AI tools.

## 4. Authorisation
`get_current_user` loads the user from the database for every request; `require_role` compares the database role. Resource-level rules sit in policies. Designations (PD-14) extend policies, not roles.

## 5. Transactions and consistency
One session per request; services own commits; state changes plus notifications/audit rows are written in the same transaction.

## 6. Background work
Worker entrypoint in the same image claims `document_processing_jobs` rows with `FOR UPDATE SKIP LOCKED`. No external queue.

## 7. Configuration
Pydantic `Settings` with production validation (WP3). No settings read from `os.environ` outside it.

## 8. Errors and logging
Standard error envelope for new modules, request-ID middleware, structured logs, redaction filter, audit service (WP11).

## 9. Dependencies
Core runtime packages in `requirements.txt`; test tools in `requirements-dev.txt`; heavy AI packages in `requirements-ai.txt` from the RAG phase (D-08).

## 10. Known defects to fix first
See baseline table in `docs/architecture/00_Source_Reconciliation_and_Baseline.md`.

## 11. Real-time, voice and biometric modules (PROPOSED)
- **WebSocket endpoints** live in the `ai` and `attendance` modules, reuse the existing JWT verification and the policy functions, run generation as cancellable tasks and keep a per-process connection registry. Verify the repository's sync/async conventions first.
- **`voice` module:** voice sessions, Vapi server-authentication check, tool dispatcher that wraps existing services; no direct database access from Vapi.
- **`biometrics` module:** consent, enrolment, verification, liveness orchestration behind `BiometricProvider`; templates encrypted; mock provider for development only.
- Cross-module calls remain service-to-service; policies are the single authorisation point.
