# 38 — Integration with the Existing Project

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Preserve (must remain working after every change)
Landing, sign-in and sign-up pages; forgot/reset password; Google OAuth; email OTP; password login; JWT behaviour (hardened); existing users and OTP rows; college-domain restrictions; `create_admin` CLI; Docker and Nginx configuration (improved, not replaced); old `Architecture/` and `Flowcharts/` folders.

## 2. Touch points that will change (and how)
| Existing file/area | Change | Package | Risk | Mitigation |
|---|---|---|---|---|
| `backend/app/auth/service.py` | fix `authenticate_user`, `verify_otp`; token issue/rotation | WP2, WP4, WP6 | breaking login | characterization tests first |
| `backend/app/auth/schemas.py` | `RegisterRequest.role` becomes a request, ADMIN rejected | WP2 | clients sending ADMIN | none expected; UI sends STUDENT/FACULTY |
| `backend/app/auth/repository.py` | `has_recent_used_email_otp` → verified check | WP2 | sign-ups in flight re-verify | communicate |
| `backend/app/auth/router.py` | new exchange/logout routes, 429/503 responses | WP2–WP6 | response-shape changes | keep shapes; version if needed |
| `backend/app/core/config.py` | validation, removal of defaults | WP3 | startup failures in misconfigured envs | clear messages; docs |
| `backend/alembic/env.py`, `models/__init__.py` | import models, clean duplicates | WP1 | wrong autogenerate | scratch DB check |
| `frontend/src/context/AuthContext.jsx` | code exchange, `apiFetch`, refresh, logout | WP4, WP7 | session loss | manual role checklist |
| `frontend/src/routes/AppRoutes.jsx` | role routes replace single `/app` | WP7, P05 | broken deep links | redirects |
| `docker-compose.yml`, `backend/Dockerfile` | migrate service, non-root, split layers | WP8 | dev workflow change | override file keeps one-command dev |
| `.env.example`, README config section | updated names/guidance | WP3, WP8 | confusion | docs |
| `backend/requirements.txt` | split dev/AI requirement files | WP8 | missing packages | import check first |

## 3. Files that must **not** be edited
`frontend/src/features/prototype-visuals/AuthScreen.jsx` and `LandingPage.jsx` visuals; existing migrations; `Architecture/*.md`.

## 4. Compatibility matrix
| Client | Impact |
|---|---|
| Existing React app | Needs the WP4/WP7 changes together with backend WP4/WP6 |
| Swagger (`/docs`) | Dev only after WP3 |
| Old tokens | Invalidated at WP6 deploy; users sign in again |
| Old in-flight OTPs | Do not count as verification after WP2 |

## 5. Data migration impact
Only additive tables/columns; no backfill. Existing elevated accounts reviewed manually. Multi-college stays; PD-07 may later add `institution_id` with a backfill derived from `users.college`.

## 6. Rollout order
Follow `Foundation_Execution_Order.md`. Deploy backend and frontend changes of a package together; take a backup before each migration; keep the previous release tag for rollback.

## 7. Roadmap reference
| Phase | Name | Stage | Depends on |
|---|---|---|---|
| P01 | Existing project audit | Stage 0 (audit, repeated on HEAD) | None (read-only) |
| P02 | Architecture and database audit | Stage 0/1 (audit) | P01 |
| P03 | UI reference audit | Stage 1 | P01; five reference images placed in `assets/references/`; AI Studio prototype extracted to `ui-reference/google-ai-studio/` |
| P04 | Design system and application shell | Stage 1 | Foundation accepted; P03 |
| P05 | Role-based dashboards and navigation | Stage 1 | P04; WP2, WP7; PD-07 and PD-14 decided |
| P06 | Student profile | Stage 2 | P05; PD-13 |
| P07 | Attendance | Stage 2 | P05; P08 (build the timetable first — sessions link to timetable entries); PD-10 for production enablement of the face slice; PD-25 for multi-worker live updates |
| P08 | Timetable | Stage 2 | P05 |
| P09 | Assignments | Stage 2 | P05, storage decision PD-12 |
| P10 | Notices and notifications | Stage 2 | P05 |
| P11 | Document management | Stage 2 | P05, PD-12 |
| P12 | CampusGPT AI interface | Stage 3 | P11; PD-11, PD-18 |
| P13 | Intent detection and routing | Stage 3 | P12; tools from P06–P10 |
| P14 | RAG ingestion and retrieval | Stage 3 | P11, P13; WP1 pgvector; PD-11; `requirements-ai.txt` |
| P15 | Academic analytics | Stage 4 | P07, P09, marks data |
| P16 | Placement intelligence | Stage 4 | P06, P10 |
| P17 | Internships and hackathons | Stage 4 | P16 |
| P18 | Course recommendations | Stage 4 | P15 |
| P19 | Visual Learning Workspace | Stage 4 | P12 (for AI generation); canvas ADR |
| P20 | Faculty dashboard | Stage 2 | P07–P11 |
| P21 | Admin dashboard | Stage 2 | P05; WP2, WP11 |
| P22 | Voice features | Stage 4 | P12, P13, P14; PD-19 (Vapi deployment details) |
| P23 | Security and permissions review | Stage 6 | All feature phases |
| P24 | Integration and UI parity | Stage 5 | P04–P22 |
| P25 | Testing and deployment | Stage 6 | P23, P24 |

## 8. Real-time, voice and biometric integration points (PROPOSED)
| Area | Integration | Risk | Mitigation |
|---|---|---|---|
| WebSocket | Reuse existing JWT verification; add Nginx upgrade config | Connection auth differs from HTTP | Shared helper, protocol tests |
| Vapi | New `voice` module calling existing services; Vapi credentials in the secret store | Provider-specific payloads unverified | Verify against current Vapi docs; stub in tests |
| Biometrics | New `biometrics` module behind an interface; attendance module consumes events | Privacy/legal exposure | PD-10, doc 14, consent and fallback first |
Existing-repository statements throughout this document are PO-RV (previously observed, re-verification required).
