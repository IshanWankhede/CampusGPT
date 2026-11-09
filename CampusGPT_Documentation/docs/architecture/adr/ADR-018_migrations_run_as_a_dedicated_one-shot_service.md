# ADR-018 — Migrations run as a dedicated one-shot service

- **Status:** ACCEPTED
- **Implementation status:** Not implemented (WP8)

## Context
API start currently runs migrations.

## Decision
`migrate` service runs before the API; production runs it explicitly after a backup; API never migrates.

## Alternatives considered
- Keep auto-migrate (rejected: races, crash loops, unreviewed prod changes)

## Consequences
One more Compose service.

## Security implications
Prevents unreviewed schema change at deploy time.
