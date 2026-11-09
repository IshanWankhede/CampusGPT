# WP11 — Logging, Monitoring and Audit Foundation

**Stage 0 foundation work package.** Position in the mandatory order: Step 16 (see `Foundation_Execution_Order.md`).
**Implementation status:** IMPLEMENTED — 161/161 backend tests passing; `alembic check` zero drift; `ruff check` clean.

## Objective
Add structured logging, request correlation IDs, redaction of sensitive data and a persistent audit trail for authentication and administrative actions.

## Implementation summary

All deliverables implemented and tested. No monitoring product introduced; alert candidates documented below.

### New files

| File | Description |
|------|-------------|
| `backend/app/core/logging.py` | `JSONLogFormatter`, `RedactionFilter`, `request_id_var` ContextVar, `configure_logging()` |
| `backend/app/core/middleware.py` | `CorrelationIdMiddleware` — accepts valid `X-Request-ID` (8–64 alphanumeric/hyphen), generates UUID4 if missing or invalid, binds to `request_id_var`, emits in response header |
| `backend/app/models/audit_log.py` | `AuditLog` SQLAlchemy model — `audit_logs` table (append-only) |
| `backend/app/audit/__init__.py` | Re-exports `record_audit_event` |
| `backend/app/audit/service.py` | `record_audit_event()` with explicit `ALLOWED_METADATA_KEYS` allowlist; independent session for failed-auth persistence; IP hashing via `rate_limiter.get_client_ip`/`hash_ip` |
| `backend/alembic/versions/0012_create_audit_logs_table.py` | Additive migration `0011 → 0012`; JSONB on PostgreSQL, JSON fallback |
| `backend/tests/test_logging_and_audit_wp11.py` | 10 WP11 tests (all passing) |

### Modified files

| File | Change |
|------|--------|
| `backend/app/main.py` | `configure_logging()` on startup; `CorrelationIdMiddleware` added before CORS |
| `backend/app/models/__init__.py` | `AuditLog` import and `__all__` entry |
| `backend/app/auth/router.py` | `record_audit_event()` calls for all auth events; `register` accepts `Request` parameter |
| `backend/app/auth/service.py` | `TOKEN_REUSE_DETECTED` audit event in `rotate_refresh_token()` |
| `backend/app/admin/router.py` | `ROLE_REQUEST_APPROVED` and `ROLE_REQUEST_REJECTED` audit events |
| `backend/tests/conftest.py` | `audit_logs` added to `TRUNCATE TABLE` in `clean_database` fixture |
| `backend/tests/test_database_wp1.py` | Assertion for `audit_logs` in `Base.metadata.tables` with column validation |
| `backend/tests/test_migration_dag.py` | Expected head updated from `0011` → `0012`; `expected_revisions` list updated |

## Audit events instrumented

| Action constant | Trigger |
|---|---|
| `AUTH_LOGIN` (success / failure) | Password login endpoint |
| `AUTH_REGISTER` | Registration endpoint |
| `ROLE_REQUEST_CREATED` | Faculty registration path |
| `OTP_SENT` | Send-OTP endpoint |
| `OTP_VERIFIED` (success / failure) | Verify-OTP endpoint |
| `PASSWORD_RESET` | Password reset endpoint |
| `TOKEN_REFRESH` | Refresh-token endpoint |
| `TOKEN_REUSE_DETECTED` | Malicious reuse branch in `rotate_refresh_token()` |
| `AUTH_LOGOUT` | Single-session logout |
| `AUTH_LOGOUT_ALL` | All-sessions logout |
| `ROLE_REQUEST_APPROVED` | Admin approval endpoint |
| `ROLE_REQUEST_REJECTED` | Admin rejection endpoint |

## Redaction policy

The following values are **never** logged in any form:

- Passwords (all fields matching `password`, `passwd`, `pwd`)
- OTP codes
- Raw tokens (access, refresh, id tokens)
- Cookies and `Authorization` headers
- Google OAuth one-time codes

Redaction is applied at two layers:
1. **`RedactionFilter`** — strips sensitive keys from dict/list/tuple log arguments before the record is emitted.
2. **`JSONLogFormatter`** — applies `SENSITIVE_VALUE_PATTERN` regex to the fully-rendered message string as a final backstop.

## Security properties

- `audit_logs` is **append-only** at application level; no update or delete endpoints exist or will be added.
- `actor_id` is a nullable foreign key with `ON DELETE SET NULL` — audit history is preserved when a user is deleted.
- Failed authentication events are persisted even when the main authentication transaction is rolled back (independent session).
- Metadata is filtered through an explicit `ALLOWED_METADATA_KEYS` allowlist before persistence.
- Raw IP addresses are never stored; only the salted SHA-256 hash via the existing `hash_ip` utility.
- Incoming `X-Request-ID` values are validated (8–64 chars, alphanumeric + hyphen); invalid or missing values generate a fresh UUID4.

## Database impact

| Migration | Revision | Description |
|---|---|---|
| 0012 | `0011 → 0012` | Additive — creates `audit_logs` table with 4 indexes |

`alembic check` confirmed zero drift after migration.
`campusgpt` (production) database remains at revision `0005` — untouched.

## Monitoring signals and alert candidates

No external monitoring product is introduced. The following structured log fields and audit actions are recommended as alert candidates when a monitoring stack is added:

| Signal | Recommended threshold | Log field / action |
|---|---|---|
| Login failure surge | > 10 failures / 15 min from same `ip_hash` | `action = AUTH_LOGIN`, `outcome = failure` |
| Token reuse detection | Any occurrence | `action = TOKEN_REUSE_DETECTED` |
| OTP brute-force attempt | > 5 OTP failures for same target email | `action = OTP_VERIFIED`, `outcome = failure` |
| Backend 5xx error rate | > 1 % of requests over 5 min | HTTP response status in structured access log |
| Account lockout | Any occurrence | `action = AUTH_LOGIN`, `outcome = locked` |
| Admin role changes | Any approval or rejection | `action = ROLE_REQUEST_APPROVED` / `ROLE_REQUEST_REJECTED` |

Log fields available on every structured entry: `timestamp`, `level`, `logger`, `message`, `request_id`, `module`, `funcName`, `lineno`.

## Testing

| Category | Tests | Result |
|---|---|---|
| Secret redaction (dict + string) | 2 | ✅ passed |
| JSON formatter + filter | 1 | ✅ passed |
| Correlation ID: generated when missing | 1 | ✅ passed |
| Correlation ID: propagated when valid | 1 | ✅ passed |
| Correlation ID: replaced when malformed | 1 | ✅ passed |
| Metadata allowlist filtering | 1 | ✅ passed |
| Login success/failure audit persistence | 1 | ✅ passed |
| OTP failure audit | 1 | ✅ passed |
| Role-request approval audit | 1 | ✅ passed |
| Logout audit | 1 | ✅ passed |
| **Total WP11 tests** | **10** | **✅ all passed** |
| **Full regression suite** | **161** | **✅ all passed** |

## Acceptance criteria — verification

| Criterion | Status |
|---|---|
| No sensitive value appears in logs in any test | ✅ Verified — redaction tests pass |
| Role approvals are auditable end to end | ✅ Verified — `test_role_request_approval_audit` passes |
| Correlation ID appears in response header and logs | ✅ Verified — `test_request_id_propagated_when_valid` passes |
| Each listed event produces exactly one audit row | ✅ Verified — event-specific tests each assert `count == 1` |
| `alembic check` returns zero drift | ✅ Verified |
| `ruff check app tests` passes clean | ✅ Verified |
| Frontend ESLint and production build pass | ✅ Verified |
| `campusgpt` DB untouched at revision `0005` | ✅ Confirmed |

## Rollback considerations

To rollback: revert code changes in `main.py`, `auth/router.py`, `auth/service.py`, `admin/router.py`. The `audit_logs` table can remain (downgrade via `alembic downgrade 0011` only if safe and after verifying the migration is reversible).

## Human approval checkpoint

Owner reviews a sample of redacted logs and audit rows before signing off in `Foundation_Acceptance_Checklist.md`.

The next work package (Foundation Acceptance Checklist sign-off, WP0–WP11) must not start until this checkpoint is complete.
