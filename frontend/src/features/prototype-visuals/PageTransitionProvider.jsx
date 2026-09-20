/**
 * PageTransitionProvider — Stairs preloader with correct timing.
 *
 * ✅ CORRECT flow:
 *   1. Call transitionTo("/path")
 *   2. Stairs panels sweep IN (covering entire screen)
 *   3. THEN React Router navigates — new page renders underneath (invisible)
 *   4. Stairs panels sweep OUT (revealing the new page cleanly)
 *
 * ❌ OLD (broken) flow:
 *   navigate() → new page flashes → stairs try to cover → too late
 *
 * Usage:
 *   const transitionTo = useTransitionNavigate();
 *   transitionTo("/auth");  // instead of navigate("/auth")
 */

import { useState, useCallback, createContext, useContext } from "react";
import { useNavigate } from "react-router-dom";
import StairsPreloader from "./StairsPreloader";

// ─── Timing (must match StairsPreloader config) ────────────────────────────
// Stairs IN total = (NUM_COLUMNS - 1) * ENTER_STAGGER + ENTER_DURATION
//                = (6 - 1) * 0.07s + 0.55s = 0.90s → 900ms
// Add 80ms buffer so last panel fully lands before we navigate
const STAIRS_IN_MS = 980;

// How long to hold the closed state before beginning exit
// (gives React time to render the new page underneath, usually one frame)
const HOLD_MS = 50;
// ───────────────────────────────────────────────────────────────────────────

const TransitionContext = createContext(null);

/**
 * Returns the transition-aware navigation function.
 * Use this everywhere instead of useNavigate() directly.
 */
export function useTransitionNavigate() {
  const ctx = useContext(TransitionContext);
  if (!ctx) {
    throw new Error("useTransitionNavigate must be used inside <PageTransitionProvider>");
  }
  return ctx.transitionTo;
}

/** @deprecated Use useTransitionNavigate() instead */
export const usePageTransition = () => useContext(TransitionContext);

export default function PageTransitionProvider({ children }) {
  const navigate = useNavigate();
  const [showPreloader, setShowPreloader] = useState(false);

  /**
   * Transition-aware navigation:
   * 1. Show stairs (animate IN)
   * 2. Wait until stairs fully cover screen
   * 3. Navigate (new page renders hidden underneath)
   * 4. Brief hold (one frame for React to commit)
   * 5. Hide stairs (animate OUT → new page revealed)
   */
  const transitionTo = useCallback(
    (path, options) => {
      // Don't double-trigger if already transitioning
      if (showPreloader) return;

      // Step 1: Cover the screen with stair panels
      setShowPreloader(true);

      // Step 2+3+4: Wait → Navigate → Hold → Exit
      setTimeout(() => {
        // Navigate while completely covered — user sees nothing
        navigate(path, options);

        setTimeout(() => {
          // Step 5: Reveal the new page by exiting stairs
          setShowPreloader(false);
        }, HOLD_MS);
      }, STAIRS_IN_MS);
    },
    [navigate, showPreloader]
  );

  return (
    <TransitionContext.Provider value={{ transitionTo, isTransitioning: showPreloader }}>
      {/* Stairs overlay — covers during transition */}
      <StairsPreloader isVisible={showPreloader} />
      {children}
    </TransitionContext.Provider>
  );
}
