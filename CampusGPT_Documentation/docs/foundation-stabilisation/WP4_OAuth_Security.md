# WP4 — Secure Google OAuth Callback

**Stage 0 foundation work package.** Position in the mandatory order: Step 10 (see `Foundation_Execution_Order.md`).
**Implementation status:** NOT STARTED. Everything below is a plan unless marked otherwise. Schema objects named here are **PROPOSED**; migration revision numbers are **illustrative** — read the real Alembic head first.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Remove access and refresh tokens from redirect URLs by introducing a one-time authorisation code exchanged by POST, and bind OAuth state to the initiating browser.

## Existing repository context
`router.google_callback` redirects to `/auth/callback?access_token=…&refresh_token=…`; `AuthContext.jsx` reads those query parameters. The OAuth `state` is a signed JWT not tied to a browser session. Google HTTP calls use `httpx` directly (Authlib is not installed).

## Files and components likely involved
- `backend/app/auth/router.py` (`google_login`, `google_callback`), `service.py` (`create_oauth_state`, `verify_oauth_state`)
- new `login_code` model and repository functions
- `frontend/src/context/AuthContext.jsx` (callback effect only)

## Required inspection steps (before editing anything)
1. Trace the complete Google flow end to end and list every place tokens are placed in a URL.
2. Confirm `/auth/callback` renders the existing auth screen and what the frontend does with the query string.

## Implementation requirements
1. Generate a cryptographically random opaque code; store only its hash with user id, creation and expiry (about 60 seconds) and `used_at`.
2. Redirect to `/auth/callback?code=…` only; never include tokens.
3. Add `POST /api/v1/auth/google/exchange` that atomically consumes the code (single use) and returns the same token response shape as login.
4. At `google_login`, set a short-lived HttpOnly, SameSite=Lax cookie with the state nonce (Secure outside development); at the callback require cookie nonce == state nonce, then clear the cookie.
5. Keep the college/domain verification, enforced server-side, and apply the account-linking rule from WP2 (verified Google email, allowed domain, verified local email before linking).
6. Change the `AuthContext.jsx` callback effect to read `code`, call the exchange endpoint and then store the session. Do not change sign-in or sign-up visuals.
7. Document the complete flow and the replay/expiry behaviour.

## Database impact
One additive revision: `login_codes` (code_hash unique, user_id, expires_at, used_at, created_at). In-flight Google logins at deploy time fail once and can be retried.

## Security impact
Codes are single use, short lived and stored hashed. The exchange response is `Cache-Control: no-store`. Error redirects must not echo untrusted input. Do not log codes or tokens.

## Testing requirements
- Callback redirect contains `code` and never `access_token`/`refresh_token`.
- Exchange succeeds once; replay fails; expired code fails; unknown code fails.
- State without matching cookie is rejected; tampered state rejected.
- Unverified Google email and domain mismatch still redirect with an error; Google HTTP calls are faked.
- Manual end-to-end check with real Google credentials is on the release checklist.

## Acceptance criteria
- No token appears in any URL in any Google flow.
- New and existing Google users can still sign in.
- Replay and expiry tests pass.

## Rollback considerations
Revert code; `login_codes` can remain unused. Old URL-token handling must **not** be restored.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- The frontend callback is used by flows not found in the audit.
- Cookies cannot be set because of the dev proxy setup — report the proxy behaviour instead of weakening the design.

## Human approval checkpoint
Owner performs the manual real-credentials Google test and approves before WP5.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
