# ADR-007 — No ChromaDB

- **Status:** ACCEPTED
- **Implementation status:** Policy

## Context
Original master prompt excludes ChromaDB; pgvector covers the need.

## Decision
Do not introduce ChromaDB or any separate vector store.

## Alternatives considered
- ChromaDB (rejected)

## Consequences
Hybrid search and permission joins stay in SQL.

## Security implications
One access-control path for vectors.
