/**
 * PageTransitionProvider — Stairs preloader triggered on every route change.
 *
 * How it works:
 * 1. On route change: stair panels animate IN (covering the screen)
 * 2. After stair-in delay: React Router has swapped the new page underneath
 * 3. Stair panels animate OUT (revealing the new page)
 *
 * The preloader sits on top (z-9999) so the new page loads underneath invisibly.
 */

import { useState, useEffect, useRef, createContext, useContext, useCallback } from "react";
import { useLocation } from "react-router-dom";
import StairsPreloader from "./StairsPreloader";

const TransitionContext = createContext({ isTransitioning: false });
export const usePageTransition = () => useContext(TransitionContext);

// Time (ms) to keep stairs IN before hiding (triggering exit animation)
// Enter total = (NUM_COLUMNS - 1) * ENTER_STAGGER + ENTER_DURATION
// = (6 - 1) * 0.07s + 0.55s = 0.90s = ~900ms
// Add 50ms buffer to let last panel fully land
const STAIRS_IN_DURATION_MS = 950;

export default function PageTransitionProvider({ children }) {
  const location = useLocation();
  const prevPathname = useRef(location.pathname);
  const [showPreloader, setShowPreloader] = useState(false);
  const holdTimerRef = useRef(null);

  useEffect(() => {
    // Skip the very first mount
    if (location.pathname === prevPathname.current) return;
    prevPathname.current = location.pathname;

    // Show the stair panels
    setShowPreloader(true);

    // After the stair-in animation finishes, begin exit
    // (The new route has already rendered underneath by now)
    if (holdTimerRef.current) clearTimeout(holdTimerRef.current);
    holdTimerRef.current = setTimeout(() => {
      setShowPreloader(false);
    }, STAIRS_IN_DURATION_MS);

    return () => {
      if (holdTimerRef.current) clearTimeout(holdTimerRef.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  const handlePreloaderComplete = useCallback(() => {
    // All columns have exited — fully done
    // (already hidden by showPreloader = false above)
  }, []);

  return (
    <TransitionContext.Provider value={{ isTransitioning: showPreloader }}>
      {/* Stairs overlay — covers the page during transition */}
      <StairsPreloader
        isVisible={showPreloader}
        onComplete={handlePreloaderComplete}
      />
      {/* Render the current route — new page loads underneath the stairs */}
      {children}
    </TransitionContext.Provider>
  );
}
