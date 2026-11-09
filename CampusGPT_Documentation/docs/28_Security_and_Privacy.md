# 28 — Security and Privacy

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Previously observed security posture (older snapshot — PO-RV; each item must be re-verified on the live repository before being treated as confirmed)
| ID | Finding | Severity | Package |
|---|---|---|---|
| C1 | Google-created accounts log in with any password | Critical | WP2 |
| C2 | Five wrong OTP guesses count as email verification | Critical | WP2 |
| C3 | Public registration accepts ADMIN/FACULTY | Critical | WP2 |
| H1 | OAuth tokens in redirect URL | High | WP4 |
| H2 | Public default JWT secret, SQLite default, no production guard | High | WP3 |
| H3 | No login/OTP rate limiting; OTP guesses reset by new codes | High | WP5 |
| H4 | Refresh not rotated/revocable; logout no-op | High | WP6, WP7 |
| M1 | Alembic does not register models | Medium | WP1 |
| M2 | Auto-migration at start; hardcoded dev credentials; root container; DB port on all interfaces | Medium | WP3, WP8 |
| M3 | Resend errors cause HTTP 500; `send-otp` without college skips domain check | Medium | WP2 |
| L1 | OAuth state not bound to browser; `OAuth2PasswordBearer` URL mismatch with JSON login (Swagger) | Low | WP4 |
| L2 | passlib/bcrypt pairing fragile | Low | WP8 |
| L3 | External CDN assets on the landing page | Low | P24 |

## 2. Threat model (summary)
| Asset | Threats | Controls |
|---|---|---|
| Accounts | credential stuffing, OTP brute force, takeover via Google-null-hash, role escalation | WP2, WP5, approval workflow, audit |
| Student records | IDOR, over-broad faculty access, AI leakage | policies in services, enrolment/assignment checks, permission-filtered retrieval |
| Uploaded files | malware, path traversal, parser exploits, decompression bombs | validation, generated names, sandboxed parsing, limits |
| Biometric data | breach, misuse, unlawful retention | consent, encryption, deletion, human fallback, PD-10 |
| Tokens | theft via XSS/URL/logs | no URL tokens, rotation, short lifetime, redaction, cookie evaluation |
| AI pipeline | prompt injection, data exfiltration through tools, jailbreak | tool allow-list, per-tool authorisation, delimiting untrusted text, output checks |
| Infrastructure | exposed DB port, weak secrets, root containers | WP3, WP8 |

## 3. Security requirements
1. Authentication: existing JWT/Google/OTP preserved and hardened; no second system.
2. Authorisation: backend-enforced; deny by default; hidden resources return 404; policies shared by routes and AI tools.
3. Input validation: Pydantic everywhere; separate schemas for create/update/admin; HTML sanitised server-side.
4. File uploads: extension + MIME + magic bytes, size/page caps, generated storage names, no execution, access through authorised endpoints only.
5. Secrets: environment only; production validation; never logged; rotation documented.
6. Transport: HTTPS in production; HSTS; secure cookies when cookies are used; correct proxy-header trust.
7. HTTP hardening: restricted CORS, security headers at Nginx (CSP designed in P23 after assets are self-hosted), docs endpoints off in production.
8. Rate limiting and abuse controls (WP5), upload and AI budgets.
9. Auditing: authentication, role and admin actions append-only (WP11).
10. Dependency hygiene: pinned versions, scheduled updates, vulnerability scan in CI (added in P23).
11. Error handling: generic messages externally; detailed logs internally without secrets.

## 4. AI-specific security
- No LLM-generated SQL. Tools have typed parameters and call the same policies as routes.
- Retrieved text and user text are untrusted: delimited, never allowed to change system instructions, and never allowed to select which user's data is fetched.
- Retrieval filters (department, subject, role, document ACL) are inside the SQL query, applied before similarity ranking results leave the database.
- Conversation content is private to its owner; logging excludes message bodies by default.
- Test suite includes injection attempts embedded in documents and cross-user queries.

## 5. Privacy
- Data minimisation in faculty views; small-group suppression in analytics.
- Biometric processing needs explicit, versioned consent, encryption at rest, retention and deletion schedule, access logging, and a privacy-impact assessment before use (doc 14). Blink detection alone is not sufficient liveness protection; GPS is not definitive proof of presence.
- Right to delete: conversations (user-initiated), biometrics (withdrawal), personal documents.
- Backups are sensitive: stored outside the repository, restricted, time-limited.
- Seed data is synthetic only (doc 32).

## 6. Review points
WP-level security verification (Stage 0 step 18); P23 full review; P25 pre-release review. Findings use severity levels and must be closed or explicitly accepted by the owner.

## 7. Biometric security and privacy (face recognition attendance)
Face recognition with liveness is a required capability (doc 14). Security requirements: explicit informed consent before processing; templates encrypted at rest with managed keys; raw images deleted after processing; retention and deletion policy enforced; access restricted to the biometrics service (faculty and admins never see templates or raw images); manual fallback and audited faculty override; liveness and spoofing threat model with honest residual risk; GPS/geofence treated as supporting evidence only; privacy and legal review before production. The provider decision is pending (PD-10); no vendor is assumed.

## 8. WebSocket security
Origin check on upgrade; authentication by first message within 5 s (no token in the URL); identity fixed per connection; per-user connection and frame limits; message-size cap; ownership checks on every conversation or session id; generic error messages; cleanup on disconnect; Nginx forwards headers only from the trusted proxy (`docs/architecture/WebSocket_Protocol.md`).

## 9. Vapi and third-party voice processing
Vapi must not bypass backend security or receive database access. Tool endpoints require Vapi server authentication and a valid voice session bound to a user; the user identity never comes from model-supplied arguments; tools return minimal data; recording disabled by default; provider credentials only in the secret store; privacy review and data-processing terms before production (PD-19) (doc 37).
