# WP3 — Environment and Production Security

**Stage 0 foundation work package.** Position in the mandatory order: Step 9 (see `Foundation_Execution_Order.md`).
**Implementation status:** NOT STARTED. Everything below is a plan unless marked otherwise. Schema objects named here are **PROPOSED**; migration revision numbers are **illustrative** — read the real Alembic head first.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Make unsafe production configuration impossible to start: validate settings, remove public defaults, and restrict documentation endpoints and CORS outside development.

## Existing repository context
`core/config.py::Settings` ships a public default JWT secret and a SQLite `DATABASE_URL` default; `ENV` is not validated; `/docs` is always enabled; CORS origins come from one comma-separated variable.

## Files and components likely involved
- `backend/app/core/config.py`, `backend/app/main.py`, `.env.example`, `README.md` (configuration section)

## Required inspection steps (before editing anything)
1. List every setting and where it is read.
2. Confirm which variables Compose injects (`DATABASE_URL`) and which come from `.env`.

## Implementation requirements
1. Restrict `ENV` to `development`, `staging`, `production`.
2. Outside development fail startup when: the JWT secret is the default, shorter than 32 characters or contains the development marker; the database URL is SQLite or contains development credentials; CORS includes localhost; `RESEND_API_KEY` is empty; Google settings are partially set.
3. Remove the SQLite default (every migration after the first is PostgreSQL-only).
4. Disable `/docs`, `/redoc` and `/openapi.json` outside development.
5. Return generic error bodies in production; never include stack traces or settings in responses.
6. Update `.env.example` to mark values as development-only and add missing names (for example `FRONTEND_URL`).

## Database impact
None.

## Security impact
Changing the JWT secret signs everyone out once (expected). Secrets are never logged. No secret values appear in the repository, docs or test output.

## Testing requirements
- Unit tests construct `Settings` for each unsafe production combination and expect a clear failure; valid production config passes.
- `/docs` returns 404 in production mode and 200 in development.

## Acceptance criteria
- Unsafe production configurations cannot start.
- Development startup is unchanged for a correctly configured `.env`.
- No new default secrets introduced.

## Rollback considerations
Revert config commits; no data impact.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- A deployment already relies on the SQLite default.
- Settings are read in places not found by inspection.

## Human approval checkpoint
Owner confirms the list of required production variables and PD-15/PD-17 inputs they can supply now.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
