# Foundation Execution Order

This is the mandatory order for Stage 0. ERP and AI development begins only after step 19.

| Step | Work | Work package | Gate |
|---|---|---|---|
| 1 | Repository audit and baseline | WP0 | Baseline report reviewed |
| 2 | Backup and database preflight | WP0 | Backup restore-tested; elevated accounts listed |
| 3 | Test infrastructure and characterization tests | WP0 (minimal), WP9 (complete) | Characterization suite green |
| 4 | Alembic model registration | WP1 | Autogenerate drift report = none |
| 5 | Migration-chain verification | WP1 | Single head |
| 6 | pgvector extension migration | WP1 | Extension on fresh DB |
| 7 | Critical authentication fixes (C1, C2) | WP2 | Regression tests green |
| 8 | Role-based registration and faculty approval (C3) | WP2 | Owner review of elevated accounts |
| 9 | Production configuration guards | WP3 | Unsafe configs fail to start |
| 10 | Secure OAuth code exchange | WP4 | Manual real-credentials Google test |
| 11 | Authentication rate limiting | WP5 | Thresholds approved |
| 12 | Refresh-token rotation and revocation | WP6 | PD-03, PD-04 answered |
| 13 | Frontend authentication integration | WP7 | Manual role checklist |
| 14 | Docker migration strategy | WP8 | Production layer reviewed |
| 15 | CI/CD | WP10 | Required checks enabled |
| 16 | Logging and audit foundation | WP11 | Redaction verified |
| 17 | Foundation regression testing | WP9 (completion) | Full suite green |
| 18 | Security verification | Security audit prompt | No open critical/high finding |
| 19 | Foundation acceptance sign-off | Acceptance checklist | Owner signature |
| 20 | Begin ERP and AI development | Phases P04 onward | — |

Notes:

- Each work package writes its own tests. WP9 formalises and completes the suite; it does not postpone testing.
- WP2 refers to audit logging; until WP11 exists the approval trail lives in the `role_requests` row (reviewer, time, note). WP11 later back-fills audit events going forward only; it never rewrites history.
- If a work package is blocked by a pending decision, continue with unrelated packages only when the dependency graph allows it (WP1 → WP2; WP2 → WP6; WP4 and WP6 → WP7).

- **WP9 completes after WP10 and WP11 by design:** earlier packages add their own tests; WP9 verifies the whole suite once CI and logging exist.
- Security verification (prompts 05 and 12) and acceptance sign-off follow WP9. P05 additionally requires PD-07 and PD-14 to be resolved.
