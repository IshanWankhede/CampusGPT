# WP11 — Logging, Monitoring and Audit Foundation

**Stage 0 foundation work package.** Position in the mandatory order: Step 16 (see `Foundation_Execution_Order.md`).
**Implementation status:** NOT STARTED. Everything below is a plan unless marked otherwise. Schema objects named here are **PROPOSED**; migration revision numbers are **illustrative** — read the real Alembic head first.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Add structured logging, request correlation IDs, redaction of sensitive data and a persistent audit trail for authentication and administrative actions.

## Existing repository context
No logging module, correlation IDs or audit table exist. README mentions `core/logging.py`, which is absent.

## Files and components likely involved
- `backend/app/main.py`, new `core/logging.py`, new middleware, new `audit_log` model/repository/service

## Required inspection steps (before editing anything)
1. Search for existing `print` or logging calls.
2. Identify all places where authentication, role and admin events occur.

## Implementation requirements
1. JSON-structured logging with level control from configuration.
2. Request-ID middleware: accept or generate `X-Request-ID`, include it in every log line and response header.
3. Redaction filter: passwords, OTPs, tokens, authorisation headers, cookies and codes are never logged.
4. `audit_logs` (actor_id, action, target_type, target_id, outcome, ip_hash, request_id, metadata JSON without secrets, created_at) — append-only.
5. Audit events: login success/failure, lockout, OTP sent/verified/failed, registration, password reset, token refresh/reuse detection, logout, role request created/approved/rejected, admin actions.
6. Document monitoring signals and alert candidates (spikes in failed logins, reuse detection, 5xx rate); no monitoring product is introduced.

## Database impact
One additive revision: `audit_logs`.

## Security impact
Audit rows hold identifiers and outcomes, not secrets. Audit table is append-only at application level; no update or delete endpoints.

## Testing requirements
- Redaction test with sentinel secrets in requests proves they never reach log output.
- Each listed event produces exactly one audit row.
- Correlation ID appears in response header and logs.

## Acceptance criteria
- No sensitive value appears in logs in any test.
- Role approvals are auditable end to end.

## Rollback considerations
Revert code; the table can remain.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- A log statement cannot be made safe — remove it rather than risk leaking.

## Human approval checkpoint
Owner reviews a sample of redacted logs and audit rows.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
