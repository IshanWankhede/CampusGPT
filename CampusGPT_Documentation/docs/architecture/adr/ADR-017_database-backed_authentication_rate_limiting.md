# ADR-017 — Database-backed authentication rate limiting

- **Status:** ACCEPTED (thresholds provisional)
- **Implementation status:** Not implemented (WP5)

## Context
No limits exist; Redis is excluded.

## Decision
`auth_attempts` with hashed identifiers; account and IP limits; proxy headers trusted only from configured proxies.

## Alternatives considered
- slowapi in-memory (rejected)
- Reverse-proxy-only limits (complement, not replacement)

## Consequences
Table growth requires pruning.

## Security implications
Mitigates brute force and OTP abuse.
