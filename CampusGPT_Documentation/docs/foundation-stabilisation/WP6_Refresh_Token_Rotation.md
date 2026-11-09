# WP6 — Refresh Token Rotation and Revocation

**Stage 0 foundation work package.** Position in the mandatory order: Step 12 (see `Foundation_Execution_Order.md`).
**Implementation status:** NOT STARTED. Everything below is a plan unless marked otherwise. Schema objects named here are **PROPOSED**; migration revision numbers are **illustrative** — read the real Alembic head first.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Add server-side tracking of refresh tokens with rotation, reuse detection by family, revocation on logout/password reset/deactivation, and a short access-token lifetime.

## Existing repository context
Refresh tokens are stateless JWTs reused until expiry; `/logout` returns 204 and does nothing; the frontend never calls `/refresh`; tokens are stored in `localStorage`.

## Files and components likely involved
- `backend/app/auth/service.py` (`create_refresh_token`, `decode_token`), `router.py` (`refresh`, `logout`), `core/dependencies.py`
- new `refresh_token` model and repository
- `frontend/src/context/AuthContext.jsx`

## Required inspection steps (before editing anything)
1. Find every place tokens are issued: login, Google exchange, refresh.
2. Confirm `get_current_user` loads the user and role from the database each request.

## Implementation requirements
1. Create `refresh_tokens` (jti, family_id, user_id, issued_at, expires_at, revoked_at, replaced_by, user_agent, ip_hash).
2. Issue refresh tokens with a `jti`; `/refresh` verifies the JWT, then atomically rotates (`UPDATE … WHERE revoked_at IS NULL` or row lock) so concurrent requests cannot both succeed.
3. Reuse detection: presenting a revoked token revokes the whole family — except a short leeway (provisional 10 seconds) after rotation, where the replay is rejected without revoking the family, to tolerate two browser tabs.
4. `/logout` accepts the refresh token and revokes it; add logout-all (revoke every token of the user).
5. Revoke all refresh tokens after password reset, after admin deactivation and after role change.
6. Access token lifetime 15 minutes (PD-03); refresh 7 days (existing).
7. Existing refresh tokens (no `jti` row) become invalid: users sign in again once.
8. Document `localStorage` limitations and the production cookie option (PD-04, PD-23).

## Database impact
One additive revision: `refresh_tokens` with indexes on `jti` (unique), `family_id`, `user_id`.

## Security impact
Store token identifiers, not raw tokens. Never log tokens. Keep rotation atomic. Document XSS exposure of `localStorage` honestly; do not claim it is the ideal design.

## Testing requirements
- Rotation returns a new pair and the old token fails.
- Reuse outside the leeway revokes the family; reuse inside the leeway does not.
- Two concurrent refresh calls: exactly one succeeds.
- Logout revokes; logout-all revokes all; password reset revokes all; deactivated user cannot refresh.
- Expired refresh token rejected.

## Acceptance criteria
- All listed behaviours pass tests.
- Existing login still works; sessions survive access-token expiry (with WP7).
- No raw token stored server-side.

## Rollback considerations
Revert code; the table can remain unused; users sign in again.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- `get_current_user` does not re-read the database role — report before relying on it.
- A concurrency test cannot be made deterministic.

## Human approval checkpoint
Owner confirms PD-03 and PD-04 answers before WP7.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
