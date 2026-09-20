import { jsx, jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { motion } from "motion/react";
import DotField from "./DotField";
import Strands from "./Strands";
import SpecularButton from "./SpecularButton";
import FloatingNav from "./FloatingNav";
const LandingPage = ({
  onNavigate = (_s) => {
  },
  onGetStarted,
  onSignIn
}) => {
  // mobile menu removed — FloatingNav handles all navigation
  const [countProgress, setCountProgress] = useState(0);
  const handleNav = (screen) => {
    if (screen === "auth") {
      if (onGetStarted) {
        onGetStarted();
        return;
      }
      if (onSignIn) {
        onSignIn();
        return;
      }
    }
    if (typeof onNavigate === "function") {
      onNavigate(screen);
    }
  };
  useEffect(() => {
    const startTime = Date.now();
    const duration = 1800;
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(1, elapsed / duration);
      setCountProgress(progress);
      if (progress >= 1) clearInterval(interval);
    }, 25);
    return () => clearInterval(interval);
  }, []);
  const responseTimeVal = Math.round(100 + countProgress * 280);
  const uptimeVal = (90 + countProgress * 9.9).toFixed(1);
  const docsVal = Math.round(countProgress * 10);
  return /* @__PURE__ */ jsxs(
    "div",
    {
      id: "landing-screen",
      className: "relative w-full min-h-screen overflow-x-hidden bg-black text-white flex flex-col justify-between select-none",
      children: [
        /* @__PURE__ */ jsxs("div", { className: "absolute inset-0 z-0 pointer-events-none overflow-hidden", children: [
          /* @__PURE__ */ jsx("div", { className: "absolute inset-0 z-[2] pointer-events-none opacity-85", children: /* @__PURE__ */ jsx(
            Strands,
            {
              colors: ["#F97316", "#7C3AED", "#06B6D4"],
              count: 2,
              speed: 0.45,
              amplitude: 1,
              waviness: 1,
              thickness: 0.7,
              glow: 2.6,
              taper: 2.2,
              spread: 0.8,
              intensity: 0.75,
              saturation: 1.5,
              opacity: 0.9,
              scale: 1.2,
              yOffset: -0.3,
              glass: false
            }
          ) }),
          /* @__PURE__ */ jsx("div", { className: "absolute inset-0 z-[1] opacity-60", children: /* @__PURE__ */ jsx(
            DotField,
            {
              dotRadius: 1.5,
              dotSpacing: 15,
              bulgeStrength: 67,
              glowRadius: 160,
              sparkle: true,
              waveAmplitude: 1.2,
              gradientFrom: "rgba(255, 255, 255, 0.45)",
              gradientTo: "rgba(168, 85, 247, 0.25)",
              glowColor: "#28282a"
            }
          ) }),
          /* @__PURE__ */ jsx(
            "video",
            {
              autoPlay: true,
              loop: true,
              muted: true,
              playsInline: true,
              className: "w-full h-full object-cover opacity-25 filter blur-[1px] brightness-75 scale-105",
              poster: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1920&auto=format&fit=crop&q=80",
              children: /* @__PURE__ */ jsx(
                "source",
                {
                  src: "https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-screens-with-charts-and-data-31913-large.mp4",
                  type: "video/mp4"
                }
              )
            }
          ),
          /* @__PURE__ */ jsx("div", { className: "absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_40%,rgba(35,35,45,0.45),rgba(0,0,0,0.95))]" }),
          /* @__PURE__ */ jsx("div", { className: "absolute inset-0 bg-black/55 backdrop-blur-[2px]" })
        ] }),
        /* @__PURE__ */ jsx("header", { className: "relative z-20 w-full pt-6 md:pt-8 px-4 flex justify-center", children: /* @__PURE__ */ jsxs(
          motion.div,
          {
            initial: { opacity: 0, y: -16 },
            animate: { opacity: 1, y: 0 },
            transition: { duration: 0.6, ease: "easeOut" },
            className: "w-full max-w-[760px] flex items-center justify-between gap-4",
            children: [
              /* @__PURE__ */ jsx(
                "button",
                {
                  id: "landing-logo-btn",
                  onClick: () => handleNav("landing"),
                  className: "shrink-0 w-11 h-11 rounded-full bg-white flex items-center justify-center text-black font-black shadow-lg hover:scale-105 active:scale-95 transition-transform",
                  title: "CampusGPT Home",
                  children: /* @__PURE__ */ jsx("span", { className: "text-lg tracking-tighter font-extrabold flex items-center justify-center", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-graduation-cap text-base" }) })
                }
              ),
              /* @__PURE__ */ jsx(FloatingNav, { onNavigate: handleNav }),
              /* @__PURE__ */ jsx(
                "button",
                {
                  id: "landing-signin-btn",
                  onClick: () => handleNav("auth"),
                  className: "shrink-0 bg-[#28282a] hover:bg-[#343438] text-[#c8c8c8] hover:text-white px-5 py-2 rounded-full text-sm font-medium border border-white/10 transition-colors active:scale-95 cursor-pointer",
                  children: "Sign in"
                }
              )
            ]
          }
        ) }),

        /* @__PURE__ */ jsxs("main", { id: "home", className: "relative z-10 w-full max-w-4xl mx-auto px-4 text-center flex flex-col items-center justify-center my-auto py-6 scroll-mt-24", children: [
          /* @__PURE__ */ jsxs(
            motion.div,
            {
              initial: { opacity: 0, y: 15 },
              animate: { opacity: 1, y: 0 },
              transition: { duration: 0.5, delay: 0.15 },
              className: "flex items-center mb-6",
              children: [
                /* @__PURE__ */ jsxs("div", { className: "flex items-center -space-x-2.5 mr-[-10px] z-10", children: [
                  /* @__PURE__ */ jsx("div", { className: "w-8 h-8 rounded-full bg-[#1c1c1e] border-2 border-black flex items-center justify-center text-xs text-white/90 shadow-md", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-graduation-cap" }) }),
                  /* @__PURE__ */ jsx("div", { className: "w-8 h-8 rounded-full bg-[#242428] border-2 border-black flex items-center justify-center text-xs text-white/90 shadow-md", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-chalkboard-user" }) }),
                  /* @__PURE__ */ jsx("div", { className: "w-8 h-8 rounded-full bg-[#2d2d32] border-2 border-black flex items-center justify-center text-xs text-white/90 shadow-md", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-building-columns" }) })
                ] }),
                /* @__PURE__ */ jsx("div", { className: "bg-[var(--trust-bg)] border border-[var(--trust-border)] text-[var(--trust-text)] text-xs font-medium pl-6 pr-4 py-1.5 rounded-full shadow-lg backdrop-blur-sm", children: "Trusted Across Every Department" })
              ]
            }
          ),
          /* @__PURE__ */ jsxs(
            motion.h1,
            {
              initial: { opacity: 0, y: 20 },
              animate: { opacity: 1, y: 0 },
              transition: { duration: 0.7, delay: 0.25 },
              className: "font-display text-white tracking-wider text-4xl sm:text-5xl md:text-6xl lg:text-[76px] xl:text-[82px] leading-[1.08] text-center mb-5 uppercase select-none",
              children: [
                /* @__PURE__ */ jsx("span", { className: "block", children: "Ask Your Campus" }),
                /* @__PURE__ */ jsx("span", { className: "block mt-1", children: "Anything, Instantly" })
              ]
            }
          ),
          /* @__PURE__ */ jsx(
            motion.p,
            {
              initial: { opacity: 0, y: 15 },
              animate: { opacity: 1, y: 0 },
              transition: { duration: 0.6, delay: 0.35 },
              className: "text-[var(--muted)] text-sm sm:text-base md:text-lg max-w-[510px] mx-auto mb-8 leading-relaxed font-normal",
              children: "Attendance, timetables, assignments, and course material \u2014 answered in seconds by an AI that actually knows your campus."
            }
          ),
          /* @__PURE__ */ jsx(
            motion.div,
            {
              initial: { opacity: 0, y: 15 },
              animate: { opacity: 1, y: 0 },
              transition: { duration: 0.6, delay: 0.45 },
              children: /* @__PURE__ */ jsxs(
                SpecularButton,
                {
                  id: "landing-get-started-btn",
                  onClick: () => handleNav("auth"),
                  size: "lg",
                  radius: 28,
                  tint: "#ffffff",
                  tintOpacity: 1,
                  textColor: "#000000",
                  lineColor: "#ffffff",
                  baseColor: "#e0e0e0",
                  intensity: 1.2,
                  shineSize: 12,
                  shineFade: 35,
                  thickness: 1.5,
                  speed: 0.4,
                  followMouse: true,
                  proximity: 260,
                  className: "font-semibold text-base sm:text-lg shadow-[0_0_35px_rgba(255,255,255,0.45)] hover:shadow-[0_0_55px_rgba(255,255,255,0.7)] transition-all cursor-pointer",
                  children: [
                    /* @__PURE__ */ jsx("span", { children: "Get Started" }),
                    /* @__PURE__ */ jsx("i", { className: "fa-solid fa-arrow-right text-sm ml-1" })
                  ]
                }
              )
            }
          )
        ] }),
        /* @__PURE__ */ jsx("footer", { id: "features", className: "relative z-20 w-full max-w-5xl mx-auto px-6 pb-6 md:pb-8 pt-6 shrink-0 scroll-mt-24", children: /* @__PURE__ */ jsxs(
          motion.div,
          {
            initial: { opacity: 0, y: 20 },
            animate: { opacity: 1, y: 0 },
            transition: { duration: 0.7, delay: 0.55 },
            className: "grid grid-cols-2 md:grid-cols-4 gap-6 text-center border-t border-white/10 pt-6",
            children: [
              /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center", children: [
                /* @__PURE__ */ jsx("div", { className: "text-white/60 mb-1 text-sm", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-bolt" }) }),
                /* @__PURE__ */ jsxs("div", { className: "font-display text-2xl sm:text-3xl lg:text-4xl text-white font-bold tracking-wider", children: [
                  "< ",
                  responseTimeVal,
                  "ms"
                ] }),
                /* @__PURE__ */ jsx("div", { className: "text-[var(--muted)] text-xs sm:text-sm mt-1", children: "Chat Response Time" })
              ] }),
              /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center", children: [
                /* @__PURE__ */ jsx("div", { className: "text-white/60 mb-1 text-sm", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-shield-halved" }) }),
                /* @__PURE__ */ jsxs("div", { className: "font-display text-2xl sm:text-3xl lg:text-4xl text-white font-bold tracking-wider", children: [
                  uptimeVal,
                  "%"
                ] }),
                /* @__PURE__ */ jsx("div", { className: "text-[var(--muted)] text-xs sm:text-sm mt-1", children: "Platform Uptime" })
              ] }),
              /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center", children: [
                /* @__PURE__ */ jsx("div", { className: "text-white/60 mb-1 text-sm", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-clock" }) }),
                /* @__PURE__ */ jsx("div", { className: "font-display text-2xl sm:text-3xl lg:text-4xl text-white font-bold tracking-wider", children: "24/7" }),
                /* @__PURE__ */ jsx("div", { className: "text-[var(--muted)] text-xs sm:text-sm mt-1", children: "Assistant Availability" })
              ] }),
              /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center", children: [
                /* @__PURE__ */ jsx("div", { className: "text-white/60 mb-1 text-sm", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-folder-open" }) }),
                /* @__PURE__ */ jsxs("div", { className: "font-display text-2xl sm:text-3xl lg:text-4xl text-white font-bold tracking-wider", children: [
                  docsVal,
                  "K+"
                ] }),
                /* @__PURE__ */ jsx("div", { className: "text-[var(--muted)] text-xs sm:text-sm mt-1", children: "Documents Indexed" })
              ] })
            ]
          }
        ) })
      ]
    }
  );
};
export {
  LandingPage
};
