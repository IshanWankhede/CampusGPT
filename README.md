# 🏗️ CampusGPT

A full-stack College/Campus Management System with an integrated AI assistant. CampusGPT combines a traditional ERP (attendance, timetable, assignments, notices, documents, analytics) with a **RAG-powered chatbot** that can answer questions from uploaded course material, query student data, or answer general questions — all routed intelligently based on intent.

> 📄 See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full system design and [`DB_SCHEMA.md`](./DB_SCHEMA.md) for the database schema.

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

## 🚀 Getting Started

### Prerequisites

- Git
- Python 3.11+
- Node.js 20 LTS
- Docker Desktop (for PostgreSQL + pgvector)
- An LLM API key (e.g. from [console.anthropic.com](https://console.anthropic.com))

### 1. Clone and set up the database

```bash
git clone https://github.com/<your-username>/campusgpt.git
cd campusgpt

docker compose up -d
docker exec -it <db_container_name> psql -U campusgpt -d campusgpt \
  -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env            # then fill in your values

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000` — API docs at `http://localhost:8000/docs`.

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

## 🔑 Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql://campusgpt:campusgpt_dev@localhost:5432/campusgpt
JWT_SECRET_KEY=replace_with_a_long_random_string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LLM_API_KEY=your_llm_api_key_here
LLM_MODEL=claude-sonnet-5
EMBEDDING_MODEL=all-MiniLM-L6-v2
CORS_ORIGINS=http://localhost:5173
ENV=development
```

> ⚠️ Never commit `.env`. It's already listed in `.gitignore`.

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

Add your license of choice here (MIT, Apache-2.0, etc.).
