# WP2 — Critical Authentication Security Fixes

**Stage 0 foundation work package.** Position in the mandatory order: Steps 7–8 (see `Foundation_Execution_Order.md`).
**Implementation status:** NOT STARTED. Everything below is a plan unless marked otherwise. Schema objects named here are **PROPOSED**; migration revision numbers are **illustrative** — read the real Alembic head first.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Close defects C1 (passwordless Google accounts), C2 (OTP bypass) and C3 (role self-assignment) with additive changes that preserve the existing login, OTP, Google and reset flows and existing user records.

## Existing repository context
`service.authenticate_user` skips password verification when `hashed_password` is null. `service.verify_otp` sets `is_used` on the fifth wrong attempt and `repository.has_recent_used_email_otp` treats any used OTP as proof of verification. `RegisterRequest.role` accepts ADMIN/FACULTY and `register_user` writes it directly.

## Files and components likely involved
- `backend/app/auth/service.py`, `repository.py`, `router.py`, `schemas.py`
- `backend/app/models/otp_verification.py`, `user.py`; new `role_request.py` model
- `backend/app/create_admin.py`; new admin router and CLI for role requests

## Required inspection steps (before editing anything)
1. Re-read the four functions above on HEAD and confirm each defect still exists (write a failing test first).
2. Check how `AuthScreen.jsx` calls register (it sends `role` as STUDENT/FACULTY) so no frontend change is needed.
3. Check existing users: any non-STUDENT accounts recorded by WP0.

## Implementation requirements
1. C1: when the user exists but has no password hash, fail authentication with the same generic error as a wrong password; run a dummy bcrypt comparison on that path and when the user is unknown.
2. C2: add nullable `verified_at` to `otp_verifications`; set it only in the success branch of `verify_otp`; registration requires a verified row for the same email within 15 minutes; lockout sets `is_used` but never `verified_at`.
3. C2: make the college-domain check mandatory when sending a verification OTP (derive the college from the domain; reject unrecognised domains).
4. C2: catch the email-sending failure and return HTTP 503 instead of an uncontrolled 500.
5. C3: public `/register` always creates a STUDENT. Keep accepting the existing `role` field; FACULTY records a PENDING request, STUDENT records nothing, ADMIN returns 422.
6. C3: add `role_requests` (id, user_id, requested_role, status PENDING/APPROVED/REJECTED, reviewed_by, reviewed_at, note, created_at) with an enum.
7. C3: admin-only endpoints to list, approve and reject requests, plus an equivalent CLI command in the style of `create_admin.py`. Admins cannot be created or promoted through any API; admins cannot change their own role.
8. C3: do **not** change existing elevated accounts; they are reviewed manually using the WP0 list.
9. User-enumeration protection: make `/auth/login`, `/auth/forgot-password` and `/auth/send-otp` return identical status, body and (approximately) timing whether or not the account exists; when an account already exists, do not send a verification code (optionally send a neutral notice email to the address owner). Registration after a verified OTP may report conflicts because the caller has proven ownership of the email.
10. Account linking and Google identity: verify the actual current behaviour first. A Google sign-in may attach to an existing local account only when Google reports a verified email, the institutional domain check passes server-side, and the local account's email is itself verified; never link on an unverified local account (pre-registration takeover), never create a passwordless route into an account that was not created by Google, and record every link event for audit.
11. Confirm server-side institutional email-domain enforcement on every path (OTP send, register, login, Google) using one shared function; client-side checks never count.

## Database impact
Two additive revisions (next free ids): nullable `verified_at` on `otp_verifications`; new `role_requests` table and status enum. No backfill. Old OTP rows simply stop counting as proof.

## Security impact
Generic errors prevent account-type disclosure. Role changes are read from the database on every request (not from the JWT claim), so approval and demotion take effect immediately. Every approval/rejection must be written to the audit trail once WP11 exists; until then it is stored in `role_requests` (reviewer, time, note).

## Testing requirements
- C1: null-hash user + any password → 401; real user + correct password → 200; Google flow still works; reset-password then login works.
- C2: five wrong codes then `/register` → rejected; correct code then register → ok; expired window → rejected; verification for email A does not authorise email B; unrecognised domain → 400; email provider failure → 503.
- Enumeration: existing and non-existing emails produce indistinguishable responses on login, forgot-password and send-otp (compare bodies, statuses, and approximate timing).
- Account linking: Google sign-in for an email that matches an unverified local account does not link; matching a verified local account links only with a verified Google email and an allowed domain.
- C3: `role=ADMIN` → 422; `role=FACULTY` → STUDENT + PENDING request; pending user gets 403 on faculty-only endpoints; student gets 403 on admin endpoints; approve → faculty access immediately; reject → stays student.
- Remove the strict xfail markers added in WP0 as each defect is fixed.

## Acceptance criteria
- C1, C2, C3 regression tests pass; WP0 characterization tests still pass.
- Existing sign-in, sign-up, Google, OTP and reset flows work from the unchanged UI.
- No existing user or OTP record modified or deleted.
- Faculty approval works through the endpoints and the CLI.

## Rollback considerations
Revert code commits; the two additive migrations can stay (nullable column and an unused table are harmless). If a rollback of schema is required, only downgrade after a fresh backup and with approval.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- The existing `/register` is called by other clients not seen in the audit.
- A test cannot reproduce a reported defect (the audit may be wrong on HEAD) — report instead of guessing.
- Any change would alter password hashes or delete users.

## Human approval checkpoint
Owner reviews the diff and the regression results, then reviews the elevated-account list (PD-06) before WP3.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
