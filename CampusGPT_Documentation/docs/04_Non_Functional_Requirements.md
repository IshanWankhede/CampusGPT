# 04 — Non-Functional Requirements

Targets are **proposed starting values** to be confirmed or measured in P25; nothing here has been measured on the repository.

| ID | Area | Requirement | Verification |
|---|---|---|---|
| NFR-SEC-01 | Security | No known critical/high authentication defect at acceptance | Foundation acceptance checklist |
| NFR-SEC-02 | Security | Authorisation enforced in the backend for every route and tool | Role × route test matrix |
| NFR-SEC-03 | Security | Secrets only through environment/secret store; none in repo, images or logs | Config tests, log redaction tests, secret scanning |
| NFR-SEC-04 | Security | Production refuses default or weak secrets (JWT ≥ 32 chars) | WP3 tests |
| NFR-SEC-05 | Security | OWASP ASVS-style checks for authentication, session, access control, file upload | P23 review |
| NFR-PRIV-01 | Privacy | Student records visible only to the student, assigned faculty and authorised admins | Authorisation tests |
| NFR-PRIV-02 | Privacy | Biometric data only with consent, encrypted, with retention and deletion | Doc 14 |
| NFR-PERF-01 | Performance | API p95 under 300 ms for standard reads on seed-scale data (excluding AI) | Load smoke test in P25 |
| NFR-PERF-02 | Performance | First token of an AI response under 3 s on typical queries (provider-dependent) | P12 measurement |
| NFR-PERF-03 | Performance | Initial app load within a budget agreed in P04 (route-level code splitting) | Build report |
| NFR-REL-01 | Reliability | Migrations are additive, reviewed, backed up; production is forward-only | WP0, WP8 |
| NFR-REL-02 | Reliability | Ingestion jobs are idempotent and retryable | Doc 22 tests |
| NFR-OBS-01 | Observability | Structured logs with request IDs; sensitive values redacted | WP11 tests |
| NFR-OBS-02 | Observability | Audit trail for authentication, role and admin actions | WP11 |
| NFR-MAINT-01 | Maintainability | Modular monolith, separation of router/service/repository/schemas | Code review |
| NFR-MAINT-02 | Maintainability | CI runs tests, migration checks, lint and build on every change | WP10 |
| NFR-A11Y-01 | Accessibility | Keyboard operability, visible focus, WCAG AA contrast on dark theme, reduced-motion respected | P24 checklist |
| NFR-UX-01 | UX | Dark mode only; consistent components; empty, loading and error states everywhere | Doc 36 |
| NFR-COMP-01 | Compatibility | Current evergreen browsers on desktop and mobile; responsive from 360 px | P24 |
| NFR-DATA-01 | Data | Seed data never reaches production; production data never altered by seeding | Doc 32 |
| NFR-PORT-01 | Portability | Docker Compose reproduces the environment; dev and production layers separated | WP8 |
| NFR-COST-01 | Cost | AI usage budgets per user and per day; configurable | P12 |

## Additional requirements (final correction)
| ID | Area | Requirement | Verification |
|---|---|---|---|
| NFR-RT-01 | Real-time | Chat and live attendance use WebSocket with authentication on connect, bounded frames, heartbeat, reconnection and cleanup (`docs/architecture/WebSocket_Protocol.md`) | WebSocket test suite, Nginx upgrade test |
| NFR-RT-02 | Real-time | No Redis is introduced for WebSocket support; scaling choices are recorded as decisions (PD-25) | ADR review |
| NFR-BIO-01 | Biometrics | Consent before processing; templates encrypted; raw images deleted after processing; retention enforced; faculty/admin cannot access templates | Doc 14 tests |
| NFR-BIO-02 | Biometrics | A manual attendance fallback exists for every verification path and every override is audited | Attendance tests |
| NFR-VOICE-01 | Voice | Vapi never receives database access; every tool call is server-authenticated and bound to the user's voice session | Voice security tests |
| NFR-VOICE-02 | Voice | Audio is not stored by default; usage is monitored; text chat is a complete fallback | Doc 37 tests |
| NFR-AUTH-01 | Authentication | Login, forgot-password and send-OTP responses are indistinguishable for existing and non-existing accounts | WP2 enumeration tests |
