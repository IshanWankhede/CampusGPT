# 40 — Acceptance Criteria

Nothing is accepted on the basis of a UI alone. Each criterion needs evidence (command output, test report, screenshot). Completion levels: UI implemented → frontend functional → backend implemented → database integrated → tested → production-ready.

## A. Global criteria (every phase)
- [ ] Existing landing, sign-in, sign-up and authentication flows still work (regression checklist executed)
- [ ] All migrations additive, reviewed, backed up, single Alembic head
- [ ] Tests executed on a PostgreSQL `_test` database; real output reported
- [ ] Authorisation matrix tests cover each new route and AI tool
- [ ] No forbidden technology introduced; no new dependency without approval
- [ ] No secrets in code, logs or reports
- [ ] Dark mode only; Lucide icons for new UI; empty/loading/error states
- [ ] Docs, ADRs and status files updated; no feature marked complete without verification

## B. Foundation (Stage 0)
See `docs/foundation-stabilisation/Foundation_Acceptance_Checklist.md` (19 gates). Key technical criteria:
- [ ] C1: a null-hash account cannot log in with a password
- [ ] C2: failed OTP attempts never create a verified state; verified window 15 minutes
- [ ] C3: public registration creates STUDENT only; faculty need admin approval; ADMIN never via API
- [ ] No tokens in URLs; Google flow uses one-time code with state cookie
- [ ] Production refuses default/weak secrets (JWT ≥ 32 chars), dev credentials, localhost CORS, SQLite
- [ ] Rate limits enforced with 429 and `Retry-After`
- [ ] Refresh rotation with family reuse detection; logout/reset/deactivation revoke
- [ ] Alembic registers all models; pgvector created by migration; migrations run through one-shot service
- [ ] CI runs backend tests, migration checks, frontend lint and build
- [ ] Logs redact secrets; audit trail records authentication and admin actions

## C. Module criteria
### Student Dashboard and Profile (P05–P06)
- [ ] Student sees only own data.
- [ ] Verified vs editable distinction enforced by API, not only by UI.
- [ ] Dashboard cards render real data when seeded and empty states otherwise.

### Attendance Management (P07)
- [ ] Calculations match fixtures.
- [ ] All mutations and overrides audited.
- [ ] No cross-student leakage.
- [ ] Face verification and liveness implemented behind the provider interface with consent, fallback and audit; no claim of production biometric readiness until PD-10 and the privacy/legal review are complete.

### Face Recognition and Liveness (P07 (slice B))
- [ ] Consent, enrolment, verification, liveness, fallback, override and audit are implemented behind the provider interface and tested.
- [ ] Production enablement only after PD-10 and the privacy/legal review are recorded as complete.

### Timetable Management (P08)
- [ ] No double-booking possible through the API.
- [ ] Students see only their classes.

### Assignment Management (P09)
- [ ] Students cannot see others' submissions or unpublished marks.
- [ ] Upload validation rejects spoofed types.

### Notices and Notifications (P10)
- [ ] No user sees a notice outside its audience.
- [ ] Sanitised rich text.

### Document Management (P11)
- [ ] ACL enforced in one place.
- [ ] Processing state visible and retryable.

### CampusGPT AI Assistant (P12)
- [ ] Answers cite authorised sources or say none found.
- [ ] No cross-user data in any test.
- [ ] WebSocket protocol implemented as documented, with tests for authentication, stop, errors and reconnection.

### Intent Detection and Routing (P13)
- [ ] Routing accuracy measured on a labelled set.
- [ ] No test shows routing bypassing authorisation.

### RAG Architecture (P14)
- [ ] Unauthorised chunks are never returned.
- [ ] Retrieval evaluation meets the agreed threshold.

### Document Ingestion and Retrieval Pipeline (P14)
- [ ] Every failure is visible and retryable.
- [ ] Pipeline is restartable without duplicates.

### Academic Analytics (P15)
- [ ] Every number traces to stored records.

### Placement Intelligence (P16)
- [ ] Eligibility is deterministic and explained.

### Internships and Hackathons (P17)
- [ ] Eligibility consistent with placements.

### Course Recommendation System (P18)
- [ ] Every recommendation has a reason.

### Visual Learning Workspace (P19)
- [ ] Invalid AI output never reaches the canvas.

### Voice Interaction (Vapi) (P22)
- [ ] Voice and text yield identical authorisation outcomes.
- [ ] No Vapi path reaches the database except through audited FastAPI tools.
- [ ] Credentials and privacy approval recorded as deployment decisions, not hard-coded.

### Faculty Dashboard (P20)
- [ ] No faculty sees data outside assignments.

### Admin Dashboard (P21)
- [ ] All admin mutations audited.


## D. Phase criteria
- **P01 Existing project audit:** Every divergence from the baseline listed; no file modified
- **P02 Architecture and database audit:** Inventory matches code; open questions recorded
- **P03 UI reference audit:** Mapping complete; prototype never copied over the real frontend; mock data not imported
- **P04 Design system and application shell:** Components documented and used by the shell; no light-mode styles; build and lint pass; existing auth pages untouched
- **P05 Role-based dashboards and navigation:** Each role sees only its navigation; backend policies tested; migrations additive
- **P06 Student profile:** IDOR tests pass; verified fields admin-only
- **P07 Attendance:** Calculations match fixtures; all marks, verifications and overrides audited; face verification implemented, tested and consent/fallback-safe behind the provider interface; no claim of production biometric readiness before PD-10 and privacy/legal review
- **P08 Timetable:** No double-booking possible
- **P09 Assignments:** Download authorisation and upload validation tests pass
- **P10 Notices and notifications:** Audience rules enforced in SQL; XSS payloads neutralised
- **P11 Document management:** One ACL function used everywhere; deletion rules documented
- **P12 CampusGPT AI interface:** No cross-user leakage; stop/regenerate work; WebSocket protocol tests pass
- **P13 Intent detection and routing:** Routing accuracy measured; no authorisation bypass
- **P14 RAG ingestion and retrieval:** Unauthorised chunks never returned; retrieval metrics meet agreed threshold
- **P15 Academic analytics:** Every number traceable to records
- **P16 Placement intelligence:** Eligibility deterministic and explained
- **P17 Internships and hackathons:** Eligibility consistent with placements
- **P18 Course recommendations:** Every recommendation explained
- **P19 Visual Learning Workspace:** Invalid AI output never reaches the canvas
- **P20 Faculty dashboard:** No data outside assignments
- **P21 Admin dashboard:** All admin mutations audited
- **P22 Voice features:** Voice and text yield identical authorisation outcomes; no Vapi path reaches the database except through audited FastAPI tools
- **P23 Security and permissions review:** No open critical/high finding
- **P24 Integration and UI parity:** Parity checklist signed; no production component uses prototype mock data
- **P25 Testing and deployment:** Production readiness checklist passed; final acceptance (doc 40)

## E. Production readiness (P25)
- [ ] End-to-end tests for all three roles
- [ ] Security review (P23) with no open critical/high finding
- [ ] Backup and restore rehearsed; migration runbook executed on a copy
- [ ] Production Compose layer validated; HTTPS and proxy-header trust configured (PD-17)
- [ ] Monitoring and alert candidates in place (doc 31)
- [ ] Seed guard verified (seed refuses production)
- [ ] UI parity checklist signed (doc 36)
- [ ] Pending decisions affecting production resolved (PD-15, PD-17, PD-22, PD-24)

## F. Cross-cutting criteria added in the final correction
- [ ] Face recognition attendance with liveness is implemented as required scope (provider pending until PD-10) and never described as optional
- [ ] Vapi voice architecture implemented as documented; no Vapi path reaches the database except through audited FastAPI tools
- [ ] WebSocket is the only real-time transport; protocol implemented and tested; no Redis, no SSE alternative
- [ ] Existing authentication preserved; account-linking and enumeration protections verified
- [ ] All statements about the repository re-verified by the read-only audit (no PO-RV statement remains unverified at acceptance)
- [ ] No mention of prohibited technologies in diagrams or docs except as exclusions
