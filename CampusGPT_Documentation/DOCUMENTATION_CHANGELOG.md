# DOCUMENTATION_CHANGELOG — final correction

Scope: documentation and prompt files only. No application code, database or Docker environment was touched. The earlier package (`CampusGPT_Complete_Documentation_and_Antigravity_Prompts.zip`, 171 files) was corrected in place; this changelog compares it with the corrected package (186 files).

## Totals
| Measure | Count |
|---|---|
| Files inspected (every file of the earlier package) | 171 |
| Files modified | 126 |
| Files added | 16 |
| Files removed | 1 |
| Files unchanged | 44 |

## Summary of corrections
1. **Face recognition is a required attendance capability.** Docs 13 and 14 rewritten; attendance data model, API, permission matrix, security/privacy, diagrams (attendance, face-recognition/liveness workflow), roadmap, P07 prompt (two required slices), ADR-026 and acceptance criteria all state the same scope. Provider and biometric policy stay pending (PD-10); production enablement waits for PD-10 and a privacy/legal review. No vendor is named.
2. **Vapi voice architecture.** Doc 37 rewritten (React → Vapi Web SDK → Vapi agent → secured FastAPI tools → PostgreSQL/pgvector, voice-session binding, server authentication, fallback, logging, privacy); diagram 19, ADR-025, P22 prompt, API spec, matrix, security and PD-19 updated. Vapi has no database access.
3. **WebSocket everywhere.** New `docs/architecture/WebSocket_Protocol.md` (connection, authentication, message format, streaming, stop, errors, reconnection, cleanup, authorisation, Nginx, FastAPI, frontend); docs 05, 06, 07, 10, 19, 30, 31; diagrams; ADR-024; P12 prompt; PD-18 direction confirmed; new PD-25 for scaling without Redis. SSE is not documented as an alternative.
4. **Existing authentication preserved and requirements completed.** Doc 11 and WP2/WP4/WP5 now cover server-side OTP verification, hashing, expiry, rate limits, Google verified-email identity, server-side institutional domain enforcement, role self-assignment, passwordless Google takeover, unauthorised account linking and user enumeration (uniform responses replaced the earlier "residual enumeration" compromise).
5. **Repository baseline no longer misrepresented.** All existing-repository statements are labelled PO-RV (previously observed, re-verification required); new provenance banner, status vocabulary, baseline table wording, PO-RV tags on status labels, status files, and prompt sections 3 and 5.
6. **Decision register reconciled.** New `DECISION_REGISTER.md`; `PENDING_DECISIONS.md` rebuilt with status, defaults, dependencies, blocked phases and approval prerequisites for PD-01…PD-25; PD-07 and PD-14 required before P05; PD-18/PD-19 reflect confirmed directions with open parameters; nothing marked approved without evidence. `PROJECT_DECISIONS.md` gained D-24…D-30.
7. **ADRs.** ADR-024 (WebSocket), ADR-025 (Vapi), ADR-026 (face recognition and privacy) added; ADR-008 amended; ADR index now computed from the files (26 ADRs).
8. **Diagrams.** Updated diagrams 01, 04, 10, 14, 19, 20; added 23 (WebSocket), 24 (face recognition and liveness), 25–28 (student, faculty, admin, placement workflows). All Mermaid blocks render.
9. **Antigravity files.** `ANTIGRAVITY.md` no longer claims automatic discovery; new root `AGENTS.md` pointer; prompt constraints, context, safety rules, dependency and PO-RV notes updated in all 54 prompts; initial audit prompt strengthened as strictly read-only.
10. **Package safety.** Package README renamed `PACKAGE_README.md`; new `docs/00_Package_Integration_Guide.md` (merge rules); real Markdown links added to indexes.
11. **UI references.** Verified: none of the five reference images exist anywhere; documented as missing, not invented.
12. **Roadmap.** P03–P25 and WP0–WP11 retained; WP9-after-WP10/WP11 documented as intentional; Stage 2 dependency order stated; P01/P02 explained.

## Files added (16)
- `AGENTS.md`
- `DECISION_REGISTER.md`
- `DOCUMENTATION_AUDIT_REPORT.md`
- `DOCUMENTATION_CHANGELOG.md`
- `PACKAGE_README.md`
- `docs/00_Package_Integration_Guide.md`
- `docs/architecture/WebSocket_Protocol.md`
- `docs/architecture/adr/ADR-024_websocket_real_time_communication.md`
- `docs/architecture/adr/ADR-025_vapi_voice_integration.md`
- `docs/architecture/adr/ADR-026_face_recognition_attendance_and_privacy.md`
- `docs/architecture/diagrams/23_websocket_communication.md`
- `docs/architecture/diagrams/24_face_recognition_liveness.md`
- `docs/architecture/diagrams/25_student_workflow.md`
- `docs/architecture/diagrams/26_faculty_workflow.md`
- `docs/architecture/diagrams/27_admin_workflow.md`
- `docs/architecture/diagrams/28_placement_workflow.md`

## Files removed (1)
- `README.md` — renamed to `PACKAGE_README.md` so it cannot overwrite a repository README

## Files modified (126)
Grouped by area (unchanged files are not listed):
- Numbered documents `docs/01–40`: 39 modified
- Foundation documents: 17 modified
- Architecture (reconciliation, traceability, ADRs, diagrams): 10 modified
- Prompt library: 54 modified
- Root files: 6 modified
