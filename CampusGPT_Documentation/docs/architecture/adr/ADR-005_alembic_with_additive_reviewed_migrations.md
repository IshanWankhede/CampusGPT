# ADR-005 — Alembic with additive, reviewed migrations

- **Status:** ACCEPTED
- **Implementation status:** Partially implemented (WP1 pending)

## Context
Five migrations exist; env.py does not register models; auto-run at start is risky.

## Decision
All schema changes are additive Alembic revisions created after reading the real head, hand-reviewed, backed up, forward-only in production.

## Alternatives considered
- Autogenerate and apply blindly (rejected)
- Edit old migrations (rejected)

## Consequences
Slower but safe; requires WP1 fixes first.

## Security implications
Protects existing data from destructive changes.
