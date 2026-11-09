# ADR-008 — No Redis

- **Status:** ACCEPTED
- **Implementation status:** Policy

## Context
Original master prompt excludes Redis; rate limiting, job queues and caching can use PostgreSQL at this scale.

## Decision
Do not introduce Redis. Rate limiting uses `auth_attempts`; jobs use `SKIP LOCKED` rows.

## Alternatives considered
- Redis for limits and queues (rejected)
- In-memory rate limiting (rejected: lost on restart, per-process)

## Consequences
Slightly higher DB load; revisit with measurements and a new ADR. WebSocket support (ADR-024) must work without Redis; any fan-out need is handled under PD-25.

## Security implications
Fewer components to secure.
