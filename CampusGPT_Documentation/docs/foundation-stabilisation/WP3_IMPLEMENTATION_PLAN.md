# WP3 Implementation Plan — Production Configuration Guards (Revision 3)

**Status:** Planning complete — Implementation pending approval  
**Revision:** 3 (adds G5b — production/staging database name protection)  
**Depends on:** WP2 (committed `975a23a` on `main`)  
**Estimated risk:** Low — no migrations, no schema changes, no frontend changes  
**New dependencies introduced:** None (validation uses stdlib `urllib.parse` and `typing.Literal` only)

---

## 1. Objective

Make unsafe production configuration **impossible to start**:

- Restrict `ENV` to `Literal["development", "staging", "production"]`
- Reject startup with clear, collected errors when dangerous defaults or reserved database names are detected in non-development modes
- Parse `DATABASE_URL` structurally (dialect, normalized database name, host) — no substring credential matching
- Disable `/docs`, `/redoc`, `/openapi.json` outside development
- Harden CORS to disallow `localhost` origins in staging/production
- Remove all SQLite compatibility code
- Produce a canonical `backend/.env.example`; update root `.env.example`
- Remove `env` field from `/health` response

**Expected outcome:** The backend cannot accidentally start in production or staging with the wrong database, a known-weak JWT secret, a reserved or development database name, exposed API docs, or development CORS policies.

---

## 2. Verified Code Inspection (Live at commit `975a23a`)

### 2.1 `backend/app/core/config.py` — Verified Defects

| ID | File location | Defect |
|----|--------------|--------|
| D1 | Line 9 | `DATABASE_URL` default is `"sqlite:///./campusgpt.db"` |
| D2 | Line 10 | `JWT_SECRET_KEY` default is `"development-only-change-me"` |
| D3 | Line 17 | `CORS_ORIGINS` has no production guard |
| D4 | Line 18 | `ENV: str` accepts any string — no Literal validation |

### 2.2 `backend/app/main.py` — Verified Defects

| ID | Location | Defect |
|----|---------|--------|
| D5 | Line 9 | `FastAPI()` created with no docs URL control — docs always enabled |
| D6 | Line 24 | `/health` returns `{"status": "ok", "env": settings.ENV}` — exposes ENV |

### 2.3 `backend/app/database/session.py` — Verified Defects

| ID | Location | Defect |
|----|---------|--------|
| D7 | Lines 6–7 | SQLite compat branch (`connect_args` special-case) is dead code |

### 2.4 `.env.example` Files

| File | Status | Issues |
|------|--------|--------|
| Root `.env.example` (15 lines) | Exists | Missing `FRONTEND_URL`; `GOOGLE_CLIENT_ID` placeholder looks like a real value; no key-generation guidance |
| `backend/.env.example` | **Does not exist** | Must be created |

### 2.5 All `settings.*` Usages — Exhaustive Verification

| File | Settings accessed |
|------|-----------------|
| `backend/app/main.py:13` | `CORS_ORIGINS` |
| `backend/app/main.py:24` | `ENV` (in `/health`) |
| `backend/app/auth/router.py:90,92,104,105,124,141,142,143,214` | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `FRONTEND_URL` |
| `backend/app/auth/service.py:62,68,227,232,237,241` | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` |
| `backend/app/core/email.py:215,217,220` | `RESEND_API_KEY`, `EMAIL_FROM` |
| `backend/app/database/session.py:6,7` | `DATABASE_URL` |

No hidden `settings.*` reads exist outside these files.

### 2.6 `docker-compose.yml` — Key Facts

- Backend reads `./backend/.env` via `env_file:`
- Compose **overrides** `DATABASE_URL` with `postgresql+psycopg2://campusgpt:campusgpt_dev@campusgpt_db:5432/campusgpt` via `environment:` key — takes precedence over `.env`
- Backend health check (line 39): `urllib.request.urlopen('http://localhost:8000/health')` checks HTTP 200 only — body content is irrelevant
- Removing the `env` field from `/health` response body does **not** break this health check

### 2.7 `backend/.env` (dev, gitignored)

Contains real `RESEND_API_KEY` and `JWT_SECRET_KEY`. Missing `FRONTEND_URL`. **This file is not modified by WP3.**

---

## 3. URL Parsing — Exact Validation Logic

> [!IMPORTANT]
> Database URL validation uses Python's stdlib `urllib.parse.urlparse`. No credential substring matching. Comparisons are **exact and normalized** (strip whitespace, lowercase) to handle case variations correctly.

### 3.1 Parsing Method

```python
from urllib.parse import urlparse

parsed      = urlparse(database_url)
scheme_base = parsed.scheme.split("+")[0]       # "postgresql" from "postgresql+psycopg2"
db_name_raw = parsed.path.lstrip("/")           # "campusgpt" from "/campusgpt"
db_name     = db_name_raw.strip().lower()       # normalize for comparison
host        = parsed.hostname or ""             # "campusgpt_db" or "localhost"
```

### 3.2 Verification Against All Known Project URL Patterns

Verified by running Python's `urlparse` against every URL format seen in the project:

| URL pattern | `scheme_base` | `db_name` (normalized) | `host` |
|------------|--------------|----------------------|--------|
| `sqlite:///./campusgpt.db` | `sqlite` | `./campusgpt.db` | `` |
| `postgresql://...@localhost:5433/campusgpt` | `postgresql` | `campusgpt` | `localhost` |
| `postgresql+psycopg2://...@campusgpt_db:5432/campusgpt` | `postgresql` | `campusgpt` | `campusgpt_db` |
| `postgresql+psycopg2://...@campusgpt_db:5432/campusgpt_test` | `postgresql` | `campusgpt_test` | `campusgpt_db` |
| `postgresql+psycopg2://...@db.staging.example.com:5432/campusgpt_staging` | `postgresql` | `campusgpt_staging` | `db.staging.example.com` |
| `postgresql+psycopg2://...@db.prod.example.com:5432/campusgpt_prod` | `postgresql` | `campusgpt_prod` | `db.prod.example.com` |
| `postgresql+psycopg2://...@db.prod.example.com:5432/myapp_production` | `postgresql` | `myapp_production` | `db.prod.example.com` |
| `postgresql+psycopg2://...@host:5432/CampusGPT` | `postgresql` | `campusgpt` ✅ normalized | `host` |

Edge case confirmed: `CampusGPT` (mixed-case database name) normalizes to `campusgpt` and is correctly rejected in staging/production.

### 3.3 Database URL Guard Rules — All Environments Mapped

```
RESERVED_NON_DEV_DB_NAMES = {"campusgpt", "campusgpt_dev", "campusgpt_test"}
```

| Environment | SQLite dialect | Reserved DB name | Localhost host |
|-------------|--------------|-----------------|---------------|
| `development` | Allowed (removed default will cause Pydantic error if unset) | Allowed | Allowed |
| `staging` | ❌ Rejected | ❌ Rejected | Allowed |
| `production` | ❌ Rejected | ❌ Rejected | ❌ Rejected |

**Rationale for each rejection:**

- **SQLite (G4):** Every migration after 0001 requires PostgreSQL. SQLite cannot run them.
- **Reserved names (G5+G5b combined):** `campusgpt_dev` and `campusgpt_test` are unambiguously development/test databases. `campusgpt` (bare name) is the development database defined in `docker-compose.yml` — using it in staging or production would risk operating against the development database.
- **Localhost host in production (G6):** A production deployment must connect to a network-accessible database. Localhost is a signal of a misconfigured deployment.
- **Localhost host in staging:** Explicitly **allowed** — running staging locally is a valid use case.

**What is not inspected in the URL:**
- Username — valid usernames vary; no development-specific guard needed
- Password — passwords must never be inspected, logged, or appear in error messages
- Port — deployment-specific; not meaningful as a guard

---

## 4. All Startup Guards — Complete Specification (Revision 3)

> [!IMPORTANT]
> All guards G1–G8 activate only when `ENV` is `staging` or `production`. Guard G6 activates only when `ENV` is `production`. Development startup is completely unaffected.

All errors are **collected** before raising a single `ValueError`, so a misconfigured environment reports every violation in one startup failure.

---

### G1 — JWT secret: default value

| Property | Value |
|----------|-------|
| **Variable** | `JWT_SECRET_KEY` |
| **Purpose** | Signs and verifies all JWT access and refresh tokens |
| **Mandatory?** | ✅ Required in all environments |
| **Feature** | Every authenticated endpoint; `auth/service.py` token issuance |
| **Guard condition** | `JWT_SECRET_KEY == "development-only-change-me"` |
| **Error** | `JWT_SECRET_KEY must not use the development default in staging/production` |
| **Blocks startup?** | Yes |

### G2 — JWT secret: development marker in value

| Property | Value |
|----------|-------|
| **Variable** | `JWT_SECRET_KEY` |
| **Guard condition** | `"development" in JWT_SECRET_KEY.lower()` |
| **Error** | `JWT_SECRET_KEY contains the word "development" — replace with a securely generated secret` |
| **Blocks startup?** | Yes |

### G3 — JWT secret: minimum length

| Property | Value |
|----------|-------|
| **Variable** | `JWT_SECRET_KEY` |
| **Guard condition** | `len(JWT_SECRET_KEY) < 32` |
| **Error** | `JWT_SECRET_KEY must be at least 32 characters in staging/production` |
| **Blocks startup?** | Yes |
| **Note** | `openssl rand -hex 32` produces a 64-character secret |

### G4 — Database URL: SQLite dialect

| Property | Value |
|----------|-------|
| **Variable** | `DATABASE_URL` |
| **Purpose** | PostgreSQL connection string; required for all migrations |
| **Mandatory?** | ✅ Required in all environments (default being removed in Task 3) |
| **Feature** | Every database operation — all models, all endpoints |
| **Guard condition** | `parsed_scheme_base == "sqlite"` |
| **Error** | `SQLite is not permitted in staging/production. Use PostgreSQL.` |
| **Blocks startup?** | Yes |

### G5 + G5b — Database URL: reserved or development database names

| Property | Value |
|----------|-------|
| **Variable** | `DATABASE_URL` |
| **Guard condition (staging + production)** | `normalized_db_name in {"campusgpt", "campusgpt_dev", "campusgpt_test"}` |
| **Error (staging)** | `DATABASE_URL points to reserved database '{name}'. Use a dedicated staging database (recommended: campusgpt_staging).` |
| **Error (production)** | `DATABASE_URL points to reserved database '{name}'. Use a dedicated production database (recommended: campusgpt_prod).` |
| **Blocks startup?** | Yes |
| **Normalization** | `db_name.strip().lower()` — exact match, case-insensitive |

**Reserved name policy by environment:**

| Database name | Development | Staging | Production |
|--------------|-------------|---------|------------|
| `campusgpt` | ✅ Allowed | ❌ Rejected | ❌ Rejected |
| `campusgpt_dev` | ✅ Allowed | ❌ Rejected | ❌ Rejected |
| `campusgpt_test` | ✅ Allowed | ❌ Rejected | ❌ Rejected |
| `campusgpt_staging` | ✅ Allowed | ✅ Recommended | ✅ Allowed |
| `campusgpt_prod` | ✅ Allowed | ✅ Allowed | ✅ Recommended |
| Any other name | ✅ Allowed | ✅ Allowed | ✅ Allowed |

> [!NOTE]
> The existing automated test database safety guard in `conftest.py` (which enforces that `TEST_DATABASE_URL` ends with `_test`) is **completely separate from and unaffected by** WP3's startup guards. The startup guards fire at application boot time via pydantic-settings. The test guard fires inside pytest fixtures. They operate independently.

### G6 — Database URL: localhost host (production only)

| Property | Value |
|----------|-------|
| **Variable** | `DATABASE_URL` |
| **Guard condition** | `ENV == "production"` and `parsed_host in {"localhost", "127.0.0.1", "::1"}` |
| **Error** | `DATABASE_URL points to localhost in a production environment. Use a network-accessible database host.` |
| **Blocks startup?** | Yes |
| **Staging exemption** | Localhost is valid for local staging runs — not checked in staging |

### G7 — CORS: localhost origins in staging/production

| Property | Value |
|----------|-------|
| **Variable** | `CORS_ORIGINS` |
| **Purpose** | Controls which browser origins may call the API |
| **Mandatory?** | ✅ Required (must be overridden for deployment) |
| **Feature** | All browser → API calls from the React frontend |
| **Guard condition** | Any origin in `CORS_ORIGINS.split(",")` starts with `http://localhost` |
| **Error** | `CORS_ORIGINS includes a localhost origin — not permitted in staging/production` |
| **Blocks startup?** | Yes |

### G8 — Google OAuth: partial configuration

| Property | Value |
|----------|-------|
| **Variables** | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| **Purpose** | Google OAuth 2.0 login flow |
| **Mandatory?** | ⚪ Optional integration — both empty = disabled; both set = enabled |
| **Feature** | `GET /api/v1/auth/google/login` and callback in `auth/router.py` |
| **Guard condition** | Exactly one of the two is non-empty |
| **Error** | `GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must both be set or both be empty — partial OAuth configuration is not permitted` |
| **Blocks startup?** | Yes |
| **Note** | Both empty is **explicitly allowed** — Google OAuth is simply disabled |

---

### Variables Not Guarded at Startup

| Variable | Reason |
|----------|--------|
| `JWT_ALGORITHM` | Safe default (`HS256`); wrong value causes runtime token errors, not silent misconfiguration |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Operational preference; 30 min is a safe default |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Operational preference; 7 days is a safe default |
| `LLM_API_KEY` | LLM integration not yet implemented; guarding would block all current deployments |
| `LLM_MODEL` | Same rationale |
| `EMBEDDING_MODEL` | Same rationale |
| `RESEND_API_KEY` | Optional integration — absent means email is disabled, not a security risk |
| `EMAIL_FROM` | Has a safe Resend default; wrong value causes delivery issues at runtime |
| `GOOGLE_REDIRECT_URI` | Only meaningful when OAuth is enabled; validated by Google's consent screen |
| `FRONTEND_URL` | Used in OAuth callbacks and email links; wrong value causes redirect errors at runtime |

> [!IMPORTANT]
> `RESEND_API_KEY` is intentionally not guarded. Email is an optional integration. Making it a startup requirement would block deployments that have not yet configured transactional email. This follows the owner instruction: *"Do not make optional integrations mandatory unless they are explicitly enabled."*

---

## 5. Ordered Implementation Tasks

> [!IMPORTANT]
> **No application code, configuration files, migrations, or databases are modified until the owner explicitly approves implementation.** This document is a plan only.

Tasks are ordered by dependency. Each is one logical change and one commit.

### Task 1 — Restrict `ENV` to known literals

**File:** `backend/app/core/config.py`

```python
# Before
ENV: str = "development"

# After
from typing import Literal
ENV: Literal["development", "staging", "production"] = "development"
```

Pydantic rejects `ENV=prod`, `ENV=test`, `ENV=dev`, or any other value with a clear `ValidationError` at startup before any guard logic runs.

---

### Task 2 — Add `model_validator` with URL parser and all 8 guards

**File:** `backend/app/core/config.py`

**New imports** (all stdlib or already-used library — no new packages):
```python
from typing import Literal
from urllib.parse import urlparse
from pydantic import model_validator
```

**Validator logic (complete pseudocode):**
```python
@model_validator(mode='after')
def validate_non_development_settings(self) -> 'Settings':
    if self.ENV == "development":
        return self   # all guards skipped in development

    env = self.ENV  # "staging" or "production"
    errors: list[str] = []

    # ── G1, G2, G3: JWT Secret ────────────────────────────────────────────
    if self.JWT_SECRET_KEY == "development-only-change-me":
        errors.append(
            "JWT_SECRET_KEY must not use the development default in "
            f"{env} environments"
        )
    elif "development" in self.JWT_SECRET_KEY.lower():
        errors.append(
            'JWT_SECRET_KEY contains the word "development" — '
            "replace it with a securely generated secret "
            "(generate with: openssl rand -hex 32)"
        )
    elif len(self.JWT_SECRET_KEY) < 32:
        errors.append(
            f"JWT_SECRET_KEY must be at least 32 characters in {env} environments "
            "(generate with: openssl rand -hex 32)"
        )

    # ── G4, G5, G5b, G6: Database URL ────────────────────────────────────
    parsed = urlparse(self.DATABASE_URL)
    scheme_base = parsed.scheme.split("+")[0]
    db_name = parsed.path.lstrip("/").strip().lower()   # exact, case-normalized
    host = parsed.hostname or ""

    RESERVED_DB_NAMES = {"campusgpt", "campusgpt_dev", "campusgpt_test"}
    LOCALHOST_HOSTS = {"localhost", "127.0.0.1", "::1"}

    if scheme_base == "sqlite":
        errors.append(
            f"SQLite is not permitted as the application database in {env}. "
            "Use PostgreSQL."
        )
    else:
        if db_name in RESERVED_DB_NAMES:
            suggestion = (
                "campusgpt_staging" if env == "staging" else "campusgpt_prod"
            )
            errors.append(
                f"DATABASE_URL points to reserved database '{db_name}'. "
                f"Use a dedicated {env} database "
                f"(recommended: '{suggestion}')."
            )
        if env == "production" and host in LOCALHOST_HOSTS:
            errors.append(
                "DATABASE_URL points to localhost in a production environment. "
                "Use a network-accessible database host."
            )

    # ── G7: CORS Origins ─────────────────────────────────────────────────
    for origin in self.CORS_ORIGINS.split(","):
        if origin.strip().startswith("http://localhost"):
            errors.append(
                f"CORS_ORIGINS includes a localhost origin "
                f"('{origin.strip()}') — this is not permitted in {env} environments"
            )
            break

    # ── G8: Partial Google OAuth ─────────────────────────────────────────
    google_flags = [bool(self.GOOGLE_CLIENT_ID), bool(self.GOOGLE_CLIENT_SECRET)]
    if any(google_flags) and not all(google_flags):
        missing = "GOOGLE_CLIENT_SECRET" if self.GOOGLE_CLIENT_ID else "GOOGLE_CLIENT_ID"
        errors.append(
            f"GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must both be set or both be "
            f"empty — '{missing}' is missing"
        )

    if errors:
        bullet_list = "\n".join(f"  • {e}" for e in errors)
        raise ValueError(
            f"CampusGPT cannot start in {env} mode due to unsafe configuration:\n"
            + bullet_list
        )

    return self
```

---

### Task 3 — Remove SQLite default and SQLite compat branch

**File:** `backend/app/core/config.py`
```python
# Before
DATABASE_URL: str = "sqlite:///./campusgpt.db"

# After (required — Pydantic fails at startup if not set)
DATABASE_URL: str
```

**File:** `backend/app/database/session.py`
```python
# Before
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# After
engine = create_engine(settings.DATABASE_URL)
```

---

### Task 4 — Control FastAPI docs endpoints by ENV

**File:** `backend/app/main.py`

```python
# Before
app = FastAPI(title="CampusGPT API")

# After
_in_development = settings.ENV == "development"
app = FastAPI(
    title="CampusGPT API",
    docs_url="/docs" if _in_development else None,
    redoc_url="/redoc" if _in_development else None,
    openapi_url="/openapi.json" if _in_development else None,
)
```

`settings` is already imported at line 6 of `main.py` — no new imports needed.

---

### Task 5 — Sanitize `/health` response

**File:** `backend/app/main.py`

```python
# Before
@app.get("/health")
def health_check():
    return {"status": "ok", "env": settings.ENV}

# After
@app.get("/health")
def health_check():
    return {"status": "ok"}
```

**Health check consumers verified:**
- `docker-compose.yml` line 39: `urlopen('http://localhost:8000/health')` — checks HTTP 200 only. ✅ Not broken.
- No other consumers found in the codebase.

---

### Task 6 — Create `backend/.env.example`

New file — placeholders only, no real credentials:

```dotenv
# CampusGPT Backend — Environment Variables
# Copy this file to backend/.env and fill in real values.
# Never commit backend/.env to version control.

# ─── Environment ─────────────────────────────────────────────────────────────
# REQUIRED. Allowed values: development | staging | production
# Any other value will cause startup to fail.
ENV=development

# ─── Database ────────────────────────────────────────────────────────────────
# REQUIRED. PostgreSQL connection string.
# SQLite is not supported (all migrations require PostgreSQL).
#
# Reserved database names that are REJECTED in staging/production:
#   campusgpt, campusgpt_dev, campusgpt_test
#
# Recommended names:
#   Development : campusgpt
#   Staging     : campusgpt_staging
#   Production  : campusgpt_prod
#
# Example (local Docker development):
#   DATABASE_URL=postgresql+psycopg2://campusgpt:PASSWORD@localhost:5433/campusgpt
DATABASE_URL=postgresql+psycopg2://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME

# ─── JWT Authentication ───────────────────────────────────────────────────────
# REQUIRED.
# In staging/production: must be at least 32 characters and must not contain
# the word "development".
# Generate a secure value: openssl rand -hex 32
JWT_SECRET_KEY=REPLACE_WITH_SECURE_RANDOM_SECRET_MIN_32_CHARS
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ─── CORS ────────────────────────────────────────────────────────────────────
# Comma-separated list of allowed browser origins.
# In staging/production: must not include http://localhost
CORS_ORIGINS=http://localhost:5173

# ─── Frontend ────────────────────────────────────────────────────────────────
# Base URL of the deployed frontend (used in OAuth callbacks and email links).
FRONTEND_URL=http://localhost:5173

# ─── Google OAuth (optional) ─────────────────────────────────────────────────
# Both must be set or both must be empty.
# Leave both empty to disable Google OAuth login.
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# ─── Email via Resend (optional) ─────────────────────────────────────────────
# Leave RESEND_API_KEY empty to disable transactional email.
# Required for OTP login, password reset, and notification emails.
RESEND_API_KEY=
EMAIL_FROM=onboarding@resend.dev

# ─── LLM Integration (optional — not yet implemented) ────────────────────────
LLM_API_KEY=
LLM_MODEL=claude-sonnet-5

# ─── Embedding Model ─────────────────────────────────────────────────────────
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

### Task 7 — Update root `.env.example`

Changes:
1. Add `FRONTEND_URL` (currently missing)
2. Replace `GOOGLE_CLIENT_ID=123456789-abc123.apps.googleusercontent.com` with `GOOGLE_CLIENT_ID=` (the current value looks like a real but invalid ID, which is confusing)
3. Add `# Generate with: openssl rand -hex 32` comment next to `JWT_SECRET_KEY`
4. Add `# REQUIRED` / `# OPTIONAL` section comments

> [!CAUTION]
> The root `.env.example` will be inspected and minimally updated — it will not be replaced wholesale. Only the four changes listed above will be made.

---

## 6. Database Impact

**None.** WP3 is a configuration-only change.

- **Alembic revision after WP3:** `0008` (unchanged from WP2)
- **Original `campusgpt` database:** Untouched. Zero risk.
- **`campusgpt_test` database:** Not touched during WP3 — no migrations run, no test database connection made
- **Existing test safety guard** in `conftest.py` (enforces `TEST_DATABASE_URL` ends in `_test`): preserved, not modified

---

## 7. API Changes

| Endpoint | Development | Staging | Production | Change |
|----------|-------------|---------|------------|--------|
| `GET /docs` | 200 | 404 | 404 | Disabled outside dev |
| `GET /redoc` | 200 | 404 | 404 | Disabled outside dev |
| `GET /openapi.json` | 200 | 404 | 404 | Disabled outside dev |
| `GET /health` | `{"status":"ok"}` | `{"status":"ok"}` | `{"status":"ok"}` | `env` field removed |

No new endpoints. All authentication endpoints unchanged.

---

## 8. Testing Strategy

### New test file: `backend/tests/test_wp3_config.py`

No new pytest plugins or test dependencies required.

#### 8.1 Startup Guard Unit Tests — All Environments

Each test constructs `Settings(...)` with explicit values (bypassing `.env` file via `model_config` override or direct field injection) and asserts the expected outcome.

**JWT Secret Guards (G1–G3):**

| Test | ENV | JWT_SECRET_KEY | Expected |
|------|-----|----------------|----------|
| `test_g1_rejects_default_jwt_in_staging` | staging | `development-only-change-me` | `ValidationError` |
| `test_g1_rejects_default_jwt_in_production` | production | `development-only-change-me` | `ValidationError` |
| `test_g2_rejects_jwt_with_development_word` | production | `my-development-secret-xxxxxxxxxxxxxxxx` | `ValidationError` |
| `test_g3_rejects_short_jwt` | production | `short` | `ValidationError` |
| `test_g1g2g3_pass_valid_jwt` | production | 40-char secret, no "development" | No error |

**Database URL Guards (G4–G6):**

| Test | ENV | DATABASE_URL | Expected |
|------|-----|-------------|----------|
| `test_g4_rejects_sqlite_in_staging` | staging | `sqlite:///./test.db` | `ValidationError` |
| `test_g4_rejects_sqlite_in_production` | production | `sqlite:///./test.db` | `ValidationError` |
| `test_g5_rejects_bare_campusgpt_in_staging` | staging | `...@host:5432/campusgpt` | `ValidationError` |
| `test_g5_rejects_bare_campusgpt_in_production` | production | `...@host:5432/campusgpt` | `ValidationError` |
| `test_g5_rejects_campusgpt_uppercase_in_production` | production | `...@host:5432/CampusGPT` | `ValidationError` (normalized) |
| `test_g5_rejects_campusgpt_dev_in_staging` | staging | `...@host:5432/campusgpt_dev` | `ValidationError` |
| `test_g5_rejects_campusgpt_test_in_staging` | staging | `...@host:5432/campusgpt_test` | `ValidationError` |
| `test_g5_rejects_campusgpt_test_in_production` | production | `...@host:5432/campusgpt_test` | `ValidationError` |
| `test_g5_allows_campusgpt_staging_in_staging` | staging | `...@host:5432/campusgpt_staging` | No error |
| `test_g5_allows_campusgpt_prod_in_production` | production | `...@host:5432/campusgpt_prod` | No error |
| `test_g5_allows_custom_name_in_production` | production | `...@host:5432/myapp_production` | No error |
| `test_g6_rejects_localhost_db_in_production` | production | `...@localhost:5432/campusgpt_prod` | `ValidationError` |
| `test_g6_allows_localhost_db_in_staging` | staging | `...@localhost:5432/campusgpt_staging` | No error |

**CORS Guard (G7):**

| Test | ENV | CORS_ORIGINS | Expected |
|------|-----|-------------|----------|
| `test_g7_rejects_localhost_cors_in_staging` | staging | `http://localhost:5173` | `ValidationError` |
| `test_g7_rejects_localhost_cors_in_production` | production | `http://localhost:5173` | `ValidationError` |
| `test_g7_allows_production_cors` | production | `https://app.example.com` | No error |

**Google OAuth Guard (G8):**

| Test | ENV | GOOGLE_CLIENT_ID | GOOGLE_CLIENT_SECRET | Expected |
|------|-----|-----------------|---------------------|----------|
| `test_g8_rejects_client_id_only` | production | `abc` | `` | `ValidationError` |
| `test_g8_rejects_secret_only` | production | `` | `abc` | `ValidationError` |
| `test_g8_allows_both_set` | production | `abc` | `xyz` | No error |
| `test_g8_allows_both_empty` | production | `` | `` | No error |

**ENV Literal Validation:**

| Test | ENV value | Expected |
|------|----------|----------|
| `test_rejects_env_prod` | `prod` | `ValidationError` |
| `test_rejects_env_test` | `test` | `ValidationError` |
| `test_rejects_env_dev` | `dev` | `ValidationError` |
| `test_accepts_development` | `development` | No error |
| `test_accepts_staging` | `staging` | No error |
| `test_accepts_production` | `production` | No error |

**Combined and Development Tests:**

| Test | Scenario | Expected |
|------|----------|----------|
| `test_all_errors_collected_together` | Multiple guard violations at once | Single `ValidationError` listing all violations |
| `test_development_accepts_campusgpt_db` | `ENV=development`, `DATABASE_URL=...campusgpt` | No error |
| `test_development_accepts_sqlite_default` | `ENV=development`, `DATABASE_URL=sqlite:///./campusgpt.db` | No error |
| `test_development_accepts_localhost_cors` | `ENV=development`, `CORS_ORIGINS=http://localhost:5173` | No error |
| `test_valid_production_config_passes` | Full valid production config | No error |
| `test_valid_staging_config_passes` | Full valid staging config | No error |

#### 8.2 Docs Endpoint Tests

| Test | ENV | Endpoint | Expected |
|------|-----|----------|----------|
| `test_docs_accessible_in_development` | `development` | `GET /docs` | 200 |
| `test_docs_disabled_in_production` | `production` | `GET /docs` | 404 |
| `test_redoc_disabled_in_production` | `production` | `GET /redoc` | 404 |
| `test_openapi_disabled_in_production` | `production` | `GET /openapi.json` | 404 |
| `test_docs_disabled_in_staging` | `staging` | `GET /docs` | 404 |

#### 8.3 Health Endpoint Tests

| Test | Expected |
|------|----------|
| `test_health_returns_ok` | 200, body `{"status": "ok"}`, no `env` key present |

#### 8.4 Regression Suite

After all tasks, run the full existing suite without modification:

```bash
docker exec \
  -e PYTHONPATH=/app \
  -e TEST_DATABASE_URL=postgresql+psycopg2://campusgpt:campusgpt_dev@campusgpt_db:5432/campusgpt_test \
  campusgpt-backend-1 pytest -v /app/tests
```

Expected: all 31 existing tests pass. Zero regressions acceptable.

---

## 9. Acceptance Criteria

| # | Criterion | Verification method |
|---|-----------|-------------------|
| AC1 | G1–G8 startup guards reject all specified unsafe inputs | WP3 unit tests |
| AC2 | Reserved DB names `campusgpt`, `campusgpt_dev`, `campusgpt_test` rejected in staging+production | G5/G5b tests |
| AC3 | Comparison is exact and case-normalized, not substring-based | `test_g5_rejects_campusgpt_uppercase_in_production` |
| AC4 | All errors reported in one startup failure, not sequentially | `test_all_errors_collected_together` |
| AC5 | Development startup unchanged with standard `.env` | Existing 31 tests pass; dev server starts |
| AC6 | Staging allows localhost DB host, production rejects it | G6 tests |
| AC7 | `/docs`, `/redoc`, `/openapi.json` return 404 in staging+production | Docs endpoint tests |
| AC8 | `/health` returns `{"status": "ok"}` with no `env` field | `test_health_returns_ok` |
| AC9 | Docker Compose health check passes (HTTP 200 from `/health`) | `docker compose ps` → backend healthy |
| AC10 | No new Python packages introduced | No additions to `requirements.txt` |
| AC11 | No schema change, no new migration | `alembic check` → no drift |
| AC12 | `backend/.env.example` created with placeholders only, no real credentials | File review |
| AC13 | Root `.env.example` updated minimally (4 changes only) | Diff review |
| AC14 | SQLite compat branch removed from `session.py` | Code review |
| AC15 | Existing test safety guard in `conftest.py` unchanged | Code review |
| AC16 | Original `campusgpt` database untouched | Alembic revision still `0005`; row counts unchanged |
| AC17 | `backend/.env` not modified | `git status` confirms no changes |

---

## 10. Security Notes

### Risks Closed by WP3

| Risk | Guard(s) |
|------|---------|
| SQLite startup in staging/production | G4 |
| Known-weak JWT secret | G1, G2 |
| Short JWT secret | G3 |
| Development/test database in staging/production | G5, G5b |
| Development database (`campusgpt`) in staging/production | G5b |
| Localhost database in production | G6 |
| CORS allowing localhost in staging/production | G7 |
| Partial Google OAuth credential misconfiguration | G8 |
| ENV variable exposed in `/health` HTTP response | Task 5 |
| API schema (`/openapi.json`) exposed in staging/production | Task 4 |

### Risks Remaining (Out of Scope)

| Risk | Planned |
|------|---------|
| OAuth redirect with authorization code in URL | WP4 |
| Authentication rate limiting | WP5 |
| Refresh token rotation and revocation | WP6 |
| Centralized audit logging | WP11 |

### Secret Handling Commitments

- Passwords and credentials are never inspected, logged, or included in error messages
- `backend/.env.example` contains placeholders only — no real credentials
- Root `.env.example` changes will be audited before writing to ensure no credentials are present

---

## 11. Unresolved Items — Carried Forward

> [!WARNING]
> The following items are **not resolved by WP3**.

| ID | Item | Status |
|----|------|--------|
| **PD-06** | Existing account roles and institutional identities need confirmation | Unresolved |
| **WP4** | Google OAuth redirect-token exposure | Unresolved — planned WP4 |
| **WP5** | Authentication rate limiting | Unresolved — planned WP5 |
| **WP6** | Refresh token rotation, revocation, and logout | Unresolved — planned WP6 |
| **WP11** | Centralized audit logging | Unresolved — planned WP11 |

---

## 12. No New Dependencies

WP3 introduces **zero new Python packages**. All validation uses:

| Import | Source | Already in project? |
|--------|--------|-------------------|
| `typing.Literal` | Python stdlib | Yes (`typing` used throughout) |
| `urllib.parse.urlparse` | Python stdlib | Yes (used in `auth/router.py`) |
| `pydantic.model_validator` | pydantic 2.x | Yes (`pydantic==2.13.4`) |

`requirements.txt` is not modified.

---

## 13. Files Summary

### Create
- `backend/.env.example` — canonical backend environment template, placeholders only, all 16 variables documented

### Modify
- `backend/app/core/config.py` — `ENV` Literal, `model_validator` with G1–G8, `DATABASE_URL` default removed
- `backend/app/main.py` — conditional docs URLs, `env` field removed from `/health`
- `backend/app/database/session.py` — SQLite compat branch removed
- `.env.example` (root) — 4 targeted changes only: add `FRONTEND_URL`, fix Google placeholder, add key-generation comment, add section labels

### Not Touched
- All Alembic migration files `0001`–`0008` ✅
- All existing test files ✅
- `backend/tests/conftest.py` (test safety guard preserved) ✅
- `backend/app/auth/` ✅
- `frontend/` ✅
- `docker-compose.yml` ✅
- `backend/.env` (gitignored — never committed, never modified) ✅
- Original `campusgpt` database ✅

### Documentation to Update After Implementation
- `CampusGPT_Documentation/docs/foundation-stabilisation/WP3_Production_Configuration.md`
- `CampusGPT_Documentation/docs/foundation-stabilisation/Foundation_Regression_Checklist.md`
- `CampusGPT_Documentation/IMPLEMENTATION_STATUS.md`

---

## 14. Rollback Strategy

WP3 makes no database changes. Rollback is a simple Git revert:

```bash
git revert <WP3-commit-hash>
docker compose restart backend
```

No data recovery steps. No migration rollback. The backend restarts cleanly with the reverted code.

---

## 15. Open Questions Resolved

All open questions from Revisions 1 and 2 are now resolved:

| Question | Resolution |
|---------|-----------|
| Is removing `env` from `/health` acceptable? | ✅ Approved by owner |
| Should `campusgpt_dev` substring be used for DB validation? | ✅ Replaced with structural URL parsing |
| Is `campusgpt` (bare name) permitted in production? | ✅ **Rejected** in staging and production (G5b) |
| Should staging enforce the same guards as production? | ✅ Approved — G6 (localhost DB host) is the only production-only guard |
| Should `RESEND_API_KEY` be required in production? | ✅ No — optional integration, not guarded |

**No open questions remain. The plan is ready for implementation approval.**
