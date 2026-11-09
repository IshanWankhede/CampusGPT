# WP7 — Frontend Authentication Integration

**Stage 0 foundation work package.** Position in the mandatory order: Step 13 (see `Foundation_Execution_Order.md`).
**Implementation status:** NOT STARTED. Everything below is a plan unless marked otherwise. Schema objects named here are **PROPOSED**; migration revision numbers are **illustrative** — read the real Alembic head first.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Give the frontend a single authenticated API client with automatic refresh, proper logout and role-aware route guards, without changing the existing sign-in, sign-up or landing visuals.

## Existing repository context
`AuthContext.jsx` has a private `request()` hard-wired to `/api/v1/auth`; there is no shared client, no 401 handling, no refresh call, and `/app` is one placeholder route for every role.

## Files and components likely involved
- `frontend/src/context/AuthContext.jsx`, `routes/AppRoutes.jsx`, new `src/services/api.js`
- existing `features/prototype-visuals/AuthScreen.jsx` (do not restyle)

## Required inspection steps (before editing anything)
1. Confirm every `fetch` call in the frontend.
2. Confirm which components import `useAuth`.
3. Check whether `/auth/verify-email` is referenced anywhere before touching it (PD-21).

## Implementation requirements
1. Create `src/services/api.js` exporting `apiFetch(path, options)` that adds the bearer token, parses JSON errors consistently and, on 401, performs exactly one single-flight refresh (shared promise; Web Locks API when available) then retries once.
2. On refresh failure clear the session and route to `/auth` with a message.
3. Update `AuthContext` to use the client, store tokens as returned by rotation, and call `/logout` with the refresh token.
4. Add `RoleRoute` guards (STUDENT, FACULTY, ADMIN) and a pending-faculty indicator hook; no visual redesign.
5. Keep sign-in, sign-up, forgot-password and reset-password behaviour identical to users.
6. Run `npm run lint` and `npm run build`.

## Database impact
None.

## Security impact
Do not log tokens; clear storage on logout; do not put tokens in URLs; document that tokens are in `localStorage` (interim).

## Testing requirements
- `npm run lint` and `npm run build` pass.
- Manual checklist: expired access token recovers silently; refresh failure signs out; logout revokes; two tabs refresh without a spurious logout; each role sees only its routes.
- If a frontend test runner is approved later, convert the checklist to tests.

## Acceptance criteria
- One API client used by authentication code.
- Existing authentication UI unchanged.
- Lint and build succeed.

## Rollback considerations
Revert the frontend commit; backend remains compatible.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- A change would require restyling the existing auth screens.
- Refresh cannot be made race-free in the browser.

## Human approval checkpoint
Owner performs the manual checklist on the three roles.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
