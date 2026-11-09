# ADR-012 — Lucide React for new application icons

- **Status:** ACCEPTED
- **Implementation status:** Not implemented (P04)

## Context
Existing pages use react-icons and a Font Awesome CDN; new UI needs a consistent set.

## Decision
Add Lucide React in P04 for new UI only; do not rewrite existing pages.

## Alternatives considered
- react-icons everywhere (rejected for new UI)

## Consequences
Two icon libraries coexist until old pages change.

## Security implications
Removing the CDN dependency later reduces third-party script risk.
