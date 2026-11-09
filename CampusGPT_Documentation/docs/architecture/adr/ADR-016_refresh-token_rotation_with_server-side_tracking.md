# ADR-016 — Refresh-token rotation with server-side tracking

- **Status:** ACCEPTED (lifetime PD-03; storage PD-04/PD-23 pending)
- **Implementation status:** Not implemented (WP6)

## Context
Stateless refresh tokens cannot be revoked.

## Decision
`refresh_tokens` table, rotation, family reuse detection with a short leeway, revocation on logout/reset/deactivation; 15-minute access tokens (provisional).

## Alternatives considered
- Stateless only (rejected)
- Token versioning only (insufficient for reuse detection)

## Consequences
Database writes on refresh.

## Security implications
Limits stolen-token impact; `localStorage` XSS exposure remains until cookies are adopted.
