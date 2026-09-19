# 🏗️ CampusGPT

A full-stack College/Campus Management System with an integrated AI assistant. CampusGPT combines a traditional ERP (attendance, timetable, assignments, notices, documents, analytics) with a **RAG-powered chatbot** that can answer questions from uploaded course material, query student data, or answer general questions — all routed intelligently based on intent.

> 📄 See [`ARCHITECTURE.md`](./Architecture/ARCHITECTURE.md) for the full system design, [`UML_DIAGRAMS.md`](./Architecture/UML_DIAGRAMS.md) for class/UML and flow diagrams, and [`DB_SCHEMA.md`](./Architecture/DB_SCHEMA.md) for the database schema.

---

## ✨ Features

- 🔐 JWT authentication with role-based access control (Student / Faculty / Admin)
- 🏫 Multi-college support (COEP / PICT / VIT) with per-college email domain validation
- 📧 OTP-based email verification and password reset (via Resend)
- 🔑 "Continue with Google" sign-in, restricted to recognized college email domains
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
| Auth | JWT (access + refresh), bcrypt, Google OAuth 2.0 (Authlib) |
| Email | Resend (OTP verification & password reset) |
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
│   ├── Dockerfile          # production build (Nginx static serve)
│   ├── Dockerfile.dev      # local development (Vite dev server + HMR)
│   └── src/
│       ├── components/{ui, common, navbar, sidebar, charts}/
│       ├── pages/{auth, student, faculty, admin}/
│       ├── features/{auth, attendance, timetable, assignments,
│       │             notices, documents, chatbot, analytics}/
│       ├── hooks/
│       ├── services/{api.js, auth.js, chatbot.js}
│       ├── context/
│       ├── routes/
│       ├── utils/
│       └── constants/
│
├── backend/
│   ├── Dockerfile
│   └── app/
│       ├── core/{config.py, security.py, dependencies.py, logging.py, email.py}
│       ├── database/{session.py, base.py, models/}
│       ├── auth/{router.py, schemas.py, service.py, repository.py, oauth.py}
│       ├── users/
│       ├── attendance/
│       ├── timetable/
│       ├── assignments/
│       ├── notices/
│       ├── documents/
│       ├── rag/
│       ├── chat/
│       ├── analytics/
│       ├── notifications/
│       └── create_admin.py   # one-time CLI bootstrap for the first Admin account
│
├── docker-compose.yml
├── .env.example
└── .gitignore
```

Each backend feature module follows a consistent four-layer pattern: `router.py → schemas.py → service.py → repository.py`. See [`ARCHITECTURE.md`](./Architecture/ARCHITECTURE.md) for details.

---

## 📐 Diagrams

All UML class diagrams and flow/sequence diagrams (auth, OTP verification, Google OAuth, attendance, assignments, RAG ingestion, RAG query, chatbot routing, notifications, and state diagrams) live in [`UML_DIAGRAMS.md`](./Architecture/UML_DIAGRAMS.md). A couple of the most-referenced ones:

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

These steps work for Windows, macOS, and Linux. On Windows, use PowerShell — commands are given for both where they differ.

### 1. Install prerequisites

- **Git** — [git-scm.com/downloads](https://git-scm.com/downloads)
- **Docker Desktop** — [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)

Open Docker Desktop and wait until it says **"Engine running"** before continuing.

### 2. Clone the repository

```bash
git clone https://github.com/IshanWankhede/CampusGPT.git
cd CampusGPT
```

### 3. Create the local backend environment file

```powershell
# Windows PowerShell
Copy-Item .env.example backend\.env
```

```bash
# macOS/Linux
cp .env.example backend/.env
```

Open `backend/.env` and fill in **at minimum**:

```env
JWT_SECRET_KEY=use-a-long-random-secret

# Resend — for OTP email verification & password reset
RESEND_API_KEY=your_resend_api_key
EMAIL_FROM=onboarding@resend.dev

# Google OAuth — for "Continue with Google" sign-in
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
FRONTEND_URL=http://localhost:5173
```

- `EMAIL_FROM` must be a sender/domain accepted by your Resend account (the default `onboarding@resend.dev` only delivers to your own Resend account email — see `ARCHITECTURE.md` §5.1 for the domain-verification steps needed to email other people).
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` come from your Google Cloud Console OAuth credentials (see `ARCHITECTURE.md` §5.3 for setup steps). Google sign-in is restricted to recognized college domains — see [Multi-College Support](#-multi-college-support) below.
- Never commit `backend/.env` or paste real keys into GitHub — it's already listed in `.gitignore`.

### 4. Build and start all services (Docker — recommended)

```bash
docker compose --env-file backend/.env up --build -d
```

```powershell
# Windows PowerShell
docker compose --env-file backend\.env up --build -d
```

This starts three containers: `campusgpt_db` (PostgreSQL + pgvector), `backend` (FastAPI, with Alembic migrations applied automatically on startup), and `frontend` (Vite dev server with hot module replacement).

> ℹ️ The first build takes several minutes — dependencies are downloaded, and the backend uses CPU-only PyTorch to avoid pulling CUDA packages.

The dev setup uses **live code reload** on both sides — no rebuild needed for ordinary code changes:
- Backend: source is bind-mounted and `uvicorn --reload` picks up changes automatically
- Frontend: `frontend/Dockerfile.dev` runs Vite's real dev server with HMR, not the production Nginx build

You only need to rebuild (`--build`) when you add a new **dependency** (a pip package or an npm package) — not for ordinary source code edits.

### 5. Check that everything is running

```bash
docker compose ps
docker compose logs --tail 100 backend
```

| Service | URL / connection |
|---|---|
| Frontend | [http://localhost:5173](http://localhost:5173/) |
| Backend API | [http://localhost:8000](http://localhost:8000/) |
| Swagger docs | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Health check | [http://localhost:8000/health](http://localhost:8000/health) |
| PostgreSQL from host (e.g. pgAdmin) | `localhost:5433` |
| PostgreSQL inside Compose network | `campusgpt_db:5432` |

Migrations run automatically when the backend container starts.

### 6. Create your first Admin account

Admin accounts aren't self-registered (they're provisioned, not signed up) — create the first one with the bootstrap script, run **inside the backend container**:

```bash
docker compose exec backend python -m app.create_admin
```

Or non-interactively with flags:
```bash
docker compose exec backend python -m app.create_admin --email admin@campusgpt.dev --name "Admin User" --password "YourSecretPassword"
```

Log in with these credentials through the normal Sign In page — the college selector on that screen can be set to anything for an Admin account, it's ignored for that role.

### 7. Stop, restart, and rebuild

```bash
# Stop containers but keep database data
docker compose down

# Start existing containers again (fast, no rebuild)
docker compose --env-file backend/.env up -d

# Rebuild after adding a new dependency (pip/npm package)
docker compose --env-file backend/.env up --build -d

# Stop and DELETE the database volume (destructive — wipes all local data)
docker compose down -v
```

---

## 🏫 Multi-College Support

CampusGPT supports multiple colleges, each restricted to its own official email domain. This applies to both local email+password signup and Google OAuth sign-in.

| College | Required email domain |
|---|---|
| COEP (College of Engineering, Pune) | `coeptech.ac.in` |
| PICT (Pune Institute of Computer Technology) | `pict.edu` |
| VIT | `vit.edu` |

> ⚠️ Double-check these are each institution's real, current student/staff email domain before relying on them in production — an incorrect domain locks out real users. The mapping lives in one place in the backend config (`COLLEGE_DOMAIN_MAP`) for easy correction.

On Sign Up, selecting a college updates the expected email domain and validates against it before an OTP is sent. On Sign In, selecting a college is only required to enable the "Continue with Google" button (the college for Google sign-in is otherwise derived automatically from the verified email's domain).

---

## 🗄️ Connect the database in pgAdmin

Start the Docker stack first, then create a new server in pgAdmin with:

| pgAdmin field | Value |
|---|---|
| Name | `CampusGPT Docker` |
| Host name/address | `localhost` |
| Port | `5433` |
| Maintenance database | `campusgpt` |
| Username | `campusgpt` |
| Password | `campusgpt_dev` |

The database is persisted in the Docker volume named `pgdata`. To inspect migrations from inside the backend container:

```bash
docker compose exec backend alembic current
docker compose exec backend alembic history
```

---

## 🧑‍💻 Running without Docker (frontend/backend on the host)

Docker is still recommended for PostgreSQL, since the project requires PostgreSQL with the `pgvector` extension.

### 1. Start only the database via Docker

```bash
docker compose --env-file backend/.env up -d campusgpt_db
```

### 2. Install and run the backend

Create `backend/.env` as described in step 3 above, then:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows
# source venv/bin/activate      # macOS/Linux

pip install -r requirements.txt
```

For a host-run backend, point the database URL at the host-mapped port (`5433`, not the internal Compose port):

```env
DATABASE_URL=postgresql+psycopg2://campusgpt:campusgpt_dev@localhost:5433/campusgpt
```

Run migrations and start the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

To create your first Admin account when running this way (no Docker exec needed):
```bash
python -m app.create_admin
```

### 3. Install and run the frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at [http://localhost:5173](http://localhost:5173/) and proxies `/api` requests to the backend during development.

---

## 🔑 Environment Variables

The committed template is [`.env.example`](./.env.example). Copy it to `backend/.env` before starting the stack — never commit `backend/.env` itself; it's already listed in `.gitignore`.

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (auto-set correctly inside Docker Compose) |
| `JWT_SECRET_KEY` | Signs access/refresh tokens — use a long random string |
| `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` | Token config |
| `RESEND_API_KEY`, `EMAIL_FROM` | OTP email delivery (verification, password reset) |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` | Google OAuth sign-in |
| `FRONTEND_URL` | Where the backend redirects after OAuth completes |
| `LLM_API_KEY`, `LLM_MODEL` | LLM provider for RAG/Chatbot (Phase 6+) |
| `EMBEDDING_MODEL` | Sentence Transformers model for RAG (Phase 6+) |
| `CORS_ORIGINS` | Allowed frontend origin(s) |

---

## 🗺️ Build Roadmap

The project is built in 11 phases, from foundation to production. Full detail in [`ARCHITECTURE.md`](./Architecture/ARCHITECTURE.md) and the live checklist in [`PHASES.md`](./Architecture/PHASES.md):

1. **Foundation** — Git, FastAPI, React, PostgreSQL wired together ✅
2. **Authentication** — Register, login, JWT, RBAC, OTP verification, password reset, multi-college Google OAuth ✅
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

All routes are versioned under `/api/v1/`. Full endpoint list in [`ARCHITECTURE.md`](./Architecture/ARCHITECTURE.md). Highlights:

```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/send-otp
POST /api/v1/auth/verify-otp
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
GET  /api/v1/auth/google/login
GET  /api/v1/auth/google/callback
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
- OTPs are hashed before storage, expire in 10 minutes, single-use, and rate-limited (max 3 sends / 15 min)
- Google OAuth's email domain check happens server-side only; college selection is never trusted from the frontend
- File uploads are validated by type/size server-side; client-supplied filenames are never trusted directly
- Secrets live in environment variables only, never committed

---

## 🤝 Contributing

This project is built incrementally, module by module (see roadmap above). When adding a new backend module, follow the existing `router/schemas/service/repository` pattern and the naming conventions already used in the codebase. Check [`PHASES.md`](./Architecture/PHASES.md) before starting a new module to confirm what's already built and what the next checklist items are.

## 📄 License

MIT License
