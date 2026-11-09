# ADR-023 — Permission-aware AI: tools and filtered retrieval, no LLM-generated SQL

- **Status:** ACCEPTED
- **Implementation status:** Not implemented (P12–P14)

## Context
Original master prompt forbids unrestricted LLM-generated SQL and requires permission-aware RAG.

## Decision
The assistant calls a fixed allow-list of typed tools and a permission-filtered retriever; authorisation is enforced inside them and never delegated to routing or the model.

## Alternatives considered
- Text-to-SQL (rejected)

## Consequences
Each new capability needs a new tool.

## Security implications
Prevents cross-user disclosure and SQL injection through the model.
