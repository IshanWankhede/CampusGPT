# 01 — Project Overview

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## What CampusGPT is
CampusGPT is an AI-powered campus ERP with a grounded AI assistant. It combines institutional operations (attendance, timetables, assignments, notices, documents), academic analytics, placement and learning support, and a conversational assistant that answers only from data and documents the asking user is authorised to see. It is meant to be a complete product for students, faculty and administrators, not a dashboard demo.

## Users
| Role | Primary goals |
|---|---|
| STUDENT | See attendance, timetable, deadlines, marks; study from authorised documents; prepare for placements |
| FACULTY | Run attendance, set and evaluate assignments, publish notices and documents, see class performance (after admin approval) |
| ADMIN | Manage institutional structure, users, policies, approvals, audit |

HOD, Dean and Coordinator are configurable designations layered on roles (PD-14), not separate roles.

## Product pillars
1. College ERP and academic management.
2. Grounded AI assistant with intent routing and permission-aware RAG.
3. Document intelligence on PostgreSQL + pgvector.
4. Academic analytics, placement intelligence, internships/hackathons, course recommendations.
5. Visual Learning Workspace and voice interaction.

## Current state (honest summary)
| Area | State |
|---|---|
| Landing, sign-in, sign-up pages | IMPLEMENTED (preserve) |
| Authentication (JWT, Google OAuth, email OTP, reset) | PO-RV: previously observed as implemented with three critical and several high issues — re-verification required |
| Application shell, dashboards, all ERP/AI modules | NOT IMPLEMENTED |
| Tests, CI, audit logging | NOT IMPLEMENTED |

## Delivery strategy
Stage 0 **foundation stabilisation** (WP0–WP11) → Stage 1 core application foundation → Stage 2 core ERP → Stage 3 AI foundation → Stage 4 advanced AI and analytics → Stage 5 UI integration → Stage 6 production readiness. See doc 39. Work is delivered through small, reviewable Antigravity prompts (`docs/prompts/`), each with approval gates.

## Fixed technology
React (JavaScript/JSX) · Vite · Tailwind CSS (v4) · Lucide React · FastAPI · Pydantic · SQLAlchemy 2.x · Alembic · PostgreSQL + pgvector · existing JWT authentication, Google OAuth and Resend email OTP · **WebSocket** real-time communication · **Vapi** voice integration (through secured FastAPI tools) · configurable LLM provider (pending, PD-11) · custom/manual RAG pipeline · Docker + Docker Compose + Nginx · Pytest + HTTPX + frontend lint/build · GitHub Actions.
**Not used:** TypeScript, ChromaDB, Redis, Qdrant or Pinecone as the primary vector database, SQLite as the application database, microservices, a second authentication system, a second user table, an alternative backend.

## Required capabilities worth stating explicitly
- **Face recognition attendance with liveness verification** is a required core capability (provider and biometric policy pending, PD-10).
- **Vapi** is the intended voice integration; Vapi never bypasses the FastAPI backend.
- **WebSocket** is the intended real-time transport for chat and live attendance.
- The **existing authentication is preserved** and hardened, not replaced.

## Where to go next
`PACKAGE_README.md` → `ANTIGRAVITY.md` → `docs/foundation-stabilisation/Foundation_Execution_Order.md`.
