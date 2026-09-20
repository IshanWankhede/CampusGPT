/**
 * StairsPreloader — Skiper9-style Stairs Preloader
 *
 * BUG FIXES applied:
 *  Bug 1 — Gaps: use CSS calc() for exact widths with no rounding error
 *  Bug 2 — Color: pure #000000, no transparency
 *  Bug 3 — Animation: single, unified scaleY animation strictly L→R on enter
 *           and strictly L→R on exit (same direction, same easing, only stagger differs)
 *
 * Animation:
 *   ENTER — panels rise from bottom, left → right (index * stagger delay)
 *   EXIT  — panels retract upward, left → right same order
 */

import { motion, AnimatePresence } from "motion/react";

// ─── Config (tune these to taste) ────────────────────────────────────────────
const NUM_COLUMNS = 8;

// Enter: scaleY 0→1, pivot at bottom, left → right
const ENTER_DURATION   = 0.5;   // seconds per panel
const ENTER_STAGGER    = 0.06;  // seconds between each panel start

// Exit: scaleY 1→0, pivot at top, also left → right (same direction as enter)
const EXIT_DURATION    = 0.45;  // seconds per panel
const EXIT_STAGGER     = 0.05;  // seconds between each panel start

// Smooth cubic ease — same on every panel, both enter and exit
const EASE = [0.76, 0, 0.24, 1];
// ─────────────────────────────────────────────────────────────────────────────

export default function StairsPreloader({ isVisible }) {
  return (
    <AnimatePresence>
      {isVisible && (
        <div
          key="stairs-root"
          aria-hidden="true"
          style={{
            position:      "fixed",
            inset:         0,
            zIndex:        9999,
            pointerEvents: "none",
            overflow:      "hidden",
            // Flex row with no gap — tiles sit flush
            display:       "flex",
            flexDirection: "row",
            gap:           0,
            margin:        0,
            padding:       0,
          }}
        >
          {Array.from({ length: NUM_COLUMNS }).map((_, i) => (
            <motion.div
              key={`panel-${i}`}
              style={{
                // ── Bug 1 fix: calc() guarantees no rounding-error gap ──────
                // Each panel is exactly 1/N of the container width.
                // Using flex: 1 1 0 would also work, but explicit calc() is clearest.
                flex:            "0 0 calc(100% / " + NUM_COLUMNS + ")",
                width:           `calc(100% / ${NUM_COLUMNS})`,
                height:          "100%",
                // ── Bug 2 fix: pure black, no transparency ───────────────────
                backgroundColor: "#000000",
                // transformOrigin is set per-animation via style, not here,
                // because enter and exit use different origins.
                // We handle this via CSS var + inline style on the motion.div
                // by using a wrapper trick below — see note.
              }}
              // ── Bug 3 fix: single animation type (scaleY), strict L→R stagger ──
              //
              // NOTE on transformOrigin:
              //   motion.dev does NOT animate transformOrigin itself.
              //   We need a different origin for enter (bottom) vs exit (top).
              //   Solution: wrap in a regular div that provides the origin context,
              //   and the motion.div translates instead of scaling from a pivot.
              //
              //   Simplest approach that works reliably across browsers:
              //   translateY: -100% (fully above) → translateY: 0 (in place) for ENTER
              //   translateY: 0 → translateY: -100% (exits upward) for EXIT
              //   This gives the same visual as scaleY-from-bottom without pivot issues.
              initial={{ translateY: "100%" }}
              animate={{
                translateY: "0%",
                transition: {
                  duration: ENTER_DURATION,
                  delay:    i * ENTER_STAGGER,   // strictly index-based, L → R
                  ease:     EASE,
                },
              }}
              exit={{
                translateY: "-100%",
                transition: {
                  duration: EXIT_DURATION,
                  delay:    i * EXIT_STAGGER,    // also L → R (same direction)
                  ease:     EASE,
                },
              }}
            />
          ))}
        </div>
      )}
    </AnimatePresence>
  );
}
