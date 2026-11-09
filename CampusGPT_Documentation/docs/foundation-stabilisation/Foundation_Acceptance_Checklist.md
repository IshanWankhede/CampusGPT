# Foundation Acceptance Checklist

Stage 0 is complete only when **every** box is ticked by the owner with evidence. Until then no ERP or AI phase (P04 onward) starts.

| # | Gate | Evidence required | Done |
|---|---|---|---|
| 1 | Baseline tag, restore-tested backup, baseline report (WP0) | files + checksum | ☐ |
| 2 | Characterization tests green on unmodified code (WP0) | CI/log | ☐ |
| 3 | Alembic registers all models; drift check clean; single head (WP1) | command output | ☐ |
| 4 | pgvector migration works on fresh and existing DB (WP1) | command output | ☐ |
| 5 | C1 fixed with tests (WP2) | test report | ☐ |
| 6 | C2 fixed with tests (WP2) | test report | ☐ |
| 7 | C3 fixed; faculty approval works; elevated accounts reviewed by owner (WP2) | test report + owner note | ☐ |
| 8 | Unsafe production configuration fails to start (WP3) | tests | ☐ |
| 9 | OAuth uses one-time code; no tokens in URLs; manual Google test passed (WP4) | test + owner | ☐ |
| 10 | Rate limits enforced; thresholds approved (WP5) | tests + owner | ☐ |
| 11 | Refresh rotation, reuse detection, revocation work (WP6) | tests | ☐ |
| 12 | Frontend client refreshes and signs out correctly; role guards work (WP7) | manual checklist | ☐ |
| 13 | Migrations run through the one-shot service; production layer validated; non-root image (WP8) | compose validation | ☐ |
| 14 | Full suite and mutation spot-checks pass (WP9) | report | ☐ |
| 15 | CI runs and is required (WP10) | screenshot/settings | ☐ |
| 16 | Structured logs redact secrets; audit events recorded (WP11) | redaction test | ☐ |
| 17 | Regression checklist fully executed (step 17) | filled checklist | ☐ |
| 18 | Security verification found no open critical/high issue (step 18) | report | ☐ |
| 19 | Pending decisions needed for Stage 1 answered (PD-07, PD-13, PD-14) | owner note | ☐ |

Sign-off: ____________________ Date: __________
