# ADR-013 — UI prototype as reference only

- **Status:** ACCEPTED
- **Implementation status:** Policy

## Context
A Google AI Studio prototype guides visuals.

## Decision
Prototype lives in `ui-reference/google-ai-studio/`, is never merged into `frontend/`, never supplies production data.

## Alternatives considered
- Adopt prototype code directly (rejected)

## Consequences
Re-implementation effort; cleaner codebase.

## Security implications
No mock data or unreviewed dependencies enter production.
