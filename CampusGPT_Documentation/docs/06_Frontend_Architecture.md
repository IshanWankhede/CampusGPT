# 06 — Frontend Architecture

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Existing (audit-reported)
- React 19, Vite 8, Tailwind CSS v4 (`@tailwindcss/vite`), `react-router-dom` 7, `motion` (Framer Motion's current package), `gsap`, `lenis`, `ogl`, `react-icons`. JavaScript/JSX only.
- Structure: `src/main.jsx`, `src/App.jsx`, `src/routes/AppRoutes.jsx`, `src/context/AuthContext.jsx`, `src/features/*`.
- Real landing and auth screens live in `src/features/prototype-visuals/` (`LandingPage.jsx`, `AuthScreen.jsx`, effects such as `DotField`, `Strands`). Do not rename or delete (D-07).
- Possibly unused: `features/auth/AuthPage.jsx`, `features/landing/LandingPage.jsx`, route `/auth/verify-email` (PD-21).
- Tokens in `localStorage`; `AuthContext` has a private `request()`; no shared API client.

## 2. Target structure (PROPOSED)
```
src/
  app/            providers, router, role guards
  components/ui/  design-system primitives (Button, Card, Dialog, Table, Input, Badge, Skeleton…)
  components/layout/ AppShell, Sidebar, Header
  features/<module>/ pages, components, hooks, api.js
  services/api.js apiFetch (WP7)
  styles/         Tailwind v4 tokens (CSS variables)
  lib/            formatters, constants
```
New work lives in new folders; existing `features/prototype-visuals/` and `features/auth/` stay as they are.

## 3. Routing
Public: `/`, `/auth`, `/auth/callback`, `/auth/forgot-password`, `/auth/reset-password`. Protected: `/app/*` with `RoleRoute` guards. Each role gets its own navigation tree (doc 34). Route-level code splitting with `React.lazy`.

## 4. State and data
- Auth in `AuthContext` (existing, improved in WP7).
- Server state through small per-feature hooks over `apiFetch`; introduce a data-fetching library only through an ADR.
- No prototype mock data in production components (D-20); empty states render when the API returns nothing.

## 5. Styling and design system
Tailwind v4 with CSS-variable tokens defined once (doc 33). Dark only: `color-scheme: dark`, no `prefers-color-scheme: light` branches, no theme toggle.

## 6. Icons and motion
Lucide React for all new UI. `motion` for component transitions, GSAP only for selected scroll effects, React Three Fiber only for the AI orb if justified by ADR. Reduced-motion honoured. No scroll hijacking.

## 7. Accessibility and responsiveness
Semantic landmarks, focus management in dialogs, keyboard navigation, contrast checks, responsive from 360 px.

## 8. Quality gates
`npm run lint`, `npm run build` in CI. A test runner (Vitest) is a later decision.

## 9. Real-time, voice and camera additions (PROPOSED)
- **WebSocket client:** a `useChatSocket` hook with a connection state machine, backoff reconnection, token refresh via `apiFetch`, and a text fallback (`docs/architecture/WebSocket_Protocol.md`). A similar hook serves the faculty live-attendance roster.
- **Vapi voice:** the voice screen uses the `@vapi-ai/web` SDK with the public key only, after creating a backend voice session; transcripts, mute/stop, permission and error states, and automatic fallback to text chat (doc 37).
- **Camera capture:** attendance verification and enrolment screens request camera permission explicitly, show quality hints and liveness prompts, handle denied/no camera, and never store frames locally (doc 14).
- All three features use Lucide icons, dark-only styling and the shared state patterns from doc 33.
