# ADR-002 — FastAPI modular monolith

- **Status:** ACCEPTED
- **Implementation status:** Partially implemented (auth module)

## Context
FastAPI backend already exists; the product has many related modules sharing one database and permission model.

## Decision
One FastAPI application organised into modules (router/service/repository/schemas/policies). Worker is a process of the same image.

## Alternatives considered
- Microservices (rejected: operational overhead, cross-service authorisation)
- Single flat app (rejected: unmaintainable)

## Consequences
Simple deployment and transactions; needs discipline at module boundaries.

## Security implications
One place for authorisation; no inter-service trust to manage.
