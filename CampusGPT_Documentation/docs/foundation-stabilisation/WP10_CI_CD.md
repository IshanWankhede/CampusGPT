# WP10 — CI/CD and Verification

**Stage 0 foundation work package.** Position in the mandatory order: Step 15 (see `Foundation_Execution_Order.md`).
**Implementation status:** NOT STARTED. Everything below is a plan unless marked otherwise. Schema objects named here are **PROPOSED**; migration revision numbers are **illustrative** — read the real Alembic head first.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Run the backend suite, migration checks and frontend lint/build automatically on every push and pull request.

## Existing repository context
README mentions GitHub Actions but `.github/` does not exist. No backend linter exists (PD-08).

## Files and components likely involved
- `.github/workflows/*.yml` (new)

## Required inspection steps (before editing anything)
1. Confirm default branch name and protection settings.
2. Confirm Python (3.11) and Node (20) versions used by the Dockerfiles.

## Implementation requirements
1. Backend job: install requirements, start a PostgreSQL service with pgvector, create the `_test` database, run migrations, run pytest, run the Alembic drift check, run the lint step if PD-08 is approved.
2. Frontend job: `npm ci`, `npm run lint`, `npm run build`.
3. Security-regression job: the OTP, password-login, role-escalation, OAuth and rate-limit tests as a named required check.
4. Pin action versions; use least-privilege `permissions`; no secrets needed for tests.
5. Document the failure-handling rule: no merge and no next work package while CI is red; fix forward, do not skip tests.

## Database impact
CI-only database.

## Security impact
No production secrets in CI. Third-party actions pinned to full versions or commit SHAs.

## Testing requirements
- A pull request that re-introduces a known defect on a branch fails CI (verified once, then discarded).

## Acceptance criteria
- Workflows run green on the baseline branch.
- Required checks documented.

## Rollback considerations
Delete the workflow files.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- CI would require repository secrets that are not approved.

## Human approval checkpoint
Owner marks the checks as required in repository settings.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
