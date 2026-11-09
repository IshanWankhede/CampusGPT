# WP1 — Alembic and Database Foundation

**Stage 0 foundation work package.** Position in the mandatory order: Steps 4–6 (see `Foundation_Execution_Order.md`).
**Implementation status:** NOT STARTED. Everything below is a plan unless marked otherwise. Schema objects named here are **PROPOSED**; migration revision numbers are **illustrative** — read the real Alembic head first.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Make migrations trustworthy: register all models with Alembic, verify the revision chain, and add an idempotent pgvector extension migration without creating vector columns.

## Existing repository context
Audit: `alembic/env.py` imports `Base` but not models, so autogenerate sees empty metadata. `models/__init__.py` contains duplicated import blocks. Revisions 0001–0005 appear linear but 0002 onward use PostgreSQL-only types while `config.py` defaults to SQLite. pgvector was enabled manually; the extension is not in a migration.

## Files and components likely involved
- `backend/alembic/env.py`, `backend/alembic/versions/*`, `backend/alembic.ini`
- `backend/app/models/__init__.py`, `user.py`, `otp_verification.py`, `backend/app/database/base.py`

## Required inspection steps (before editing anything)
1. Read all five migrations and the model files; compare column by column, index by index.
2. Run `alembic heads` — confirm exactly one head — and `alembic history`.
3. Check which dialect each migration assumes.

## Implementation requirements
1. Import `app.models` in `alembic/env.py` before `target_metadata` is set; clean `models/__init__.py` so each model is exported once.
2. Set `compare_type=True` for autogenerate only; do not add a retroactive constraint naming convention.
3. Create a scratch database, run `alembic upgrade head`, then run autogenerate in a throwaway directory and confirm it proposes **no** operations. Investigate every proposed operation; apply none blindly.
4. Add one new revision (next free id; do not assume numbers) that runs `CREATE EXTENSION IF NOT EXISTS vector` on PostgreSQL only; `downgrade` is a documented no-op.
5. Do not create vector columns or tables.
6. Document upgrade/downgrade behaviour of the new revision and the extension-privilege caveat for managed databases.

## Database impact
One new additive revision (extension only). No table or column changes. Existing revisions are never edited.

## Security impact
Extension creation needs sufficient database privileges; use the migration role, never widen application-role privileges. Do not run autogenerate output against a real database unreviewed.

## Testing requirements
- Metadata test: `Base.metadata` contains `users` and `otp_verifications` (and every later model).
- Fresh database: `upgrade head` succeeds and `vector` appears in `pg_extension`.
- Existing dev database copy: `upgrade head` is a clean no-op apart from the new revision.
- Autogenerate drift check reports no changes.

## Acceptance criteria
- Single Alembic head; chain verified.
- Autogenerate against a scratch database yields no operations.
- pgvector extension created by migration on a fresh database.
- No existing migration file modified.

## Rollback considerations
Remove the new revision file before it has been applied anywhere; if applied, leave the extension in place (dropping it would destroy future vector data) and revert only code changes.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- More than one Alembic head, or a revision gap.
- Autogenerate proposes drops or alters — stop and report.
- Extension creation is denied by the database role — report; do not escalate privileges silently.

## Human approval checkpoint
Owner approves the autogenerate drift report and the new revision before it is applied to any non-scratch database.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
