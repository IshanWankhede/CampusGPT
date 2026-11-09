# ADR-025 — Vapi voice integration through secured FastAPI tools

- **Status:** ACCEPTED (deployment details PD-19)
- **Implementation status:** Not implemented (P22)

## Context
The owner requires Vapi for voice. Browser-native speech was previously documented as the main direction, which was incorrect.

## Decision
Architecture: React → Vapi Web SDK → Vapi voice agent → Vapi custom Function Tools → secured FastAPI tool endpoints → PostgreSQL/pgvector. Tool calls require Vapi server authentication and a voice session bound to the user; the user identity never comes from model arguments; Vapi has no database access; text chat is the fallback; recording is off by default (doc 37).

## Alternatives considered
- Browser-native speech API (not the owner's direction)
- Giving the voice platform direct database or MCP access (rejected: bypasses backend security)

## Consequences
Dependence on a third-party platform; exact payload fields and credential method must be verified against current Vapi documentation; credentials, pricing, assistant configuration and privacy approval are deployment decisions.

## Security implications
Voice data is processed by a third party; consent, retention and data-processing terms required; minimal tool results; replay protection; rate limits.
