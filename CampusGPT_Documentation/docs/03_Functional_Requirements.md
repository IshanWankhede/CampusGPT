# 03 — Functional Requirements

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

Requirement IDs are stable and used by the prompts and acceptance criteria. Functional requirements for the existing authentication system are listed first, with their audited status. All other requirements are planned and **NOT IMPLEMENTED**. Detailed per-module documents are docs 13–27, 37.

## Authentication and account foundation (existing)

| ID | Requirement | Status |
|---|---|---|
| FR-AUTH-01 | Register with email, password and college; email OTP verification required | IMPLEMENTED BUT DEFECTIVE (PO-RV) (C2, C3) |
| FR-AUTH-02 | Sign in with email and password | IMPLEMENTED BUT DEFECTIVE (PO-RV) (C1) |
| FR-AUTH-03 | Sign in and sign up with Google; college-domain restriction | IMPLEMENTED BUT DEFECTIVE (PO-RV) (H1) |
| FR-AUTH-04 | Forgot and reset password through OTP | IMPLEMENTED (PO-RV) |
| FR-AUTH-05 | Short-lived access token and refresh | PARTIALLY IMPLEMENTED (PO-RV) (no rotation, no revocation; frontend never refreshes) |
| FR-AUTH-06 | Public registration creates students only; faculty requires admin approval | NOT IMPLEMENTED (WP2) |
| FR-AUTH-07 | Rate limiting on login/OTP/reset | NOT IMPLEMENTED (WP5) |
| FR-AUTH-08 | Audit trail of authentication and admin events | NOT IMPLEMENTED (WP11) |
| FR-AUTH-09 | Multi-college domain validation (COEP, PICT, VIT) | IMPLEMENTED (PO-RV) (isolation design PENDING, PD-07) |

## Planned modules

### Student Dashboard and Profile (P05–P06)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-STU-01 | Dashboard cards: welcome, profile summary, overall and subject-wise attendance, today's timetable and upcoming classes, pending assignments, upcoming exams, recent notices, notifications, SGPA/CGPA, learning progress, placement readiness, recommended courses, recent activity, reminders. | P05–P06 | NOT IMPLEMENTED |
| FR-STU-02 | Empty states for every card when no records exist (production starts empty). | P05–P06 | NOT IMPLEMENTED |
| FR-STU-03 | Profile shows a verified badge on institutional fields; student edits are limited to the editable set. | P05–P06 | NOT IMPLEMENTED |
| FR-STU-04 | Year-specific behaviour: final-year students see the full placement workspace; earlier years see readiness features. | P05–P06 | NOT IMPLEMENTED |
| FR-STU-05 | Verified fields are writable only by ADMIN (and by import). | P05–P06 | NOT IMPLEMENTED |
| FR-STU-06 | A student sees only their own record; the student id is taken from the token, never from a client-supplied id for self-service routes. | P05–P06 | NOT IMPLEMENTED |
| FR-STU-07 | SGPA/CGPA are computed from stored marks and credits; no fabricated values. | P05–P06 | NOT IMPLEMENTED |

### Attendance Management (P07)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-ATT-01 | A session is created by the assigned faculty from a **timetable entry** (class, subject, slot) and closed manually or by timeout. | P07 | NOT IMPLEMENTED |
| FR-ATT-02 | Students verify their presence through **face recognition plus liveness verification** during an open session; the outcome (PRESENT/LATE/REJECTED/NEEDS_REVIEW) and evidence summary are stored on a verification event linked to the attendance record. Face verification is a planned core product requirement, not an optional extra (see doc 14). | P07 | NOT IMPLEMENTED |
| FR-ATT-03 | **Duplicate attendance prevention:** one record per (session, student), enforced by a database unique constraint and by server-side checks (including repeated or concurrent attempts). | P07 | NOT IMPLEMENTED |
| FR-ATT-04 | **Geofence** (campus boundary) is recorded as supporting evidence; GPS is never treated as definitive proof of physical presence. | P07 | NOT IMPLEMENTED |
| FR-ATT-05 | **Real-time status:** the faculty roster updates live over the WebSocket channel (see `docs/architecture/WebSocket_Protocol.md`); the student sees their own verification result immediately. | P07 | NOT IMPLEMENTED |
| FR-ATT-06 | **Manual fallback and override:** when verification fails, is unavailable, the student has not consented, or a device lacks a camera, faculty can mark attendance manually; every override stores reason, actor, time and the previous value. | P07 | NOT IMPLEMENTED |
| FR-ATT-07 | Statuses PRESENT, ABSENT, LATE; attendance percentage = present-equivalent ÷ conducted sessions per subject; overall = across subjects (late weighting configurable). | P07 | NOT IMPLEMENTED |
| FR-ATT-08 | **Shortage calculation:** for threshold T (default 75%), present p, conducted c: classes the student can still miss = floor(p/T − c) when positive; classes needed to recover = ceil((T·c − p)/(1 − T)) when below threshold; the UI shows the formula inputs. | P07 | NOT IMPLEMENTED |
| FR-ATT-09 | Notifications when a subject falls below threshold (P10). | P07 | NOT IMPLEMENTED |
| FR-ATT-10 | Student attendance history, calendar view and subject-wise breakdown. | P07 | NOT IMPLEMENTED |
| FR-ATT-11 | Every session, verification event, override and policy change is written to the attendance audit log. | P07 | NOT IMPLEMENTED |
| FR-ATT-12 | Default threshold 75%, configurable per policy. | P07 | NOT IMPLEMENTED |
| FR-ATT-13 | Faculty can only open sessions for entries assigned to them. | P07 | NOT IMPLEMENTED |
| FR-ATT-14 | Corrections and overrides after the fact require a reason and create an audit record; the original value is retained. | P07 | NOT IMPLEMENTED |
| FR-ATT-15 | Blink detection is one liveness signal, never the complete liveness solution; liveness must also address photo and replay spoofing (doc 14). | P07 | NOT IMPLEMENTED |
| FR-ATT-16 | Biometric processing requires explicit informed consent; students without consent use the manual fallback without penalty. | P07 | NOT IMPLEMENTED |
| FR-ATT-17 | Faculty see verification outcomes and scores summaries, **not** raw images or templates. | P07 | NOT IMPLEMENTED |
| FR-ATT-18 | The face-recognition provider is an unresolved decision (PD-10); implementation is provider-agnostic behind an interface. No production enablement of biometrics before PD-10 and the privacy/legal review are completed. | P07 | NOT IMPLEMENTED |

### Face Recognition and Liveness (P07 (slice B))

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-FACE-01 | Consent first: no biometric processing without explicit, informed, versioned consent that can be withdrawn. | P07 (slice B) | NOT IMPLEMENTED |
| FR-FACE-02 | Enrolment captures several samples, produces an encrypted template and discards raw images after processing. | P07 (slice B) | NOT IMPLEMENTED |
| FR-FACE-03 | Verification compares a live capture with the enrolled template and runs liveness checks; the result feeds the attendance record. | P07 (slice B) | NOT IMPLEMENTED |
| FR-FACE-04 | Liveness combines multiple signals (active challenge-response, passive presentation-attack detection, blink as one signal); the threat model states which attacks are and are not covered. | P07 (slice B) | NOT IMPLEMENTED |
| FR-FACE-05 | Geofence and device signals are supporting evidence only. | P07 (slice B) | NOT IMPLEMENTED |
| FR-FACE-06 | Failure, low confidence, missing consent or provider outage routes to the manual fallback. | P07 (slice B) | NOT IMPLEMENTED |
| FR-FACE-07 | Blink detection alone is not sufficient liveness protection. | P07 (slice B) | NOT IMPLEMENTED |
| FR-FACE-08 | GPS is not definitive proof of physical presence. | P07 (slice B) | NOT IMPLEMENTED |
| FR-FACE-09 | Never describe simulated verification as real secure biometric verification. | P07 (slice B) | NOT IMPLEMENTED |
| FR-FACE-10 | No provider is selected: the provider decision (PD-10) is pending and nothing here claims one. | P07 (slice B) | NOT IMPLEMENTED |
| FR-FACE-11 | Faculty override is always available and always audited. | P07 (slice B) | NOT IMPLEMENTED |

### Timetable Management (P08)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-TT-01 | Entries have day, start/end, subject, class/section, faculty, room. | P08 | NOT IMPLEMENTED |
| FR-TT-02 | Conflict detection: same faculty, room or class in overlapping slots is rejected. | P08 | NOT IMPLEMENTED |
| FR-TT-03 | Cancellations and changes create `timetable_changes` and notify affected students. | P08 | NOT IMPLEMENTED |
| FR-TT-04 | Google Calendar integration is deferred (PD-20). | P08 | NOT IMPLEMENTED |
| FR-TT-05 | Only admins edit the master timetable; faculty changes are requests or limited cancellations within policy. | P08 | NOT IMPLEMENTED |
| FR-TT-06 | Times are stored in the institution's timezone with explicit zone handling. | P08 | NOT IMPLEMENTED |

### Assignment Management (P09)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-ASG-01 | Statuses: not submitted, submitted, late, evaluated, returned. | P09 | NOT IMPLEMENTED |
| FR-ASG-02 | Resubmission keeps history; the latest valid submission is evaluated. | P09 | NOT IMPLEMENTED |
| FR-ASG-03 | Deadlines use server time; late policy configurable (accept-late with flag vs block). | P09 | NOT IMPLEMENTED |
| FR-ASG-04 | Evaluation records rubric scores, total and feedback. | P09 | NOT IMPLEMENTED |
| FR-ASG-05 | Only assigned faculty may create or evaluate for a class. | P09 | NOT IMPLEMENTED |
| FR-ASG-06 | Students can submit only to assignments of classes they are enrolled in. | P09 | NOT IMPLEMENTED |
| FR-ASG-07 | Marks visible to the student only after the faculty publishes them. | P09 | NOT IMPLEMENTED |

### Notices and Notifications (P10)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-NOT-01 | Audience targeting by institution, department, branch, year, class, role. | P10 | NOT IMPLEMENTED |
| FR-NOT-02 | Scheduled publish and expiry; expired notices archive automatically. | P10 | NOT IMPLEMENTED |
| FR-NOT-03 | Read receipts and optional acknowledgements. | P10 | NOT IMPLEMENTED |
| FR-NOT-04 | Notifications are generated by events (new notice, assignment due, attendance shortage, role decision) and shown in-app. | P10 | NOT IMPLEMENTED |
| FR-NOT-05 | Users only receive notices their audience rules match. | P10 | NOT IMPLEMENTED |
| FR-NOT-06 | Rich text is sanitised on the server before storage and again on render. | P10 | NOT IMPLEMENTED |

### Document Management (P11)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-DOC-01 | Upload → validate → store → register metadata → queue processing (extract/index, P14). | P11 | NOT IMPLEMENTED |
| FR-DOC-02 | Processing status shown per document (pending, processing, indexed, failed with reason). | P11 | NOT IMPLEMENTED |
| FR-DOC-03 | Version management: a new version supersedes the previous for retrieval; older versions kept per retention rule. | P11 | NOT IMPLEMENTED |
| FR-DOC-04 | Deletion propagates to chunks and embeddings. | P11 | NOT IMPLEMENTED |
| FR-DOC-05 | Personal uploads are visible only to the owner (and not to faculty unless shared). | P11 | NOT IMPLEMENTED |
| FR-DOC-06 | Institutional documents follow audience rules (department/subject/role). | P11 | NOT IMPLEMENTED |
| FR-DOC-07 | Retention and deletion rules are explicit and logged. | P11 | NOT IMPLEMENTED |

### CampusGPT AI Assistant (P12)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-AI-01 | Conversation sidebar (new, recent, search, rename, delete), message input, attachments, streaming responses, stop generation, regenerate, copy, feedback, suggested questions, citations and document references. | P12 | NOT IMPLEMENTED |
| FR-AI-02 | Real-time transport is **WebSocket** (`/api/v1/ws/chat`): authenticated on connect, typed JSON events for generation status, token deltas, sources, errors and stop; reconnection with backoff (`docs/architecture/WebSocket_Protocol.md`). | P12 | NOT IMPLEMENTED |
| FR-AI-03 | Per request: authenticate → classify intent → call permitted tools / retrieve documents with the caller's permissions → assemble context → generate → attach sources. | P12 | NOT IMPLEMENTED |
| FR-AI-04 | When no authorised source supports an answer, the assistant says so and does not guess. | P12 | NOT IMPLEMENTED |
| FR-AI-05 | Voice interaction is provided through Vapi (doc 37) and always passes through the same backend tools. | P12 | NOT IMPLEMENTED |
| FR-AI-06 | The model never receives data the caller may not see. | P12 | NOT IMPLEMENTED |
| FR-AI-07 | The model never generates SQL; data is fetched by fixed, parameterised, permission-checked tools. | P12 | NOT IMPLEMENTED |
| FR-AI-08 | User text and document text are untrusted and cannot change system rules (prompt-injection defence). | P12 | NOT IMPLEMENTED |
| FR-AI-09 | Conversation history belongs to the user; admins cannot read it without an explicit audited process. | P12 | NOT IMPLEMENTED |
| FR-AI-10 | The LLM and embedding providers are configurable and still pending (PD-11); nothing here names a chosen provider. | P12 | NOT IMPLEMENTED |

### Intent Detection and Routing (P13)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-INT-01 | Routes: STRUCTURED (database tools), DOCUMENT_RAG, MULTI_SOURCE, GENERAL, CLARIFY, REFUSE. | P13 | NOT IMPLEMENTED |
| FR-INT-02 | A classifier (rules first, model-assisted second) returns intent, entities (subject, date range) and a confidence. | P13 | NOT IMPLEMENTED |
| FR-INT-03 | Below the confidence threshold the system asks a clarifying question; ambiguous or unsupported requests fall back to GENERAL with a disclaimer or REFUSE. | P13 | NOT IMPLEMENTED |
| FR-INT-04 | Examples: 'What is my attendance?' → STRUCTURED; 'Explain Unit 2 from my notes' → DOCUMENT_RAG; 'Compare my marks with concepts in my notes' → MULTI_SOURCE; 'Explain binary search' → GENERAL. | P13 | NOT IMPLEMENTED |
| FR-INT-05 | Authorisation is checked inside each tool, after routing; routing cannot grant access. | P13 | NOT IMPLEMENTED |
| FR-INT-06 | Tools are an explicit allow-list with typed parameters; no free-form SQL. | P13 | NOT IMPLEMENTED |
| FR-INT-07 | The route and tools used are logged without message content for evaluation. | P13 | NOT IMPLEMENTED |

### RAG Architecture (P14)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-RAG-01 | Chunks carry document, version, subject, unit/topic, page/section, audience metadata. | P14 | NOT IMPLEMENTED |
| FR-RAG-02 | Hybrid retrieval: vector similarity plus PostgreSQL full-text search, merged; reranking only if evaluation shows benefit. | P14 | NOT IMPLEMENTED |
| FR-RAG-03 | Permission filtering is part of the SQL (join against the same ACL used by document download). | P14 | NOT IMPLEMENTED |
| FR-RAG-04 | Context assembly respects a token budget and preserves source ids for citations. | P14 | NOT IMPLEMENTED |
| FR-RAG-05 | Grounded generation instructions: answer only from context, cite, say 'not found' otherwise. | P14 | NOT IMPLEMENTED |
| FR-RAG-06 | No ChromaDB, no Redis, no separate vector database. | P14 | NOT IMPLEMENTED |
| FR-RAG-07 | Re-index on new version; delete chunks when a document or version is deleted. | P14 | NOT IMPLEMENTED |
| FR-RAG-08 | Evaluation set maintained: retrieval hit-rate and groundedness checks. | P14 | NOT IMPLEMENTED |

### Document Ingestion and Retrieval Pipeline (P14)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-ING-01 | Stages: upload → validate → store → parse → OCR if needed → normalise → sections → tables → semantic chunking → metadata → embed → store vectors → ready. | P14 | NOT IMPLEMENTED |
| FR-ING-02 | Jobs are rows in `document_processing_jobs`, claimed with `SELECT … FOR UPDATE SKIP LOCKED` by a worker process in the same codebase (no Redis, no external queue). | P14 | NOT IMPLEMENTED |
| FR-ING-03 | Retries with backoff and a maximum; permanent failures surfaced with a reason. | P14 | NOT IMPLEMENTED |
| FR-ING-04 | Retrieval: embed query → permission-filtered hybrid search → (optional rerank) → context assembly → generation → citations. | P14 | NOT IMPLEMENTED |
| FR-ING-05 | Each stage is idempotent and re-runnable. | P14 | NOT IMPLEMENTED |
| FR-ING-06 | Parsing runs with CPU/memory/time limits. | P14 | NOT IMPLEMENTED |
| FR-ING-07 | Ingestion never makes a document visible beyond its ACL. | P14 | NOT IMPLEMENTED |

### Academic Analytics (P15)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-ANA-01 | Trends over time, subject comparisons, assignment score distributions, attendance vs performance views. | P15 | NOT IMPLEMENTED |
| FR-ANA-02 | Risk indicators from transparent rules (for example attendance below threshold plus falling marks) with the rule shown. | P15 | NOT IMPLEMENTED |
| FR-ANA-03 | Predictions are shown only when sufficient data exists and are labelled as estimates with the method; otherwise 'insufficient data'. | P15 | NOT IMPLEMENTED |
| FR-ANA-04 | No fabricated or unsupported predictions. | P15 | NOT IMPLEMENTED |
| FR-ANA-05 | Aggregates for small groups suppress identifying detail (minimum group size configurable). | P15 | NOT IMPLEMENTED |

### Placement Intelligence (P16)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-PLC-01 | Eligibility rules: CGPA, backlogs, branch, year, skills; the result lists each rule as met/unmet with the student's value. | P16 | NOT IMPLEMENTED |
| FR-PLC-02 | Application pipeline with rounds and outcomes; offers recorded. | P16 | NOT IMPLEMENTED |
| FR-PLC-03 | Readiness score from transparent inputs (skills vs target role, courses done). | P16 | NOT IMPLEMENTED |
| FR-PLC-04 | Explanations must name the failing rule. | P16 | NOT IMPLEMENTED |
| FR-PLC-05 | Statistics aggregate only; no individual disclosure to other students. | P16 | NOT IMPLEMENTED |

### Internships and Hackathons (P17)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-INTN-01 | Opportunity types INTERNSHIP and HACKATHON share one table with a type field. | P17 | NOT IMPLEMENTED |
| FR-INTN-02 | Eligibility reuses the placement rules engine. | P17 | NOT IMPLEMENTED |
| FR-INTN-03 | Deadline reminders via notifications. | P17 | NOT IMPLEMENTED |
| FR-INTN-04 | External links are validated and opened with `rel=noopener`. | P17 | NOT IMPLEMENTED |
| FR-INTN-05 | Expired opportunities are archived automatically. | P17 | NOT IMPLEMENTED |

### Course Recommendation System (P18)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-CRS-01 | Inputs: weak subjects (analytics), declared interests, skill gaps for target roles, prerequisites and difficulty. | P18 | NOT IMPLEMENTED |
| FR-CRS-02 | Output: ranked list with a plain-language reason for each. | P18 | NOT IMPLEMENTED |
| FR-CRS-03 | Feedback (not relevant / done) adjusts future ranking. | P18 | NOT IMPLEMENTED |
| FR-CRS-04 | Recommendations are explainable; no opaque scores shown as facts. | P18 | NOT IMPLEMENTED |
| FR-CRS-05 | Only the student's own data is used for their recommendations. | P18 | NOT IMPLEMENTED |

### Visual Learning Workspace (P19)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-VIS-01 | Board data is a versioned JSON scene (elements, groups, connectors). | P19 | NOT IMPLEMENTED |
| FR-VIS-02 | AI generation returns a diagram object that is validated against a schema before it is converted to scene elements; invalid output is rejected, never rendered raw. | P19 | NOT IMPLEMENTED |
| FR-VIS-03 | Export client-side where possible. | P19 | NOT IMPLEMENTED |
| FR-VIS-04 | Build on a maintained canvas approach decided by ADR in P19 (reuse vs custom); do not claim Excalidraw compatibility without testing. | P19 | NOT IMPLEMENTED |
| FR-VIS-05 | AI-generated content is clearly marked and editable. | P19 | NOT IMPLEMENTED |

### Voice Interaction (Vapi) (P22)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-VOI-01 | Session start: the frontend asks the backend for a short-lived voice session; the backend binds it to the authenticated user and returns only what the Vapi Web SDK needs; the browser requests microphone permission; the call starts. | P22 | NOT IMPLEMENTED |
| FR-VOI-02 | During the call Vapi performs speech input, transcription, response generation and text-to-speech; the user can interrupt the assistant; transcripts are shown on screen. | P22 | NOT IMPLEMENTED |
| FR-VOI-03 | When the agent needs campus data it invokes **Vapi custom Function Tools**, which call secured FastAPI endpoints; the backend authenticates the call, resolves the user from the voice session (never from model-supplied arguments), applies the same policies as text chat, and returns only permitted data. | P22 | NOT IMPLEMENTED |
| FR-VOI-04 | End of call: explicit stop, timeout or error ends the session and invalidates the voice session; failures fall back to text chat. | P22 | NOT IMPLEMENTED |
| FR-VOI-05 | Usage, latency and error metrics are logged without storing audio or transcripts by default. | P22 | NOT IMPLEMENTED |
| FR-VOI-06 | Vapi never gets database access and never receives unrestricted data; tools return the minimum needed to answer. | P22 | NOT IMPLEMENTED |
| FR-VOI-07 | The identity of the end user is derived server-side from the voice session; the model cannot choose a user id. | P22 | NOT IMPLEMENTED |
| FR-VOI-08 | Tool endpoints reject requests that fail Vapi server authentication or that reference an expired, ended or mismatched voice session. | P22 | NOT IMPLEMENTED |
| FR-VOI-09 | Credentials, pricing, exact assistant configuration and final privacy approval are deployment decisions (PD-19) and are not asserted here. | P22 | NOT IMPLEMENTED |

### Faculty Dashboard (P20)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-FAC-01 | Landing view: today's classes, open sessions, pending evaluations, recent submissions, notices composer shortcut. | P20 | NOT IMPLEMENTED |
| FR-FAC-02 | Class view: roster (limited fields), attendance summary, assignment status, performance. | P20 | NOT IMPLEMENTED |
| FR-FAC-03 | Access is derived from `faculty_assignments`; no assignment, no data. | P20 | NOT IMPLEMENTED |

### Admin Dashboard (P21)

| ID | Requirement | Phase | Status |
|---|---|---|---|
| FR-ADM-01 | Role-request approval queue (replaces the interim Swagger/CLI path). | P21 | NOT IMPLEMENTED |
| FR-ADM-02 | Audit log viewer (read-only). | P21 | NOT IMPLEMENTED |
| FR-ADM-03 | CSV import for institutional records (PD-13) with dry-run preview. | P21 | NOT IMPLEMENTED |
| FR-ADM-04 | System analytics: users, usage, indexing health. | P21 | NOT IMPLEMENTED |
| FR-ADM-05 | Every admin action is audited. | P21 | NOT IMPLEMENTED |
| FR-ADM-06 | No admin function can create another ADMIN except through the controlled process documented in WP2. | P21 | NOT IMPLEMENTED |
