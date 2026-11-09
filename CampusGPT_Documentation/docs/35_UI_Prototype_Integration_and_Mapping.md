# 35 — UI Prototype Integration and Mapping

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Strategy
A frontend-only visual prototype is generated in **Google AI Studio** from the five reference images (prompt: `docs/prompts/ui/01_Google_AI_Studio_Master_Prompt.md`). It is a visual and interaction reference, **never** production code or data.

## 2. Rules
1. Extract the prototype into `ui-reference/google-ai-studio/` — a separate folder; it must never overwrite `frontend/`.
2. Prototype mock data stays inside the prototype (data environment A). It is not copied into production components, seeds or tests.
3. The prototype contains a removable development role switcher in its own component; it is not ported.
4. Git-ignoring `ui-reference/` is optional and does **not** hide it from Antigravity.
5. The prototype's own dependencies (including any TypeScript or light-mode code it might generate) are not adopted: the production frontend stays JavaScript/JSX, dark only, Tailwind v4, Lucide.

## 3. Mapping method (P03)
For each prototype screen record: prototype file → production route (doc 34) → production component → API dependency → shared components needed → required changes → status. Output file: `docs/architecture/ui-mapping.md` created during P03.

| Prototype area | Production target | Notes |
|---|---|---|
| App shell, sidebar, header | `components/layout/AppShell` (P04) | reference 1 |
| Student dashboard cards | `features/student/DashboardPage` (P06) | reference 4 widgets |
| Chat workspace and orb | `features/ai/ChatWorkspace` (P12) | reference 2 |
| Timetable timeline | `features/timetable` (P08) | reference 3 |
| Document library | `features/documents` (P11) | reference 5 |
| Visual workspace | `features/visual` (P19) | |
| Faculty and admin screens | `features/faculty`, `features/admin` | |

## 4. Integration steps
1. P03: audit and mapping (read-only).
2. P04: build tokens and components from the mapping, not by copying code.
3. Per phase: implement screens against real APIs; empty states replace mock data.
4. P24: parity review against doc 36.

## 5. Handling differences
If the prototype uses a pattern that conflicts with D-01…D-23 (TypeScript, light theme, localStorage data, new libraries), re-implement it within the constraints and note the deviation in the mapping file.
