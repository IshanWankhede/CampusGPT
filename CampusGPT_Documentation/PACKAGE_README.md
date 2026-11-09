# CampusGPT — Documentation and Antigravity Prompt Package (final corrected)

> **Do not copy this file over your repository's own `README.md`.** It is deliberately named `PACKAGE_README.md`. See `docs/00_Package_Integration_Guide.md`.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. What the package contains
| Path | Contents |
|---|---|
| `AGENTS.md`, `ANTIGRAVITY.md` | Agent instructions (see section 3 for how Antigravity finds them) |
| `docs/01–40_*.md` | The 40 core documents (overview → acceptance criteria) |
| `docs/00_Package_Integration_Guide.md` | Safe merge rules for an existing repository |
| `docs/foundation-stabilisation/` | Stage 0 work packages WP0–WP11, execution order, safety procedures, checklists |
| `docs/architecture/` | Source reconciliation, traceability matrix, Mermaid diagrams (`diagrams/`), ADRs (`adr/`), WebSocket protocol |
| `docs/prompts/` | Antigravity and AI Studio prompts (`master/`, `foundation/`, `implementation/`, `ui/`, `seed-data/`, `phases/`) with an index |
| `DECISION_REGISTER.md`, `PENDING_DECISIONS.md`, `PROJECT_DECISIONS.md` | Decision register, detail, approved decisions |
| `IMPLEMENTATION_STATUS.md`, `UI_IMPLEMENTATION_STATUS.md` | Honest status trackers — update after every prompt |
| `DOCUMENTATION_CHANGELOG.md`, `DOCUMENTATION_AUDIT_REPORT.md`, `GENERATION_PROGRESS.md` | What changed, validation results, generation record |
| `assets/references/` | Where the five UI reference images belong (**not present in this package**) |

## 2. How to integrate it into an existing repository
Follow `docs/00_Package_Integration_Guide.md`. In short: copy `docs/` and `assets/` in without overwriting, merge root files by hand if names collide, never touch application code, existing migrations, Docker files, the repository README, `Architecture/`, `Flowcharts/` or `frontend/src/features/prototype-visuals/`. Work on a branch.

## 3. Using Antigravity
`ANTIGRAVITY.md` is the human-readable master instruction document; it is **not automatically discovered by Antigravity**. Community documentation reports that Antigravity reads `GEMINI.md`, `AGENTS.md` (since v1.20.3) and rule files under `.agent/rules/` (some references write `.agents/rules/`) — verify against your installed version. This package therefore ships a small root `AGENTS.md` that points to `ANTIGRAVITY.md`. You can also paste a prompt directly.

## 4. The initial read-only audit
Run `docs/prompts/master/02_Initial_Repository_Audit_Prompt.md` first. It must not modify code, run migrations, reset databases, delete records, replace authentication, change Docker volumes or start implementation; it produces a report and waits for your approval. All "existing repository" statements in this package are **PO-RV (previously observed in an older snapshot, re-verification required)** until that audit confirms them.

## 5. UI reference images
Five references were expected (dark LMS dashboard, AI chatbot with orb, timeline/workflow, neon widgets, resource dashboard). **They are not present in this package or in any file supplied so far**, so no screenshots are claimed. Provide them and place them in `assets/references/` using the names in `assets/references/README.md` before P03 and the AI Studio prompt.

## 6. Executing the foundation work packages
Stage 0 comes first. Run `docs/prompts/foundation/WP0…WP11` in the order given in `docs/foundation-stabilisation/Foundation_Execution_Order.md` (WP9 regression completion intentionally follows WP10 and WP11), stop at each approval checkpoint, then run security verification and sign `Foundation_Acceptance_Checklist.md`. Do not start ERP or AI work before that.

## 7. Executing phase prompts
After foundation acceptance: P03 → P04 → P05, then Stage 2 in dependency order (P06, P08, P07, P09, P10, P11, P21, P20), Stage 3 (P12–P14), Stage 4 (P15–P19, P22), Stage 5 (P24), Stage 6 (P23, P25, final readiness). See `docs/39_Implementation_Roadmap.md`. Run one prompt at a time.

## 8. Managing pending decisions
`DECISION_REGISTER.md` is the one-page register; `PENDING_DECISIONS.md` has the detail. Review PD-01 to PD-06 first. **PD-07 (multi-college isolation) and PD-14 (designations and permissions) must be resolved before P05.** Pending decisions stay pending until you approve them; temporary defaults are labelled provisional.

## 9. Development seed data safely
Seed data is synthetic, small, idempotent, marked as demo, guarded by environment checks, and never runs in production (doc 32). Prototype mock data, development seed data and production data are three separate things.

## 10. Verifying completion
Nothing is complete because documentation or UI exists. Use the six completion levels in `IMPLEMENTATION_STATUS.md`, require real test output, run the regression checklist and the acceptance criteria in `docs/40_Acceptance_Criteria.md`.

## Technology (fixed)
React (JavaScript/JSX) + Vite + Tailwind CSS (v4) + Lucide React · FastAPI + Pydantic + SQLAlchemy 2.x + Alembic · PostgreSQL + pgvector · existing JWT, Google OAuth, Resend email OTP · WebSocket real-time · Vapi voice · configurable LLM provider (pending) · custom RAG · Docker + Compose + Nginx · Pytest + HTTPX · GitHub Actions. **Not used:** TypeScript, ChromaDB, Redis, Qdrant/Pinecone as primary vector DB, SQLite as the application database, microservices, a second authentication system or user table.

## Required product capabilities (all documented consistently)
Face recognition attendance with liveness verification (required; provider pending PD-10) · Vapi voice interaction · WebSocket chat · permission-aware AI tools and RAG · preservation of the existing authentication.

## Quick links
[Integration guide](docs/00_Package_Integration_Guide.md) · [Decision register](DECISION_REGISTER.md) · [Pending decisions](PENDING_DECISIONS.md) · [Project decisions](PROJECT_DECISIONS.md) · [Implementation status](IMPLEMENTATION_STATUS.md) · [Roadmap](docs/39_Implementation_Roadmap.md) · [Foundation execution order](docs/foundation-stabilisation/Foundation_Execution_Order.md) · [Prompt index](docs/prompts/README.md) · [WebSocket protocol](docs/architecture/WebSocket_Protocol.md) · [Face recognition and liveness](docs/14_Face_Recognition_and_Liveness.md) · [Vapi voice architecture](docs/37_Voice_Interaction_Architecture.md) · [ADR index](docs/architecture/adr/README.md) · [Changelog](DOCUMENTATION_CHANGELOG.md) · [Audit report](DOCUMENTATION_AUDIT_REPORT.md)
