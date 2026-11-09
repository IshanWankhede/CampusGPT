# Architecture Decision Records

**Count (computed from the files in this folder): 26 ADRs** — 25 accepted (some with provisional parameters), 1 pending approval.

Status values: **ACCEPTED** (approved by the owner or by the master instructions; parameters in brackets are still pending), **PENDING APPROVAL** (not decided). Nothing is marked accepted without a source. The original master prompt contained decisions but no written ADR text; these records were authored from it, from the repository audit (previously observed, PO-RV) and from the owner's final instructions.

| ADR | Decision | Status | Implementation |
|---|---|---|---|
| [ADR-001](ADR-001_use_javascript_jsx_instead_of_typescript.md) | Use JavaScript/JSX instead of TypeScript | ACCEPTED | Existing; enforced by policy |
| [ADR-002](ADR-002_fastapi_modular_monolith.md) | FastAPI modular monolith | ACCEPTED | Partially implemented (auth module) |
| [ADR-003](ADR-003_postgresql_as_the_only_database.md) | PostgreSQL as the only database | ACCEPTED | Implemented |
| [ADR-004](ADR-004_sqlalchemy_2.x_with_pydantic_schemas.md) | SQLAlchemy 2.x with Pydantic schemas | ACCEPTED | Implemented |
| [ADR-005](ADR-005_alembic_with_additive_reviewed_migrations.md) | Alembic with additive, reviewed migrations | ACCEPTED | Partially implemented (WP1 pending) |
| [ADR-006](ADR-006_pgvector_for_vector_search.md) | pgvector for vector search | ACCEPTED | Not implemented (extension migration PROPOSED) |
| [ADR-007](ADR-007_no_chromadb.md) | No ChromaDB | ACCEPTED | Policy |
| [ADR-008](ADR-008_no_redis.md) | No Redis | ACCEPTED | Policy |
| [ADR-009](ADR-009_preserve_and_incrementally_harden_the_existing_authenticatio.md) | Preserve and incrementally harden the existing authentication | ACCEPTED | Implemented but defective |
| [ADR-010](ADR-010_preserve_existing_landing_sign-in_and_sign-up_pages.md) | Preserve existing landing, sign-in and sign-up pages | ACCEPTED | Implemented |
| [ADR-011](ADR-011_tailwind_css_v4.md) | Tailwind CSS v4 | ACCEPTED | Implemented |
| [ADR-012](ADR-012_lucide_react_for_new_application_icons.md) | Lucide React for new application icons | ACCEPTED | Not implemented (P04) |
| [ADR-013](ADR-013_ui_prototype_as_reference_only.md) | UI prototype as reference only | ACCEPTED | Policy |
| [ADR-014](ADR-014_separate_prototype_development_and_production_data.md) | Separate prototype, development and production data | ACCEPTED | Not implemented |
| [ADR-015](ADR-015_google_oauth_with_one-time_code_exchange.md) | Google OAuth with one-time code exchange | ACCEPTED (parameters provisional) | Not implemented (WP4) |
| [ADR-016](ADR-016_refresh-token_rotation_with_server-side_tracking.md) | Refresh-token rotation with server-side tracking | ACCEPTED (lifetime PD-03; storage PD-04/PD-23 pending) | Not implemented (WP6) |
| [ADR-017](ADR-017_database-backed_authentication_rate_limiting.md) | Database-backed authentication rate limiting | ACCEPTED (thresholds provisional) | Not implemented (WP5) |
| [ADR-018](ADR-018_migrations_run_as_a_dedicated_one-shot_service.md) | Migrations run as a dedicated one-shot service | ACCEPTED | Not implemented (WP8) |
| [ADR-019](ADR-019_isolated_postgresql_test_database.md) | Isolated PostgreSQL test database | ACCEPTED (exact name PD-05) | Not implemented (WP0, WP9) |
| [ADR-020](ADR-020_separate_development_and_production_docker_layers.md) | Separate development and production Docker layers | ACCEPTED | Not implemented (WP8) |
| [ADR-021](ADR-021_faculty_accounts_require_administrator_approval.md) | Faculty accounts require administrator approval | ACCEPTED (interim tooling PD-01) | Not implemented (WP2) |
| [ADR-022](ADR-022_multi-college_data_isolation_strategy.md) | Multi-college data isolation strategy | PENDING APPROVAL (PD-07) | Pending |
| [ADR-023](ADR-023_permission-aware_ai_tools_and_filtered_retrieval_no_llm-gene.md) | Permission-aware AI: tools and filtered retrieval, no LLM-generated SQL | ACCEPTED | Not implemented (P12–P14) |
| [ADR-024](ADR-024_websocket_real_time_communication.md) | WebSocket as the real-time communication approach | ACCEPTED (protocol parameters PD-18; scaling PD-25) | Not implemented (P12; live attendance in P07) |
| [ADR-025](ADR-025_vapi_voice_integration.md) | Vapi voice integration through secured FastAPI tools | ACCEPTED (deployment details PD-19) | Not implemented (P22) |
| [ADR-026](ADR-026_face_recognition_attendance_and_privacy.md) | Face recognition attendance with liveness is a required capability | ACCEPTED (provider and biometric policy PD-10) | Not implemented (P07 slice B) |

Required coverage check: JavaScript/JSX (001), FastAPI modular monolith (002), PostgreSQL (003) and SQLAlchemy (004), pgvector (006), no Redis (008) and no ChromaDB (007), existing authentication preservation (009), UI prototype-first development (013), seed-data safety (014), WebSocket (024), Vapi (025), face recognition attendance and privacy (026), permission-aware AI tools and RAG (023). No duplicate ADRs exist for these decisions.
