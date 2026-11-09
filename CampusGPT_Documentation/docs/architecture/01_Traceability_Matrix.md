# 01 — Traceability Matrix (original master prompt → this package)

Every requirement area from the original master prompt is mapped to a document and an implementation phase. Phase numbers are the original 25 phases (`P01`–`P25`); `S0` is the new Stage 0 foundation (WP0–WP11), which precedes P04.

| Original module / topic | Docs | Phase(s) | Implementation status |
|---|---|---|---|
| M1 Student dashboard | 02, 03, 06, 34 | P05, P06 | NOT IMPLEMENTED (placeholder `/app` only) |
| M2 Student profile | 03, 08, 09 | P06 | NOT IMPLEMENTED |
| M3 Attendance incl. face recognition and liveness (required; provider PD-10) | 13, 14 | P07 (slices A and B) | NOT IMPLEMENTED |
| M4 Timetable | 15 | P08 | NOT IMPLEMENTED |
| M5 Assignments | 16 | P09 | NOT IMPLEMENTED |
| M6 Notices and notifications | 17 | P10 | NOT IMPLEMENTED |
| M7 Document management | 18 | P11 | NOT IMPLEMENTED |
| M8 AI workspace (WebSocket chat) | 19, 33 and `architecture/WebSocket_Protocol.md` | P12 | NOT IMPLEMENTED |
| M9 Intent detection and routing | 20 | P13 | NOT IMPLEMENTED |
| M10 Production RAG | 21, 22 | P14 | NOT IMPLEMENTED (pgvector extension not migrated) |
| M11 Academic analytics | 23 | P15 | NOT IMPLEMENTED |
| M12 Placement intelligence | 24 | P16 | NOT IMPLEMENTED |
| M13 Internships and hackathons | 25 | P17 | NOT IMPLEMENTED |
| M14 Course recommendations | 26 | P18 | NOT IMPLEMENTED |
| M15 Visual Learning Workspace | 27 | P19 | NOT IMPLEMENTED |
| M16 Faculty dashboard | 03, 12 | P20 | NOT IMPLEMENTED |
| M17 Admin dashboard | 03, 12 | P21 | NOT IMPLEMENTED |
| RBAC (Part 6) | 11, 12 | S0 (WP2), P05, P23 | PARTIALLY IMPLEMENTED (PO-RV) |
| Dark-mode-only identity (Part 7) | 33, 34, 36 | P04, P24 | PARTIALLY IMPLEMENTED (PO-RV) (auth/landing are dark) |
| Prototype strategy (Part 8) | 35, prompts/ui/01 | P03, P24 | NOT IMPLEMENTED |
| Three data environments (Part 9) | 32 | P25 / seed prompt | NOT IMPLEMENTED |
| Backend architecture (Part 11) | 05, 07 | P02 | PARTIALLY IMPLEMENTED (PO-RV) (auth module only) |
| Database architecture (Part 12) | 08, 09 | P02 | PARTIALLY IMPLEMENTED (PO-RV) (2 tables) |
| API design (Part 13) | 10 | all | PARTIALLY IMPLEMENTED (PO-RV) (auth routes) |
| Security and privacy (Part 14) | 28 and `foundation-stabilisation/` | S0, P23 | IMPLEMENTED BUT DEFECTIVE (PO-RV) |
| Development workflow (Part 15) | `ANTIGRAVITY.md`, 38, 39 | — | — |
| Voice interaction via Vapi (Ref 2) | 37 | P22 | NOT IMPLEMENTED |
| Testing and deployment | 29, 30, 31, 40 | S0 (WP8–WP11), P25 | NOT IMPLEMENTED |
| Documentation (Part 17, 41 topics) | docs 01–40 | — | this package |
