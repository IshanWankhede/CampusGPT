# CampusGPT — Product Requirements Document (PRD)

| | |
|---|---|
| **Status** | Draft — In Development |
| **Current Phase** | Phase 2 (Authentication) — Phase 1 complete |
| **Owner** | Ishan |
| **Related docs** | [`ARCHITECTURE.md`](./ARCHITECTURE.md) · [`DB_SCHEMA.md`](./DB_SCHEMA.md) · [`PHASES.md`](./PHASES.md) · [`REQUIREMENTS.md`](./REQUIREMENTS.md) |

---

## 1. Problem Statement

Colleges run on a patchwork of disconnected tools: attendance registers (paper or spreadsheets), a separate timetable notice board, WhatsApp groups for announcements, email for assignments, and no single place a student or faculty member can ask "what's going on with my academics right now" and get a real answer. Information is scattered, and no one can query it in natural language.

## 2. Vision

CampusGPT is a single platform that unifies core campus operations (attendance, timetable, assignments, notices, documents) **and** layers an AI assistant on top that can answer questions using that data — either by querying the database directly, searching uploaded course material (RAG), or answering general questions — through one conversational interface.

## 3. Goals

- Replace fragmented, manual campus record-keeping with one structured system
- Give students and faculty a natural-language way to get their own information ("what's my attendance in DBMS?") instead of navigating multiple screens
- Make uploaded course material (PDFs, notes, syllabi) instantly searchable and explainable via AI
- Ship as a real, working full-stack system — not a prototype — with production-grade auth, RBAC, and security from day one

## 4. Non-Goals (Out of Scope for v1)

- Payment/fee management
- Hostel/room allocation
- Alumni networking features
- Native mobile apps (web-responsive only for v1)
- Multi-institution / multi-tenant support (single campus per deployment for v1)

Face recognition, voice assistant, and advanced recommendations are explicitly **optional, later-phase** features (Phases 9–10) — not required for a v1 launch.

## 5. Target Users / Personas

| Persona | Needs |
|---|---|
| **Student** | Check attendance, timetable, assignments, notices; ask CampusGPT questions about course material and their own records |
| **Faculty** | Mark attendance, post assignments/notices, upload course documents, view class/student analytics |
| **Admin** | Manage users, departments, subjects, timetables campus-wide; view system-wide analytics |

## 6. Core Features (v1 Scope)

| # | Feature | Priority |
|---|---|---|
| 1 | Authentication & Role-Based Access (Student/Faculty/Admin) | Must-have |
| 2 | User, Department, Subject, Timetable management | Must-have |
| 3 | Attendance tracking (session-based, per subject) | Must-have |
| 4 | Assignments (post, submit, grade) | Must-have |
| 5 | Notices/announcements | Must-have |
| 6 | Document upload & management | Must-have |
| 7 | RAG-based Q&A over uploaded documents | Must-have |
| 8 | AI Chatbot with intent routing (DB query / RAG / general LLM) | Must-have |
| 9 | Role-specific analytics dashboards | Should-have |
| 10 | Notifications | Should-have |
| 11 | Face-recognition attendance | Nice-to-have (optional) |
| 12 | Voice assistant, study planner, recommendations | Nice-to-have (optional) |

## 7. Success Metrics

- All three roles can log in and see only the data/actions permitted by their role (RBAC verified)
- A student can ask CampusGPT "explain unit 3 of [subject]" and receive an answer grounded in an actually-uploaded document, with source reference
- A student can ask CampusGPT "what's my attendance in [subject]" and get a correct, live number from the database — not a hallucinated one
- Core ERP flows (attendance marked → visible to student; assignment posted → submittable → gradable) work end to end without manual DB intervention
- No sensitive data (passwords, raw tokens) ever appears in logs, JWT payloads, or API responses

## 8. Key Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Chatbot hallucinates database facts (e.g. wrong attendance %) | Intent router sends structured questions to real DB queries, never lets the LLM guess (see `ARCHITECTURE.md` §7) |
| RAG returns irrelevant or outdated document chunks | Chunk with overlap, always return source citations, re-index on document update |
| Scope creep before v1 core ERP is stable | Strict phase order — RAG/Chatbot (Phases 6–7) are not started until Core ERP (Phase 3) is complete and tested |
| Auth/RBAC gaps expose data across roles | Every protected endpoint independently verifies role server-side, never trusts frontend UI state |

## 9. Assumptions

- Single-campus deployment for v1
- Faculty/Admin accounts are provisioned by an Admin (no public faculty self-signup)
- Course documents are primarily PDF
- LLM access is via an external API (Claude or equivalent) — no self-hosted model required for v1

## 10. Release Criteria (v1 "Done")

Phases 1–8 from [`PHASES.md`](./PHASES.md) complete and verified, security checklist in `ARCHITECTURE.md` §11 satisfied, and the app runs via `docker compose` for the database with documented setup for backend/frontend. Phases 9–11 (face recognition, advanced AI, production deployment) are post-v1.
