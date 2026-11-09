# ADR-020 — Separate development and production Docker layers

- **Status:** ACCEPTED
- **Implementation status:** Not implemented (WP8)

## Context
One dev-oriented Compose file with hardcoded credentials and exposed ports.

## Decision
Base + override (dev) + production layers; fail-fast required variables; non-root; no DB port in production; Nginx front.

## Alternatives considered
- Single file with conditionals (rejected)

## Consequences
More files to maintain.

## Security implications
Smaller attack surface, no default secrets.
