# DECISION_REGISTER

The single consolidated register of every pending decision (`PD-xx`). Approved decisions (`D-xx`) are in `PROJECT_DECISIONS.md`; full detail per decision is in `PENDING_DECISIONS.md`; accepted architectural decisions are in `docs/architecture/adr/`.

**Status meanings:** PENDING — not decided · PENDING — explicit owner review required (provisional default) — foundational, a temporary default exists · DIRECTION CONFIRMED BY OWNER — parameters pending — the owner has fixed the direction, details still need approval.

## Gates that must be cleared before specific phases
- **Before P05:** PD-07 (multi-college data isolation) and PD-14 (designation and permission model).
- **Before Stage 0 acceptance:** PD-01 to PD-06 reviewed.
- **Before production enablement of face verification (P07 slice B):** PD-10.
- **Before P22 production enablement:** PD-19.

## Register
| ID | Topic | Status | Existing documented default | Recommended direction | Dependencies | Blocked implementation | Must happen before approval |
|---|---|---|---|---|---|---|---|
| PD-01 | Interim faculty-approval path | PENDING — explicit owner review required (provisional default) | (a) Swagger + CLI | (a) | WP2 | WP2 sign-off (not WP2 start) | Owner states choice in `DECISION_REGISTER.md` |
| PD-02 | Staff and student email domains | PENDING — explicit owner review required (provisional default) | (a) assume shared | (a), approval only | WP2 | WP2 policy details | Owner confirms real domain structure |
| PD-03 | Access-token lifetime | PENDING — explicit owner review required (provisional default) | 15 | 15 | WP6, WP7 | WP6 configuration default | Owner approves; WP7 ships with WP6 |
| PD-04 | Interim token storage | PENDING — explicit owner review required (provisional default) | (a) now, re-evaluate at P23 | (a) now, cookies evaluated under PD-23 | WP6, WP7 | none for Stage 0 (documented limitation) | Owner accepts the documented risk |
| PD-05 | Test database name | PENDING — explicit owner review required (provisional default) | (a) | (a) | WP0 | WP0 harness | Owner confirms; guard requires the name to end in `_test` |
| PD-06 | Review of existing elevated accounts | PENDING — explicit owner review required (provisional default) | (a); never auto-demote | (a) | WP0 list | WP2 sign-off | Owner reviews the masked list from WP0 |
| PD-07 | Multi-college data isolation | PENDING | None adopted; design tables so an institution key can be added additively | Evaluate (b) with P02 findings | P02 audit | **P05 and every later academic table** — must be resolved before P05 | Owner reviews the P02 impact report and chooses |
| PD-08 | Backend linter for CI | APPROVED | Ruff (single fast tool) | Ruff | WP10 | WP10 lint step only | Owner approved Ruff in WP10 implementation |
| PD-09 | Document formats and delivery order | PENDING | (a) | (a) | P11, P14 | P14 parser slices (not P11 upload/storage) | Owner approves order |
| PD-10 | Face-recognition provider and biometric policies | PENDING | None adopted; build provider-agnostic with a clearly-labelled mock provider in development | Shortlist after a privacy-impact assessment | Privacy/legal review; P07 slice A | **Production enablement of P07 slice B** (slice A and the provider-agnostic code are not blocked) | Provider chosen; retention/consent policy approved; privacy and legal review recorded |
| PD-11 | LLM and embedding providers, vector dimension | PENDING | None adopted (configurable provider adapter) | Decide at the start of P12 (LLM) and P14 (embeddings) | P11 outputs | P12 provider adapter go-live; **P14 vector column creation** | Owner chooses providers; dimension recorded in an ADR |
| PD-12 | Document and upload storage provider | PENDING | Docker volume behind a storage interface for development | Storage interface now, provider later | WP8 | P09, P11 | Owner chooses production storage |
| PD-13 | Institutional data import | PENDING | Admin CSV import with dry-run | CSV import | P05 structure | P06 (and P21 import wizard) | Owner provides the data source and format |
| PD-14 | Designation and permission model | PENDING | Roles stay ADMIN/FACULTY/STUDENT; designations add scoped permissions | Designation rows with scope (department/institution/function) | P02 audit | **P05 and P10 notice targeting** — must be resolved before P05 | Owner approves the permission sets |
| PD-15 | Actual institutional email domains | PENDING | Use the documented mapping in development only | Confirm before production | — | Production go-live (WP2/WP3 can proceed in development) | Owner supplies verified domains |
| PD-16 | UI palette / design-system alignment | PENDING | (a) | (a) | P03 reference images | P04 final token values | Owner reviews the five reference images and the token proposal |
| PD-17 | Hosting and deployment target | PENDING | Generic Nginx + HTTPS documentation | Decide before WP8 production layer is finalised | — | WP8 production layer finalisation, P25 | Owner states target and domain |
| PD-18 | Real-time communication — WebSocket | DIRECTION CONFIRMED BY OWNER — parameters pending | WebSocket; first-message auth with the access token (no token in the URL); limits as in `docs/architecture/WebSocket_Protocol.md` | As documented | — | P12 protocol sign-off (not P12 start) | Owner reviews `docs/architecture/WebSocket_Protocol.md` |
| PD-19 | Voice — Vapi | DIRECTION CONFIRMED BY OWNER — parameters pending | Vapi with recording disabled by default and secured FastAPI tools | As documented in doc 37 | P12–P14 tools | **P22 production enablement** (design and development against a test Vapi account are not blocked) | Owner approves credentials handling, plan, configuration and privacy review |
| PD-20 | Google Calendar integration | PENDING | Design only; export first | Export | P08 | P08 calendar-sync slice | Owner chooses scope |
| PD-21 | Cleanup of dead routes and files | PENDING | Verify references in a later cleanup task | Cleanup after verification | P01/WP0 re-verification | A cleanup task after P24 | Owner approves a verified list |
| PD-22 | Verified Resend sender domain | PENDING | Development sender only | Verify a domain | — | Production go-live | Owner verifies domain |
| PD-23 | Production token design | PENDING | Evaluate in P23 | Evaluate cookies + CSRF | PD-04 | P23 | Security review recommendation |
| PD-24 | Admin bootstrap and recovery | PENDING | CLI with a documented runbook | CLI runbook | WP2 | P25 | Owner approves runbook |
| PD-25 | WebSocket scaling and server push without Redis | PENDING | (a) with (c) as fallback; evaluate (b) | Evaluate (b) in P10/P12 | PD-17 | Live attendance roster scale-out (P07), notification push (P10), multi-worker chat (P12) | Owner approves an approach in an ADR |

## Foundational decisions for explicit approval (PD-01 to PD-06)
| ID | Decision | Default | Approve? |
|---|---|---|---|
| PD-01 | Interim faculty approval path | Swagger + CLI | ☐ approve ☐ change to: ____ |
| PD-02 | Staff and students share an email domain | Assume yes; approval is the only gate | ☐ approve ☐ change to: ____ |
| PD-03 | Access-token lifetime | 15 minutes | ☐ approve ☐ change to: ____ |
| PD-04 | Interim token storage | `localStorage`, re-evaluated under PD-23 | ☐ approve ☐ change to: ____ |
| PD-05 | Test database | `campusgpt_test` in the existing PostgreSQL | ☐ approve ☐ change to: ____ |
| PD-06 | Existing elevated accounts | Owner reviews the WP0 list; no auto-demotion | ☐ approve ☐ change to: ____ |
