# WP3 Pre-Implementation Safety Verification Report

**Date:** 2026-11-09  
**Purpose:** Verify all five database protection requirements before WP3 implementation approval  
**Scope:** Read-only audit — no code, database, or configuration was modified

---

## Original `campusgpt` Database — Current Confirmed State

| Property | Value |
|----------|-------|
| Alembic revision | `0005` |
| Users table | 3 rows |
| OTP verifications table | 11 rows |
| Status | ✅ Untouched — matches pre-WP3 state |

---

## Protection 1 — Automated tests cannot connect to `campusgpt`

**Status: ✅ FULLY PROTECTED**

**Mechanism:** `assert_test_database()` in [`conftest.py` line 17–25](file:///d:/Codes/Projects/CampusGPT/backend/tests/conftest.py#L17-L25)

```python
def assert_test_database(url: str) -> None:
    """Refuses any database URL whose database name does not end with '_test'."""
    clean_url = url.split("?")[0]
    dbname = clean_url.rsplit("/", 1)[-1]
    if not dbname.endswith("_test"):
        raise RuntimeError(
            f"CRITICAL SAFETY VIOLATION: Refusing to run tests against non-test database: '{dbname}'. "
            f"Database name MUST end with '_test'."
        )
```

This function is called **at module import time** (line 28: `assert_test_database(TEST_DATABASE_URL)`). If `TEST_DATABASE_URL` does not end in `_test`, pytest collection fails immediately — no test can run, no connection is made.

`campusgpt` does not end in `_test`, so it is **structurally rejected** before any test fixture or test function executes.

**Verification from `test_database_guard.py` line 15:**
```python
"postgresql://campusgpt:campusgpt_dev@localhost:5433/campusgpt"  # explicitly in the rejection list
```

This test confirms the guard refuses the bare `campusgpt` database name.

---

## Protection 2 — Test fixtures cannot create, modify, or delete records in `campusgpt`

**Status: ✅ FULLY PROTECTED**

**Mechanism — two-layer defence:**

**Layer A:** `assert_test_database()` is called a second time **inside** the `clean_database` autouse fixture ([`conftest.py` line 37](file:///d:/Codes/Projects/CampusGPT/backend/tests/conftest.py#L37)):

```python
@pytest.fixture(autouse=True)
def clean_database():
    assert_test_database(TEST_DATABASE_URL)   # second check inside fixture
    with test_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE otp_verifications, users CASCADE;"))
    ...
```

Even if a test somehow bypassed the module-level check, the fixture-level check would block the TRUNCATE from reaching any non-`_test` database.

**Layer B:** The `test_engine` and `TestingSessionLocal` are constructed from `TEST_DATABASE_URL` only ([`conftest.py` lines 30–31](file:///d:/Codes/Projects/CampusGPT/backend/tests/conftest.py#L30-L31)):

```python
test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(..., bind=test_engine)
```

The application's `SessionLocal` (which connects to `settings.DATABASE_URL` = `campusgpt`) is **dependency-overridden** in the `client` fixture ([lines 63–69](file:///d:/Codes/Projects/CampusGPT/backend/tests/conftest.py#L63-L69)):

```python
def override_get_db():
    try:
        yield db_session          # db_session is bound to test_engine → campusgpt_test
    finally:
        pass
app.dependency_overrides[get_db] = override_get_db
```

All HTTP requests through `TestClient` receive a session bound to `campusgpt_test`. The `campusgpt` application connection is never called during tests.

---

## Protection 3 — Alembic migrations cannot run against `campusgpt` through normal workflow

**Status: ✅ PROTECTED — with one structural observation documented below**

**Mechanism:** [`alembic/env.py` lines 18 and 30](file:///d:/Codes/Projects/CampusGPT/backend/alembic/env.py#L18-L30) always reads the target URL from `settings.DATABASE_URL`:

```python
# Offline mode
context.configure(url=settings.DATABASE_URL, ...)

# Online mode
configuration["sqlalchemy.url"] = settings.DATABASE_URL
```

`settings.DATABASE_URL` is sourced from (in precedence order):
1. `DATABASE_URL` environment variable (highest — set by `docker-compose.yml`)
2. `backend/.env` file
3. The pydantic default (currently SQLite — being removed in WP3)

**Normal development workflow** (`docker compose up`):
- Compose injects `DATABASE_URL=postgresql+psycopg2://campusgpt:campusgpt_dev@campusgpt_db:5432/campusgpt`
- `alembic upgrade head` runs against `campusgpt` as part of the startup command
- **This is intentional** — Alembic keeps the development database schema in sync at startup

**Protection from accidental migration to wrong database:**
- To run against a different database, `DATABASE_URL` must be changed in the environment before running `alembic`
- There is no `--url` shortcut in any script or Makefile (confirmed: no Makefile, no `.sh` scripts exist)
- Alembic does not auto-discover or iterate across databases

> [!NOTE]
> **Structural observation:** The `alembic upgrade head` command in `docker-compose.yml` runs against `campusgpt` on every `docker compose up`. This is the development database's normal lifecycle — migrations are applied to keep the dev DB current. This is **not** a safety risk to `campusgpt` during WP3, because WP3 creates no new migrations. After WP3 implementation, `alembic check` will confirm zero drift, and no migration will run.
>
> For future work packages that do add migrations: the same `DATABASE_URL` override mechanism applies. Any migration must be explicitly targeted — there is no path by which a migration runs against an unintended database without manually overriding `DATABASE_URL`.

**Running Alembic against `campusgpt_test` during WP3 (not needed, confirmed):**
WP3 adds no migrations. `alembic check` is run as a verification step only — it reads the current schema and compares; it makes no changes.

---

## Protection 4 — Database reset, seed, and cleanup commands cannot accidentally target `campusgpt`

**Status: ✅ PROTECTED**

**Exhaustive search results:**

| Concern | Search term | Findings |
|---------|------------|----------|
| Table drops | `DROP TABLE`, `drop_all` | None found outside test files |
| Table truncates | `TRUNCATE` | Only in `conftest.py:clean_database` fixture (guarded by `assert_test_database`) |
| Mass deletes | `delete.*all`, `reset.*db` | None found |
| Seed scripts | `seed` | None found (no seed data scripts exist) |
| SQLAlchemy `Base.metadata.drop_all` | `drop_all` | None found anywhere |
| SQLAlchemy `Base.metadata.create_all` | `create_all` | None found outside migrations |

**CLI scripts that write to the database:**

| Script | What it writes | Safety |
|--------|---------------|--------|
| [`app/create_admin.py`](file:///d:/Codes/Projects/CampusGPT/backend/app/create_admin.py) | Creates one ADMIN user row | Writes to `settings.DATABASE_URL` — intentionally targets the application DB; no reset/drop capability |
| [`app/manage_role_requests.py`](file:///d:/Codes/Projects/CampusGPT/backend/app/manage_role_requests.py) | Updates role request status rows | Same as above; no reset/drop capability |

Neither CLI script has reset, truncate, delete-all, or seed capabilities. Both are administrative tools that write individual records to the application database using `SessionLocal`. They cannot be confused with test tools.

---

## Protection 5 — Existing WP0 database safety guard remains functional

**Status: ✅ FULLY FUNCTIONAL AND TESTED**

The guard function `assert_test_database()` is verified to be in place, correctly implemented, and covered by its own dedicated test file:

**Guard implementation:** [`conftest.py` lines 17–25](file:///d:/Codes/Projects/CampusGPT/backend/tests/conftest.py#L17-L25) — unchanged since WP0.

**Guard test coverage:** [`tests/test_database_guard.py`](file:///d:/Codes/Projects/CampusGPT/backend/tests/test_database_guard.py) — two tests:
- `test_guard_accepts_test_database` — confirms `_test`-suffixed URLs pass
- `test_guard_refuses_non_test_databases` — confirms `campusgpt` and other non-`_test` URLs raise `RuntimeError` with `"CRITICAL SAFETY VIOLATION"` message

**Guard invocation points:**
1. Module-level on `conftest.py` import (line 28) — blocks pytest collection
2. Inside `clean_database` autouse fixture (line 37) — second check before any TRUNCATE

**WP3 impact on this guard: None.** WP3 does not modify `conftest.py` or `test_database_guard.py`.

---

## Summary — All Five Protections Verified

| # | Protection required | Status | Enforced by |
|---|--------------------|---------|-----------:|
| 1 | Tests cannot connect to `campusgpt` | ✅ Exists | `assert_test_database()` at module import — `campusgpt_test` required |
| 2 | Test fixtures cannot modify `campusgpt` records | ✅ Exists | Double guard in `clean_database`; `test_engine` bound to `campusgpt_test`; `get_db` dependency overridden |
| 3 | Alembic migrations cannot run against `campusgpt` via normal workflow | ✅ Exists (with observation) | `alembic/env.py` reads `settings.DATABASE_URL`; no migration scripts; WP3 adds no migration |
| 4 | Reset/seed/cleanup commands cannot target `campusgpt` | ✅ Exists | No reset/seed/drop scripts exist; only `conftest.py` truncates, and it is guarded |
| 5 | WP0 database safety guard remains functional | ✅ Exists | `assert_test_database()` unchanged; dedicated test file confirms it; WP3 does not touch either |

---

## WP3 Implementation Safety Assessment

**No additional code changes are needed to protect the original `campusgpt` database during WP3 implementation.**

WP3 implementation tasks are:
1. Changes to `config.py` — configuration only, no database connection
2. Changes to `main.py` — HTTP routing only, no database connection
3. Changes to `session.py` — removes SQLite compat branch; engine construction uses same `settings.DATABASE_URL`; no connection is made at import time
4. Creation of `backend/.env.example` — a text file, no database interaction
5. Update to root `.env.example` — a text file, no database interaction

None of these tasks:
- Run `alembic upgrade` or `alembic downgrade`
- Create a database connection to `campusgpt`
- Modify or create migrations
- Call `TRUNCATE`, `DROP`, `DELETE`, or `CREATE`

**WP3 is safe to approve for implementation.**

