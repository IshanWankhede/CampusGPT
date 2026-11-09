# ADR-009 — Preserve and incrementally harden the existing authentication

- **Status:** ACCEPTED
- **Implementation status:** Implemented but defective

## Context
JWT, Google OAuth and email OTP exist and work, with defects.

## Decision
Keep the system; fix defects (WP2–WP7); no second auth system or user table.

## Alternatives considered
- Replace with a third-party auth service (rejected for now)
- Rewrite (rejected)

## Consequences
Must carefully fix without breaking users.

## Security implications
Defects C1–C3 and H1–H4 are closed in Stage 0.
