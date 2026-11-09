# WP5 — Authentication Rate Limiting

**Stage 0 foundation work package.** Position in the mandatory order: Step 11 (see `Foundation_Execution_Order.md`).
**Implementation status:** IMPLEMENTED (Tested). All requirements implemented in revision 0010 (`auth_attempts`), tested with 121/121 green tests.

## Implementation Summary
- Database table `auth_attempts` created via additive migration `0010_create_auth_attempts_table.py`.
- Rate limiter engine implemented in `backend/app/auth/rate_limiter.py`.
- Configurable thresholds and trusted proxies in `backend/app/core/config.py`.
- Endpoint instrumentation across `login`, `send-otp`, `verify-otp`, `forgot-password`, `reset-password`.
- Dual-dimension throttling (account identifier hash + client IP hash) preventing campus shared-IP lockouts while blocking credential stuffing.
- Header spoofing defense: `X-Forwarded-For` / `X-Real-IP` honored only from verified `TRUSTED_PROXIES`.
- HTTP 429 with `Retry-After` header and generic non-revealing messages.
- Probabilistic and callable lazy pruning of attempts older than 24 hours.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Add database-backed rate limiting to login, OTP send, OTP verify and password reset, without Redis and without in-memory limiters.

## Existing repository context
No limits exist on login. OTP send is limited to 3 per 15 minutes per email. OTP guesses reset each time a new code is requested. The deployment sits behind Nginx in production, so the client IP arrives only through forwarded headers.

## Files and components likely involved
- `backend/app/auth/router.py`, `service.py`, `repository.py`, new `rate_limit` module and `auth_attempts` model
- `backend/app/core/config.py` (limit settings, trusted proxy list)
- `frontend/nginx.conf` (forwarded headers)

## Required inspection steps (before editing anything)
1. List every unauthenticated endpoint.
2. Confirm how uvicorn is started (proxy-header handling) in dev and production.
3. Check which responses currently reveal account existence (WP2 removes these).

## Implementation requirements
1. Create `auth_attempts` (action, identifier_hash, ip_hash, success, created_at) with an index on (action, identifier_hash, created_at).
2. Starting limits (provisional, configurable): login 5 failures / 15 min per email and 20 / 15 min per IP; OTP send 3 / 15 min per email and 10 / hour per IP; OTP verify and reset: total guesses capped per email per hour regardless of new codes.
3. Return HTTP 429 with `Retry-After` and a message that does not reveal whether the account exists.
4. Trust forwarded IP headers only from configured proxy addresses; otherwise use the socket address. Never trust arbitrary `X-Forwarded-For`.
5. Prune old rows lazily.
6. Keep responses uniform (see WP2 enumeration protection): limits and 429 messages must never reveal whether an account exists.

## Database impact
One additive revision: `auth_attempts`. Identifiers are hashed so the table does not become a second store of emails.

## Security impact
Hash identifiers; do not store passwords or OTPs; protect against lockout abuse by combining account and IP limits and keeping lockouts temporary.

## Testing requirements
- Each limit triggers at the threshold with a controllable clock; 429 and `Retry-After` present.
- Success or window expiry resets the counter; one account's lockout does not affect another's.
- Spoofed `X-Forwarded-For` from an untrusted peer is ignored.
- Requesting a new OTP does not reset guess limits.

## Acceptance criteria
- All listed limits enforced and tested.
- Existing happy paths unaffected.
- Limits configurable without code changes.

## Rollback considerations
Disable limits through configuration; revert code; the table can remain.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- The proxy topology is unknown (PD-17) — implement socket-address limiting only and report.
- Limits would lock out legitimate users in a shared-IP campus network — report the concern.

## Human approval checkpoint
Owner approves final thresholds (provisional values above) before WP6.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
