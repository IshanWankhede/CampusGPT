# CampusGPT — Requirements

This document covers **functional requirements** (what the system must do), **non-functional requirements** (how well it must do it), and **system/environment requirements** (what's needed to build and run it). For pip package versions, see `backend/requirements.txt`; for the reasoning behind tech choices, see [`ARCHITECTURE.md`](./ARCHITECTURE.md) §14.

---

## 1. Functional Requirements

Grouped by module, referencing the endpoints defined in [`ARCHITECTURE.md`](./ARCHITECTURE.md) §8 and tables in [`DB_SCHEMA.md`](./DB_SCHEMA.md).

### 1.1 Authentication & Authorization
- FR-1.1: Users register with email + password; passwords are hashed (bcrypt) before storage, never stored in plaintext.
- FR-1.2: Users log in and receive a short-lived JWT access token and a longer-lived refresh token.
- FR-1.3: Every protected endpoint verifies the JWT and resolves the current user server-side.
- FR-1.4: Every protected endpoint enforces role restrictions (`STUDENT`, `FACULTY`, `ADMIN`) independently of frontend UI state.
- FR-1.5: Refresh tokens can be exchanged for a new access token without requiring re-login.
- FR-1.6: Users can log out, invalidating their session client-side (and server-side if a token blocklist is implemented).

### 1.2 User & Role Management
- FR-2.1: Admins can list, view, update, and deactivate/delete users.
- FR-2.2: Students and Faculty each have a profile linked 1:1 to a `users` record, plus role-specific fields (roll number, department, designation, etc.).
- FR-2.3: Departments, Courses, and Subjects are managed by Admins and referenced by Students/Faculty/Timetable/Attendance.

### 1.3 Timetable
- FR-3.1: Admins/Faculty can create, update, and delete timetable entries (subject, faculty, classroom, day, time).
- FR-3.2: Students and Faculty can view their own filtered timetable.

### 1.4 Attendance
- FR-4.1: Faculty can create an attendance session for a subject on a given date/time.
- FR-4.2: Faculty can mark attendance records (PRESENT/ABSENT/LATE/EXCUSED) per student per session.
- FR-4.3: A student cannot have more than one attendance record per session (enforced at the database level).
- FR-4.4: Students can view their own attendance history and computed attendance percentage per subject.
- FR-4.5: Faculty/Admin can view attendance by subject or by student.

### 1.5 Assignments
- FR-5.1: Faculty can create, update, and delete assignments (title, description, due date, max marks, optional attachment).
- FR-5.2: Students can submit a file against an assignment; one submission per student per assignment (enforced at the database level).
- FR-5.3: Faculty can grade a submission (marks + feedback).
- FR-5.4: Students can view their own submissions and grades.

### 1.6 Notices
- FR-6.1: Admins/Faculty can post notices, targeted to all users, a specific role, or a specific department.
- FR-6.2: Notices can be pinned and can optionally expire.
- FR-6.3: Users see only notices relevant to their role/department.

### 1.7 Documents
- FR-7.1: Faculty/Admin can upload documents (PDF primarily), associated with a subject/department where relevant.
- FR-7.2: The system validates file type and size server-side before accepting an upload; the client-supplied filename is never trusted directly for storage.
- FR-7.3: Text is extracted from uploaded PDFs automatically on upload.
- FR-7.4: Users can list and view metadata of documents they have permission to see.

### 1.8 RAG (Retrieval-Augmented Generation)
- FR-8.1: On upload, document text is chunked (with overlap) and each chunk is embedded and stored with its vector.
- FR-8.2: A query embeds the user's question and performs a vector similarity search (pgvector) to retrieve the top-k relevant chunks.
- FR-8.3: Retrieved chunks are assembled into a context block sent to the LLM along with the question.
- FR-8.4: Answers returned to the user include source references (which document/chunk the answer was grounded in).

### 1.9 AI Chatbot
- FR-9.1: Incoming chat messages are classified by an intent router into: database query, RAG search, or general LLM.
- FR-9.2: Questions about the user's own structured data (e.g. attendance) are answered via real, permissioned database queries — never left to the LLM to guess.
- FR-9.3: Questions about course material are routed to RAG.
- FR-9.4: General knowledge questions are answered directly by the LLM.
- FR-9.5: Chat history is persisted per session and retrievable later.
- FR-9.6: Chat responses support streaming (WebSocket or SSE).

### 1.10 Analytics
- FR-10.1: Students see personal analytics (attendance trend, assignment performance).
- FR-10.2: Faculty see class-level analytics (attendance trends, assignment completion rates per subject).
- FR-10.3: Admins see system-wide analytics across departments.

### 1.11 Notifications
- FR-11.1: Users receive notifications for relevant events (new notice, new assignment, graded submission, etc.).
- FR-11.2: Users can mark notifications as read.

---

## 2. Non-Functional Requirements

### 2.1 Security
- NFR-1.1: All secrets (DB credentials, JWT signing key, LLM API key) are stored in environment variables, never committed to source control.
- NFR-1.2: JWT payloads contain identity/session claims only — no passwords, no sensitive personal data.
- NFR-1.3: All API input is validated via Pydantic schemas before reaching business logic.
- NFR-1.4: SQL is executed exclusively through the ORM (SQLAlchemy) with parameterized queries — no raw string-interpolated SQL.
- NFR-1.5: CORS is restricted to an explicit allow-list of frontend origins.
- NFR-1.6: Rate limiting is applied to authentication and chat endpoints to reduce abuse/brute-force risk.

### 2.2 Performance
- NFR-2.1: Standard CRUD endpoints (attendance, timetable, assignments) respond within ~300ms under normal load on local/dev hardware.
- NFR-2.2: RAG query responses (embedding + vector search + LLM call) complete within a few seconds; streaming is used for chat to avoid perceived latency.
- NFR-2.3: A pgvector index (IVFFlat/HNSW) is added once `document_chunks` grows large enough to need it (see `DB_SCHEMA.md` §12) — not required at small scale.

### 2.3 Reliability & Data Integrity
- NFR-3.1: Unique constraints prevent duplicate attendance records and duplicate assignment submissions at the database level, not just application logic.
- NFR-3.2: Foreign key constraints enforce referential integrity across all relational tables.
- NFR-3.3: Database migrations are managed exclusively through Alembic — no manual, undocumented schema changes.

### 2.4 Maintainability
- NFR-4.1: Every backend feature module follows the same four-layer pattern (router → schema → service → repository) defined in `ARCHITECTURE.md` §4.
- NFR-4.2: Frontend code is organized by feature (`features/`), not just by page, per `ARCHITECTURE.md` §9.
- NFR-4.3: `ARCHITECTURE.md`, `DB_SCHEMA.md`, `PHASES.md`, and this document are kept up to date as the single source of truth — AI coding tools are pointed at these docs rather than re-deriving structure ad hoc.

### 2.5 Usability
- NFR-5.1: The web app is responsive down to typical laptop/tablet widths (mobile-optimized is a stretch goal, not required for v1).
- NFR-5.2: Role-based dashboards show only actions/data relevant to that role — no dead links or disabled buttons for permissions a user will never have.

### 2.6 Portability / Dev Experience
- NFR-6.1: The database (PostgreSQL + pgvector) runs identically across any teammate's machine via Docker Compose — no manual Postgres installation required for the project.
- NFR-6.2: Any teammate can go from `git clone` to a running local environment using only the steps in `README.md` → "Team Setup."

---

## 3. System / Environment Requirements

### 3.1 Software (development machine)

| Requirement | Version | Notes |
|---|---|---|
| Git | latest | Version control |
| Python | 3.11 or 3.12 | Backend runtime |
| Node.js | 20 LTS | Frontend tooling |
| Docker Desktop | latest | Runs PostgreSQL + pgvector — required on every teammate's machine |
| PostgreSQL + pgvector | 15/16 + pgvector 0.6+ | Provided via the `pgvector/pgvector:pg16` Docker image — no separate manual install needed |
| VS Code (or similar) | latest | Recommended editor; Antigravity/Copilot for AI-assisted coding |
| Postman / Insomnia / Thunder Client | latest | Manual API testing |

### 3.2 Accounts / External Services

| Requirement | Notes |
|---|---|
| GitHub account | Source control, CI/CD (Phase 11) |
| LLM API key (Claude or equivalent) | Required for RAG (Phase 6) and Chatbot (Phase 7); not needed before then |

### 3.3 Hardware (minimum, local dev)

- 8GB RAM minimum (16GB recommended once running Docker + backend + frontend + embedding model simultaneously)
- ~5GB free disk space (Docker images, `node_modules`, Python venv, model weights for Sentence Transformers)

### 3.4 Key Python Packages (backend)

See `backend/requirements.txt` for exact versions. Core set: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `psycopg2-binary`, `pydantic`, `pydantic-settings`, `python-jose`, `passlib[bcrypt]`, `python-multipart`, `python-dotenv`, `pgvector`, `sentence-transformers`, `pymupdf`, `httpx`.

### 3.5 Key npm Packages (frontend)

Core set: `react`, `vite`, `tailwindcss`, `axios`, `react-router-dom`, `recharts`.

### 3.6 Environment Variables

See `README.md` → "Environment Variables" for the full `.env` template. Never committed to git; each teammate creates their own local copy.

---

## 4. Traceability

Every functional requirement above maps to a specific phase in [`PHASES.md`](./PHASES.md):

| Requirement group | Phase |
|---|---|
| Auth & Authorization (1.1) | Phase 2 |
| User/Role/Timetable/Attendance/Assignments/Notices (1.2–1.6) | Phase 3 |
| Documents (1.7) | Phase 5 |
| RAG (1.8) | Phase 6 |
| Chatbot (1.9) | Phase 7 |
| Analytics (1.10) | Phase 8 |
| Notifications (1.11) | Phase 3/4 (backend model + UI surfacing throughout) |
