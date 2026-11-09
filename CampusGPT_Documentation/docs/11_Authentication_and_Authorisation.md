# 11 — Authentication and Authorisation

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Existing authentication (preserve; improve incrementally)
| Capability | Implementation (audit-reported) | Target change |
|---|---|---|
| Passwords | bcrypt via passlib | fix C1; pin compatible bcrypt/passlib (REQUIRES VERIFICATION at runtime) |
| Email OTP | Resend; 6-digit; hashed; 10 min; 5 attempts; 3 sends / 15 min | `verified_at` (WP2), rate limits (WP5), 503 on provider failure |
| JWT | HS256 access (30 min) + refresh (7 days), `type` claim | 15-min access (PD-03), refresh rotation (WP6) |
| Google OAuth | manual code exchange with `httpx`, state = signed JWT, verified-email and domain checks | one-time code exchange and state cookie (WP4) |
| Password reset | OTP-based | revoke sessions after reset (WP6) |
| College domains | COEP, PICT, VIT map | verify domains (PD-15); isolation (PD-07) |
| Admin bootstrap | `create_admin.py` CLI | keep; documented runbook (PD-24) |

## 2. Target flows
Registration: send OTP → verify → register (STUDENT; faculty request recorded) → sign in. Login: credentials → access + refresh. Google: authorise → callback → one-time code → POST exchange → tokens. Refresh: rotate. Logout: revoke. Diagrams in `docs/architecture/diagrams/05–09`.

## 3. Token handling
- Access token: short-lived, sent as bearer; contains subject and `type`; the `role` claim is informational — **authorisation uses the database role**.
- Refresh token: rotated, tracked by `jti` and family, revoked on logout/reset/deactivation.
- Interim storage: `localStorage` (PD-04) — XSS-exposed; production target evaluated: HttpOnly + Secure + SameSite cookies with CSRF protection (PD-23). This package does not claim `localStorage` is ideal.

## 4. Authorisation model
1. **Role** (ADMIN, FACULTY, STUDENT) from the database each request.
2. **Resource policies** in service code: ownership, enrolment, faculty assignment, document ACL, audience rules.
3. **Designations** (HOD/Dean/Coordinator) add scoped permissions (PD-14).
4. **AI tools** call the same policies as HTTP routes.

Rules: deny by default; hidden resources return 404; mass-assignment prevented with separate schemas; privileged role changes only through the approval workflow or CLI.

## 5. Brute-force and abuse controls (WP5)
Database-backed limits per account and per IP; proxy headers trusted only from configured proxies; 429 with `Retry-After`.

## 6. Session security checklist
No tokens in URLs; no tokens in logs; logout revokes server-side; password reset revokes all sessions; deactivation takes effect on the next request.

## 7. Testing
Security-regression suite (WP9) covers C1–C3, OAuth, rate limits, refresh rotation; authorisation matrix tests are added with every module.

## 8. Required capabilities and security requirements (preserve the existing implementation)
Capabilities to preserve and improve: local registration and login; JWT access and refresh tokens; Google OAuth; email OTP through Resend; email verification; password reset; current-user endpoint; role-based access control; protected frontend routes; backend authorisation; refresh-token rotation; logout and token invalidation. How each currently behaves must be **re-verified on the live repository** (PO-RV).

| Requirement | Planned in |
|---|---|
| OTP verified server-side, stored hashed, expiring, single use | WP2 (`verified_at`), existing hashing to be confirmed |
| Rate limits on OTP requests and attempts, login and reset | WP5 |
| Verify Google identity (token/profile) and verified email status | WP4 / WP2 |
| Institutional email-domain restriction enforced server-side on every path | WP2, WP4 |
| No role self-assignment; faculty approval; ADMIN only via CLI | WP2 |
| No passwordless Google account takeover (null password hash never authenticates a password login) | WP2 |
| No unauthorised account linking (Google links to a local account only if the Google email is verified, the domain is allowed and the local email is verified; link events audited) | WP2, WP4 |
| User-enumeration protection (uniform responses and timing on login, forgot-password, send-otp) | WP2 |
| Every protected operation validated in the backend; frontend role information is never authorisation | all phases |
| Refresh rotation, logout and token invalidation | WP6, WP7 |
| No destructive authentication migrations; existing users and records preserved | all |

Any weakness listed in the older audit must first be **verified against the actual current repository** before documentation treats it as confirmed (prompts 02 and 05).
