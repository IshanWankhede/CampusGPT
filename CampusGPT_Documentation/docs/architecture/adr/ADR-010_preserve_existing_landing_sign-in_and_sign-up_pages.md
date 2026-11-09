# ADR-010 — Preserve existing landing, sign-in and sign-up pages

- **Status:** ACCEPTED
- **Implementation status:** Implemented

## Context
These pages are complete and approved by the owner.

## Decision
Do not redesign or replace them; only logic wiring in `AuthContext` changes (WP4, WP7). Folder and unused-file cleanup waits for verification.

## Alternatives considered
- Restyle to the new palette (deferred, PD-16)

## Consequences
Visual seam between auth pages and app until PD-16.

## Security implications
No UI regression risk to sign-in.
