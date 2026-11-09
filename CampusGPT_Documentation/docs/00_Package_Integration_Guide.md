# 00 — Package Integration Guide (safe merge into an existing repository)

This package is documentation and prompts only. It contains **no application code**. Copy it into an existing CampusGPT repository carefully; never overwrite the project's own files.

## 1. What goes where
| Package path | Destination in the repository | Conflict behaviour |
|---|---|---|
| `docs/` (all numbered documents, `foundation-stabilisation/`, `architecture/`, `prompts/`) | `docs/` | Merge. If the repository already has `docs/`, copy these files in without deleting existing files; if a name collides, keep both and rename the package copy |
| `assets/references/` | `assets/references/` | Merge; place the five UI reference images here (they were never supplied) |
| `AGENTS.md` | repository root | If the repository already has an `AGENTS.md`, **do not replace it**: append the pointer block from this file |
| `ANTIGRAVITY.md` | repository root | Merge manually if one exists |
| `IMPLEMENTATION_STATUS.md`, `UI_IMPLEMENTATION_STATUS.md`, `PROJECT_DECISIONS.md`, `PENDING_DECISIONS.md`, `DECISION_REGISTER.md` | repository root | Merge manually if names collide |
| `DOCUMENTATION_CHANGELOG.md`, `DOCUMENTATION_AUDIT_REPORT.md`, `GENERATION_PROGRESS.md` | `docs/package/` (optional) | Informational |
| `PACKAGE_README.md` | keep the name `PACKAGE_README.md`, e.g. inside your repository's `docs` folder | **Never copy it over the repository's own `README.md`.** It is named differently on purpose |

## 2. Never touch
Application source code, existing migrations, `docker-compose.yml`, the existing `README.md`, the historical `Architecture/` and `Flowcharts/` folders, and `frontend/src/features/prototype-visuals/`.

## 3. Relative links
Links inside the package are relative to the package root. Keep the `docs/` and `assets/` folder names so references (for example `docs/prompts/phases/…`) keep resolving. After copying, run a link check (the package ships its results in `DOCUMENTATION_AUDIT_REPORT.md`).

## 4. Merge procedure
1. Create a branch (for example `docs/campusgpt-package`).
2. Copy folders with a non-overwriting command (for example `cp -rn`, or your file manager's "keep both") and review every collision by hand.
3. Commit the documentation separately from any code work.
4. Do not run implementation prompts on the same branch until the read-only audit (prompt 02) has been reviewed.

## 5. Git ignore
Add `ui-reference/` to `.gitignore` only if you want it untracked; Git-ignoring a folder does not stop Antigravity from reading it.
