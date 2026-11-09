# 39 — Implementation Roadmap

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

The original 25 phases are preserved (P01–P25) and re-sequenced under seven stages so that **foundation stabilisation comes first**. Phase numbers are stable identifiers, not strict execution order — dependencies decide order.

## Stages
| Stage | Name | Contents |
|---|---|---|
| Stage 0 | Repository and foundation stabilisation | WP0–WP11, P01–P02 re-audits |
| Stage 1 | Core application foundation | P03, P04, P05 (backend modular structure, app shell, role routing, API client, permission framework) |
| Stage 2 | Core ERP | P06–P11, P20, P21 — recommended build order by dependency: P06, P08, P07, P09, P10, P11, P21 (approval UI), P20 |
| Stage 3 | CampusGPT AI foundation | P12–P14 |
| Stage 4 | Advanced AI and analytics | P15–P19, P22 |
| Stage 5 | UI integration and refinement | P24 |
| Stage 6 | Production readiness | P23, P25 |

## Stage 0 detail
WP0–WP11 in the order given in `docs/foundation-stabilisation/Foundation_Execution_Order.md`. ERP and AI development starts only after the Foundation Acceptance Checklist is signed.

## Dependency summary
Foundation → P04 → P05 → (P06, P08, P09, P10, P11) → P07 (with timetable linkage) → P20, P21 → P12 → P13 → P14 → (P15…P19, P22) → P24 → P23 → P25. Decisions needed before specific phases: PD-07 and PD-14 before P05; PD-13 before P06; PD-12 before P09/P11; PD-10 before advanced P07; PD-11 and PD-18 before P12; PD-19 before P22.

## Phases
Each phase follows the same loop: inspect → plan → small implementation steps → tests → report → human approval.

### P01 — Existing project audit
- **Stage:** Stage 0 (audit, repeated on HEAD)
- **Dependencies:** None (read-only)
- **Deliverables:** Audit report of the live repository HEAD compared with `docs/architecture/00_Source_Reconciliation_and_Baseline.md`
- **Acceptance criteria:** Every divergence from the baseline listed; no file modified
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P01_Existing_project_audit.md](prompts/phases/P01_Existing_project_audit.md)

### P02 — Architecture and database audit
- **Stage:** Stage 0/1 (audit)
- **Dependencies:** P01
- **Deliverables:** Verified inventory of models, migrations, endpoints, settings; gap list for academic structure and PD-07/PD-14 inputs
- **Acceptance criteria:** Inventory matches code; open questions recorded
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P02_Architecture_and_database_audit.md](prompts/phases/P02_Architecture_and_database_audit.md)

### P03 — UI reference audit
- **Stage:** Stage 1
- **Dependencies:** P01; five reference images placed in `assets/references/`; AI Studio prototype extracted to `ui-reference/google-ai-studio/`
- **Deliverables:** Mapping of prototype screens/routes/components to the real frontend (doc 35) and the required-changes list
- **Acceptance criteria:** Mapping complete; prototype never copied over the real frontend; mock data not imported
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P03_UI_reference_audit.md](prompts/phases/P03_UI_reference_audit.md)

### P04 — Design system and application shell
- **Stage:** Stage 1
- **Dependencies:** Foundation accepted; P03
- **Deliverables:** Tailwind v4 token layer, component library (doc 33), AppShell with sidebar/header, Lucide icons, dark-only, loading/empty/error patterns
- **Acceptance criteria:** Components documented and used by the shell; no light-mode styles; build and lint pass; existing auth pages untouched
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P04_Design_system_and_application_shell.md](prompts/phases/P04_Design_system_and_application_shell.md)

### P05 — Role-based dashboards and navigation
- **Stage:** Stage 1
- **Dependencies:** P04; WP2, WP7; PD-07 and PD-14 decided
- **Deliverables:** Role-aware routing and navigation, permission policy framework, academic structure tables (departments, branches, programs, years, semesters, subjects, classes, enrolments, designations), empty-state dashboards per role
- **Acceptance criteria:** Each role sees only its navigation; backend policies tested; migrations additive
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P05_Role-based_dashboards_and_navigation.md](prompts/phases/P05_Role-based_dashboards_and_navigation.md)

### P06 — Student profile
- **Stage:** Stage 2
- **Dependencies:** P05; PD-13
- **Deliverables:** Student profile, verified vs editable fields, student dashboard aggregation (empty states)
- **Acceptance criteria:** IDOR tests pass; verified fields admin-only
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P06_Student_profile.md](prompts/phases/P06_Student_profile.md)

### P07 — Attendance
- **Stage:** Stage 2
- **Dependencies:** P05; P08 (build the timetable first — sessions link to timetable entries); PD-10 for production enablement of the face slice; PD-25 for multi-worker live updates
- **Deliverables:** Slice A: sessions from timetable entries, manual marking, calculations, history, shortage and recovery, real-time roster, audit. Slice B (required scope): face recognition and liveness behind a provider interface, consent, enrolment, geofence evidence, duplicate prevention, manual fallback and override. Production enablement of slice B waits for PD-10 and the privacy/legal review
- **Acceptance criteria:** Calculations match fixtures; all marks, verifications and overrides audited; face verification implemented, tested and consent/fallback-safe behind the provider interface; no claim of production biometric readiness before PD-10 and privacy/legal review
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P07_Attendance.md](prompts/phases/P07_Attendance.md)

### P08 — Timetable
- **Stage:** Stage 2
- **Dependencies:** P05
- **Deliverables:** Entries, conflict detection, changes, calendar, student/faculty views
- **Acceptance criteria:** No double-booking possible
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P08_Timetable.md](prompts/phases/P08_Timetable.md)

### P09 — Assignments
- **Stage:** Stage 2
- **Dependencies:** P05, storage decision PD-12
- **Deliverables:** Assignment lifecycle, submissions, evaluation, secure file handling
- **Acceptance criteria:** Download authorisation and upload validation tests pass
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P09_Assignments.md](prompts/phases/P09_Assignments.md)

### P10 — Notices and notifications
- **Stage:** Stage 2
- **Dependencies:** P05
- **Deliverables:** Notice targeting/publishing, read tracking, in-app notifications and event hooks
- **Acceptance criteria:** Audience rules enforced in SQL; XSS payloads neutralised
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P10_Notices_and_notifications.md](prompts/phases/P10_Notices_and_notifications.md)

### P11 — Document management
- **Stage:** Stage 2
- **Dependencies:** P05, PD-12
- **Deliverables:** Library, versions, ACL service, processing status (no indexing yet)
- **Acceptance criteria:** One ACL function used everywhere; deletion rules documented
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P11_Document_management.md](prompts/phases/P11_Document_management.md)

### P12 — CampusGPT AI interface
- **Stage:** Stage 3
- **Dependencies:** P11; PD-11, PD-18
- **Deliverables:** Chat workspace, conversations, WebSocket streaming channel (auth on connect, typed events, stop, reconnection), provider adapter, citations placeholder, token budgets
- **Acceptance criteria:** No cross-user leakage; stop/regenerate work; WebSocket protocol tests pass
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P12_CampusGPT_AI_interface.md](prompts/phases/P12_CampusGPT_AI_interface.md)

### P13 — Intent detection and routing
- **Stage:** Stage 3
- **Dependencies:** P12; tools from P06–P10
- **Deliverables:** Router, tool registry with permission-checked tools, clarification and refusal behaviour, evaluation set
- **Acceptance criteria:** Routing accuracy measured; no authorisation bypass
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P13_Intent_detection_and_routing.md](prompts/phases/P13_Intent_detection_and_routing.md)

### P14 — RAG ingestion and retrieval
- **Stage:** Stage 3
- **Dependencies:** P11, P13; WP1 pgvector; PD-11; `requirements-ai.txt`
- **Deliverables:** Ingestion worker, chunking, embeddings, hybrid permission-filtered retrieval, citations, evaluation (docs 21–22)
- **Acceptance criteria:** Unauthorised chunks never returned; retrieval metrics meet agreed threshold
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P14_RAG_ingestion_and_retrieval.md](prompts/phases/P14_RAG_ingestion_and_retrieval.md)

### P15 — Academic analytics
- **Stage:** Stage 4
- **Dependencies:** P07, P09, marks data
- **Deliverables:** Student, faculty and admin analytics with transparent rules
- **Acceptance criteria:** Every number traceable to records
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P15_Academic_analytics.md](prompts/phases/P15_Academic_analytics.md)

### P16 — Placement intelligence
- **Stage:** Stage 4
- **Dependencies:** P06, P10
- **Deliverables:** Companies, opportunities, eligibility engine with explanations, applications, statistics
- **Acceptance criteria:** Eligibility deterministic and explained
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P16_Placement_intelligence.md](prompts/phases/P16_Placement_intelligence.md)

### P17 — Internships and hackathons
- **Stage:** Stage 4
- **Dependencies:** P16
- **Deliverables:** Opportunity listings, bookmarks, participation tracking
- **Acceptance criteria:** Eligibility consistent with placements
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P17_Internships_and_hackathons.md](prompts/phases/P17_Internships_and_hackathons.md)

### P18 — Course recommendations
- **Stage:** Stage 4
- **Dependencies:** P15
- **Deliverables:** Catalogue, recommendations with reasons, progress, feedback
- **Acceptance criteria:** Every recommendation explained
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P18_Course_recommendations.md](prompts/phases/P18_Course_recommendations.md)

### P19 — Visual Learning Workspace
- **Stage:** Stage 4
- **Dependencies:** P12 (for AI generation); canvas ADR
- **Deliverables:** Canvas editor, save/export, validated AI diagram generation
- **Acceptance criteria:** Invalid AI output never reaches the canvas
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P19_Visual_Learning_Workspace.md](prompts/phases/P19_Visual_Learning_Workspace.md)

### P20 — Faculty dashboard
- **Stage:** Stage 2
- **Dependencies:** P07–P11
- **Deliverables:** Faculty workspace composed from module services
- **Acceptance criteria:** No data outside assignments
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P20_Faculty_dashboard.md](prompts/phases/P20_Faculty_dashboard.md)

### P21 — Admin dashboard
- **Stage:** Stage 2
- **Dependencies:** P05; WP2, WP11
- **Deliverables:** Admin workspace including role-request approval UI, audit viewer, import wizard
- **Acceptance criteria:** All admin mutations audited
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P21_Admin_dashboard.md](prompts/phases/P21_Admin_dashboard.md)

### P22 — Voice features
- **Stage:** Stage 4
- **Dependencies:** P12, P13, P14; PD-19 (Vapi deployment details)
- **Deliverables:** Voice mode through Vapi: Web SDK client, backend voice sessions, secured Vapi custom Function Tool endpoints calling the same policies as text chat, fallback to text, usage logging
- **Acceptance criteria:** Voice and text yield identical authorisation outcomes; no Vapi path reaches the database except through audited FastAPI tools
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P22_Voice_features.md](prompts/phases/P22_Voice_features.md)

### P23 — Security and permissions review
- **Stage:** Stage 6
- **Dependencies:** All feature phases
- **Deliverables:** Full authorisation-matrix test run, dependency and secret scan, upload and prompt-injection review, findings fixed
- **Acceptance criteria:** No open critical/high finding
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P23_Security_and_permissions_review.md](prompts/phases/P23_Security_and_permissions_review.md)

### P24 — Integration and UI parity
- **Stage:** Stage 5
- **Dependencies:** P04–P22
- **Deliverables:** Real frontend compared with the AI Studio prototype using the parity checklist (doc 36); responsive and accessibility fixes; animations within motion rules
- **Acceptance criteria:** Parity checklist signed; no production component uses prototype mock data
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P24_Integration_and_UI_parity.md](prompts/phases/P24_Integration_and_UI_parity.md)

### P25 — Testing and deployment
- **Stage:** Stage 6
- **Dependencies:** P23, P24
- **Deliverables:** End-to-end tests, performance smoke, production Compose deployment runbook, backups/restore rehearsal, monitoring, seed-data guard verification
- **Acceptance criteria:** Production readiness checklist passed; final acceptance (doc 40)
- **Approval gate:** owner reviews the implementation report, runs the listed checks, and updates `IMPLEMENTATION_STATUS.md` before the next phase.
- **Prompt:** [P25_Testing_and_deployment.md](prompts/phases/P25_Testing_and_deployment.md)


## Original phase names (traceability)
P01 Existing project audit · P02 Architecture and database audit · P03 UI reference audit · P04 Design system and application shell · P05 Role-based dashboards and navigation · P06 Student profile · P07 Attendance · P08 Timetable · P09 Assignments · P10 Notices and notifications · P11 Document management · P12 CampusGPT AI interface · P13 Intent detection and routing · P14 RAG ingestion and retrieval · P15 Academic analytics · P16 Placement intelligence · P17 Internships and hackathons · P18 Course recommendations · P19 Visual Learning Workspace · P20 Faculty dashboard · P21 Admin dashboard · P22 Voice features · P23 Security and permissions review · P24 Integration and UI parity · P25 Testing and deployment.

## Ordering notes (final correction)
- **WP9 after WP10 and WP11 is intentional:** each work package writes its own tests; WP9 completes and verifies the whole regression suite after CI and logging exist.
- **P01 and P02** are the repository and architecture/database audits; they run inside Stage 0 (prompt 02, WP0, prompt 05) and again as read-only prompts when the repository changes materially.
- **Stage 2 recommended build order by dependency:** P06 → P08 → P07 → P09 → P10 → P11 → P21 (role-request approval UI) → P20.
- **P07 contains two required slices:** (A) core attendance, (B) face recognition and liveness behind a provider interface. Only the production enablement of slice B waits for PD-10 and the privacy/legal review.
- **P12** delivers the WebSocket chat channel; **P22** delivers Vapi voice and depends on P12–P14 tools.
- **PD-07 and PD-14 must be resolved before P05.**
- Phase identifiers P03–P25 and work packages WP0–WP11 are unchanged from the earlier package.
