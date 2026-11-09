# ADR-021 — Faculty accounts require administrator approval

- **Status:** ACCEPTED (interim tooling PD-01)
- **Implementation status:** Not implemented (WP2)

## Context
Public registration can request privileged roles.

## Decision
Public registration creates STUDENT; faculty requests are `role_requests`; only ADMIN approves; admins created only via CLI.

## Alternatives considered
- Domain-based auto-faculty (rejected: staff and students may share domains, PD-02)

## Consequences
Admins must process requests.

## Security implications
Closes C3; creates an audit trail.
