# 02 — Product Requirements Document

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Problem
Campus information is scattered across portals, spreadsheets, notice boards and personal notes. Students cannot easily ask "how many classes can I miss in DBMS?" or "summarise Unit 3 from my notes" and trust the answer; faculty and administrators spend time on manual reporting.

## 2. Goals
1. One platform for academic operations with role-based access.
2. An assistant that answers from authorised records and documents, cites sources and admits when it does not know.
3. Personalised, explainable insights (attendance recovery, eligibility, recommendations).
4. A secure, maintainable, production-oriented codebase.

## 3. Non-goals
- A generic chatbot unrelated to institutional data.
- A second authentication system or a microservice architecture.
- Fabricated predictions or unsupported analytics.
- A light theme.

## 4. Personas
| Persona | Needs | Success measure |
|---|---|---|
| Student (any year) | Clear academic status, deadlines, study help | Finds any academic answer in under a minute with a source |
| Final-year student | Placement workspace and eligibility explanations | Knows why eligible or not |
| Faculty | Fast attendance (with live face-verification monitoring and manual override) and evaluation | Session start-to-roster under a defined latency target agreed in P07 |
| Administrator | Control and auditability | Every privileged action is traceable |

## 5. Scope by module
17 modules from the original master prompt are in scope (see doc 03 and `docs/architecture/01_Traceability_Matrix.md`). Face recognition attendance with liveness verification is a **required** capability; only its provider and production enablement depend on PD-10.

## 6. Constraints
- Fixed stack (doc 01) including WebSocket real-time and Vapi voice. Dark mode only. Preserve existing authentication and existing landing/sign-in/sign-up pages.
- Three separate data environments (doc 32).
- Foundation stabilisation precedes feature work.

## 7. Assumptions (REQUIRE VERIFICATION)
- Staff and students share college email domains (PD-02).
- A single deployment serves one or more colleges (PD-07).
- Real institutional data will be imported by administrators (PD-13).

## 8. Release plan
Stage 0 → … → Stage 6 (doc 39). Each phase ends with acceptance criteria and an approval gate.

## 9. Risks
| Risk | Mitigation |
|---|---|
| Security defects in existing auth | Stage 0 before features |
| AI leaks data across users | Permission filtering inside tools and retrieval; adversarial tests |
| Biometric privacy/legal exposure | Consent, encryption, retention/deletion, human fallback, restricted access, provider decision PD-10 and privacy/legal review before production enablement |
| Scope too large | Phase-by-phase delivery, small prompts, honest status tracking |
| Multi-college data isolation unknown | PD-07 decided before academic tables |

## 10. Success metrics (to be baselined)
Foundation acceptance passed; zero cross-user leakage in tests; assistant groundedness rate on the evaluation set; attendance calculation fixtures at 100%; page load budgets (doc 04).
