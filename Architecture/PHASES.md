# CampusGPT — Phase Tracker

This is the working checklist for building CampusGPT module by module. Check items off as you complete and verify them — don't start the next phase until the current one's acceptance criteria all pass.

> For *why* things are ordered this way, see [`ARCHITECTURE.md`](./ARCHITECTURE.md) §12 and §14. For the product-level scope, see [`PRD.md`](./PRD.md).

**Legend:** ✅ Done &nbsp;·&nbsp; 🔄 In Progress &nbsp;·&nbsp; ⬜ Not Started

---

## ✅ Phase 1 — Foundation

**Goal:** React ↔ FastAPI ↔ PostgreSQL(+pgvector) all connected, nothing else.

- [x] Git repo created and pushed to GitHub
- [x] `docker-compose.yml` running PostgreSQL + pgvector (port 5433 to avoid conflict with native Postgres)
- [x] `pgvector` extension enabled and verified (`\dx`)
- [x] pgAdmin (or equivalent) connected to the Dockerized database
- [x] Backend: FastAPI app with `/health` endpoint, reads config from `.env`
- [x] Frontend: Vite + React app, calls `/health` and displays the result
- [x] `.gitignore` correctly excludes `venv/`, `node_modules/`, `.env`

**Status: COMPLETE**

---

## 🔄 Phase 2 — Authentication

**Goal:** Register, login, JWT issuing, current-user resolution, role-based access control.

- [ ] `users` table SQLAlchemy model (see `DB_SCHEMA.md` §1)
- [ ] Alembic initialized, first migration creates `users` table
- [ ] `POST /api/v1/auth/register` — hashes password (bcrypt), creates user
- [ ] `POST /api/v1/auth/login` — verifies password, issues access + refresh JWT
- [ ] `POST /api/v1/auth/refresh` — issues new access token from a valid refresh token
- [ ] `POST /api/v1/auth/logout`
- [ ] `GET /api/v1/auth/me` — returns current user from JWT
- [ ] `get_current_user` dependency (reusable across all future modules)
- [ ] Role-check dependency (e.g. `require_role("ADMIN")`) reusable across all future modules
- [ ] Manually tested via Swagger UI (`/docs`) or Postman: register → login → call `/me` with token → confirm role enforcement blocks wrong-role access

**Acceptance criteria:** A user can register, log in, receive a token, and access `/me`; an endpoint protected with `require_role("ADMIN")` correctly rejects a STUDENT-role token.

---

## ⬜ Phase 3 — Core ERP

**Goal:** Build the non-AI campus management backbone, in this exact order.

- [ ] Departments (model, migration, CRUD)
- [ ] Students & Faculty (model, migration, linked 1:1 to `users`)
- [ ] Courses & Subjects (model, migration, CRUD)
- [ ] Timetable (model, migration, CRUD, filtered by student/faculty)
- [ ] Attendance (`attendance_sessions`, `attendance_records`, mark + fetch endpoints)
- [ ] Assignments (post, submit, grade endpoints)
- [ ] Notices (CRUD, role/department targeting)

**Acceptance criteria:** All endpoints in `ARCHITECTURE.md` §8 under Users/Students/Faculty/Attendance/Timetable/Assignments/Notices are implemented and RBAC-protected. A functional campus management system exists, no AI yet.

---

## ⬜ Phase 4 — Dashboards

**Goal:** Real UI, wired to real APIs, for all three roles.

- [ ] Student dashboard (attendance, today's classes, assignments, notices, performance)
- [ ] Faculty dashboard (classes, students, attendance, assignments, notices, documents, analytics placeholder)
- [ ] Admin dashboard (users, students, faculty, departments, subjects, timetables, notices)
- [ ] Auth-aware routing (role guards in `routes/`, redirect unauthenticated users to login)

**Acceptance criteria:** Logging in as each role lands on the correct dashboard showing real data from Phase 3's APIs — no mock/hardcoded data left in the UI.

---

## ⬜ Phase 5 — Documents

**Goal:** Reliable document management, before any AI touches it.

- [ ] `documents` table (model, migration)
- [ ] `POST /api/v1/documents/upload` — validates file type/size server-side, stores file, never trusts client filename
- [ ] Text extraction from PDF (PyMuPDF) on upload
- [ ] `GET /api/v1/documents`, `GET /api/v1/documents/{id}`, `DELETE /api/v1/documents/{id}`
- [ ] Document list UI (faculty/admin can view/manage uploaded documents)

**Acceptance criteria:** A faculty member can upload a PDF, see it listed, and delete it; extracted raw text is stored/logged correctly before moving to chunking.

---

## ⬜ Phase 6 — RAG ⭐

**Goal:** Manually built retrieval pipeline — no LangChain yet.

- [ ] `document_chunks` table with `VECTOR(384)` column (or matching your embedding model's dimension)
- [ ] Chunking function (~500 tokens, with overlap)
- [ ] Embedding generation (Sentence Transformers) on chunk creation
- [ ] Store chunks + embeddings in `document_chunks`
- [ ] `POST /api/v1/rag/search` — embed query, pgvector similarity search, return top-k chunks
- [ ] `POST /api/v1/rag/query` — search + build context + call LLM + return answer with source references

**Acceptance criteria:** Uploading a document and querying it returns an answer that's actually grounded in that document's content, with a traceable source chunk.

---

## ⬜ Phase 7 — AI Chatbot

**Goal:** Intent router combining DB tools, RAG, and general LLM.

- [ ] `chat_sessions` and `chat_messages` tables
- [ ] Intent router logic (rules-based or small LLM call) classifying: DB query / RAG / general
- [ ] DB-query tool functions (e.g. `get_attendance(student_id, subject_id)`)
- [ ] `POST /api/v1/chat` — routes the message, returns response + `source_type`
- [ ] `GET /api/v1/chat/sessions`, session history endpoints
- [ ] Streaming via WebSocket or SSE (`/api/v1/chat/ws`)
- [ ] Chat UI (`ChatWindow.jsx`, `Message.jsx`, `ChatInput.jsx`)

**Acceptance criteria:** All three example question types from `ARCHITECTURE.md` §7 route correctly and return accurate answers.

---

## ⬜ Phase 8 — Analytics

**Goal:** Charts and reporting per role.

- [ ] `GET /api/v1/analytics/student|faculty|admin|attendance|assignments`
- [ ] Attendance trend charts (Recharts)
- [ ] Assignment completion/grade charts
- [ ] Admin system-wide analytics view

**Acceptance criteria:** Each dashboard shows at least one real, data-backed chart — no placeholder/sample data.

---

## ⬜ Phase 9 — Face Recognition *(optional)*

- [ ] Camera capture UI
- [ ] Face detection + embedding pipeline
- [ ] Face matching against enrolled student embeddings
- [ ] `POST /api/v1/attendance/face/recognize` → writes to `attendance_records`

**Note:** Keep isolated from core attendance logic — different performance/privacy profile. Skip for v1 if not required.

---

## ⬜ Phase 10 — Advanced AI *(optional)*

- [ ] Voice assistant
- [ ] Study planner
- [ ] Recommendations engine
- [ ] Multilingual support

**Note:** Post-v1. Only start after Phases 1–8 are stable in real use.

---

## ⬜ Phase 11 — Production

- [ ] Dockerize backend and frontend (not just the database)
- [ ] `docker-compose.yml` extended for full-stack local + prod parity
- [ ] Nginx reverse proxy + HTTPS
- [ ] CI/CD pipeline (GitHub Actions) — test + deploy
- [ ] Cloud deployment (choose provider)
- [ ] Monitoring/logging (e.g. Sentry, basic uptime checks)
- [ ] Automated database backups

---

## How to use this file

1. Work top to bottom — don't skip ahead into a later phase's checkboxes.
2. When starting a phase, use the AI-prompting template in `ARCHITECTURE.md` §13, pasting in only that phase's relevant checklist items + schema section.
3. Check items off only after you've actually run and verified them (via `/docs`, Postman, or the UI) — not just after the AI generates the code.
4. Commit to git at the end of each phase with a message referencing the phase, e.g. `git commit -m "feat: Phase 3 complete - core ERP modules"`.
