# ADR-015 — Google OAuth with one-time code exchange

- **Status:** ACCEPTED (parameters provisional)
- **Implementation status:** Not implemented (WP4)

## Context
Tokens are placed in redirect URLs.

## Decision
Redirect carries only a one-time opaque code (hashed, ~60 s, single use); exchange by POST; state bound to an HttpOnly nonce cookie.

## Alternatives considered
- Tokens in URL fragment (rejected: remains in history)
- HttpOnly cookies set at callback (candidate for production, PD-23)

## Consequences
Extra table and request.

## Security implications
Removes token leakage via URLs, logs and referrers.
