# ADR-003 — PostgreSQL as the only database

- **Status:** ACCEPTED
- **Implementation status:** Implemented

## Context
PostgreSQL already holds users and OTP data; vectors, relational data and full-text search can coexist.

## Decision
Use PostgreSQL for relational, full-text and vector data. No second datastore.

## Alternatives considered
- Separate vector database (rejected, see ADR-007)
- SQLite for tests (rejected: migrations are PostgreSQL-only)

## Consequences
Single operational surface; scaling limits are revisited only with evidence.

## Security implications
Row-level filtering in one query path.
