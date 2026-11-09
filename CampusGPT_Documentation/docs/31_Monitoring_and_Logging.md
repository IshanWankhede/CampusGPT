# 31 — Monitoring and Logging

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

**Current state (PO-RV — previously observed):** no logging module, request IDs, audit table or monitoring were found. Everything is PROPOSED (WP11); re-verify first.

## 1. Structured logging
JSON lines to stdout with fields: timestamp, level, logger, message, `request_id`, `user_id` (when known), route, status, duration_ms. Level from configuration; production default INFO. Container logs are collected by the host's log driver; no log-shipping product is introduced here.

## 2. Request correlation
Middleware accepts a well-formed `X-Request-ID` or generates one, adds it to all log records and returns it in the response header and in the error envelope.

## 3. Redaction (mandatory)
Never log: passwords, OTP values, access/refresh tokens, authorisation headers, cookies, one-time login codes, reset links, full email bodies, AI message bodies (by default), biometric data. A logging filter masks known keys; tests inject sentinel secrets and assert they never appear in output.

## 4. Audit log
Append-only `audit_logs` (actor, action, target, outcome, hashed IP, request ID, non-secret metadata). Events: login success/failure, lockout, OTP sent/verified/failed, registration, password reset, token refresh and reuse detection, logout, role request created/approved/rejected, admin actions, document access by admins, policy changes. Read-only viewer for admins (P21). Retention set by the institution.

## 5. Metrics and alerts (candidates)
| Signal | Why |
|---|---|
| failed-login rate, lockouts | credential attacks |
| refresh-token reuse detections | token theft |
| 5xx rate, latency p95 | availability |
| email provider failures | OTP outage |
| ingestion job failures and queue age | RAG health |
| LLM latency, errors, token spend | cost and reliability |
Starting point: `/health`, container healthchecks and log-based alerts; a metrics endpoint or monitoring product is a later ADR.

## 6. Error handling
Generic messages to clients; stack traces only in logs; unhandled exceptions return the error envelope with the request ID.

## 7. Operational runbooks (to be written in P25)
Backup/restore, migration, secret rotation, admin recovery (PD-24), incident response for suspected token theft (revoke families, rotate secret).

## 8. Voice, WebSocket and biometric signals
WebSocket: active connections, auth failures, close codes, generation durations, cancelled generations. Voice (Vapi): sessions per user/day, minutes, tool-call denials, tool latency, provider errors — **no audio, transcripts, tool arguments or results by default**. Biometrics: verification outcomes by session (accepted/rejected/needs review/manual), provider latency and failures, override counts, consent withdrawals — **never images, templates or per-frame scores**. All are candidates for the audit log and alerts.
