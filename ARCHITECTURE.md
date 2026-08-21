# CampusGPT — Architecture

This document is the source of truth for CampusGPT's system design. Keep it updated as the project evolves, and feed the relevant section to your AI coding tool (Antigravity, GitHub Copilot, Claude, etc.) at the start of each build phase so generated code stays consistent.

> For table-level schema details, see [`DB_SCHEMA.md`](./DB_SCHEMA.md).

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [Backend Architecture](#4-backend-architecture)
5. [Authentication & RBAC](#5-authentication--rbac)
6. [RAG Architecture](#6-rag-architecture)
7. [AI Chatbot Architecture](#7-ai-chatbot-architecture)
8. [API Reference](#8-api-reference)
9. [Frontend Architecture](#9-frontend-architecture)
10. [Dashboards](#10-dashboards)
11. [Production Security Checklist](#11-production-security-checklist)
12. [Build Roadmap (11 Phases)](#12-build-roadmap-11-phases)
13. [Prompting AI Tools Per Module](#13-prompting-ai-tools-per-module)
14. [Key Architectural Decisions](#14-key-architectural-decisions)

---

## 1. System Overview

CampusGPT is a full-stack Campus Management System with an AI layer on top. Three roles — **Student**, **Faculty**, **Admin** — use a shared React frontend backed by a single FastAPI service. The system covers standard ERP modules (attendance, timetable, assignments, notices, documents, analytics) plus an AI assistant that can:

- Answer questions from uploaded course documents (RAG)
- Answer questions about the user's own data (database tool calls)
- Answer general knowledge questions (direct LLM)

```
Frontend (React + Tailwind)
        │  REST API / WebSocket
        ▼
Backend (FastAPI)
        ├── JWT Authentication
        ├── User & RBAC
        ├── Attendance
        ├── Timetable
        ├── Assignments
        ├── Notices
        ├── Documents
        ├── Analytics
        └── AI / RAG
                ├── Document Processing
                ├── Embeddings
                ├── Retrieval
                └── LLM
        ▼
PostgreSQL (+ pgvector)
```

---

## 2. Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 18, Vite, Tailwind CSS | SPA UI, dashboards, chat window |
| Backend | FastAPI (Python 3.11+) | REST API, business logic, auth |
| ORM | SQLAlchemy 2.0 + Alembic | Models & migrations |
| Database | PostgreSQL 15/16 + `pgvector` | Relational data + vector search in one DB |
| Auth | JWT (access + refresh), passlib/bcrypt | Stateless auth, password hashing |
| Document parsing | PyMuPDF (fitz) | Extract text from uploaded PDFs |
| Embeddings | Sentence Transformers (local) or an embeddings API | Text chunks → vectors |
| LLM | Claude API (or any LLM API) | Answer generation, chat, tool routing |
| Realtime | WebSocket or Server-Sent Events | Streaming chat responses |
| Containerization | Docker + Docker Compose | Local dev parity & deployment |
| Reverse proxy | Nginx | HTTPS, routing frontend/backend |
| CI/CD | GitHub Actions | Test + deploy pipeline |

**Deliberately deferred:** LangChain/LangGraph, a separate vector DB (Qdrant/Pinecone), and face recognition — see [Key Architectural Decisions](#14-key-architectural-decisions).

---

## 3. Project Structure

```
campusgpt/
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── assets/
│       ├── components/{ui, common, navbar, sidebar, charts}/
│       ├── pages/{auth, student, faculty, admin}/
│       ├── features/{attendance, timetable, assignments,
│       │             notices, documents, chatbot, analytics}/
│       ├── hooks/
│       ├── services/{api.js, auth.js, chatbot.js}
│       ├── context/
│       ├── routes/
│       ├── utils/
│       ├── constants/
│       ├── App.jsx
│       └── main.jsx
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── core/{config.py, security.py, dependencies.py, logging.py}
│       ├── database/{session.py, base.py, models/}
│       ├── auth/{router.py, schemas.py, service.py, dependencies.py}
│       ├── users/
│       ├── attendance/
│       ├── timetable/
│       ├── assignments/
│       ├── notices/
│       ├── documents/
│       ├── rag/
│       ├── chat/
│       ├── analytics/
│       └── notifications/
│
├── docker-compose.yml
└── .env
```

---

## 4. Backend Architecture

Every feature module follows the same four-layer pattern, keeping `router.py` small and testable:

```
Router      → handles HTTP verbs/paths, calls the Service
Schema      → Pydantic models validating request/response shapes
Service     → business logic
Repository  → raw database operations (SQLAlchemy)
```

Example — attendance module:

```
attendance/
├── router.py       # POST /attendance, GET /attendance
├── schemas.py       # AttendanceCreate, AttendanceOut, ...
├── service.py       # mark_attendance(), calculate_percentage(), ...
└── repository.py    # DB inserts/selects for attendance tables
```

> When prompting an AI tool to build a module, always require it to follow this exact four-file pattern and reuse naming conventions from earlier modules.

---

## 5. Authentication & RBAC

### Login flow

```
React → POST /api/v1/auth/login → FastAPI
  → verify password (bcrypt) → generate JWT (access + refresh)
  → JWT returned to React → stored (memory / httpOnly cookie)
```

### Authenticated request flow

```
React → Authorization: Bearer <token> → FastAPI
  → JWT verification (dependency) → resolve current_user
  → role check (dependency) → endpoint logic runs
```

### Roles

- `ADMIN`
- `FACULTY`
- `STUDENT`

**Rules:**
- Never put sensitive data in the JWT payload — identity claims only (user id, role, expiry).
- Every protected route independently verifies permissions server-side.

---

## 6. RAG Architecture

RAG (Retrieval-Augmented Generation) lets the LLM answer using the campus's actual documents instead of only general training knowledge.

### 6.1 Ingestion pipeline

```
Faculty uploads PDF → FastAPI receives file
  → Store original file (disk / S3-compatible storage)
  → Extract raw text (PyMuPDF)
  → Clean text (strip headers/footers, fix whitespace)
  → Chunk text (~500 tokens, with overlap)
  → Generate embeddings per chunk (Sentence Transformers)
  → Store chunk text + embedding vector + metadata in document_chunks
```

### 6.2 Query pipeline

```
User: "Explain Unit 3" → Chat API
  → Embed the user's question (same embedding model)
  → Vector similarity search in pgvector (cosine distance)
  → Take top-k relevant chunks
  → Build a context block (chunks + citations)
  → Send context + question to the LLM
  → Return answer + source references
```

> Build this pipeline manually first (no LangChain) — see [Key Architectural Decisions](#14-key-architectural-decisions). Schema details in `DB_SCHEMA.md`.

---

## 7. AI Chatbot Architecture

The chatbot never accesses every database table directly, and never sends every question through RAG. An intent router decides where a question goes:

```
                 User Question
                      │
                 AI Router (rules or a small LLM call)
          ┌───────────┼────────────┐
          ▼           ▼            ▼
     DB Query Tool  RAG Search  General LLM
          └───────────┼────────────┘
                      ▼
                  Response (+ sources if applicable)
```

| Example question | Routed to |
|---|---|
| "What is my attendance?" | Database Tool (structured query) |
| "Explain Unit 3 of DBMS." | RAG (search uploaded course documents) |
| "Explain polymorphism." | General LLM |

---

## 8. API Reference

All routes versioned under `/api/v1/`.

### Authentication
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
```

### Users (admin-protected)
```
GET    /api/v1/users
GET    /api/v1/users/{id}
PATCH  /api/v1/users/{id}
DELETE /api/v1/users/{id}
```

### Students
```
GET /api/v1/students/me
GET /api/v1/students/{id}
GET /api/v1/students/{id}/attendance
GET /api/v1/students/{id}/assignments
GET /api/v1/students/{id}/timetable
```

### Faculty
```
GET /api/v1/faculty/me
GET /api/v1/faculty/{id}/students
GET /api/v1/faculty/{id}/subjects
```

### Attendance
```
POST /api/v1/attendance/sessions
GET  /api/v1/attendance/sessions
POST /api/v1/attendance/records
GET  /api/v1/attendance/student/{student_id}
GET  /api/v1/attendance/subject/{subject_id}
POST /api/v1/attendance/face/recognize      # later phase, optional
```

### Timetable
```
GET    /api/v1/timetable
GET    /api/v1/timetable/student/{id}
GET    /api/v1/timetable/faculty/{id}
POST   /api/v1/timetable
PATCH  /api/v1/timetable/{id}
DELETE /api/v1/timetable/{id}
```

### Assignments
```
POST   /api/v1/assignments
GET    /api/v1/assignments
GET    /api/v1/assignments/{id}
PATCH  /api/v1/assignments/{id}
DELETE /api/v1/assignments/{id}
POST   /api/v1/assignments/{id}/submit
GET    /api/v1/assignments/{id}/submissions
```

### Notices
```
POST   /api/v1/notices
GET    /api/v1/notices
GET    /api/v1/notices/{id}
PATCH  /api/v1/notices/{id}
DELETE /api/v1/notices/{id}
```

### Documents / RAG
```
POST   /api/v1/documents/upload
GET    /api/v1/documents
GET    /api/v1/documents/{id}
DELETE /api/v1/documents/{id}
POST   /api/v1/rag/query
POST   /api/v1/rag/search
```

### AI Chat
```
POST   /api/v1/chat
GET    /api/v1/chat/sessions
GET    /api/v1/chat/sessions/{id}
GET    /api/v1/chat/sessions/{id}/messages
DELETE /api/v1/chat/sessions/{id}
WS     /api/v1/chat/ws          # or SSE, for streaming
```

### Analytics
```
GET /api/v1/analytics/student
GET /api/v1/analytics/faculty
GET /api/v1/analytics/admin
GET /api/v1/analytics/attendance
GET /api/v1/analytics/assignments
```

### Notifications
```
GET   /api/v1/notifications
PATCH /api/v1/notifications/{id}/read
POST  /api/v1/notifications
```

---

## 9. Frontend Architecture

Organize React around **features**, not just pages, so each domain owns its components, API calls, and helpers:

```
features/
├── attendance/
│   ├── AttendanceCard.jsx
│   ├── AttendanceChart.jsx
│   ├── attendanceApi.js
│   └── attendanceUtils.js
├── timetable/
│   ├── Timetable.jsx
│   ├── ScheduleCard.jsx
│   └── timetableApi.js
└── chatbot/
    ├── ChatWindow.jsx
    ├── Message.jsx
    ├── ChatInput.jsx
    └── chatApi.js
```

`pages/` compose these features per role. `routes/` maps URLs to pages with role guards driven by JWT claims from `context/`.

---

## 10. Dashboards

| Student Dashboard | Faculty Dashboard | Admin Dashboard |
|---|---|---|
| Attendance | Classes | Users |
| Today's Classes | Students | Students |
| Assignments | Attendance | Faculty |
| Notices | Assignments | Departments |
| Upcoming Exams | Notices | Subjects |
| Performance | Documents | Timetables |
| CampusGPT chat | Analytics | Notices |
| | | System Analytics |

---

## 11. Production Security Checklist

- **Auth:** JWT with expiry, bcrypt password hashing, refresh token rotation
- **Authorization:** role check on every protected endpoint — never inferred from the frontend
- **API security:** CORS allow-list, rate limiting, strict Pydantic input validation
- **File uploads:** validate type/size server-side, never trust client-supplied filenames, store with generated names
- **Database:** parameterized queries only (SQLAlchemy handles this)
- **Secrets:** environment variables only, never committed

---

## 12. Build Roadmap (11 Phases)

| Phase | Focus | Outcome |
|---|---|---|
| 1 | Foundation | Git, FastAPI, React, PostgreSQL wired together; one working CRUD endpoint |
| 2 | Authentication | Register → login → JWT → current user → RBAC |
| 3 | Core ERP | Users → Departments → Students/Faculty → Subjects → Timetable → Attendance → Assignments → Notices |
| 4 | Dashboards | Student / Faculty / Admin UIs wired to real APIs |
| 5 | Documents | Upload → storage → text extraction → metadata |
| 6 | RAG ⭐ | Chunking → embeddings → pgvector search → context → LLM answer |
| 7 | AI Chatbot | Router combining DB tools + RAG + general LLM |
| 8 | Analytics | Charts per role (Recharts) |
| 9 | Face Recognition *(optional)* | Isolated module — different perf/privacy profile |
| 10 | Advanced AI *(optional)* | Voice, study planner, recommendations, multilingual |
| 11 | Production | Docker, Nginx, HTTPS, CI/CD, monitoring, backups |

Each phase should end with something runnable and testable before the next begins.

---

## 13. Prompting AI Tools Per Module

Reusable template for Antigravity, GitHub Copilot Chat, or Claude:

```
I'm building [module name] for CampusGPT, a FastAPI + React + PostgreSQL
(pgvector) project. Here is the relevant slice of the architecture:

[paste the relevant entities / endpoints / folder structure from ARCHITECTURE.md]

Here is the code already written in previous modules (for consistency):
[paste auth/core/database boilerplate, or relevant existing files]

Please generate [router.py / schemas.py / service.py / repository.py]
for this module, following the same four-layer pattern as the existing
modules. Use SQLAlchemy 2.0 style and Pydantic v2. Include docstrings
and basic input validation. Do not invent new folder names or
conventions not already used in the project.
```

Give the AI tool only what's relevant to the current module plus shared boilerplate — not the whole project at once. After generating each module, run it and check it against the API list in Section 8 before moving on.

---

## 14. Key Architectural Decisions

- **PostgreSQL + pgvector instead of a separate vector DB** — one database to run, back up, and query for the first production version. Migrate to Qdrant only if scale actually requires it.
- **No LangChain/LangGraph at first** — build the RAG pipeline by hand so every step (embedding, chunking, retrieval, context building) is understood. Introduce a framework later for reusable components, LangGraph specifically only for stateful/agentic workflows.
- **Router pattern for the chatbot** — prevents the LLM from improvising database access, which is both unreliable and a security risk. Structured data questions go through real, permissioned queries.
- **Feature-based frontend structure** — scales better than a flat pages/components split once there are 7+ domains.
- **Four-layer backend pattern** (router/schema/service/repository) — keeps individual files small and testable as the API surface grows past 40+ endpoints.
