# ADR-022 — Multi-college data isolation strategy

- **Status:** PENDING APPROVAL (PD-07)
- **Implementation status:** Pending

## Context
Multi-college login exists; no tenant model or isolation design exists.

## Decision
Undecided. Options: attribute-only; `institution_id` on academic tables; drop multi-college. Until decided, new tables must allow adding an institution key additively.

## Alternatives considered
- See options

## Consequences
Decision affects every academic table.

## Security implications
Wrong isolation could leak records across institutions.
