# 🏗️ CampusGPT

A full-stack College/Campus Management System with an integrated AI assistant. CampusGPT combines a traditional ERP (attendance, timetable, assignments, notices, documents, analytics) with a **RAG-powered chatbot** that can answer questions from uploaded course material, query student data, or answer general questions — all routed intelligently based on intent.

> 📄 See [`ARCHITECTURE.md`](./Architecture/ARCHITECTURE.md) for the full system design, [`UML_DIAGRAMS.md`](./Architecture/UML_DIAGRAMS.md) for class/UML and flow diagrams, and [`DB_SCHEMA.md`](./Architecture/DB_SCHEMA.md) for the database schema.

---

## ✨ Features

- 🔐 JWT authentication with role-based access control (Student / Faculty / Admin)
- 📊 Attendance tracking with per-subject and per-student analytics
- 📅 Timetable management
- 📝 Assignments with submission tracking
- 📢 Notices/announcements
- 📄 Document upload and management
- 🤖 **CampusGPT AI Assistant** — RAG over course documents, database-aware Q&A, and general LLM chat, all through one intent router
- 📈 Role-specific analytics dashboards
- 🔔 Notifications

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend | FastAPI (Python 3.11+) |
| ORM / Migrations | SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL 15/16 + `pgvector` |
| Auth | JWT (access + refresh), bcrypt |
| Document parsing | PyMuPDF |
| Embeddings | Sentence Transformers |
| LLM | Claude API (or any LLM API) |
| Realtime | WebSocket / Server-Sent Events |
| Infra | Docker, Docker Compose, Nginx, GitHub Actions |

---

## 📁 Project Structure

```
campusgpt/
├── frontend/
│   └── src/
│       ├── components/{ui, common, navbar, sidebar, charts}/
│       ├── pages/{auth, student, faculty, admin}/
│       ├── features/{attendance, timetable, assignments,
│       │             notices, documents, chatbot, analytics}/
│       ├── hooks/
│       ├── services/{api.js, auth.js, chatbot.js}
│       ├── context/
│       ├── routes/
│       ├── utils/
│       └── constants/
│
├── backend/
│   └── app/
│       ├── core/{config.py, security.py, dependencies.py, logging.py}
│       ├── database/{session.py, base.py, models/}
│       ├── auth/
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

Each backend feature module follows a consistent four-layer pattern: `router.py → schemas.py → service.py → repository.py`. See `ARCHITECTURE.md` for details.

---

## 📐 Diagrams

All UML class diagrams and flow/sequence diagrams (auth, attendance, assignments, RAG ingestion, RAG query, chatbot routing, notifications, and state diagrams) live in [`UML_DIAGRAMS.md`](./Architecture/UML_DIAGRAMS.md). A couple of the most-referenced ones:

**System data flow**
```mermaid
flowchart LR
    A[React Frontend] -->|REST / WebSocket| B[FastAPI Backend]
    B --> C[(PostgreSQL + pgvector)]
    B --> D[LLM API]
```

**Chatbot intent routing**
```mermaid
flowchart TD
    A[User Question] --> B[AI Router]
    B --> C[DB Query Tool]
    B --> D[RAG Search]
    B --> E[General LLM]
    C --> F[Response]
    D --> F
    E --> F
```

---

## 🚀 Getting Started

## Run on a new laptop with Docker (recommended)

These steps work for Windows, macOS, and Linux. On Windows, use PowerShell.

### 1. Install prerequisites

Install:

- Git: [git-scm.com/downloads](https://git-scm.com/downloads)
- Docker Desktop: [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)

Open Docker Desktop and wait until the Docker Engine is running.

### 2. Clone the repository

```bash
git clone https://github.com/IshanWankhede/CampusGPT.git
cd CampusGPT
```

### 3. Create the local backend environment file

Copy the example file:

```powershell
# Windows PowerShell
Copy-Item .env.example backend\.env
```

```bash
# macOS/Linux
cp .env.example backend/.env
```

Open `backend/.env` and set:

```env
JWT_SECRET_KEY=use-a-long-random-secret
RESEND_API_KEY=your_resend_api_key
EMAIL_FROM=your-verified-sender@example.com
```

`EMAIL_FROM` must be a sender or domain accepted by your Resend account. Do not commit
`backend/.env` or paste the API key into GitHub.

### 4. Build and start all services

The `--env-file` option is important because Docker Compose reads the Resend and JWT
values from `backend/.env`:

```bash
docker compose --env-file backend/.env up --build -d
```

On Windows PowerShell, the equivalent path is:

```powershell
docker compose --env-file backend\.env up --build -d
```

The first build can take several minutes because dependencies are downloaded. The
backend uses CPU-only PyTorch to avoid downloading CUDA packages.

### 5. Check that everything is running

```bash
docker compose ps
docker compose logs --tail 100 backend
```

Expected services:

| Service | URL / connection |
|---|---|
| Frontend | [http://localhost:5173](http://localhost:5173/) |
| Backend API | [http://localhost:8000](http://localhost:8000/) |
| Swagger docs | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Health check | [http://localhost:8000/health](http://localhost:8000/health) |
| PostgreSQL from host | `localhost:5433` |
| PostgreSQL inside Compose | `campusgpt_db:5432` |

Migrations run automatically when the backend container starts. The current migration
chain creates users, OTP verification records, and support for pre-registration email OTPs.

### 6. Stop, restart, and rebuild

```bash
# Stop containers but keep database data
docker compose down

# Start existing images again
docker compose --env-file backend/.env up -d

# Rebuild after source changes
docker compose --env-file backend/.env up --build -d

# Stop and delete the database volume (destructive: deletes local data)
docker compose down -v
```

## Connect the database in pgAdmin

Start the Docker stack first, then create a new server in pgAdmin with:

| pgAdmin field | Value |
|---|---|
| Name | `CampusGPT Docker` |
| Host name/address | `localhost` |
| Port | `5433` |
| Maintenance database | `campusgpt` |
| Username | `campusgpt` |
| Password | `campusgpt_dev` |

The database is persisted in the Docker volume named `pgdata`. To inspect migrations
from the backend container:

```bash
docker compose exec backend alembic current
docker compose exec backend alembic history
```

## Run without Docker for frontend/backend development

Docker is still recommended for PostgreSQL because the project requires PostgreSQL
with `pgvector`.

### 1. Start only the database

```bash
docker compose --env-file backend/.env up -d campusgpt_db
```

### 2. Install and run the backend

Create `backend/.env` as described above, then use:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For a host-run backend, set the database URL to port `5433`:

```env
DATABASE_URL=postgresql+psycopg2://campusgpt:campusgpt_dev@localhost:5433/campusgpt
```

Run migrations and the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Install and run the frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at [http://localhost:5173](http://localhost:5173/) and proxies
`/api` requests to the backend during development.

## 🔑 Environment Variables

The committed template is [`.env.example`](./.env.example). Copy it to
`backend/.env` before starting the stack. Never commit `backend/.env`; it is already
listed in `.gitignore`.

---

## 🗺️ Build Roadmap

The project is designed to be built in 11 phases, from foundation to production. Full detail in `ARCHITECTURE.md`, summarized here:

1. **Foundation** — Git, FastAPI, React, PostgreSQL wired together
2. **Authentication** — Register, login, JWT, RBAC
3. **Core ERP** — Users → Departments → Students/Faculty → Subjects → Timetable → Attendance → Assignments → Notices
4. **Dashboards** — Student / Faculty / Admin UIs
5. **Documents** — Upload, storage, text extraction
6. **RAG** — Chunking, embeddings, pgvector search, LLM context building
7. **AI Chatbot** — Intent router combining DB tools + RAG + general LLM
8. **Analytics** — Charts and reporting per role
9. **Face Recognition** *(optional)*
10. **Advanced AI** *(optional)* — voice, recommendations, study planner
11. **Production** — Docker, Nginx, HTTPS, CI/CD, monitoring, backups

---

## 📖 API Overview

All routes are versioned under `/api/v1/`. Full endpoint list in `ARCHITECTURE.md`. Highlights:

```
POST /api/v1/auth/login
GET  /api/v1/students/{id}/attendance
POST /api/v1/attendance/records
POST /api/v1/documents/upload
POST /api/v1/rag/query
POST /api/v1/chat
GET  /api/v1/analytics/admin
```

---

## 🔐 Security Notes

- All protected endpoints verify JWT + role server-side — never trust the frontend to hide UI as the only guard
- Passwords hashed with bcrypt; JWTs carry identity claims only, never sensitive data
- File uploads are validated by type/size server-side; client-supplied filenames are never trusted directly
- Secrets live in environment variables only

---

## 🤝 Contributing

This project is built incrementally, module by module (see roadmap above). When adding a new backend module, follow the existing `router/schemas/service/repository` pattern and the naming conventions already used in the codebase.

## 📄 License

MIT License
