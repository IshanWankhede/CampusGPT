# PENDING_DECISIONS

Detail for every open decision. The one-page register is `DECISION_REGISTER.md`; approved decisions are in `PROJECT_DECISIONS.md`. PD-01 to PD-06 are the foundational decisions that need your explicit review. **Nothing is marked approved without evidence.** Defaults are temporary and provisional until you confirm them.

### PD-01 — Interim faculty-approval path

- **Status:** PENDING — explicit owner review required (provisional default)
- **Question:** Faculty approval until the admin dashboard exists: Swagger + CLI only, or a temporary admin UI?
- **Why it matters:** Faculty cannot receive privileges until someone approves.
- **Options:** (a) Swagger + CLI; (b) temporary minimal admin page
- **Existing documented default (provisional/temporary):** (a) Swagger + CLI
- **Recommended direction:** (a)
- **Dependencies:** WP2
- **Implementation that is blocked:** WP2 sign-off (not WP2 start)
- **What must happen before approval:** Owner states choice in `DECISION_REGISTER.md`
- **Risks:** (b) adds UI work before the app shell exists
- **Can unrelated work proceed?** Yes (WP2 builds endpoints and CLI either way)

### PD-02 — Staff and student email domains

- **Status:** PENDING — explicit owner review required (provisional default)
- **Question:** Do faculty and students share the same college email domain (e.g. `vit.edu`)?
- **Why it matters:** If shared, the domain cannot distinguish staff from students; approval is the only gate.
- **Options:** (a) shared; (b) separate staff domains; (c) staff allow-list
- **Existing documented default (provisional/temporary):** (a) assume shared
- **Recommended direction:** (a), approval only
- **Dependencies:** WP2
- **Implementation that is blocked:** WP2 policy details
- **What must happen before approval:** Owner confirms real domain structure
- **Risks:** Wrong assumption blocks real staff or weakens review
- **Can unrelated work proceed?** Yes

### PD-03 — Access-token lifetime

- **Status:** PENDING — explicit owner review required (provisional default)
- **Question:** Approve a 15-minute access token (the previously observed code used 30)?
- **Why it matters:** Shorter lifetime limits stolen-token damage but raises refresh traffic.
- **Options:** 15 / 30 minutes
- **Existing documented default (provisional/temporary):** 15
- **Recommended direction:** 15
- **Dependencies:** WP6, WP7
- **Implementation that is blocked:** WP6 configuration default
- **What must happen before approval:** Owner approves; WP7 ships with WP6
- **Risks:** Needs the refresh helper to avoid surprise logouts
- **Can unrelated work proceed?** Yes, but ship WP7 together with WP6

### PD-04 — Interim token storage

- **Status:** PENDING — explicit owner review required (provisional default)
- **Question:** Is `localStorage` acceptable as the interim token store?
- **Why it matters:** XSS can read `localStorage`; cookies need CSRF design.
- **Options:** (a) `localStorage` now; (b) HttpOnly cookies now
- **Existing documented default (provisional/temporary):** (a) now, re-evaluate at P23
- **Recommended direction:** (a) now, cookies evaluated under PD-23
- **Dependencies:** WP6, WP7
- **Implementation that is blocked:** none for Stage 0 (documented limitation)
- **What must happen before approval:** Owner accepts the documented risk
- **Risks:** Higher XSS exposure until PD-23
- **Can unrelated work proceed?** Yes

### PD-05 — Test database name

- **Status:** PENDING — explicit owner review required (provisional default)
- **Question:** Use `campusgpt_test` inside the existing PostgreSQL instance?
- **Why it matters:** Isolation and CI simplicity.
- **Options:** (a) same instance; (b) separate container
- **Existing documented default (provisional/temporary):** (a)
- **Recommended direction:** (a)
- **Dependencies:** WP0
- **Implementation that is blocked:** WP0 harness
- **What must happen before approval:** Owner confirms; guard requires the name to end in `_test`
- **Risks:** Misconfiguration could reach dev data (mitigated by the guard)
- **Can unrelated work proceed?** Yes

### PD-06 — Review of existing elevated accounts

- **Status:** PENDING — explicit owner review required (provisional default)
- **Question:** How are existing FACULTY/ADMIN accounts reviewed?
- **Why it matters:** Some may have been self-registered through the previously observed role-assignment weakness (re-verify).
- **Options:** (a) owner reviews the WP0 list one by one; (b) keep admins, review faculty
- **Existing documented default (provisional/temporary):** (a); never auto-demote
- **Recommended direction:** (a)
- **Dependencies:** WP0 list
- **Implementation that is blocked:** WP2 sign-off
- **What must happen before approval:** Owner reviews the masked list from WP0
- **Risks:** Missed review leaves illegitimate privileges
- **Can unrelated work proceed?** Yes, review happens in WP0/WP2

### PD-07 — Multi-college data isolation

- **Status:** PENDING
- **Question:** Single institution with a `college` attribute, or true multi-tenant isolation?
- **Why it matters:** Every academic table either carries an institution key or does not; retrofitting is costly. Multi-college login exists in the previously observed code.
- **Options:** (a) attribute only; (b) `institution_id` on academic tables; (c) drop multi-college
- **Existing documented default (provisional/temporary):** None adopted; design tables so an institution key can be added additively
- **Recommended direction:** Evaluate (b) with P02 findings
- **Dependencies:** P02 audit
- **Implementation that is blocked:** **P05 and every later academic table** — must be resolved before P05
- **What must happen before approval:** Owner reviews the P02 impact report and chooses
- **Risks:** Wrong choice can leak or strand data across institutions
- **Can unrelated work proceed?** Stage 0 and P03–P04 yes; P05 onward no

### PD-08 — Backend linter for CI

- **Status:** PENDING
- **Question:** Which backend linter should CI use (none is known to exist)?
- **Why it matters:** The master instructions require backend linting in CI.
- **Options:** Ruff / flake8 / none
- **Existing documented default (provisional/temporary):** Ruff (single fast tool)
- **Recommended direction:** Ruff
- **Dependencies:** WP10
- **Implementation that is blocked:** WP10 lint step only
- **What must happen before approval:** Owner approves one dev-only tool
- **Risks:** Adds a dev dependency
- **Can unrelated work proceed?** Yes (lint step can follow later)

### PD-09 — Document formats and delivery order

- **Status:** PENDING
- **Question:** All four formats (PDF, DOCX, PPTX, XLSX) are required; in what order are parsers delivered?
- **Why it matters:** The product requires four formats; parsing complexity differs.
- **Options:** (a) PDF+DOCX first, PPTX/XLSX next; (b) all four together
- **Existing documented default (provisional/temporary):** (a)
- **Recommended direction:** (a)
- **Dependencies:** P11, P14
- **Implementation that is blocked:** P14 parser slices (not P11 upload/storage)
- **What must happen before approval:** Owner approves order
- **Risks:** Delay for slide/sheet notes
- **Can unrelated work proceed?** Yes

### PD-10 — Face-recognition provider and biometric policies

- **Status:** PENDING
- **Question:** Which face-recognition/liveness approach and provider, and what consent, retention and template-handling policy? (Face recognition itself is a **required** feature.)
- **Why it matters:** Biometric data is highly sensitive; no provider is approved and none is assumed.
- **Options:** Self-hosted library / managed API / on-device, each behind `BiometricProvider`
- **Existing documented default (provisional/temporary):** None adopted; build provider-agnostic with a clearly-labelled mock provider in development
- **Recommended direction:** Shortlist after a privacy-impact assessment
- **Dependencies:** Privacy/legal review; P07 slice A
- **Implementation that is blocked:** **Production enablement of P07 slice B** (slice A and the provider-agnostic code are not blocked)
- **What must happen before approval:** Provider chosen; retention/consent policy approved; privacy and legal review recorded
- **Risks:** Legal/privacy exposure; spoofing risk
- **Can unrelated work proceed?** Yes for slice A and for provider-agnostic slice B development

### PD-11 — LLM and embedding providers, vector dimension

- **Status:** PENDING
- **Question:** Which LLM provider/model and embedding model, and what vector dimension?
- **Why it matters:** The dimension fixes the `document_chunks.embedding` column; providers affect cost and privacy.
- **Options:** Hosted API / self-hosted models; per provider
- **Existing documented default (provisional/temporary):** None adopted (configurable provider adapter)
- **Recommended direction:** Decide at the start of P12 (LLM) and P14 (embeddings)
- **Dependencies:** P11 outputs
- **Implementation that is blocked:** P12 provider adapter go-live; **P14 vector column creation**
- **What must happen before approval:** Owner chooses providers; dimension recorded in an ADR
- **Risks:** Re-embedding cost if changed later
- **Can unrelated work proceed?** Yes until P12–P14

### PD-12 — Document and upload storage provider

- **Status:** PENDING
- **Question:** Docker volume, S3-compatible object store, or other?
- **Why it matters:** Needed by assignments and documents.
- **Options:** Volume / object store
- **Existing documented default (provisional/temporary):** Docker volume behind a storage interface for development
- **Recommended direction:** Storage interface now, provider later
- **Dependencies:** WP8
- **Implementation that is blocked:** P09, P11
- **What must happen before approval:** Owner chooses production storage
- **Risks:** Migration to object storage later
- **Can unrelated work proceed?** Yes until P09/P11

### PD-13 — Institutional data import

- **Status:** PENDING
- **Question:** How are real records loaded and linked to users (roll number, PRN)?
- **Why it matters:** `users` lacks academic identity fields in the previously observed schema.
- **Options:** Admin entry / CSV import / institutional integration
- **Existing documented default (provisional/temporary):** Admin CSV import with dry-run
- **Recommended direction:** CSV import
- **Dependencies:** P05 structure
- **Implementation that is blocked:** P06 (and P21 import wizard)
- **What must happen before approval:** Owner provides the data source and format
- **Risks:** Account-to-student mismatches
- **Can unrelated work proceed?** Yes until P06

### PD-14 — Designation and permission model

- **Status:** PENDING
- **Question:** How are HOD, Dean and Coordinator modelled?
- **Why it matters:** They must be configurable without new primary roles.
- **Options:** Designation → permission-set mapping with scopes
- **Existing documented default (provisional/temporary):** Roles stay ADMIN/FACULTY/STUDENT; designations add scoped permissions
- **Recommended direction:** Designation rows with scope (department/institution/function)
- **Dependencies:** P02 audit
- **Implementation that is blocked:** **P05 and P10 notice targeting** — must be resolved before P05
- **What must happen before approval:** Owner approves the permission sets
- **Risks:** Over-complex permissions
- **Can unrelated work proceed?** Stage 0 and P03–P04 yes; P05 onward no

### PD-15 — Actual institutional email domains

- **Status:** PENDING
- **Question:** What are the real, current domains for each college?
- **Why it matters:** The previously observed code and an old README disagreed on one domain; a wrong domain locks out users.
- **Options:** Confirm per institution
- **Existing documented default (provisional/temporary):** Use the documented mapping in development only
- **Recommended direction:** Confirm before production
- **Dependencies:** —
- **Implementation that is blocked:** Production go-live (WP2/WP3 can proceed in development)
- **What must happen before approval:** Owner supplies verified domains
- **Risks:** Lockout
- **Can unrelated work proceed?** Yes in development

### PD-16 — UI palette / design-system alignment

- **Status:** PENDING
- **Question:** How does the monochrome existing auth/landing look relate to the new violet/indigo/teal application palette?
- **Why it matters:** Visual coherence at the sign-in → app boundary.
- **Options:** (a) keep auth as-is, new app uses the new palette; (b) restyle auth later
- **Existing documented default (provisional/temporary):** (a)
- **Recommended direction:** (a)
- **Dependencies:** P03 reference images
- **Implementation that is blocked:** P04 final token values
- **What must happen before approval:** Owner reviews the five reference images and the token proposal
- **Risks:** Slight visual seam
- **Can unrelated work proceed?** Yes (P04 uses provisional tokens)

### PD-17 — Hosting and deployment target

- **Status:** PENDING
- **Question:** Where and how is production hosted, and how is HTTPS terminated?
- **Why it matters:** Affects proxy-header trust, cookie flags, WebSocket proxying and CORS.
- **Options:** VPS + Nginx + certificates / managed platform
- **Existing documented default (provisional/temporary):** Generic Nginx + HTTPS documentation
- **Recommended direction:** Decide before WP8 production layer is finalised
- **Dependencies:** —
- **Implementation that is blocked:** WP8 production layer finalisation, P25
- **What must happen before approval:** Owner states target and domain
- **Risks:** Insecure defaults if unspecified
- **Can unrelated work proceed?** Yes until WP8/P25

### PD-18 — Real-time communication — WebSocket

- **Status:** DIRECTION CONFIRMED BY OWNER — parameters pending
- **Question:** WebSocket is the confirmed transport for CampusGPT chat; which protocol parameters are approved (auth handshake, limits, reconnection policy)?
- **Why it matters:** Earlier text treated SSE as an alternative; the owner has confirmed WebSocket. Parameters still need approval.
- **Options:** Auth by first message vs one-time ticket; limits; heartbeat
- **Existing documented default (provisional/temporary):** WebSocket; first-message auth with the access token (no token in the URL); limits as in `docs/architecture/WebSocket_Protocol.md`
- **Recommended direction:** As documented
- **Dependencies:** —
- **Implementation that is blocked:** P12 protocol sign-off (not P12 start)
- **What must happen before approval:** Owner reviews `docs/architecture/WebSocket_Protocol.md`
- **Risks:** Mismatch between docs and code if not reviewed
- **Can unrelated work proceed?** Yes

### PD-19 — Voice — Vapi

- **Status:** DIRECTION CONFIRMED BY OWNER — parameters pending
- **Question:** Vapi is the confirmed voice integration; which deployment details are approved (credentials, pricing/plan, exact assistant configuration, server-authentication method, data retention, privacy review)?
- **Why it matters:** The owner requires Vapi; operational and privacy details are provider- and deployment-specific.
- **Options:** Vapi server-authentication variants; Vapi-hosted vs custom LLM; recording off/on
- **Existing documented default (provisional/temporary):** Vapi with recording disabled by default and secured FastAPI tools
- **Recommended direction:** As documented in doc 37
- **Dependencies:** P12–P14 tools
- **Implementation that is blocked:** **P22 production enablement** (design and development against a test Vapi account are not blocked)
- **What must happen before approval:** Owner approves credentials handling, plan, configuration and privacy review
- **Risks:** Third-party processing of voice data; cost
- **Can unrelated work proceed?** Yes until P22

### PD-20 — Google Calendar integration

- **Status:** PENDING
- **Question:** What scope: none, export, or two-way sync?
- **Why it matters:** Extra OAuth scopes and privacy impact.
- **Options:** Defer / read-only export / two-way sync
- **Existing documented default (provisional/temporary):** Design only; export first
- **Recommended direction:** Export
- **Dependencies:** P08
- **Implementation that is blocked:** P08 calendar-sync slice
- **What must happen before approval:** Owner chooses scope
- **Risks:** Scope creep
- **Can unrelated work proceed?** Yes

### PD-21 — Cleanup of dead routes and files

- **Status:** PENDING
- **Question:** What to do with the apparently unused `/auth/verify-email` route and unused auth/landing files (previously observed)?
- **Why it matters:** Decision D-07 forbids deleting before verification.
- **Options:** Verify then remove / keep
- **Existing documented default (provisional/temporary):** Verify references in a later cleanup task
- **Recommended direction:** Cleanup after verification
- **Dependencies:** P01/WP0 re-verification
- **Implementation that is blocked:** A cleanup task after P24
- **What must happen before approval:** Owner approves a verified list
- **Risks:** —
- **Can unrelated work proceed?** Yes

### PD-22 — Verified Resend sender domain

- **Status:** PENDING
- **Question:** Which domain is verified with Resend for production OTP email?
- **Why it matters:** The default test sender only emails the account owner.
- **Options:** Verify a domain / other provider
- **Existing documented default (provisional/temporary):** Development sender only
- **Recommended direction:** Verify a domain
- **Dependencies:** —
- **Implementation that is blocked:** Production go-live
- **What must happen before approval:** Owner verifies domain
- **Risks:** OTP emails fail for real users
- **Can unrelated work proceed?** Yes in development

### PD-23 — Production token design

- **Status:** PENDING
- **Question:** Final production design: bearer tokens or HttpOnly cookies with CSRF protection?
- **Why it matters:** Security posture beyond the interim PD-04.
- **Options:** As PD-04
- **Existing documented default (provisional/temporary):** Evaluate in P23
- **Recommended direction:** Evaluate cookies + CSRF
- **Dependencies:** PD-04
- **Implementation that is blocked:** P23
- **What must happen before approval:** Security review recommendation
- **Risks:** —
- **Can unrelated work proceed?** Yes

### PD-24 — Admin bootstrap and recovery

- **Status:** PENDING
- **Question:** How is the first production admin created and how is access recovered?
- **Why it matters:** ADMIN accounts must never come from public registration.
- **Options:** CLI in container / one-time secret / controlled seed
- **Existing documented default (provisional/temporary):** CLI with a documented runbook
- **Recommended direction:** CLI runbook
- **Dependencies:** WP2
- **Implementation that is blocked:** P25
- **What must happen before approval:** Owner approves runbook
- **Risks:** Admin lockout
- **Can unrelated work proceed?** Yes

### PD-25 — WebSocket scaling and server push without Redis

- **Status:** PENDING
- **Question:** How do multi-worker deployments deliver live attendance updates and notification pushes without Redis?
- **Why it matters:** WebSocket connections are per process; fan-out across workers needs a decision. Redis is not permitted.
- **Options:** (a) single backend worker initially; (b) PostgreSQL LISTEN/NOTIFY fan-out; (c) polling fallback
- **Existing documented default (provisional/temporary):** (a) with (c) as fallback; evaluate (b)
- **Recommended direction:** Evaluate (b) in P10/P12
- **Dependencies:** PD-17
- **Implementation that is blocked:** Live attendance roster scale-out (P07), notification push (P10), multi-worker chat (P12)
- **What must happen before approval:** Owner approves an approach in an ADR
- **Risks:** Missed live updates under multiple workers
- **Can unrelated work proceed?** Yes (single-worker initial deployment)
