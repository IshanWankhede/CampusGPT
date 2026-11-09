# ADR-001 — Use JavaScript/JSX instead of TypeScript

- **Status:** ACCEPTED
- **Implementation status:** Existing; enforced by policy

## Context
The existing frontend is JavaScript/JSX (audit: no .ts/.tsx/tsconfig); the original master prompt forbids TypeScript.

## Decision
The production frontend stays JavaScript/JSX. Prototype output in TypeScript is re-implemented, not adopted.

## Alternatives considered
- Migrate to TypeScript (rejected: not requested, large rewrite)

## Consequences
Fewer compile-time guarantees; mitigated by lint, tests and Pydantic-validated APIs.

## Security implications
None directly; type confusion bugs are caught by tests.
