# 33 — Frontend UI Design System

**Status:** PROPOSED for new application screens. Existing landing and auth pages are monochrome black/white and are **not** restyled (D-04); the palette bridge is PD-16. Colour values below are proposals derived from the original master prompt's description; the five reference images were not available to the generator, so exact hues must be confirmed against them in P03.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Principles
Dark mode only (no toggle, no light branches, charts/dialogs/dropdowns/forms included). Premium SaaS feel: generous spacing, clear hierarchy, consistent cards, restrained gradients and neon, subtle purposeful motion. Not a generic AI-generated dashboard.

## 2. Colour tokens (PROPOSED; defined once as CSS variables in the Tailwind v4 theme)
| Token | Value | Use |
|---|---|---|
| `--bg` | #0B0C10 | page background (near-black) |
| `--bg-2` | #10142A | secondary surface (dark navy) |
| `--card` | #14161D | cards (slightly lighter charcoal) |
| `--sidebar` | #0E0F14 | sidebar (deep charcoal) |
| `--border` | #272A35 | subtle dark-grey borders |
| `--primary` | #7C6CF2 | violet accent |
| `--primary-2` | #4F46E5 | indigo accent |
| `--teal` | #2DD4BF | secondary accent |
| `--success` | #84CC16 | controlled green/lime |
| `--warning` | #F59E0B | amber |
| `--error` | #E5675F | muted red |
| `--text` | #EDEEF3 | primary text (soft white) |
| `--muted` | #9AA3B2 | secondary text (cool grey) |

### Computed contrast (WCAG formula, calculated for this package)
| Pair | Ratio | Result |
|---|---|---|
| `text` #EDEEF3 on `bg` #0B0C10 | 16.87:1 | AA text |
| `text` #EDEEF3 on `card` #14161D | 15.59:1 | AA text |
| `muted` #9AA3B2 on `bg` #0B0C10 | 7.68:1 | AA text |
| `muted` #9AA3B2 on `card` #14161D | 7.10:1 | AA text |
| `primary` #7C6CF2 on `card` #14161D | 4.55:1 | AA text |
| `teal` #2DD4BF on `card` #14161D | 9.71:1 | AA text |
| `success` #84CC16 on `card` #14161D | 9.15:1 | AA text |
| `warn` #F59E0B on `card` #14161D | 8.41:1 | AA text |
| `err` #E5675F on `card` #14161D | 5.54:1 | AA text |
| `text` #EDEEF3 on `primary2` #4F46E5 | 5.43:1 | AA text |

Any pair marked "FAIL" must not carry body text. Final values are re-checked against the reference images in P03 and in the P24 accessibility pass.

## 3. Typography
One sans-serif family for UI, one monospace for code/IDs. Concrete families are chosen in P04 (the existing pages use their own fonts loaded from an external CDN; the new shell should self-host fonts). Scale: 12/14/16/18/20/24/30/36 px; line height 1.4–1.6; weights 400/500/600.

## 4. Spacing, radius, elevation
4-px base scale (4, 8, 12, 16, 24, 32, 48). Radii: 8 (inputs), 12 (cards), 16 (dialogs). Elevation by border + faint shadow, not heavy glows.

## 5. Components (to build in P04, each with states)
Button, IconButton, Input, Select, Textarea, Checkbox, Switch, Badge, Avatar, Card, StatCard, Table (sortable, paginated), Tabs, Dialog, Drawer, Dropdown, Tooltip, Toast, Skeleton, EmptyState, ErrorState, Progress/Ring, Chart wrapper (a charting library chosen by ADR in P04), Calendar, Timeline, FileDropzone, ChatMessage, CitationChip, Sidebar, Header, PageHeader, Breadcrumbs.

## 6. Navigation
Persistent sidebar (collapsible; bottom sheet or drawer on mobile), header with search, notifications, profile menu. Role-specific item sets (doc 34).

## 7. States
Every data component defines loading (skeleton), empty (helpful message + action), error (retry), and permission-denied states.

## 8. Icons
Lucide React only for new UI; consistent 20 px default, 1.75 stroke.

## 9. Motion
`motion` for transitions (150–250 ms), GSAP only for selected scroll effects, React Three Fiber only for the AI orb if an ADR approves it. Respect `prefers-reduced-motion`; no scroll hijacking; no expensive continuous animations.

## 10. Responsive and accessibility
Breakpoints 360/768/1024/1280/1536. Keyboard operable, visible focus ring in `--primary`, labelled controls, ARIA for dialogs/menus/live regions (streaming chat announces completed messages, not each token), minimum 44-px touch targets.

## 11. Rules for contributors
No hard-coded colours in components; use tokens. No light backgrounds anywhere. No mock data in production components.
