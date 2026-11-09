# ADR-024 — WebSocket as the real-time communication approach

- **Status:** ACCEPTED (protocol parameters PD-18; scaling PD-25)
- **Implementation status:** Not implemented (P12; live attendance in P07)

## Context
Chat needs streamed responses, stop-generation and status events; live attendance needs push updates to the faculty roster. An earlier package draft treated SSE as the default, which contradicted the owner's direction.

## Decision
WebSocket is the single intended real-time transport for chat and live attendance (`docs/architecture/WebSocket_Protocol.md`): authenticated by a first message (no token in the URL), typed JSON events, stop generation, error events, reconnection with backoff, per-user limits, Nginx upgrade proxying, FastAPI WebSocket endpoints.

## Alternatives considered
- SSE as the primary transport (rejected: not the owner's direction; one-way only)
- Long polling (kept only as a fallback for notifications)
- Adding Redis for fan-out (rejected: prohibited)

## Consequences
Connections are per process; multi-worker fan-out for live attendance and notification pushes is an open decision (PD-25: single worker first, polling fallback, or PostgreSQL LISTEN/NOTIFY). No Redis.

## Security implications
Origin checks, authentication timeout, identity fixed per connection, ownership checks on every id, frame/rate limits, generic error messages, no tokens in URLs or logs.
