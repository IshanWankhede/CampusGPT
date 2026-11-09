# WP9 — Testing Infrastructure

**Stage 0 foundation work package.** Position in the mandatory order: Step 3 (minimal) and step 17 (complete regression suite) (see `Foundation_Execution_Order.md`).
**Implementation status:** IMPLEMENTED (Level 5 Tested).
- Complete test suite: 151 tests passing across 10 test modules (all 136 existing regression tests preserved + 15 new tests).
- `backend/pytest.ini`: Standardized configuration with `asyncio_default_fixture_loop_scope = function`, `addopts = -v --tb=short`, and clean warning filters.
- Alembic Migration DAG (`test_migration_dag.py`): Revisions inspected via Alembic's `ScriptDirectory`; verified exactly one head (`0011`), single base (`0001`), linear continuity with no branches or merge points.
- RBAC & Schemas (`test_rbac_and_schemas.py`): Full 401 Unauthorized matrix for unauthenticated requests, 403 Forbidden matrix for STUDENT/FACULTY on ADMIN endpoints, 404/409 error handling for role requests, full HTTP role request approve/reject lifecycle with user promotion to FACULTY, strict Pydantic response schema validation (`UserResponse`, `RoleRequestResponse`, `TokenResponse`).
- Isolation & Fixtures (`conftest.py`): Explicit truncation of `auth_attempts, login_codes, refresh_tokens, otp_verifications, role_requests, users CASCADE`; `assert_test_database` safety guard enforcing `*_test` database naming; standardized `mock_google_oauth` fixture; role-specific user and access token fixtures.
- CI/CD (`.github/workflows/ci.yml`): Production-grade GitHub Actions pipeline with `pgvector/pgvector:pg16` service container, database safety verification, Alembic migrations, Pytest suite with coverage, frontend ESLint, and Vite production build.
- Database Safety: Original `campusgpt` database remains untouched at revision `0005`. SQLite strictly prohibited.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Provide a complete, safe backend test suite on PostgreSQL covering authentication, migrations and every foundation fix, with fakes for email and Google.

## Existing repository context
No tests exist. WP0 adds a minimal harness; this package completes it. Migrations are PostgreSQL-only, so SQLite cannot substitute.

## Files and components likely involved
- `backend/tests/` (new), `backend/requirements-dev.txt`, `backend/pytest.ini` or `pyproject` section (new), `backend/app/core/email.py` (injection point)

## Required inspection steps (before editing anything)
1. Read the WP0 harness and characterization tests.
2. Identify seams for faking `send_email` and the Google HTTP calls.

## Implementation requirements
1. Fixtures: test database lifecycle that refuses any database whose name does not end in `_test`; migrations applied via Alembic; per-test isolation.
2. Fakes: capture OTP emails; fake Google token/userinfo; controllable clock.
3. Suites: characterization, authentication, OTP security, password-login regression, role-escalation regression, OAuth, rate limiting, refresh tokens, migration/drift tests, API smoke tests.
4. Frontend: `npm run lint` and `npm run build` documented as required checks (no new runner without approval).
5. Coverage report for `app/auth` and `app/core`.

## Database impact
Creates/uses `campusgpt_test` only.

## Security impact
Tests never touch the development or production database. No real credentials. No real emails sent.

## Testing requirements
- The suite itself is verified by mutation spot-checks: temporarily re-introduce each critical defect on a branch and confirm a test fails (then discard).

## Acceptance criteria
- Full suite green on a clean checkout.
- Guard test proves refusal on non-`_test` names.
- No SQLite anywhere in integration tests.

## Rollback considerations
Tests are additive; delete the directory to revert.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- A test would need to modify a non-test database.
- Fakes cannot be injected without large refactors — propose the smallest seam and ask.

## Human approval checkpoint
Owner reviews coverage and the mutation spot-check results.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
