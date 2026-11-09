# ADR-026 — Face recognition attendance with liveness is a required capability

- **Status:** ACCEPTED (provider and biometric policy PD-10)
- **Implementation status:** Not implemented (P07 slice B)

## Context
Attendance must be verified by face recognition with liveness verification; an earlier draft described it as optional or deferred, which was incorrect. Biometric data is highly sensitive and no provider is approved.

## Decision
Face verification is part of the required scope of attendance (P07 slice B), built behind a `BiometricProvider` interface with a labelled mock provider for development. Consent, encrypted templates, raw-image deletion, retention/deletion, restricted access, manual fallback, faculty override and audit are mandatory. Blink detection is one liveness signal only; GPS is supporting evidence only. Production enablement waits for PD-10 and a privacy/legal review. No vendor is selected here.

## Alternatives considered
- Optional/deferred feature (rejected: incorrect product scope)
- Select a vendor now (rejected: not approved)
- Biometrics without fallback (rejected)

## Consequences
Provider choice, accuracy/spoofing evaluation, and legal review gate production use; manual fallback keeps attendance workable meanwhile.

## Security implications
Templates encrypted with managed keys; faculty and admins never access templates or raw images; audit of every override; spoofing residual risk documented honestly (doc 14).
