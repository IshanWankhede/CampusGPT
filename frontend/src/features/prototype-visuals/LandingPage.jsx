import { jsx, jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import DotField from "./DotField";
import Strands from "./Strands";
import SpecularButton from "./SpecularButton";
const LandingPage = ({
  onNavigate = (_s) => {
  },
  onGetStarted,
  onSignIn
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
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
      className: "relative w-full min-h-screen overflow-x-hidden overflow-y-auto bg-black text-white flex flex-col justify-between select-none",
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
          /* @__PURE__ */ jsx("div", { className: "absolute inset-0 bg-black/55 backdrop-blur-[2px]" }),
          /* @__PURE__ */ jsxs("div", { className: "absolute inset-0 overflow-hidden pointer-events-none opacity-30 z-0", children: [
            /* @__PURE__ */ jsxs("svg", { className: "absolute w-full h-full", xmlns: "http://www.w3.org/2000/svg", children: [
              /* @__PURE__ */ jsx("line", { x1: "28%", y1: "36%", x2: "38%", y2: "44%", stroke: "rgba(255,255,255,0.15)", strokeDasharray: "3 3" }),
              /* @__PURE__ */ jsx("line", { x1: "38%", y1: "44%", x2: "68%", y2: "34%", stroke: "rgba(255,255,255,0.12)", strokeDasharray: "3 3" }),
              /* @__PURE__ */ jsx("line", { x1: "68%", y1: "34%", x2: "78%", y2: "48%", stroke: "rgba(255,255,255,0.15)", strokeDasharray: "3 3" })
            ] }),
            /* @__PURE__ */ jsxs(
              "div",
              {
                className: "absolute top-[28%] left-[18%] md:left-[24%] w-28 md:w-36 h-36 md:h-44 rounded-xl border border-white/20 bg-white/[0.03] backdrop-blur-md p-3 animate-float-1 hidden sm:block",
                style: { boxShadow: "0 0 35px rgba(255,255,255,0.06)" },
                children: [
                  /* @__PURE__ */ jsx("div", { className: "w-5 h-1.5 rounded-full bg-white/40 mb-3" }),
                  /* @__PURE__ */ jsx("div", { className: "w-full h-1 bg-white/20 rounded mb-1.5" }),
                  /* @__PURE__ */ jsx("div", { className: "w-3/4 h-1 bg-white/20 rounded mb-1.5" }),
                  /* @__PURE__ */ jsx("div", { className: "w-5/6 h-1 bg-white/20 rounded mb-4" }),
                  /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-1.5 text-[9px] text-white/50 font-mono", children: [
                    /* @__PURE__ */ jsx("i", { className: "fa-solid fa-file-lines text-xs text-white/70" }),
                    /* @__PURE__ */ jsx("span", { children: "Syllabus.pdf" })
                  ] })
                ]
              }
            ),
            /* @__PURE__ */ jsxs(
              "div",
              {
                className: "absolute top-[32%] right-[16%] md:right-[22%] w-32 md:w-40 h-44 md:h-52 rounded-xl border border-white/25 bg-white/[0.04] backdrop-blur-md p-3.5 animate-float-2 hidden sm:block",
                style: { boxShadow: "0 0 45px rgba(255,255,255,0.08)" },
                children: [
                  /* @__PURE__ */ jsx("div", { className: "w-7 h-1.5 rounded-full bg-white/50 mb-3" }),
                  /* @__PURE__ */ jsx("div", { className: "w-full h-1 bg-white/25 rounded mb-2" }),
                  /* @__PURE__ */ jsx("div", { className: "w-4/5 h-1 bg-white/25 rounded mb-2" }),
                  /* @__PURE__ */ jsx("div", { className: "w-2/3 h-1 bg-white/25 rounded mb-4" }),
                  /* @__PURE__ */ jsxs("div", { className: "p-1.5 rounded bg-white/10 text-[9px] text-white/70 font-mono flex items-center justify-between", children: [
                    /* @__PURE__ */ jsx("span", { children: "Vector Chunk" }),
                    /* @__PURE__ */ jsx("span", { className: "text-[8px] bg-white/20 px-1 py-0.5 rounded", children: "98%" })
                  ] })
                ]
              }
            ),
            /* @__PURE__ */ jsxs(
              "div",
              {
                className: "absolute bottom-[24%] left-[45%] w-24 h-32 rounded-lg border border-white/15 bg-white/[0.02] backdrop-blur-sm p-2.5 animate-float-3 hidden lg:block",
                children: [
                  /* @__PURE__ */ jsx("div", { className: "w-4 h-1 bg-white/30 rounded mb-2" }),
                  /* @__PURE__ */ jsx("div", { className: "w-full h-1 bg-white/15 rounded mb-1" }),
                  /* @__PURE__ */ jsx("div", { className: "w-2/3 h-1 bg-white/15 rounded mb-2" }),
                  /* @__PURE__ */ jsx("div", { className: "text-[8px] text-white/40 font-mono", children: "Attendance.sql" })
                ]
              }
            )
          ] })
        ] }),
        /* @__PURE__ */ jsx("header", { className: "relative z-20 w-full pt-6 md:pt-8 px-4 flex justify-center", children: /* @__PURE__ */ jsxs(
          motion.div,
          {
            initial: { opacity: 0, y: -16 },
            animate: { opacity: 1, y: 0 },
            transition: { duration: 0.6, ease: "easeOut" },
            className: "w-full max-w-[720px] flex items-center justify-between",
            children: [
              /* @__PURE__ */ jsx(
                "button",
                {
                  id: "landing-logo-btn",
                  onClick: () => handleNav("landing"),
                  className: "w-11 h-11 rounded-full bg-white flex items-center justify-center text-black font-black shadow-lg hover:scale-105 active:scale-95 transition-transform",
                  title: "CampusGPT Home",
                  children: /* @__PURE__ */ jsx("span", { className: "text-lg tracking-tighter font-extrabold flex items-center justify-center", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-graduation-cap text-base" }) })
                }
              ),
              /* @__PURE__ */ jsxs(
                "nav",
                {
                  id: "landing-desktop-nav",
                  className: "hidden md:flex items-center bg-white text-[#2e2e2e] rounded-full px-5 py-2 nav-card-shadow text-sm font-medium space-x-7",
                  children: [
                    /* @__PURE__ */ jsxs("div", { className: "relative flex flex-col items-center cursor-pointer group", children: [
                      /* @__PURE__ */ jsx("span", { className: "text-black font-semibold text-[14px]", children: "Home" }),
                      /* @__PURE__ */ jsxs("div", { className: "flex gap-[3px] mt-0.5", children: [
                        /* @__PURE__ */ jsx("span", { className: "w-1 h-1 rounded-full bg-black" }),
                        /* @__PURE__ */ jsx("span", { className: "w-1 h-1 rounded-full bg-black" }),
                        /* @__PURE__ */ jsx("span", { className: "w-1 h-1 rounded-full bg-black" })
                      ] })
                    ] }),
                    /* @__PURE__ */ jsx(
                      "button",
                      {
                        onClick: () => handleNav("auth"),
                        className: "text-[#2e2e2e] hover:text-black transition-colors font-medium text-[14px] cursor-pointer",
                        children: "Dashboard"
                      }
                    ),
                    /* @__PURE__ */ jsx(
                      "button",
                      {
                        onClick: () => handleNav("documents"),
                        className: "text-[#2e2e2e] hover:text-black transition-colors font-medium text-[14px] cursor-pointer",
                        children: "Documents"
                      }
                    ),
                    /* @__PURE__ */ jsx(
                      "button",
                      {
                        onClick: () => handleNav("chat"),
                        className: "text-[#2e2e2e] hover:text-black transition-colors font-medium text-[14px] cursor-pointer",
                        children: "Contact"
                      }
                    )
                  ]
                }
              ),
              /* @__PURE__ */ jsx("div", { className: "hidden md:flex items-center", children: /* @__PURE__ */ jsx(
                "button",
                {
                  id: "landing-signin-btn",
                  onClick: () => handleNav("auth"),
                  className: "bg-[#28282a] hover:bg-[#343438] text-[#c8c8c8] hover:text-white px-5 py-2 rounded-full text-sm font-medium border border-white/10 transition-colors active:scale-95 cursor-pointer",
                  children: "Sign in"
                }
              ) }),
              /* @__PURE__ */ jsx(
                "button",
                {
                  id: "landing-mobile-burger",
                  onClick: () => setMobileMenuOpen(true),
                  className: "md:hidden w-11 h-11 rounded-full bg-[#28282a] border border-white/15 text-white flex items-center justify-center active:scale-95 transition-transform",
                  "aria-label": "Open Navigation Menu",
                  children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-bars text-sm" })
                }
              )
            ]
          }
        ) }),
        /* @__PURE__ */ jsx(AnimatePresence, { children: mobileMenuOpen && /* @__PURE__ */ jsx(
          motion.div,
          {
            initial: { opacity: 0 },
            animate: { opacity: 1 },
            exit: { opacity: 0 },
            className: "fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex flex-col justify-end p-4 md:hidden",
            onClick: () => setMobileMenuOpen(false),
            children: /* @__PURE__ */ jsxs(
              motion.div,
              {
                initial: { y: 50, opacity: 0 },
                animate: { y: 0, opacity: 1 },
                exit: { y: 50, opacity: 0 },
                className: "bg-white text-[#2e2e2e] rounded-[24px] p-6 w-full max-w-sm mx-auto nav-card-shadow",
                onClick: (e) => e.stopPropagation(),
                children: [
                  /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between pb-4 border-b border-gray-100", children: [
                    /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-2", children: [
                      /* @__PURE__ */ jsx("div", { className: "w-8 h-8 rounded-full bg-black text-white flex items-center justify-center text-xs", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-graduation-cap" }) }),
                      /* @__PURE__ */ jsx("span", { className: "font-bold text-black tracking-tight", children: "CampusGPT" })
                    ] }),
                    /* @__PURE__ */ jsx(
                      "button",
                      {
                        onClick: () => setMobileMenuOpen(false),
                        className: "w-8 h-8 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center",
                        children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-xmark text-sm" })
                      }
                    )
                  ] }),
                  /* @__PURE__ */ jsxs("div", { className: "flex flex-col space-y-3 py-5", children: [
                    /* @__PURE__ */ jsxs(
                      "button",
                      {
                        onClick: () => {
                          setMobileMenuOpen(false);
                          handleNav("landing");
                        },
                        className: "text-left font-semibold text-black py-2 px-3 rounded-lg bg-gray-50 flex items-center justify-between",
                        children: [
                          /* @__PURE__ */ jsx("span", { children: "Home" }),
                          /* @__PURE__ */ jsxs("div", { className: "flex gap-1", children: [
                            /* @__PURE__ */ jsx("span", { className: "w-1.5 h-1.5 rounded-full bg-black" }),
                            /* @__PURE__ */ jsx("span", { className: "w-1.5 h-1.5 rounded-full bg-black" }),
                            /* @__PURE__ */ jsx("span", { className: "w-1.5 h-1.5 rounded-full bg-black" })
                          ] })
                        ]
                      }
                    ),
                    /* @__PURE__ */ jsx(
                      "button",
                      {
                        onClick: () => {
                          setMobileMenuOpen(false);
                          handleNav("auth");
                        },
                        className: "text-left font-medium text-gray-700 hover:text-black py-2 px-3 rounded-lg",
                        children: "Dashboard"
                      }
                    ),
                    /* @__PURE__ */ jsx(
                      "button",
                      {
                        onClick: () => {
                          setMobileMenuOpen(false);
                          handleNav("documents");
                        },
                        className: "text-left font-medium text-gray-700 hover:text-black py-2 px-3 rounded-lg",
                        children: "Documents"
                      }
                    ),
                    /* @__PURE__ */ jsx(
                      "button",
                      {
                        onClick: () => {
                          setMobileMenuOpen(false);
                          handleNav("chat");
                        },
                        className: "text-left font-medium text-gray-700 hover:text-black py-2 px-3 rounded-lg",
                        children: "CampusGPT Chat"
                      }
                    )
                  ] }),
                  /* @__PURE__ */ jsx(
                    "button",
                    {
                      onClick: () => {
                        setMobileMenuOpen(false);
                        handleNav("auth");
                      },
                      className: "w-full bg-[#28282a] text-[#c8c8c8] hover:text-white py-3 rounded-full text-sm font-semibold transition-colors mt-2 text-center",
                      children: "Sign in"
                    }
                  )
                ]
              }
            )
          }
        ) }),
        /* @__PURE__ */ jsxs("main", { className: "relative z-10 w-full max-w-4xl mx-auto px-4 text-center flex flex-col items-center justify-center my-auto py-6", children: [
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
        /* @__PURE__ */ jsx("footer", { className: "relative z-20 w-full max-w-5xl mx-auto px-6 pb-6 md:pb-8 pt-6 shrink-0", children: /* @__PURE__ */ jsxs(
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
