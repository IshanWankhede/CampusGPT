# 29 — Testing Strategy

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

**Current state (PO-RV — previously observed in an older snapshot):** no automated tests were found. Everything below is PROPOSED; re-verify in WP0.

## 1. Principles
Test on PostgreSQL, never SQLite. Test database name ends with `_test` and the harness refuses otherwise. Fakes for email and Google. Characterization tests before changing existing behaviour. Security regressions are permanent tests. No claim "tests passed" without real output.

## 2. Test layers
| Layer | Tools | Scope |
|---|---|---|
| Unit | Pytest | pure functions (attendance %, eligibility rules, chunker, token helpers) |
| Service/repository | Pytest + PostgreSQL | business rules, transactions |
| API | Pytest + HTTPX test client | routes, status codes, authorisation matrix |
| Migration | Pytest + Alembic | upgrade from scratch, from copy of real data, drift check, single head |
| Security regression | Pytest | C1, C2, C3, OAuth, rate limit, refresh, IDOR, injection |
| AI evaluation | Pytest + labelled sets | routing accuracy, retrieval hit-rate, groundedness, permission isolation |
| Frontend static | `npm run lint`, `npm run build` | in CI |
| Manual | checklists | Google real-credentials flow, role walkthrough, UI parity, accessibility |

A frontend unit-test runner (Vitest) and Playwright end-to-end tests are later decisions (P25) and need approval.

## 3. Test database
`campusgpt_test` inside the existing PostgreSQL instance (PD-05); created by script; migrations applied through Alembic; per-test isolation by transaction or table reset. CI uses the pgvector image as a service container.

## 4. Fakes and fixtures
- Email: capture sent messages and OTPs in memory.
- Google: fake token and userinfo responses.
- Time: controllable clock for expiry, rate limits and rotation leeway.
- LLM/embeddings: deterministic stub provider for pipeline tests; real provider only in manual evaluation.
- Users: factories for STUDENT, pending FACULTY, approved FACULTY, ADMIN, deactivated, Google-only.

## 5. Mandatory suites
- **Characterization (WP0):** register→verify→login, `/me`, refresh, reset, Google new/existing, `/health`.
- **Authentication:** every auth route and state.
- **OTP security:** lockout, window, wrong email, domain, provider failure, replay.
- **Password login:** null-hash user, wrong/correct password, timing-safe path executed.
- **Role escalation:** ADMIN rejected, FACULTY pending, approval and rejection, self-approval, pending-user access.
- **OAuth:** code exchange, replay, expiry, state/cookie mismatch.
- **Rate limiting:** each limit, reset, spoofed forwarded headers.
- **Refresh tokens:** rotation, reuse, leeway, concurrency, revocation.
- **Authorisation matrix:** for every module, each role × route.
- **Mutation spot-checks:** re-introduce each critical defect on a throwaway branch; a test must fail.

## 6. Coverage and quality gates
Coverage is reported for `app/auth` and `app/core` first; thresholds are set after the baseline (no arbitrary number promised here). CI must be green before merging and before starting the next work package.

## 7. Defect handling
Known defects found by characterization are captured as `xfail(strict=True)` with their ID, then converted to normal tests when fixed.

## 8. Test data
Synthetic only; never production data; seeds are separate from test factories.

## 9. Additional suites (final correction)
- **WebSocket:** authentication timeout and failure, expired token, identity fixed per connection, cross-user conversation id rejected, stop generation, disconnect cancels generation, idempotent reconnect, oversize frame, rate limit, Origin rejection, attendance channel owner check.
- **Biometrics (mock provider):** no enrolment without consent, withdrawal deletes template, single-use challenge, duplicate prevention under concurrency, manual fallback, override audit and previous-value retention, faculty/admin cannot read templates or images, production refuses the mock provider.
- **Voice (Vapi stubbed):** tool call without Vapi authentication → 401; valid Vapi authentication with expired/unbound voice session → 403; spoofed user id in arguments ignored; cross-user data never returned; fallback to text chat; session invalidation after end.
- **Authentication enumeration:** identical responses for existing and non-existing emails on login, forgot-password and send-otp; Google account-linking rules.
Never use real Vapi, Google, Resend or LLM credentials in tests.
