# ADR-014 — Separate prototype, development and production data

- **Status:** ACCEPTED
- **Implementation status:** Not implemented

## Context
Original master prompt defines three data environments.

## Decision
Seed scripts are dev/test only, idempotent, marked demo, guarded by `ENV`; production is never seeded.

## Alternatives considered
- One shared fixture set (rejected)

## Consequences
Separate maintenance.

## Security implications
Prevents demo accounts or data reaching production.
