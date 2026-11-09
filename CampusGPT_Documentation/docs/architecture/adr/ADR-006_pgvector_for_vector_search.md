# ADR-006 — pgvector for vector search

- **Status:** ACCEPTED
- **Implementation status:** Not implemented (extension migration PROPOSED)

## Context
Docker image already includes pgvector; Python package present but unused; extension enabled manually.

## Decision
Create the extension by migration (WP1); define vector columns only in P14 once the embedding model is chosen (PD-11).

## Alternatives considered
- Store embeddings as arrays without an index (rejected)

## Consequences
Dimension is fixed at column creation; changing it requires re-embedding.

## Security implications
Permission filters can run in the same SQL as similarity search.
