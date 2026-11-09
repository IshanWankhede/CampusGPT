# 27 — Visual Learning Workspace

**Implementation status:** NOT IMPLEMENTED (planned architecture). Nothing below exists in the audited repository. Tables and endpoints are **PROPOSED**. Planned phase: **P19**. Starts only after Stage 0 foundation acceptance.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Purpose
An Excalidraw-inspired interactive canvas for learning: drawing, shapes, connectors, text, sticky notes, zoom/pan, undo/redo, grouping, save and export (PNG, SVG, PDF), with AI-generated editable flowcharts, mind maps, concept maps and decision trees from validated structured objects.

## 2. User roles
| Role | Capabilities |
|---|---|
| STUDENT | Create, save, export boards; ask AI to generate diagrams |
| FACULTY | Create boards for classes (sharing in a later iteration) |
| ADMIN | None beyond oversight |

## 3. Functional behaviour
- Board data is a versioned JSON scene (elements, groups, connectors).
- AI generation returns a diagram object that is validated against a schema before it is converted to scene elements; invalid output is rejected, never rendered raw.
- Export client-side where possible.

## 4. Business rules
- Build on a maintained canvas approach decided by ADR in P19 (reuse vs custom); do not claim Excalidraw compatibility without testing.
- AI-generated content is clearly marked and editable.

## 5. Frontend responsibilities
- Canvas editor, toolbar, export menu, AI prompt panel.

Cross-cutting UI rules (doc 33): dark mode only, Tailwind v4 tokens, Lucide React icons, loading/empty/error states, keyboard accessibility, reduced-motion respected.

## 6. Backend responsibilities
- `visual` module storing scenes; schema validator for AI diagrams.

## 7. Database requirements (PROPOSED)
- visual_boards(id, owner_id, title, scene JSON, version, updated_at)
- visual_board_shares(board_id, principal_type, principal_id, permission)

All tables are created by additive Alembic migrations after reading the real revision head. Foreign keys to `users` reuse the existing table; no second user table is created. Institution scoping follows the outcome of PD-07.

## 8. API contracts (PROPOSED)
| Method | Path (PROPOSED) | Allowed | Purpose |
|---|---|---|---|
| POST | `/api/v1/visual/boards` | any | create |
| GET | `/api/v1/visual/boards` | any | list own |
| PUT | `/api/v1/visual/boards/{id}` | owner | save |
| POST | `/api/v1/visual/generate` | any | AI diagram from prompt, schema-validated |

Conventions: JSON, `/api/v1` prefix, Pydantic request/response models, pagination `?page=&page_size=` (default 20, max 100) on list endpoints.

## 9. Authentication
Existing JWT bearer authentication (after Stage 0: 15-minute access token with refresh rotation). All routes above require an authenticated, verified, active user unless stated otherwise.

## 10. Authorisation
- Owner-only until sharing is designed.

Roles are read from the database on each request. Permission checks live in the service layer, not only in route decorators, so internal callers (such as AI tools) cannot bypass them.

## 11. Validation
- Scene size cap; element type allow-list; diagram JSON schema.

## 12. Error handling
All errors use the standard envelope from `10_API_Specification.md` (`{ "error": { "code", "message", "request_id", "details" } }`): 401 unauthenticated, 403 forbidden, 404 not found **or** hidden-by-permission (never reveal existence of unauthorised records), 409 conflict, 422 validation, 429 rate limited, 503 dependency unavailable.

## 13. Security
- Sanitise text and SVG on export; reject scripts in SVG.

## 14. Testing
- Schema rejection tests; save/load round trip; export smoke tests.

Plus: authorisation matrix tests (each role × each route), pagination bounds, and a regression run of the Foundation suite.

## 15. Dependencies
- P12 for AI generation

## 16. Acceptance criteria
- Invalid AI output never reaches the canvas.

Acceptance additionally requires: tests actually executed and reported, migrations reviewed, docs and status files updated, and no claim of completion for UI-only work (see the six completion levels in `IMPLEMENTATION_STATUS.md`).
