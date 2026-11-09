# 30 — Deployment and Docker

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Previously observed (older snapshot — PO-RV, re-verify)
| Item | State |
|---|---|
| `docker-compose.yml` with `campusgpt_db` (`pgvector/pgvector:pg16`), `backend`, `frontend` | IMPLEMENTED (PO-RV) (dev-oriented) |
| Backend command `alembic upgrade head && uvicorn … --reload`; Dockerfile CMD also migrates | IMPLEMENTED BUT DEFECTIVE (PO-RV) |
| Credentials hardcoded in Compose and docs | IMPLEMENTED BUT DEFECTIVE (PO-RV) |
| DB (5433) and API (8000) ports published on all host interfaces | IMPLEMENTED BUT DEFECTIVE (PO-RV) |
| Backend runs as root; heavy AI packages installed though unused | IMPLEMENTED BUT DEFECTIVE (PO-RV) |
| Production frontend `Dockerfile` + `nginx.conf` | IMPLEMENTED (PO-RV) (unused by Compose) |
| Production Compose layer, healthchecks, HTTPS | NOT IMPLEMENTED |

## 2. Target layout (PROPOSED, WP8)
```
docker-compose.yml            base services (db, migrate, backend, frontend)
docker-compose.override.yml   development (auto-loaded): bind mounts, reload, ports on 127.0.0.1, dev creds from .env
docker-compose.prod.yml       production: built images, no bind mounts, no DB port, required secrets, healthchecks, restart
```
Services: `db` (PostgreSQL + pgvector), `migrate` (one-shot, same backend image), `backend` (API, non-root), `worker` (same image, added in P14), `frontend` (Nginx serving the built SPA and proxying `/api`).

## 3. Migration procedure
Development: `migrate` runs automatically before `backend`; failure stops the API. Production: take backup → run `migrate` → verify → start API. Forward-only; no `down -v`; downgrades only in development after a backup. The API image never runs Alembic at start.

## 4. Environment variables
Names are documented in `.env.example` (development) and a production template listing **names only**. Required in production: `ENV=production`, `DATABASE_URL`, `JWT_SECRET_KEY` (≥ 32 chars, not default), `CORS_ORIGINS`, `FRONTEND_URL`, `RESEND_API_KEY`, `EMAIL_FROM` (verified domain, PD-22), `GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI`, trusted proxy list, and later LLM/embedding settings. Compose uses fail-fast substitution so missing values abort startup.

## 5. Networking and exposure
Internal Docker network; only Nginx publishes 80/443; DB not published in production; backend not published directly. Forwarded headers trusted only from Nginx. HTTPS termination (certificates, HSTS, secure cookies) is required before production (PD-17).

## 6. Persistence and backup
Named volumes for PostgreSQL data and uploaded files; scheduled `pg_dump` plus file-volume backup; restore rehearsal documented in P25. Never remove the data volume casually.

## 7. Images
Multi-stage frontend build; backend image minimal with pinned dependencies; `requirements.txt` (runtime), `requirements-dev.txt` (tests), `requirements-ai.txt` (RAG phase). Non-root user; read-only filesystem where practical; no secrets baked in.

## 8. Health and resilience
`/health` for liveness; a readiness check that also queries the database is PROPOSED. Healthchecks on `db` and `backend`; restart policies; `migrate` has `restart: no`.

## 9. CI/CD
GitHub Actions (WP10): backend tests with a pgvector service, migration/drift check, frontend lint and build. Deployment automation is out of scope until PD-17 is decided.

## 10. Production checklist
See `docs/40_Acceptance_Criteria.md` section E.

## 11. WebSocket proxying
Nginx must forward `/api/v1/ws/` to the backend with `proxy_http_version 1.1`, `Upgrade`/`Connection` headers, `proxy_buffering off` and read/send timeouts above the heartbeat interval; forwarded headers are trusted only from Nginx. The full block is in `docs/architecture/WebSocket_Protocol.md` §12. Service names and ports in that block are previously observed — verify. Redis is not part of the deployment.

## 12. Third-party endpoints used by voice
Vapi calls the backend's tool endpoints over HTTPS, so the production deployment needs a publicly reachable HTTPS endpoint for `/api/v1/voice/tools/*` protected by Vapi server authentication and rate limits; development uses a secure tunnel to a developer machine (decision recorded with PD-19/PD-17). The Vapi public key is a frontend build-time setting; private keys live only in the backend secret store.
