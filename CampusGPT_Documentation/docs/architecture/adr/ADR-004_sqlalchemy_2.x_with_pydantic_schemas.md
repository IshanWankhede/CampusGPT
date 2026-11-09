# ADR-004 — SQLAlchemy 2.x with Pydantic schemas

- **Status:** ACCEPTED
- **Implementation status:** Implemented

## Context
Existing models and repositories use SQLAlchemy 2.x and Pydantic v2.

## Decision
Keep SQLAlchemy 2.x style models and Pydantic request/response schemas, separate per use-case.

## Alternatives considered
- Raw SQL everywhere (rejected)
- Another ORM (rejected)

## Consequences
Consistency; legacy `declarative_base()` usage is acceptable.

## Security implications
Separate schemas prevent mass assignment.
