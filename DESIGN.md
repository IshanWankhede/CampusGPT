# CampusGPT — Landing Page Design System

This is a **build-ready design spec** for the CampusGPT marketing/landing page — a single-viewport, full-bleed, video-background hero page with retro dot-matrix display type, subtle glow, and orchestrated entrance animations. It adapts a proven design (see reference screenshot) to CampusGPT's subject matter, kept in **React** (matching the rest of the codebase) rather than vanilla JS.

> **How to use this file:** paste this entire document into your AI coding tool (Antigravity / Copilot / Claude) as the spec for `features/landing/`. It's self-contained — tokens, copy, animation timing, and component structure are all exact, so the output should need minimal correction.

---

## Table of Contents

1. [Assumptions & Adaptation Notes](#1-assumptions--adaptation-notes)
2. [Design Tokens](#2-design-tokens)
3. [Fonts](#3-fonts)
4. [Content (Exact Copy)](#4-content-exact-copy)
5. [Layout Composition](#5-layout-composition)
6. [Section Specs](#6-section-specs)
7. [Animation System](#7-animation-system)
8. [Mobile Behavior](#8-mobile-behavior)
9. [React Component / Folder Structure](#9-react-component--folder-structure)
10. [Where to Use React Bits & Skiper UI](#10-where-to-use-react-bits--skiper-ui)
11. [Implementation Notes for React](#11-implementation-notes-for-react)
12. [Visual Constraints — Do Not Deviate](#12-visual-constraints--do-not-deviate)
13. [3D Element: Floating Document Constellation](#13-3d-element-floating-document-constellation)

---

## 1. Assumptions & Adaptation Notes

The reference design was for a generic AI platform ("Intelligence Designed To Evolve"). Copy, stats, and trust-row content below are **rewritten for CampusGPT** (a campus AI assistant) while keeping the exact visual system — colors, fonts, spacing, animation timing, and structure — unchanged. If you want different copy, only Section 4 needs editing; everything else stays as-is.

---

## 2. Design Tokens

```css
:root {
  --bg: #000000;
  --text: #ffffff;
  --muted: #8e8e8e;
  --nav-text: #2e2e2e;
  --pill-dark: #28282a;
  --sign-in-text: #c8c8c8;
  --nav-shadow: 0 4px 14px rgba(0, 0, 0, 0.16);
  --trust-bg: #28282a;
  --trust-border: rgba(255, 255, 255, 0.4);
  --trust-text: #c4c2c3;
  --font-sans: "Inter", "Segoe UI", system-ui, sans-serif;
  --font-display: "BubbledotICG-FinePos", "Geist Pixel Circle", monospace;
}
```

Body: `background: #000`, `overflow: hidden`, `height: 100vh` / `100dvh` fallback, antialiased text.

---

## 3. Fonts

**Inter** (UI) — Google Fonts, weights 400/500/600:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
```

**BubbledotICG-FinePos** (primary display — retro dot-matrix), via OnlineWebFonts CDN — do not substitute a local Bubbledot file:
```html
<link
  href="https://db.onlinewebfonts.com/c/8cb707a9b8a73f8a7403336b861c3074?family=BubbledotICG-FinePos"
  rel="stylesheet"
/>
```
Family name exactly: `"BubbledotICG-FinePos"`

**Geist Pixel Circle** (fallback display only) — local `@font-face`:
```css
@font-face {
  font-family: "Geist Pixel Circle";
  src: url("/fonts/GeistPixel-Circle.woff2") format("woff2");
  font-weight: 400;
  font-display: swap;
}
```

**Font Awesome 6.5.2** (icons), from cdnjs:
```html
<link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"
  integrity="sha512-SnH5WK+bZxgPHs44uWIX+LLJAJ9/2PkPKZ5QiAj6Ta86w+fsb2TkcmfRyVX3pBnMFcV7oQPJkl9QevSCWr3W6A=="
  crossorigin="anonymous"
  referrerpolicy="no-referrer"
/>
```

---

## 4. Content (Exact Copy)

**Document title:** `CampusGPT — Intelligence For Every Classroom`

**Nav links:** `Home` (active) · `Dashboard` · `Documents` · `Contact`

**Sign-in button:** `Sign in`

**Trust row icons** (three overlapping rings, Font Awesome, department/role motif instead of enterprise brand logos):
1. `fa-solid fa-graduation-cap` (Students)
2. `fa-solid fa-chalkboard-user` (Faculty)
3. `fa-solid fa-building-columns` (Admin)

**Trust pill text:** `Trusted Across Every Department`

**Headline** (two lines, exact):
```
Ask Your Campus
Anything, Instantly
```

**Subhead** (exact):
```
Attendance, timetables, assignments, and course material —
answered in seconds by an AI that actually knows your campus.
```

**CTA button:** `Get Started`

**Stats footer** (four metrics, CampusGPT-relevant):

| Icon glyph | Target | Suffix | Decimals | Label |
|---|---|---|---|---|
| `<` | 400 | `ms` | 0 | Chat Response Time |
| `%` | 99.9 | `%` | 1 | Platform Uptime |
| `*` | 24 | `/7` | 0 | Assistant Availability |
| `#` | 10 | `K+` | 0 | Documents Indexed |

---

## 5. Layout Composition

Single viewport, no scroll, 3 vertical regions in a centered flex column:

```
.page (flex column, height: 100dvh, overflow: hidden,
       padding: clamp(16px, 2.4vh, 28px) clamp(14px, 3vw, 32px))
│
├── Header        (shrink 0, top)
├── Hero          (flex: 1, centered)
└── Stats footer  (shrink 0, bottom)
```

Background video sits behind everything at `z-index: 0`; header/hero/stats/mobile-menu at `z-index: 1`.

```
<div class="page">
  <video class="bg-video" autoplay muted loop playsinline>...</video>
  <header class="header anim" style="--d:0s">...</header>
  <main class="hero">
    <div class="trust-row anim" style="--d:0.05s">...</div>
    <h1 class="headline anim">...</h1>
    <p class="subhead anim" style="--d:0.28s">...</p>
    <a class="cta anim" style="--d:0.4s">Get Started</a>
  </main>
  <footer class="stats anim" style="--d:0.5s">...</footer>
  <div class="mobile-overlay" hidden>...</div>
</div>
```

---

## 6. Section Specs

### 6.1 Header (desktop)

Centered row, max-width `720px`, gap `clamp(18px, 2.8vw, 28px)`.

**Logo**
- Circular button `clamp(40px, 4.4vw, 46px)`, `border-radius: 50%`, white background `#fff`, shadow `var(--nav-shadow)`
- Image (CampusGPT mark) scaled to 72% width/height inside the circle via CSS grid centering, `object-fit: contain`
- Hover: `scale(1.04)`

**Nav pill (white)**
- White pill, height `clamp(44px, 5.2vw, 48px)`, max-width `430px`, flex 1, padding `4px 8px`, radius `999px`, shadow `var(--nav-shadow)`
- Links: Inter 500, `clamp(13px, 1.4vw, 15px)`, letter-spacing `-0.01em`, color `#2e2e2e`
- Opacity: default `0.5`, hover `0.75`, active `1`
- Active indicator: three 3×3px black dots under the label via `::after` + `box-shadow` offsets `-5px`/`+5px`, `bottom: 5px`

**Sign in**
- Dark pill `#28282a`, text `#c8c8c8`, same height as nav pill, radius `999px`, shadow `var(--nav-shadow)`
- Hover: bg `#323234`, text `#fff`, `translateY(-1px)`

**Entrance:** `slideDown 0.7s cubic-bezier(0.22, 1, 0.36, 1) both` (opacity 0, `translateY(-18px)` → settled)

### 6.2 Hero (center)

Column, text-center, max-width `900px`.

**Trust row**
- `--trust-size: clamp(36px, 4.5vw, 42px)` (34px at ≤420px), margin-bottom `clamp(16px, 2.5vh, 26px)`
- Three overlapping rings: outer `--trust-size`, bg `#28282a`, border `1px solid rgba(255,255,255,0.4)`, padding `5px`; inner white circle fills the padded area
- Icons black `#111`, font-size `calc(var(--trust-size) * 0.34)`
- Overlap: later avatars `margin-left: calc(var(--trust-size) * -0.42)`; z-index 1/2/4
- Hover lift: ring 1 `-2px`, ring 2 `-4px`, ring 3 `-2px` (0.35s)
- Trust pill overlaps the last ring: same height, bg `#28282a`, same border, radius `999px`, left margin `-0.42 * trust-size`, left padding `0.58 * trust-size`
- Pill text: Inter 500, `#c4c2c3`, `clamp(12px, 1.4vw, 13.5px)` (12px on mobile)

**Headline**
- Font: BubbledotICG-FinePos / Geist Pixel Circle fallback, solid white — **no gradient, no shimmer**
- Size: `clamp(28px, 6.2vw, 80px)`
- Letter-spacing: `-0.04em` desktop, `-0.08em` ≤720px, `-0.09em` ≤420px
- Line-height: 1.12 (1.05 at ≤720px, 1.04 at ≤420px)
- `white-space: nowrap`, overflow hidden per line
- Per-line fade: opacity 0 + `translateY(14px)` → `headlineFade 0.85s cubic-bezier(0.22, 1, 0.36, 1)`; line 1 delay `0.12s`, line 2 delay `0.3s`

**Subhead**
- Max-width `min(500px, 92%)`
- Font-size: `clamp(15.5px, calc(1.55vw + 2pt), 18.5px)`
- Color `#d0d0d0`, opacity `0.8`, line-height 1.55, weight 400
- Delay `--d: 0.28s`

**CTA**
- White pill, black text, Inter 600, `clamp(13.5px, 1.5vw, 14.5px)`
- Padding `clamp(11px, 1.6vh, 13px) clamp(22px, 3vw, 28px)`, radius `999px`
- Glow: `0 0 0 1px rgba(255,255,255,0.15), 0 0 22px rgba(255,255,255,0.32), 0 0 44px rgba(255,255,255,0.12)`
- Hover: `translateY(-2px) scale(1.02)` + stronger glow
- Entrance uses `revealPulse` (not the plain reveal), delay `--d: 0.4s`

### 6.3 Stats footer

Grid, 4 columns (2×2 at ≤720px), max-width `920px`. Each cell: icon (display font, white) → counting value → muted label.

- Icon size `clamp(22px, 3vw, 33px)`, BubbledotICG-FinePos
- Value: Inter, white, `clamp(18px, 2.2vw, 26px)`, letter-spacing `-0.025em`, tabular-nums
- Label: `#8e8e8e`, `clamp(11px, 1.2vw, 12.5px)`
- Stagger delays: `0.5s`, `0.58s`, `0.66s`, `0.74s`
- Count-up: easeOutCubic, duration `1500 + i*80` ms, start offset `480 + i*90` ms, fires once via `IntersectionObserver` at threshold `0.25`

---

## 7. Animation System

**Shared `.anim` entrance:**
- Start: opacity 0, `translateY(22px) scale(0.98)`, `blur(6px)`
- Animate: `reveal 0.85s cubic-bezier(0.22, 1, 0.36, 1) forwards`
- Delay from an inline CSS variable `--d`

**`prefers-reduced-motion: reduce`:** disable all animations, render final state immediately, headline stays solid white (no motion-dependent effect is load-bearing for meaning).

---

## 8. Mobile Behavior (≤720px)

- Hide desktop nav pill and desktop Sign-in button
- Header becomes `justify-content: space-between`; logo 48×48 left, circular burger 48×48 right (`#28282a` bg, three white 18×1.5px bars)
- Burger open state: bg turns white, bars morph into a black X (`translateY(±6.5px) rotate(±45deg)`)
- Overlay: fixed full-screen, `rgba(0,0,0,0.62)`, `backdrop-filter: blur(6px)`, `overlayIn 0.28s`
- White sheet menu: centered under header, radius `28px`, padding `22px 18px 20px`, shadow `0 20px 60px rgba(0,0,0,0.45)`, `menuIn 0.38s`
- Links: Home / Dashboard / Documents / Contact + full-width Sign in, staggered `linkIn`, active three-dot indicator at bottom `8px`
- Behavior: toggle `aria-expanded`, `hidden`, and `body.menu-open`; close on overlay click, `Escape`, link click, or resize to >720px
- Stats grid collapses to 2 columns
- Extra tweaks: headline/trust-row sizing at ≤420px; tighter hero spacing at ≤700px viewport height

---

## 9. React Component / Folder Structure

Following the feature-based frontend architecture in `ARCHITECTURE.md` §9, the landing page is its own feature:

```
frontend/src/
├── features/
│   └── landing/
│       ├── LandingPage.jsx            # top-level composition, renders the 3 regions
│       ├── components/
│       │   ├── BackgroundVideo.jsx    # <video> full-bleed layer, z-index 0
│       │   ├── Header.jsx             # desktop nav + mobile burger, composes the below
│       │   │   ├── Logo.jsx
│       │   │   ├── NavPill.jsx        # renders NavLink[] with active-dot indicator
│       │   │   ├── SignInButton.jsx
│       │   │   └── MobileMenu.jsx     # overlay + sheet, own open/close state
│       │   ├── Hero.jsx               # composes trust row + headline + subhead + CTA
│       │   │   ├── TrustRow.jsx       # overlapping rings + trust pill
│       │   │   ├── Headline.jsx       # two <span> lines, per-line fade
│       │   │   ├── Subhead.jsx
│       │   │   └── CtaButton.jsx
│       │   └── StatsFooter.jsx        # grid of StatItem, owns the IntersectionObserver
│       │       └── StatItem.jsx       # icon + count-up value + label
│       ├── hooks/
│       │   ├── useCountUp.js          # easeOutCubic count-up hook, IntersectionObserver-driven
│       │   └── useMobileMenu.js       # open state, escape/resize/outside-click handling
│       ├── landing.module.css         # or Tailwind config + a few custom keyframes
│       └── content.js                 # all copy + stats data (Section 4) as exported constants
├── assets/
│   └── logo.webp
└── fonts/
    └── GeistPixel-Circle.woff2
```

**Why this shape:**
- `content.js` isolates copy/stats as data, so rewriting headline/stats later never touches component logic — matches the "content as data" principle used elsewhere in the app (e.g. notices, assignments).
- `hooks/useCountUp.js` and `hooks/useMobileMenu.js` are extracted because both carry non-trivial imperative logic (`IntersectionObserver`, event listeners) that shouldn't live inline in JSX.
- Every visual sub-piece (`Logo`, `TrustRow`, `Headline`, `StatItem`) is its own component even though small, because each has independent animation delay/timing — keeping them separate makes the `--d` stagger values easy to reason about and tweak.

**Suggested `LandingPage.jsx` skeleton:**

```jsx
import BackgroundVideo from "./components/BackgroundVideo";
import Header from "./components/Header";
import Hero from "./components/Hero";
import StatsFooter from "./components/StatsFooter";
import "./landing.module.css";

export default function LandingPage() {
  return (
    <div className="page">
      <BackgroundVideo />
      <Header />
      <Hero />
      <StatsFooter />
    </div>
  );
}
```

---

## 10. Where to Use React Bits & Skiper UI

You mentioned wanting to bring in [React Bits](https://reactbits.dev) and [Skiper UI](https://skiper-ui.com) components for extra interactivity. Here's where they slot in naturally without fighting this spec's exact timing/positioning:

| Section | Stock element in this spec | React Bits / Skiper UI swap-in candidate |
|---|---|---|
| Headline | Per-line CSS fade (`headlineFade`) | React Bits **`SplitText`** or **`BlurText`** — for a per-character or per-word reveal instead of per-line, if you want more texture than the spec's two-line fade |
| CTA button | Static glow pill with hover lift | Skiper UI **glow/shine button** component — keep the exact colors/padding from §6.2 but swap in their shine-sweep interaction on hover |
| Trust row | Static overlapping rings | React Bits **`AnimatedTooltip`**-style hover card — lets each ring show a label ("Students", "Faculty", "Admin") on hover instead of only lifting |
| Stats footer | Custom `useCountUp` hook | React Bits **`CountUp`** — can replace the custom hook directly; keep your own `IntersectionObserver` trigger logic from §6.3 so stagger timing stays exact |
| Background | Plain `<video>` | Optionally layer a React Bits **`Particles`** or **`Aurora`** background *behind* the video at a very low opacity for extra depth — only if it doesn't compete with the video for attention |
| Mobile menu | CSS `overlayIn`/`menuIn` keyframes | Skiper UI **drawer/sheet** component — same visual spec (radius, shadow, padding) but their built-in focus-trap and swipe-to-close for free |

**Guidance on restraint:** per the design principles this project already follows (see `ARCHITECTURE.md`'s general "don't over-engineer early" philosophy), pick **one** of these swap-ins to start — the CTA glow button or the stats count-up are the lowest-risk, highest-payoff choices. Adding all six at once risks fighting the deliberately restrained, single-moment feel of the reference design (one bold element, everything else quiet).

---

## 11. Implementation Notes for React

- **Video autoplay:** `autoPlay muted loop playsInline` as JSX props (camelCase), and keep `muted` — browsers block autoplay with sound regardless of the `autoPlay` attribute.
- **CSS custom properties for stagger delays:** pass `style={{ "--d": "0.28s" }}` inline on each `.anim` element rather than hardcoding delays in the stylesheet — keeps `content.js`-driven stagger values (e.g. stats indices) computable in JS: `style={{ "--d": `${0.5 + i * 0.08}s` }}`.
- **IntersectionObserver in React:** wrap it in a `useEffect` inside `useCountUp.js`, observe a `ref` on the stats container, disconnect after first trigger (`once` behavior from §6.3), and clean up the observer on unmount.
- **`prefers-reduced-motion`:** check via `window.matchMedia("(prefers-reduced-motion: reduce)")` inside the same hook/effect, and skip both the CSS animation classes and the count-up tweening — jump values straight to their targets.
- **Font loading:** `<link>` tags for Google Fonts / OnlineWebFonts / Font Awesome go in `index.html`'s `<head>`, not injected via JS — avoids a flash of unstyled text on first paint.
- **Tailwind vs. CSS Modules:** this spec's values (many `clamp()` expressions, custom keyframes, CSS custom properties) are easiest expressed as a dedicated `landing.module.css` rather than forcing every clamp() into Tailwind's arbitrary-value syntax — reserve Tailwind for the rest of the app's dashboards, per `ARCHITECTURE.md` §9, and let this one landing page own its stylesheet.

---

## 12. Visual Constraints — Do Not Deviate

- No cards in the hero — one composition, single focal moment
- No gradient or shimmer animation on the headline — solid white only
- Display type is BubbledotICG-FinePos from OnlineWebFonts, not a local Bubbledot file
- Trust icons are small white/black inner circles inside dark padded rings, not full-bleed white outer discs
- Nav/logo shadow stays soft: `0 4px 14px rgba(0,0,0,0.16)` — never a heavy drop shadow
- First viewport must contain: header + trust row + headline + subhead + CTA + stats, all over the looping background video, with no scroll required

---

## 13. 3D Element: Floating Document Constellation

**Concept:** A slowly drifting cluster of thin, glowing card-planes — each representing an uploaded document/note — connected by faint lines that pulse when a "query" fires, visually echoing the RAG pipeline (retrieval pulling relevant chunks together). Sits as a depth layer, not a literal illustration.

**Where it lives:** Behind/beside the hero, not competing with the headline. Two valid placements:
- **Option A (recommended):** Positioned to the right/left of center, partially behind the headline text, at low opacity/blur — reads as atmosphere, not a competing focal point.
- **Option B:** Full-bleed behind everything, replacing or layered under `.bg-video` at very low opacity (~0.15–0.25) so the dot-matrix headline stays the clear focal point.

Start with Option A — safer against the "one bold element" restraint principle in Section 10.

### 13.1 Visual Spec

| Property | Value |
|---|---|
| Card count | 8–14 planes (fewer = calmer, more premium; more starts to look busy) |
| Card geometry | Thin `RoundedBox` or plane, ~`1.2 × 1.6 × 0.02` units, subtle rounded corners |
| Card material | `MeshTransmissionMaterial` or simple `MeshStandardMaterial` with low roughness, near-black `#0a0a0a` base, thin white-ish edge via a fresnel/rim shader or a simple `Edges` outline at `rgba(255,255,255,0.25)` |
| Card "content" | A few thin horizontal `Line` segments on the card face (suggesting text lines) — 3-4 lines, `#8e8e8e`, low opacity — do not render real text in 3D, too costly and unreadable at this scale |
| Connecting lines | `drei`'s `<Line>` between 3-5 nearest neighbor pairs, `#ffffff` at opacity `0.06–0.12` static, pulsing to `0.4` on trigger |
| Ambient motion | Each card has an independent slow float: `position.y` sine wave, tiny random rotation drift — no card should ever be fully still |
| Lighting | One soft key light + ambient, avoid dramatic shadows — keep it flat/moody like the reference video background, not a product-render |
| Color harmony | Everything stays in the existing token palette: black base, white/`#c4c2c3` accents — no new hues introduced |

### 13.2 Interaction: the "query pulse"

When the CTA button is clicked, or on a timed interval (~every 6-8s, subtle, non-distracting), trigger a "pulse":
1. Two or three cards nearest to a random "focal" point brighten (edge opacity → 0.6, brief scale-up to 1.03)
2. Connecting lines between them animate opacity 0.1 → 0.5 → 0.1 over ~1.2s
3. This should read as "the assistant just retrieved something" — a quiet, recurring ambient event, not a flashy effect

This directly reinforces the product's actual mechanism (RAG retrieval) rather than being decoration for its own sake.

### 13.3 React Three Fiber Component Structure

```
frontend/src/features/landing/components/
└── DocumentConstellation/
    ├── DocumentConstellation.jsx     # <Canvas> wrapper, camera, lighting setup
    ├── DocumentCard.jsx              # single floating card plane + float animation
    ├── ConnectionLines.jsx           # computes + renders nearest-neighbor lines
    ├── useQueryPulse.js              # interval + CTA-triggered pulse state
    └── constellationData.js          # card positions/seed data (deterministic, not random each render)
```

**`DocumentConstellation.jsx` skeleton:**

```jsx
import { Canvas } from "@react-three/fiber";
import { Suspense } from "react";
import DocumentCard from "./DocumentCard";
import ConnectionLines from "./ConnectionLines";
import { cardPositions } from "./constellationData";
import { useQueryPulse } from "./useQueryPulse";

export default function DocumentConstellation() {
  const activeIndices = useQueryPulse(cardPositions.length);

  return (
    <Canvas
      camera={{ position: [0, 0, 6], fov: 40 }}
      gl={{ alpha: true, antialias: true }}
      style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
    >
      <ambientLight intensity={0.4} />
      <directionalLight position={[3, 4, 5]} intensity={0.6} />
      <Suspense fallback={null}>
        {cardPositions.map((pos, i) => (
          <DocumentCard key={i} position={pos} active={activeIndices.includes(i)} />
        ))}
        <ConnectionLines positions={cardPositions} activeIndices={activeIndices} />
      </Suspense>
    </Canvas>
  );
}
```

**`DocumentCard.jsx` — the float animation:**

```jsx
import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { RoundedBox, Edges } from "@react-three/drei";

export default function DocumentCard({ position, active }) {
  const ref = useRef();
  const seed = useRef(Math.random() * Math.PI * 2);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() + seed.current;
    ref.current.position.y = position[1] + Math.sin(t * 0.4) * 0.15;
    ref.current.rotation.z = Math.sin(t * 0.25) * 0.03;
    const targetScale = active ? 1.03 : 1;
    ref.current.scale.lerp({ x: targetScale, y: targetScale, z: targetScale }, 0.08);
  });

  return (
    <group ref={ref} position={position}>
      <RoundedBox args={[1.2, 1.6, 0.02]} radius={0.06}>
        <meshStandardMaterial color="#0a0a0a" roughness={0.6} />
        <Edges color={active ? "#ffffff" : "#4a4a4a"} />
      </RoundedBox>
    </group>
  );
}
```

**`useQueryPulse.js` — the recurring highlight:**

```js
import { useEffect, useState } from "react";

export function useQueryPulse(cardCount, intervalMs = 7000) {
  const [activeIndices, setActiveIndices] = useState([]);

  useEffect(() => {
    const pulse = () => {
      const focal = Math.floor(Math.random() * cardCount);
      const neighbors = [focal, (focal + 1) % cardCount, (focal + 2) % cardCount];
      setActiveIndices(neighbors);
      setTimeout(() => setActiveIndices([]), 1200);
    };
    const id = setInterval(pulse, intervalMs);
    return () => clearInterval(id);
  }, [cardCount, intervalMs]);

  return activeIndices;
}
```

Wire the CTA button's `onClick` to also call an exposed `triggerPulse()` (lift the pulse state up or use a small event emitter/context) so clicking "Get Started" visibly "asks the constellation a question" — a nice moment of cause-and-effect between the 2D UI and the 3D layer.

### 13.4 Performance & Integration Notes

- **Don't block the background video.** `<Canvas>` renders with `pointer-events: none` and a transparent background (`gl={{ alpha: true }}`), layered at `z-index: 1` between the video (`z-index: 0`) and the header/hero text (`z-index: 2`) — bump the existing `z-index: 1` on header/hero/stats up by one to make room.
- **Mount cost:** lazy-load the whole `DocumentConstellation` component (`React.lazy` + `Suspense`) so it doesn't block first paint of the headline/CTA — the 3D layer can pop in a beat after the 2D content, which actually reads as intentional layering rather than a loading glitch.
- **Mobile:** disable or drastically simplify (drop to 4-5 cards, no pulse interval) below 720px — R3F scenes are expensive on mobile GPUs and this element is genuinely optional atmosphere, not load-bearing content. Gate with a `useMediaQuery` check and skip the `<Canvas>` mount entirely on small screens if performance testing shows jank.
- **Respect `prefers-reduced-motion`:** skip the float animation and pulse interval, render cards static, same rule as the 2D `.anim` system in Section 7.
- **GSAP/Framer Motion integration:** this component intentionally uses `useFrame` (R3F's own render loop) for the continuous float rather than GSAP/Framer — mixing animation systems for the same continuously-running motion causes sync issues. Reserve GSAP ScrollTrigger and Framer Motion for the 2D DOM layer (entrance reveals, scroll-linked sections elsewhere in the app) and keep this 3D scene self-contained.
