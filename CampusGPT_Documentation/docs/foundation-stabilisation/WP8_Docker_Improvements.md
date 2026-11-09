# WP8 — Docker and Deployment Improvements

**Stage 0 foundation work package.** Position in the mandatory order: Step 14 (see `Foundation_Execution_Order.md`).
**Implementation status:** IMPLEMENTED (Level 5 Tested).
- Base Compose (`docker-compose.yml`) + dev override (`docker-compose.override.yml`) + production overlay (`docker-compose.prod.yml`).
- One-shot `migrate` service (`restart: "no"`); backend depends on `service_completed_successfully`; migrations removed from API command and Dockerfile `CMD`.
- Backend image executes as non-root user `appuser` (UID 10001 / GID 10001).
- Unused heavy AI packages segregated into `backend/requirements-ai.txt`; CPU torch install step removed.
- Production environment variable fail-fast validation configured via `${VAR:?error}`.
- Nginx reverse proxy hardened with security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`), WebSocket proxy upgrade support (`$connection_upgrade`) on `/api/`, and unbuffered API streaming.
- Production migration procedure: DB backup first, explicit one-shot migration run, verify, start API. Downgrades are never automated in production; recovery relies on DB backup restore.
- Production HTTPS and TLS termination pending hosting and domain decision (PD-17). Certbot / reverse proxy TLS termination specifications documented.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## Objective
Separate development and production Compose configurations, run migrations as an explicit one-shot step, harden the backend image, and trim dependencies for the current phase.

## Existing repository context
One dev-oriented Compose file runs `alembic upgrade head && uvicorn --reload`; the Dockerfile CMD also runs migrations; credentials are hardcoded in Compose; DB and API ports are published on all interfaces; backend runs as root; heavy AI packages are installed but not imported in the snapshot; Nginx config exists only for the production frontend image.

## Files and components likely involved
- `docker-compose.yml` (+ new override and production files), `backend/Dockerfile`, `backend/requirements.txt`, `frontend/Dockerfile`, `frontend/nginx.conf`, `.env.example`

## Required inspection steps (before editing anything)
1. Verify with a search of `backend/app` which of torch, transformers, sentence-transformers, scikit-learn, scipy, sympy, networkx, pymupdf, websockets are imported. Do not remove anything that is imported.
2. Read how `DATABASE_URL` is injected and where credentials appear.

## Implementation requirements
1. Add a one-shot `migrate` service using the backend image (`restart: no`); the API depends on `service_completed_successfully`. Remove migration commands from the API command and Dockerfile CMD.
2. Base `docker-compose.yml`; `docker-compose.override.yml` for development (bind mounts, reload, dev credentials from `.env`, ports bound to `127.0.0.1`); `docker-compose.prod.yml` (built images, no bind mounts, no published DB port, required variables fail fast, restart policies, healthchecks).
3. Run the backend as a non-root user.
4. Move unused heavy AI packages to `requirements-ai.txt` (for the RAG phase) only if the import check confirms they are unused; add `requirements-dev.txt`; remove the CPU-torch install step only together with that.
5. Document the production migration procedure: backup, run `migrate`, verify, start API; forward-only policy; downgrade only in development.
6. Document HTTPS termination requirements (certificates, forwarded headers, secure cookies) without choosing a host (PD-17).

## Database impact
No schema change.

## Security impact
No secrets in images or Compose files; required production variables use fail-fast substitution; DB not reachable from the host in production; non-root container.

## Testing requirements
- `docker compose config` validates each combination.
- Fresh volume: migrate runs, then API starts. Existing volume: migrate is a no-op.
- Failing migration prevents API start.
- Production layer refuses to start without secrets and publishes no DB port.
- Backend image builds and `/health` responds after dependency trimming.

## Acceptance criteria
- API never runs migrations at start.
- Dev workflow still works with one command.
- Production layer is defined and validated (not deployed).
- Image size reduced only by verified-unused packages.

## Rollback considerations
Restore the previous Compose file and Dockerfile from git; no data impact. Keep named volumes — never use `docker compose down -v` on the data volume.

## Explicit stop conditions
Stop and report (do not guess or work around) if:
- An imported package would be removed.
- The production topology is unknown and a choice would be guesswork — document options instead.

## Human approval checkpoint
Owner reviews the production layer and procedure before any real deployment.

The next work package must not start until this checkpoint is signed off in `Foundation_Acceptance_Checklist.md`.
