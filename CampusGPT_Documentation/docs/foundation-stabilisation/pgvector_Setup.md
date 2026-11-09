# pgvector Setup

**Status:** Docker image supports pgvector (`pgvector/pgvector:pg16`) — IMPLEMENTED (PO-RV). Extension created by migration — NOT IMPLEMENTED (audit: enabled by hand). Vector columns — NOT IMPLEMENTED and **deliberately deferred**.

## What exists
- Compose database image already contains the pgvector binaries.
- The Python `pgvector` package is in `requirements.txt` but unused in the snapshot.
- Old `Architecture/PHASES.md` records the extension as enabled manually.

## What WP1 does
- Adds one migration: `CREATE EXTENSION IF NOT EXISTS vector` (PostgreSQL only). Idempotent, safe on databases where it already exists.
- `downgrade` is a documented no-op: dropping the extension later would destroy vector data.

## What WP1 does not do
- It creates no tables or vector columns. The dimension depends on the embedding model (PD-11) and belongs to Phase P14.

## Privileges and environments
| Environment | Note |
|---|---|
| Development (Compose) | Superuser role; migration works |
| CI | pgvector image as the service container |
| Production / managed Postgres | The role may lack `CREATE EXTENSION`; the administrator may need to enable it first. Document the manual step; never grant the application role extra privileges silently |

## Verification
Fresh DB → `upgrade head` → `SELECT extname FROM pg_extension` lists `vector`. Existing dev DB → `upgrade head` has no side effect other than the new revision.

## Later (P14, PROPOSED)
`document_chunks.embedding vector(N)` with an HNSW or IVFFlat index, chosen after the embedding model is fixed; permission filtering via metadata columns applied in the same SQL query as similarity search.
