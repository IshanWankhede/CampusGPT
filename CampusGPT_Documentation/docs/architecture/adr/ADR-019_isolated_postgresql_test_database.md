# ADR-019 — Isolated PostgreSQL test database

- **Status:** ACCEPTED (exact name PD-05)
- **Implementation status:** Not implemented (WP0, WP9)

## Context
No tests exist; destructive test setup is dangerous.

## Decision
Tests use PostgreSQL database named `*_test`; the harness refuses other names; no SQLite.

## Alternatives considered
- SQLite (rejected)
- Shared dev DB (rejected)

## Consequences
Needs a Postgres service in CI.

## Security implications
Prevents tests from touching development or production data.
