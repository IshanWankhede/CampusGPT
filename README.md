# CampusGPT

CampusGPT is a full-stack campus management application with a React frontend,
FastAPI backend, PostgreSQL database, and `pgvector` support. The current
implementation is the foundation and authentication phase. The ERP, dashboards,
document RAG, chatbot, and analytics modules are planned in later phases.

## Current integrated functionality

- React + Vite frontend with the CampusGPT landing page and authentication UI.
- FastAPI backend with SQLAlchemy and Alembic migrations.
- PostgreSQL 16 with the `pgvector` extension.
- JWT access and refresh tokens.
- Password hashing with bcrypt.
- Student, Faculty, and Admin roles with reusable server-side RBAC dependencies.
- Signup email verification with Resend OTP emails.
- Inline six-digit signup OTP verification:
  - verification starts before account creation;
  - OTP boxes advance automatically while typing;
  - resend countdown;
  - green locked success state;
  - red error state with backend error messages.
- Password reset through email OTP.
- Protected placeholder application page after login.
- Docker Compose stack containing the frontend, backend, and `campusgpt_db`.
- Persistent PostgreSQL data through the `pgdata` Docker volume.

## Architecture and database documentation

The design and implementation source documents are in the
[`Architecture/`](./Architecture/) directory:

- [`ARCHITECTURE.md`](./Architecture/ARCHITECTURE.md) — system architecture,
  authentication, RBAC, API conventions, and future modules.
- [`DB_SCHEMA.md`](./Architecture/DB_SCHEMA.md) — database tables and
  relationships.
- [`DESIGN.md`](./Architecture/DESIGN.md) — visual design tokens and UI rules.
- [`PHASES.md`](./Architecture/PHASES.md) — delivery phases and checklists.
- [`PRD.md`](./Architecture/PRD.md) — product requirements.
- [`REQUIREMENTS.md`](./Architecture/REQUIREMENTS.md) — functional requirements.
- [`UML_DIAGRAMS.md`](./Architecture/UML_DIAGRAMS.md) — class, flow, and
  sequence diagrams.

Backend feature modules follow the four-layer pattern:

```text
router.py -> schemas.py -> service.py -> repository.py
```

## Project structure

```text
CampusGPT/
├── Architecture/
│   ├── ARCHITECTURE.md
│   ├── DB_SCHEMA.md
│   ├── DESIGN.md
│   ├── PHASES.md
│   ├── PRD.md
│   ├── REQUIREMENTS.md
│   └── UML_DIAGRAMS.md
├── backend/
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── auth/
│   │   ├── core/
│   │   ├── database/
│   │   └── models/
│   ├── .env                 # local secrets; never commit
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── context/
│   │   ├── features/
│   │   └── routes/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── .env.example
```

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS, React Router |
| Visual effects | Motion, OGL, Font Awesome |
| Backend | FastAPI, Python 3.11+ |
| Database access | SQLAlchemy 2, Alembic |
| Database | PostgreSQL 16 + pgvector |
| Authentication | JWT, bcrypt, role-based access control |
| Email | Resend |
| Deployment | Docker, Docker Compose, Nginx |

## Run on a new laptop with Docker (recommended)

These steps work for Windows, macOS, and Linux. On Windows, use PowerShell.

### 1. Install prerequisites

Install:

- Git: <https://git-scm.com/downloads>
- Docker Desktop: <https://www.docker.com/products/docker-desktop/>

Open Docker Desktop and wait until the Docker Engine is running.

### 2. Clone the repository

```bash
git clone https://github.com/IshanWankhede/CampusGPT.git
cd CampusGPT
```

### 3. Create the local backend environment file

Copy the example file:

```bash
# Windows PowerShell
Copy-Item .env.example backend\.env

# macOS/Linux
cp .env.example backend/.env
```

Open `backend/.env` and set:

```env
JWT_SECRET_KEY=use-a-long-random-secret
RESEND_API_KEY=your_resend_api_key
EMAIL_FROM=your-verified-sender@example.com
```

`EMAIL_FROM` must be a sender/domain accepted by your Resend account. Do not
commit `backend/.env` or paste the API key into GitHub.

### 4. Build and start all services

The `--env-file` option is important because Docker Compose reads the Resend
and JWT values from `backend/.env`:

```bash
docker compose --env-file backend/.env up --build -d
```

On Windows PowerShell the equivalent path is:

```powershell
docker compose --env-file backend\.env up --build -d
```

The first build can take several minutes because dependencies are downloaded.
The backend uses CPU-only PyTorch to avoid downloading CUDA packages.

### 5. Check that everything is running

```bash
docker compose ps
docker compose logs --tail 100 backend
```

Expected services:

| Service | URL/connection |
|---|---|
| Frontend | <http://localhost:5173> |
| Backend API | <http://localhost:8000> |
| Swagger docs | <http://localhost:8000/docs> |
| Health check | <http://localhost:8000/health> |
| PostgreSQL from host | `localhost:5433` |
| PostgreSQL inside Compose | `campusgpt_db:5432` |

Migrations run automatically when the backend container starts. The current
migration chain creates users, OTP verification records, and support for
pre-registration email OTPs.

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

The database is persisted in the Docker volume named `pgdata`. To inspect
migrations from the backend container:

```bash
docker compose exec backend alembic current
docker compose exec backend alembic history
```

## Run without Docker for frontend/backend development

Docker is still recommended for PostgreSQL because the project requires
PostgreSQL with `pgvector`.

### 1. Start only the database

```bash
docker compose --env-file backend/.env up -d campusgpt_db
```

### 2. Install and run the backend

Create `backend/.env` as described above, then use:

```bash
cd backend

# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

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

The frontend runs at <http://localhost:5173> and proxies `/api` requests to
the backend during development.

## Authentication flow

### Available authentication endpoints

All authentication routes are under `/api/v1/auth`:

```text
POST /register
POST /login
POST /refresh
POST /logout
GET  /me
GET  /admin-test
POST /send-otp
POST /verify-otp
POST /forgot-password
POST /reset-password
```

### Signup

1. Enter a name, email, role, and password.
2. A valid email shows the inline **Verify Email** button.
3. The backend sends a six-digit `EMAIL_VERIFY` OTP through Resend.
4. Entering all six digits verifies the email automatically.
5. The backend stores the verification proof against the normalized email.
6. Account creation is rejected server-side unless a matching, used, and
   non-expired OTP exists.
7. The new account is created with `is_email_verified=true`.

The frontend verification state is not trusted as security proof.

### Login and protected page

Successful login returns access and refresh tokens. The frontend stores the
session locally, checks `/me` when the app loads, and opens the protected
placeholder page at `/app`. Signing out clears the local session and returns
to the landing page.

## Environment variables

The tracked [`.env.example`](./.env.example) contains placeholders only.
Create the real ignored file at `backend/.env`:

```env
JWT_SECRET_KEY=change-this-secret-in-production
RESEND_API_KEY=your_resend_api_key_here
EMAIL_FROM=onboarding@resend.dev
```

Docker Compose supplies the database URL and other defaults to the backend
container. Optional variables supported by `docker-compose.yml` include:

```env
LLM_API_KEY=
LLM_MODEL=claude-sonnet-5
EMBEDDING_MODEL=all-MiniLM-L6-v2
CORS_ORIGINS=http://localhost:5173
ENV=development
```

Never commit real API keys, passwords, or `.env` files.

## Troubleshooting

### Docker command cannot connect

Open Docker Desktop and wait for the Engine to become ready:

```bash
docker info
```

### Changed `.env` values are not taking effect

Recreate the backend container:

```bash
docker compose --env-file backend/.env up -d --build backend
```

### Email is not delivered

Check that:

1. `RESEND_API_KEY` is present in `backend/.env`.
2. `EMAIL_FROM` is a valid Resend sender.
3. The backend was recreated after editing `.env`.
4. The backend logs do not show a Resend error:

```bash
docker compose logs --tail 100 backend
```

### Port already in use

The default host ports are `5173`, `8000`, and `5433`. Stop the process using
the port or change the host side of the mapping in `docker-compose.yml`.

### Database or migration problems

```bash
docker compose ps
docker compose logs --tail 100 campusgpt_db
docker compose logs --tail 100 backend
docker compose exec backend alembic current
```

For a completely fresh local database only, remove the volume:

```bash
docker compose down -v
docker compose --env-file backend/.env up --build -d
```

## Roadmap

The planned phases are tracked in [`PHASES.md`](./Architecture/PHASES.md):

1. Foundation — complete
2. Authentication and OTP verification — complete
3. Core ERP modules
4. Student, Faculty, and Admin dashboards
5. Documents and text extraction
6. RAG and pgvector search
7. AI chatbot and intent routing
8. Analytics and reporting
9. Optional face recognition
10. Optional advanced AI features
11. Production hardening and operations

## Contributing

When adding a backend feature, follow the existing
`router -> schemas -> service -> repository` structure. Add an Alembic
migration for every database schema change, update the relevant architecture
documentation, and keep secrets out of source control.

## License

MIT License
