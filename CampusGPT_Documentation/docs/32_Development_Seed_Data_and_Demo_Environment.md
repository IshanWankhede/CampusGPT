# 32 — Development Seed Data and Demo Environment

**Status:** NOT IMPLEMENTED. Planned for implementation after the academic structure exists (P05) and refined per module; the seed prompt is `docs/prompts/seed-data/`.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Three data environments (never mixed)
| Env | What | Lives in | Rule |
|---|---|---|---|
| A. AI Studio prototype mock data | Fictional data inside the frontend prototype | `ui-reference/google-ai-studio/` | Never imported into production code, seeds or tests |
| B. Development seed data | Small, consistent, synthetic records in the dev PostgreSQL | `database/development-seed/` (PROPOSED) | Dev/test only; clearly marked as demo |
| C. Production institutional data | Real records entered or imported by authorised users | production database | Never touched by seed scripts |

## 2. Quantities (from the original master prompt)
| Entity | Approx. quantity |
|---|---:|
| Students | 8–10 |
| Faculty | 3–4 |
| Departments | 2 |
| Branches | 2 |
| Subjects | 6–8 |
| Attendance records | 20–30 |
| Timetable | 1 sample week |
| Assignments | 5–6 |
| Notices | 4–5 |
| Documents | 5–6 |
| Placement opportunities | 4–5 |
| Internships | 2–3 |
| Hackathons | 2–3 |
| Courses | 10–12 |
| AI conversations | 3–4 |

## 3. Consistency rules
Reuse the same students and faculty across modules; subjects, enrolments and attendance agree; assignments belong to real subjects and faculty; submissions link real students and assignments; dashboard analytics are computed from the seeded rows, not typed in; foreign keys respected; no thousands of rows; no random unrelated data.

## 4. Safety rules
1. **Environment guard:** the seed command refuses to run unless `ENV=development` (and, for tests, a database name ending `_test`). It aborts if `ENV` is `staging` or `production`.
2. **Marked as demo:** every seeded user uses a reserved synthetic email domain (for example `@demo.campusgpt.invalid`, which cannot receive mail) and every seeded row carries a demo marker where the table allows (`is_demo` flag or demo-prefixed natural key).
3. **Synthetic identities only.** No real student names, emails, PRNs or photos.
4. **Idempotent:** natural keys + upsert; running twice creates no duplicates.
5. **Never overwrites** existing non-demo records; if a natural key collides with a real row it aborts and reports.
6. **Existing authentication only:** demo accounts are created through the existing user-creation service so passwords are hashed by the same function; demo passwords come from an environment variable, never hard-coded in the repository. No second auth system.
7. **Demo FACULTY/ADMIN accounts** are created through the same controlled paths (approval/CLI), not by bypassing role rules.
8. **Reset:** a separate explicit `reset-demo` command deletes only rows flagged as demo, in development only, after confirmation and a backup reminder. It is the single sanctioned deletion path and needs the owner's approval before first use.
9. Seeds are versioned files; no seed runs automatically at container start.

## 5. Empty states
The real frontend must render useful empty states when no records exist (production starts empty); seed data must not be needed for the UI to function.

## 6. Documents and AI seed
Five or six synthetic documents (short, original text) placed in storage with normal versions and ACLs; embeddings are generated through the real pipeline in P14, not inserted by hand. AI conversations are seeded as plain messages with sources referencing seeded documents.

## 7. Verification
After seeding: row counts match the table above; a student sees only their rows; analytics numbers match hand calculations; running the seed twice leaves counts unchanged; running it with `ENV=production` fails.

## 8. Biometric, voice and real-time seed rules
- No real biometric data is ever seeded; demo students have no face templates unless produced by the **mock provider** in development, and mock-provider data is clearly labelled and refused in production.
- Seeded attendance records use source `manual` or `mock-face` with a demo marker; seeded overrides carry reasons.
- No Vapi or LLM credentials appear in seed files; voice and AI features are tested with stubs.
- Seed scripts reuse existing API endpoints and database models where available, and the real application renders real API responses with polished empty states when none exist.
