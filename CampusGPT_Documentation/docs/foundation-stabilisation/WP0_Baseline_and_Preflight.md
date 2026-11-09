# WP0 — Baseline, Backup and Preflight

**Stage 0 foundation work package.** Position in the mandatory order: Execution steps 1–3 (audit/baseline, backup/preflight, minimal test harness) (see `Foundation_Execution_Order.md`).
**Implementation status:** NOT STARTED. Everything below is a plan unless marked otherwise. Schema objects named here are **PROPOSED**; migration revision numbers are **illustrative** — read the real Alembic head first.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Establish a verified, recoverable starting point before any code or schema changes: backups, a factual picture of the live repository and database, a working test harness, and characterization tests that lock in today's behaviour.

## Existing repository context
The audited snapshot has 2 tables (`users`, `otp_verifications`), Alembic revisions 0001–0005, a dev-oriented Compose file, no tests and no CI. Whether the live HEAD, live database and live user records match the snapshot is REQUIRES VERIFICATION.

## Files and components likely involved
- `docker-compose.yml`, `backend/Dockerfile`, `backend/alembic/versions/*`, `backend/alembic/env.py`
- `backend/app/models/*`, `backend/app/auth/*`, `backend/app/core/config.py`
- `frontend/package.json`, `frontend/vite.config.js`, `.env.example`, `.gitignore`

## Required inspection steps (before editing anything)
1. Run `git status`, `git log -n 20`, and record the HEAD commit; confirm the working tree is clean or list uncommitted changes (do not discard them).
2. Read every file under `backend/app` and `backend/alembic`; compare with the audit baseline in `docs/architecture/00_Source_Reconciliation_and_Baseline.md` and list differences.
3. Record `alembic current`, `alembic heads` and `alembic history` against the development database (read-only commands).
4. List environment variable **names** the code reads (never print values).

## Implementation requirements
1. Create a git tag or branch (for example `pre-foundation-baseline`) at the current HEAD; do not rewrite history.
2. Take a logical database backup with `pg_dump` into an ignored location outside the repository; record its size and checksum; verify it restores into a scratch database.
3. Run the read-only preflight queries in `docs/foundation-stabilisation/Database_Backup_and_Migration_Safety.md`: user counts by `role` and `auth_provider`, users with null `hashed_password`, all non-STUDENT users, OTP row counts, `alembic_version`, installed extensions.
4. Produce `docs/foundation-stabilisation/BASELINE_REPORT.md` containing HEAD, counts, elevated-account list (emails masked), Alembic head, extension list, build/lint/startup results, and any divergence from the audit.
5. Verify startup in a disposable environment: backend `/health`, frontend dev server, existing sign-in page loads. Record results honestly, including failures.
6. Add `requirements-dev.txt` (pytest, httpx, pytest-cov) and a minimal `backend/tests/` harness with a database-name guard (refuses any DB whose name does not end in `_test`).
7. Create the `campusgpt_test` database (separately from the dev database) and apply migrations to it.
8. Write characterization tests for current behaviour: register + verify + login happy path, `/me`, refresh, forgot/reset password, Google callback for new and existing user (Google HTTP calls faked), `/health`. Tests that capture a known defect are marked `xfail(strict=True)` with the defect ID.

## Database impact
No schema change. Read-only queries on the development database. Creates a separate empty `campusgpt_test` database.

## Security impact
Backups may contain password hashes and emails: store outside the repository, restrict permissions, never commit. Do not print secrets or full emails in reports. No production data is used in tests.

## Testing requirements
- Characterization suite passes against the unmodified code.
- Database-name guard test: running destructive setup against a non-`_test` URL raises before touching the database.
- Backup restore rehearsal succeeds in a scratch database.

## Acceptance criteria
- Baseline tag exists; backup exists, checksummed and restore-tested.
- `BASELINE_REPORT.md` exists and lists divergences from the audit.
- Characterization suite runs green; known defects captured as strict xfail with IDs C1–C3.
- No application code or migration was modified (only test files, dev requirements and the report were added).

## Rollback considerations
Delete the added test files and `requirements-dev.txt`; drop `campusgpt_test`; the tag and backup are kept. Application code is untouched, so nothing else needs reverting.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- The live HEAD differs significantly from the audit (new modules or tables) — report and wait.
- `pg_dump` or restore rehearsal fails.
- The test database name guard cannot be guaranteed.
- Preflight shows unexpected non-student accounts — report, do not change them.

## Human approval checkpoint
Owner reviews `BASELINE_REPORT.md`, confirms the backup, and decides PD-06 (how elevated accounts are reviewed) before WP1 starts.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
