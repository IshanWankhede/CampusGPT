# Baseline, Backup, and Preflight Report (WP0)

**Date:** 2026-11-09  
**Stage:** Stage 0 — Foundation Stabilisation (Work Package 0)  
**Git Baseline Tag:** `pre-foundation-baseline`  
**Git HEAD Commit:** `0ede917` (incorporating repository audit baseline)  
**Auditor:** Google Antigravity Agent  

---

## 1. Executive Summary

Work Package 0 (WP0) establishes the verified, recoverable starting baseline before any code, schema, or configuration modifications occur. A logical PostgreSQL backup was taken and successfully restore-tested against an isolated scratch database. Read-only preflight queries were executed against the live development database, establishing exact user and OTP row counts, extension statuses, and verifying elevated accounts. A minimal test harness with a strict database-name safety guard was created, and characterization tests were executed against an isolated `campusgpt_test` database, validating current system behavior and capturing known defects **C1**, **C2**, and **C3** as strict `xfail` items.

---

## 2. Git Baseline and Repository State

* **Git Tag:** `pre-foundation-baseline` created at commit `0ede917`.
* **Working Tree:** Clean (excluding newly added test harness and reports).
* **Application Code:** **Zero lines** of existing backend or frontend production code modified.

---

## 3. Database Backup & Restore Rehearsal

A full logical database dump was generated using `pg_dump` custom archive format (`-Fc`) and moved to an isolated, secure directory outside the repository.

* **Backup Storage Location:** `C:\Users\ishan\.gemini\antigravity\brain\eef70785-59f6-4126-a7c6-578fd3683934\scratch\backups\campusgpt_backup_20261109.dump`
* **File Size:** `8,990 bytes`
* **SHA-256 Checksum:** `9C665DB606C6018934512DA833A28642924F0C3976D725C83D66E5083C17497C`
* **Restore Rehearsal Execution:**
  1. Scratch database `campusgpt_scratch_restore` created via PostgreSQL container `campusgpt-campusgpt_db-1`.
  2. Backup restored via `pg_restore -U campusgpt -d campusgpt_scratch_restore`.
  3. Row counts and schema state verified:
     * `users`: 3 rows (matches live `campusgpt`)
     * `otp_verifications`: 11 rows (matches live `campusgpt`)
     * `alembic_version`: `0005` (matches live `campusgpt`)
  4. Scratch database `campusgpt_scratch_restore` dropped cleanly.

---

## 4. Live Database Preflight Findings

### 4.1 Schema Position and Extensions
* **Alembic Version:** `0005` (linear head: `0001` -> `0002_add_email_verification` -> `0003` -> `0004` -> `0005`).
* **Installed Extensions:** `plpgsql` (PostgreSQL 16.15).
* **Vector Extension Status:** The `vector` extension is **not present** in the database.

### 4.2 User Accounts Summary
* **Total Users:** 3
* **Users by Role & Auth Provider:**
  * `ADMIN` (LOCAL): 1
  * `STUDENT` (LOCAL): 2
  * `FACULTY`: 0
* **Users with Null Password Hash:** 0 (no Google OAuth accounts currently registered in database).

### 4.3 Elevated Accounts Review (PD-06)
Only one elevated account exists on the live database:

| Account ID | Masked Email | Role | College | Auth Provider | Verified | Created At (UTC) |
|---|---|---|---|---|---|---|
| `e4c8a854-68d0-479d-907d-e9cfcc184647` | `a***n@campusgpt.dev` | `ADMIN` | None | `LOCAL` | `true` | `2026-10-02 17:56:30` |

* **Observation:** Created via `create_admin.py` CLI during initial system bootstrap. No rogue admin or faculty accounts exist.

### 4.4 OTP Verifications Summary
* **Total Records:** 11
* **Breakdown by Purpose and Status:**
  * `EMAIL_VERIFY` (`is_used = true`): 4
  * `EMAIL_VERIFY` (`is_used = false`): 6
  * `PASSWORD_RESET` (`is_used = false`): 1

---

## 5. Development Environment Startup Verification

* **Backend API (`campusgpt-backend-1`):**
  * Health endpoint `http://localhost:8000/health` returns HTTP 200 OK:
    ```json
    {"status": "ok", "env": "development"}
    ```
* **Frontend Dev Server (`campusgpt-frontend-1`):**
  * `http://localhost:5173/` returns HTTP 200 OK.
  * `http://localhost:5173/auth` returns HTTP 200 OK.
  * Landing page and authentication flow load successfully.

---

## 6. Test Infrastructure and Characterization Suite

### 6.1 Test Harness Configuration
* **Dependencies:** Defined in [`backend/requirements-dev.txt`](file:///d:/Codes/Projects/CampusGPT/backend/requirements-dev.txt) (`pytest>=8.3.0`, `pytest-asyncio>=0.24.0`, `pytest-cov>=6.0.0`, `httpx>=0.28.0`).
* **Isolated Test Database:** Dedicated PostgreSQL database `campusgpt_test` created and migrated to revision `0005`.
* **Database Safety Guard:** Implemented in [`backend/tests/conftest.py`](file:///d:/Codes/Projects/CampusGPT/backend/tests/conftest.py) (`assert_test_database`).
  * Any database URL not ending with `_test` raises `RuntimeError` before executing any query or truncate.
  * Tested explicitly in [`backend/tests/test_database_guard.py`](file:///d:/Codes/Projects/CampusGPT/backend/tests/test_database_guard.py).
* **Test Isolation:** Automatic pre- and post-test table truncate ensures clean test runs.
* **External Calls:** Email delivery (`app.core.email.send_email`) and Google OAuth HTTP requests are strictly mocked with fakes.

### 6.2 Characterization Test Results
Executed inside `campusgpt-backend-1` via:
```bash
docker exec -e PYTHONPATH=/app -e TEST_DATABASE_URL=postgresql+psycopg2://campusgpt:campusgpt_dev@campusgpt_db:5432/campusgpt_test campusgpt-backend-1 pytest -v /app/tests
```

**Real Command Output:**
```
============================= test session starts ==============================
platform linux -- Python 3.11.17, pytest-9.2.0, pluggy-1.7.0 -- /usr/local/bin/python3.11
rootdir: /app
plugins: cov-7.1.0, asyncio-1.4.1.post1, anyio-4.14.2
collecting ... collected 10 items

tests/test_characterization.py::test_health_endpoint PASSED              [ 10%]
tests/test_characterization.py::test_register_verify_login_happy_path PASSED [ 20%]
tests/test_characterization.py::test_me_and_refresh_endpoints PASSED     [ 30%]
tests/test_characterization.py::test_forgot_and_reset_password PASSED    [ 40%]
tests/test_characterization.py::test_google_oauth_callback_new_and_existing_user PASSED [ 50%]
tests/test_characterization.py::test_c1_google_user_null_password_bypass XFAIL [ 60%]
tests/test_characterization.py::test_c2_five_failed_otp_verification_bypass XFAIL [ 70%]
tests/test_characterization.py::test_c3_role_escalation_on_public_register XFAIL [ 80%]
tests/test_database_guard.py::test_guard_accepts_test_database PASSED    [ 90%]
tests/test_database_guard.py::test_guard_refuses_non_test_databases PASSED [100%]

================== 7 passed, 3 xfailed, 3 warnings in 14.96s ===================
```

### 6.3 Known Defects Captured as Strict XFAIL
1. **Defect C1 (`test_c1_google_user_null_password_bypass`):** Captures password authentication bypass on accounts created via Google OAuth.
2. **Defect C2 (`test_c2_five_failed_otp_verification_bypass`):** Captures 5 failed OTP attempts marking `is_used=True`, allowing unauthorized registration.
3. **Defect C3 (`test_c3_role_escalation_on_public_register`):** Captures client-supplied `ADMIN` role assignment on public `/register`.

---

## 7. Divergences from Initial Audit Hypothesis

1. **Active Users in Dev Database:** The live development database contains 3 real user rows (1 Admin, 2 Students) and 11 OTP verification records, rather than being completely empty.
2. **No Google Users in Database:** All 3 existing users are `LOCAL` accounts; no users currently have `auth_provider = GOOGLE`.
3. **Absence of pgvector Extension:** Confirmed that `pgvector` has never been initialized in PostgreSQL (`CREATE EXTENSION vector` has not been run), confirming the necessity of WP1.

---

## 8. Approval Checkpoint (WP0 -> WP1)

* [x] Baseline git tag created (`pre-foundation-baseline`).
* [x] Backup created, checksummed, and restore rehearsal verified.
* [x] Elevated accounts audited (`admin@campusgpt.dev` only).
* [x] Characterization suite green with 3 strict xfails.
* [ ] **Owner Approval:** Owner to review elevated account list, confirm backup, and approve proceeding to **WP1 (Alembic Model Registration & pgvector Extension)**.

