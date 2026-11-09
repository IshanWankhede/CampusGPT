# Database Backup and Migration Safety

**Status:** PROPOSED procedure; applies to every work package that adds a migration (WP1, WP2, WP4, WP5, WP6, WP11).

## 1. Non-negotiable rules

1. No destructive operation: no `DROP`, `TRUNCATE`, `DELETE` of user data, no `docker compose down -v`, no database reset.
2. Every migration is additive: new tables, new nullable columns, or columns with a server default. No column type changes, renames or drops without a separate written approval.
3. Existing migration files are never edited or re-numbered. New revisions are created after reading the real Alembic head; numbers in this package are illustrative.
4. Back up before any migration runs against a database that holds real data.
5. Review every migration by hand. Autogenerate output is a draft, never an instruction.
6. Production is **forward-only**. Downgrades are rehearsed in development only.

## 2. Backup procedure (PROPOSED)

1. Create a git tag at HEAD (for example `pre-foundation-baseline`).
2. Run a logical dump with `pg_dump` (custom format) into a directory that is outside the repository and git-ignored; restrict file permissions.
3. Record size and SHA-256 checksum.
4. **Restore rehearsal:** restore the dump into a scratch database and confirm row counts of `users` and `otp_verifications` match.
5. Keep the dump until Foundation acceptance is signed.

The dump contains emails and password hashes. Never commit it, attach it to a ticket or paste it into a prompt.

## 3. Read-only preflight queries (PROPOSED)

Run only `SELECT` statements. Mask emails in any report.

```sql
-- Alembic position
SELECT version_num FROM alembic_version;

-- Extensions present
SELECT extname FROM pg_extension ORDER BY 1;

-- Users by role and provider
SELECT role, auth_provider, count(*) FROM users GROUP BY 1,2 ORDER BY 1,2;

-- Accounts without a password hash (Google-created accounts)
SELECT count(*) FROM users WHERE hashed_password IS NULL;

-- Elevated accounts for manual review (PD-06)
SELECT id, email, role, college, auth_provider, is_email_verified, created_at
FROM users WHERE role <> 'STUDENT' ORDER BY created_at;

-- OTP row counts by purpose
SELECT purpose, is_used, count(*) FROM otp_verifications GROUP BY 1,2;
```

Column names are taken from the audit snapshot and are REQUIRES VERIFICATION on HEAD.

## 4. Migration review checklist

- [ ] Only `CREATE TABLE`, `ADD COLUMN` (nullable or defaulted), `CREATE INDEX`, `CREATE EXTENSION IF NOT EXISTS`.
- [ ] No data rewrite of existing rows.
- [ ] Enum creation uses a check-first pattern; downgrade is documented.
- [ ] Applied to a copy of real data first.
- [ ] `alembic heads` shows a single head afterwards.
- [ ] The autogenerate drift check is clean afterwards.
- [ ] Backup taken and restore-tested.

## 5. Order of operations for production

Backup → run the one-shot `migrate` service → verify (`alembic current`, smoke tests) → start the API. If migration fails, the API does not start; fix forward or restore the backup with owner approval.

## 6. Rollback verification (required before real data)
1. Restore the backup into a scratch database and run the new migration (`upgrade`) there.
2. Where the revision defines a `downgrade`, run it on the scratch copy and confirm the schema returns to the previous state with row counts unchanged; where it is a deliberate no-op (for example the pgvector extension) record that.
3. Record the exact backup restore command and its duration in the work-package report.
4. Production rollback means restoring the backup or fixing forward with owner approval — never an ad-hoc downgrade.
