/**
 * StairsPreloader — Skiper9 Stairs Preloader style
 * A cinematic staircase panel animation for page transitions.
 * Uses `motion` (Framer Motion / motion.dev) — already in this project.
 *
 * Panels slide UP from the bottom (enter), hold, then slide UP out from the top (exit).
 * Left-to-right stagger on enter, right-to-left stagger on exit.
 */

import { motion, AnimatePresence } from "motion/react";

// ─── Config ──────────────────────────────────────────────────────────────────
const NUM_COLUMNS = 6;
const PANEL_COLOR = "#0a0a0a"; // Near-black panel colour

// Enter animation per column (slide up from bottom)
const ENTER_DURATION = 0.55;
const ENTER_STAGGER = 0.07; // left → right

// Exit animation per column (slide up out the top)
const EXIT_DURATION = 0.55;
const EXIT_STAGGER = 0.065; // right → left (reversed)
const EXIT_HOLD_DELAY = 0.0; // extra delay before exit starts

// Cubic ease for the stair slide
const STAIR_EASE = [0.76, 0, 0.24, 1];
// ─────────────────────────────────────────────────────────────────────────────

/**
 * @param {boolean} isVisible - Show/hide the preloader
 */
export default function StairsPreloader({ isVisible }) {
  return (
    <AnimatePresence>
      {isVisible && (
        <div
          key="stairs-preloader-root"
          className="fixed inset-0 overflow-hidden pointer-events-none"
          style={{ zIndex: 9998 }}
          aria-hidden="true"
        >
          {Array.from({ length: NUM_COLUMNS }).map((_, i) => {
            const enterDelay = i * ENTER_STAGGER;
            // Exit: rightmost column exits first (reversed stagger)
            const exitDelay = (NUM_COLUMNS - 1 - i) * EXIT_STAGGER + EXIT_HOLD_DELAY;

            return (
              <motion.div
                key={`stair-${i}`}
                style={{
                  position: "absolute",
                  top: 0,
                  bottom: 0,
                  left: `${(i / NUM_COLUMNS) * 100}%`,
                  width: `${100 / NUM_COLUMNS}%`,
                  backgroundColor: PANEL_COLOR,
                  // Use transformOrigin for scaleY — enter from bottom, exit from top
                  originY: "100%",
                }}
                initial={{ scaleY: 0 }}
                animate={{
                  scaleY: 1,
                  originY: "100%",
                  transition: {
                    duration: ENTER_DURATION,
                    delay: enterDelay,
                    ease: STAIR_EASE,
                  },
                }}
                exit={{
                  scaleY: 0,
                  originY: "0%",
                  transition: {
                    duration: EXIT_DURATION,
                    delay: exitDelay,
                    ease: STAIR_EASE,
                  },
                }}
              />
            );
          })}
        </div>
      )}
    </AnimatePresence>
  );
}
