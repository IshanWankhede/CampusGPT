import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import DotField from "./DotField";
import Strands from "./Strands";
import SpecularButton from "./SpecularButton";
import FloatingNav from "./FloatingNav";
import StarBorder from "./StarBorder";
import ScrollVelocity from "./ScrollVelocity";

const PREVIEW_SAMPLES = [
  {
    id: "timetable",
    label: "Timetable & Classrooms",
    question: "Where is my DBMS lecture today?",
    response: "Your Database Management Systems lecture is scheduled at 10:00 AM in Room 402, Computer Engineering Building.",
    source: "Official Timetable API (CS-2026-B)",
    icon: "fa-solid fa-clock"
  },
  {
    id: "syllabus",
    label: "Document Q&A",
    question: "Summarize the Operating Systems syllabus PDF.",
    response: "The OS course covers 5 units: Process Synchronization, Memory Management, File Systems, Virtualization, and Distributed Systems.",
    source: "OS_Syllabus_2026.pdf (3 Vector Chunks)",
    icon: "fa-solid fa-file-pdf"
  },
  {
    id: "attendance",
    label: "Attendance Analytics",
    question: "What is my current attendance status in CS302?",
    response: "Minimum required attendance is 75%. Your current attendance is 88.5% (21 of 24 sessions attended). You can safely miss 2 more sessions.",
    source: "Student Portal (Verified)",
    icon: "fa-solid fa-chart-line"
  }
];

const MARQUEE_ROW_1 = [
  "AI CAMPUS ASSISTANT",
  "RAG POWERED",
  "SMART CAMPUS",
  "INSTANT ANSWERS",
  "CAMPUS KNOWLEDGE",
  "AUTOMATED TIMETABLES",
  "VECTOR INDEXING"
];

const MARQUEE_ROW_2 = [
  "ATTENDANCE ANALYTICS",
  "TIMETABLES",
  "ASSIGNMENTS",
  "PDF Q&A",
  "COURSE MATERIAL",
  "SYLLABUS SEARCH",
  "DEPARTMENTAL PORTAL"
];

const INTELLIGENCE_CHIPS = [
  { label: "DBMS Syllabus", cat: "Academics" },
  { label: "Room 402 Location", cat: "Campus" },
  { label: "CS302 Attendance", cat: "System" },
  { label: "Exam Schedule", cat: "Academics" },
  { label: "Faculty Cabins", cat: "Campus" },
  { label: "Library Core RAG", cat: "System" },
  { label: "Lab Slots", cat: "Academics" },
  { label: "Hostel Wi-Fi Rules", cat: "Student Life" },
  { label: "Fee Payment Deadline", cat: "System" },
  { label: "Club Announcements", cat: "Student Life" }
];

const LandingPage = ({
  onNavigate = (_s) => {},
  onGetStarted,
  onSignIn
}) => {
  const [countProgress, setCountProgress] = useState(0);
  const [activePreviewIndex, setActivePreviewIndex] = useState(0);

  const handleNav = (screen) => {
    if (screen === "services" || screen === "capabilities") {
      const el = document.getElementById("capabilities") || document.getElementById("services");
      if (el) {
        if (window.__lenis) {
          window.__lenis.scrollTo(el, { duration: 1.2, offset: -40 });
        } else {
          el.scrollIntoView({ behavior: "smooth" });
        }
      }
      return;
    }
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

  const currentPreview = PREVIEW_SAMPLES[activePreviewIndex];

  return (
    <div
      id="landing-screen"
      className="relative w-full min-h-screen bg-black text-white flex flex-col justify-between select-none font-sans-ui overflow-x-hidden"
    >
      {/* =========================================================================
          GLOBAL CONTINUOUS BACKGROUND (Subtle Dotted Canvas behind all sections)
          ========================================================================= */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute inset-0 z-[1] opacity-70">
          <DotField
            dotRadius={1.4}
            dotSpacing={14}
            bulgeStrength={75}
            glowRadius={180}
            sparkle={true}
            waveAmplitude={1.2}
            gradientFrom="rgba(255, 255, 255, 0.65)"
            gradientTo="rgba(192, 132, 252, 0.40)"
            glowColor="#28282a"
          />
        </div>
        <div className="absolute inset-0 z-[2] bg-[radial-gradient(ellipse_85%_65%_at_50%_40%,transparent_30%,rgba(0,0,0,0.70)_100%)] pointer-events-none" />
      </div>

      {/* =========================================================================
          SECTION 1 — HERO (Strands overflow seamlessly into Section 2)
          ========================================================================= */}
      <section
        id="hero-section"
        className="relative z-10 w-full min-h-screen flex flex-col justify-between"
      >
        {/* HERO STRANDS LAYER (Bleeds into Section 2 Marquee) */}
        <div className="absolute top-0 left-0 right-0 -bottom-28 md:-bottom-40 z-0 pointer-events-none overflow-visible">
          <div className="absolute inset-0 z-[2] pointer-events-none opacity-85">
            <Strands
              colors={["#F97316", "#7C3AED", "#06B6D4"]}
              count={2}
              speed={0.45}
              amplitude={1}
              waviness={1}
              thickness={0.7}
              glow={2.6}
              taper={2.2}
              spread={0.8}
              intensity={0.75}
              saturation={1.5}
              opacity={0.9}
              scale={1.2}
              yOffset={-0.3}
              glass={false}
            />
          </div>
        </div>

        {/* HEADER & NAVIGATION */}
        <header className="relative z-20 w-full pt-6 md:pt-8 px-4 flex justify-center">
          <motion.div
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="w-full max-w-[760px] flex items-center justify-between gap-4"
          >
            <button
              id="landing-logo-btn"
              onClick={() => handleNav("landing")}
              className="shrink-0 w-11 h-11 rounded-full bg-white flex items-center justify-center text-black font-black shadow-lg hover:scale-105 active:scale-95 transition-transform"
              title="CampusGPT Home"
            >
              <span className="text-lg tracking-tighter font-extrabold flex items-center justify-center">
                <i className="fa-solid fa-graduation-cap text-base" />
              </span>
            </button>
            <FloatingNav onNavigate={handleNav} />
            <button
              id="landing-signin-btn"
              onClick={() => handleNav("auth")}
              className="shrink-0 bg-[#28282a] hover:bg-[#343438] text-[#c8c8c8] hover:text-white px-5 py-2 rounded-full text-sm font-medium border border-white/10 transition-colors active:scale-95 cursor-pointer"
            >
              Sign in
            </button>
          </motion.div>
        </header>

        {/* HERO MAIN BODY */}
        <main
          id="home"
          className="relative z-10 w-full max-w-4xl mx-auto px-4 text-center flex flex-col items-center justify-center my-auto py-8 scroll-mt-24"
        >
          {/* TRUST BADGE */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="flex items-center mb-6"
          >
            <div className="flex items-center -space-x-2.5 mr-[-10px] z-10">
              <div className="w-8 h-8 rounded-full bg-[#1c1c1e] border-2 border-black flex items-center justify-center text-xs text-white/90 shadow-md">
                <i className="fa-solid fa-graduation-cap" />
              </div>
              <div className="w-8 h-8 rounded-full bg-[#242428] border-2 border-black flex items-center justify-center text-xs text-white/90 shadow-md">
                <i className="fa-solid fa-chalkboard-user" />
              </div>
              <div className="w-8 h-8 rounded-full bg-[#2d2d32] border-2 border-black flex items-center justify-center text-xs text-white/90 shadow-md">
                <i className="fa-solid fa-building-columns" />
              </div>
            </div>
            <div className="bg-[var(--trust-bg)] border border-[var(--trust-border)] text-[var(--trust-text)] text-xs font-medium pl-6 pr-4 py-1.5 rounded-full shadow-lg backdrop-blur-sm">
              Trusted Across Every Department
            </div>
          </motion.div>

          {/* PIXEL/RETRO HEADLINE */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.25 }}
            className="font-display text-white tracking-wider text-4xl sm:text-5xl md:text-6xl lg:text-[76px] xl:text-[82px] leading-[1.08] text-center mb-5 uppercase select-none"
          >
            <span className="block">Ask Your Campus</span>
            <span className="block mt-1">Anything, Instantly</span>
          </motion.h1>

          {/* DESCRIPTION */}
          <motion.p
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="text-[var(--muted)] text-sm sm:text-base md:text-lg max-w-[510px] mx-auto mb-8 leading-relaxed font-normal"
          >
            Attendance, timetables, assignments, and course material — answered in seconds by an AI that actually knows your campus.
          </motion.p>

          {/* GET STARTED CTA BUTTON */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.45 }}
          >
            <SpecularButton
              id="landing-get-started-btn"
              onClick={() => handleNav("auth")}
              size="lg"
              radius={28}
              tint="#ffffff"
              tintOpacity={1}
              textColor="#000000"
              lineColor="#ffffff"
              baseColor="#e0e0e0"
              intensity={1.2}
              shineSize={12}
              shineFade={35}
              thickness={1.5}
              speed={0.4}
              followMouse={true}
              proximity={260}
              className="font-semibold text-base sm:text-lg shadow-[0_0_35px_rgba(255,255,255,0.45)] hover:shadow-[0_0_55px_rgba(255,255,255,0.7)] transition-all cursor-pointer"
            >
              <span>Get Started</span>
              <i className="fa-solid fa-arrow-right text-sm ml-1" />
            </SpecularButton>
          </motion.div>
        </main>

        {/* HERO STATS BAR */}
        <div
          id="stats"
          className="relative z-20 w-full max-w-5xl mx-auto px-6 pb-6 md:pb-8 pt-4 shrink-0 scroll-mt-24"
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.55 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center border-t border-white/10 pt-6"
          >
            <div className="flex flex-col items-center">
              <div className="text-white/60 mb-1 text-sm">
                <i className="fa-solid fa-bolt" />
              </div>
              <div className="font-display text-2xl sm:text-3xl lg:text-4xl text-white font-bold tracking-wider">
                &lt; {responseTimeVal}ms
              </div>
              <div className="text-[var(--muted)] text-xs sm:text-sm mt-1">
                Chat Response Time
              </div>
            </div>

            <div className="flex flex-col items-center">
              <div className="text-white/60 mb-1 text-sm">
                <i className="fa-solid fa-shield-halved" />
              </div>
              <div className="font-display text-2xl sm:text-3xl lg:text-4xl text-white font-bold tracking-wider">
                {uptimeVal}%
              </div>
              <div className="text-[var(--muted)] text-xs sm:text-sm mt-1">
                Platform Uptime
              </div>
            </div>

            <div className="flex flex-col items-center">
              <div className="text-white/60 mb-1 text-sm">
                <i className="fa-solid fa-clock" />
              </div>
              <div className="font-display text-2xl sm:text-3xl lg:text-4xl text-white font-bold tracking-wider">
                24/7
              </div>
              <div className="text-[var(--muted)] text-xs sm:text-sm mt-1">
                Assistant Availability
              </div>
            </div>

            <div className="flex flex-col items-center">
              <div className="text-white/60 mb-1 text-sm">
                <i className="fa-solid fa-folder-open" />
              </div>
              <div className="font-display text-2xl sm:text-3xl lg:text-4xl text-white font-bold tracking-wider">
                {docsVal}K+
              </div>
              <div className="text-[var(--muted)] text-xs sm:text-sm mt-1">
                Documents Indexed
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 2 — VELOCITY MARQUEE (React Bits ScrollVelocity)
          ========================================================================= */}
      <section className="relative z-10 w-full py-12 md:py-16 overflow-hidden flex flex-col justify-center">
        <ScrollVelocity
          texts={[
            "AI CAMPUS ASSISTANT ✦ RAG POWERED ✦ SMART CAMPUS ✦ INSTANT ANSWERS ✦ VECTOR INDEXING ✦ AUTOMATED TIMETABLES ✦",
            "ATTENDANCE ANALYTICS ✦ TIMETABLES ✦ ASSIGNMENTS ✦ PDF Q&A ✦ COURSE MATERIAL ✦ SYLLABUS SEARCH ✦ DEPARTMENTAL PORTAL ✦"
          ]}
          velocity={50}
          className="font-mono text-xl sm:text-2xl md:text-3xl lg:text-4xl font-extrabold tracking-widest uppercase text-neutral-300 hover:text-white transition-colors py-3"
          scrollerClassName="flex whitespace-nowrap text-center items-center gap-6"
        />
      </section>

      {/* =========================================================================
          SECTION 3 — INTERACTIVE CAMPUSGPT PREVIEW (Live AI UI Mockup Card)
          ========================================================================= */}
      <section id="preview-section" className="relative z-10 w-full max-w-5xl mx-auto px-4 py-20 scroll-mt-24">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.7 }}
          className="text-center mb-10"
        >
          <div className="inline-block px-3 py-1 rounded-full bg-[#1c1c1e] border border-white/10 text-xs font-semibold text-neutral-300 mb-3 uppercase tracking-wider">
            Interactive Experience
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-semibold text-white tracking-tight">
            See CampusGPT In Action
          </h2>
          <p className="text-neutral-400 text-sm sm:text-base max-w-xl mx-auto mt-2">
            Ask complex queries about timetables, PDFs, or attendance — get structured answers backed by university sources.
          </p>
        </motion.div>

        {/* INTERACTIVE SAMPLE PROMPT SELECTOR TABS */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-6">
          {PREVIEW_SAMPLES.map((sample, idx) => (
            <button
              key={sample.id}
              onClick={() => setActivePreviewIndex(idx)}
              className={`px-4 py-2 rounded-full text-xs font-medium transition-all flex items-center gap-2 cursor-pointer ${
                activePreviewIndex === idx
                  ? "bg-white text-black font-semibold shadow-md"
                  : "bg-[#141416] text-neutral-400 hover:text-white border border-white/10"
              }`}
            >
              <i className={sample.icon} />
              <span>{sample.label}</span>
            </button>
          ))}
        </div>

        {/* MOCKUP INTERFACE CARD */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="w-full bg-[#101012] border border-white/15 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.8)] overflow-hidden"
        >
          {/* MOCKUP HEADER BAR */}
          <div className="px-5 py-3.5 bg-[#17171a] border-b border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
              <span className="text-xs font-mono text-neutral-400 ml-2">campusgpt-ai-core v2.4</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-neutral-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Live Vector Index</span>
            </div>
          </div>

          {/* MOCKUP CHAT AREA */}
          <div className="p-6 sm:p-8 min-h-[300px] flex flex-col justify-between bg-gradient-to-b from-[#101012] to-[#0c0c0e]">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentPreview.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.35 }}
                className="space-y-6"
              >
                {/* USER QUESTION */}
                <div className="flex items-start gap-3.5">
                  <div className="w-8 h-8 rounded-full bg-neutral-800 border border-white/15 flex items-center justify-center text-white text-xs shrink-0 mt-0.5">
                    <i className="fa-solid fa-user" />
                  </div>
                  <div className="bg-[#1c1c20] border border-white/10 rounded-2xl px-4 py-3 text-sm text-white max-w-xl shadow-sm">
                    {currentPreview.question}
                  </div>
                </div>

                {/* AI RESPONSE */}
                <div className="flex items-start gap-3.5">
                  <div className="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 shadow-md">
                    <i className="fa-solid fa-graduation-cap" />
                  </div>
                  <div className="space-y-2.5 max-w-2xl">
                    <div className="bg-[#151518] border border-white/15 rounded-2xl p-4 sm:p-5 text-sm text-neutral-200 leading-relaxed shadow-inner">
                      <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-white">
                        <span>CampusGPT AI</span>
                        <span className="text-[10px] text-neutral-500">Verified Citation</span>
                      </div>
                      <p>{currentPreview.response}</p>
                    </div>

                    {/* SOURCE CITATION METADATA BADGE */}
                    <div className="inline-flex items-center gap-2 text-[11px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 px-3 py-1 rounded-full">
                      <i className="fa-solid fa-circle-check text-[10px]" />
                      <span>{currentPreview.source}</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* MOCK INPUT BAR */}
            <div className="mt-8 pt-4 border-t border-white/10">
              <StarBorder className="w-full" color="white" speed="6s" thickness={1} backgroundColor="#141416" borderColor="rgba(255, 255, 255, 0.15)">
                <div className="relative flex items-center px-4 py-3 text-xs text-neutral-400">
                  <i className="fa-solid fa-sparkles text-neutral-500 mr-3" />
                  <span className="truncate">Ask CampusGPT anything about timetables, attendance, syllabus...</span>
                  <button className="ml-auto w-7 h-7 rounded-full bg-white text-black flex items-center justify-center font-bold">
                    <i className="fa-solid fa-arrow-up text-xs" />
                  </button>
                </div>
              </StarBorder>
            </div>
          </div>
        </motion.div>
      </section>

      {/* =========================================================================
          SECTION 4 — BENTO FEATURES / CAPABILITIES
          ========================================================================= */}
      <section id="capabilities" className="relative z-10 w-full max-w-6xl mx-auto px-4 py-20 scroll-mt-24">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.7 }}
          className="text-center mb-14"
        >
          <div className="inline-block px-3 py-1 rounded-full bg-[#1c1c1e] border border-white/10 text-xs font-semibold text-neutral-300 mb-3 uppercase tracking-wider">
            Capabilities
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-semibold text-white tracking-tight">
            Engineered For University Ecosystems
          </h2>
          <p className="text-neutral-400 text-sm sm:text-base max-w-xl mx-auto mt-2">
            High-precision RAG vector search meets real-time academic schedule integration.
          </p>
        </motion.div>

        {/* BENTO GRID */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* FEATURE 1: LARGE AI ASSISTANT (Span 2 cols) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            whileHover={{ y: -4 }}
            transition={{ duration: 0.4 }}
            className="md:col-span-2 bg-[#121215] border border-white/15 rounded-3xl p-7 flex flex-col justify-between hover:border-white/35 transition-all group shadow-lg"
          >
            <div>
              <div className="w-10 h-10 rounded-2xl bg-[#1c1c20] border border-white/15 flex items-center justify-center text-white mb-5 group-hover:bg-white group-hover:text-black transition-colors">
                <i className="fa-solid fa-brain text-base" />
              </div>
              <span className="text-xs font-mono text-neutral-400 uppercase tracking-widest">Core Intelligence</span>
              <h3 className="text-2xl font-semibold text-white mt-1 mb-2">AI Campus Assistant</h3>
              <p className="text-neutral-400 text-sm leading-relaxed max-w-md">
                Ask natural questions regarding your specific university curriculum, class locations, and faculty hours with accurate vector RAG citations.
              </p>
            </div>
            <div className="mt-8 p-4 rounded-2xl bg-[#17171b] border border-white/10 flex items-center justify-between text-xs font-mono text-neutral-300">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                RAG Response Latency
              </span>
              <span className="text-white font-bold">&lt; 280ms</span>
            </div>
          </motion.div>

          {/* FEATURE 2: TIMETABLES (Span 1 col) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            whileHover={{ y: -4 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="md:col-span-1 bg-[#121215] border border-white/15 rounded-3xl p-7 flex flex-col justify-between hover:border-white/35 transition-all group shadow-lg"
          >
            <div>
              <div className="w-10 h-10 rounded-2xl bg-[#1c1c20] border border-white/15 flex items-center justify-center text-white mb-5 group-hover:bg-white group-hover:text-black transition-colors">
                <i className="fa-solid fa-calendar-days text-base" />
              </div>
              <span className="text-xs font-mono text-neutral-400 uppercase tracking-widest">Schedules</span>
              <h3 className="text-xl font-semibold text-white mt-1 mb-2">Automated Timetables</h3>
              <p className="text-neutral-400 text-xs leading-relaxed">
                Instant class schedules, batch labs, and exam timetable lookups without navigating confusing portals.
              </p>
            </div>
            <div className="mt-6 p-3.5 rounded-2xl bg-[#17171b] border border-white/10 text-[11px] font-mono text-neutral-300 flex items-center justify-between">
              <span>Next Class: DBMS</span>
              <span className="text-amber-400 font-bold">10:00 AM · Rm 402</span>
            </div>
          </motion.div>

          {/* FEATURE 3: DOCUMENT Q&A (Span 1 col) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            whileHover={{ y: -4 }}
            transition={{ duration: 0.4, delay: 0.15 }}
            className="md:col-span-1 bg-[#121215] border border-white/15 rounded-3xl p-7 flex flex-col justify-between hover:border-white/35 transition-all group shadow-lg"
          >
            <div>
              <div className="w-10 h-10 rounded-2xl bg-[#1c1c20] border border-white/15 flex items-center justify-center text-white mb-5 group-hover:bg-white group-hover:text-black transition-colors">
                <i className="fa-solid fa-file-invoice text-base" />
              </div>
              <span className="text-xs font-mono text-neutral-400 uppercase tracking-widest">Document Q&A</span>
              <h3 className="text-xl font-semibold text-white mt-1 mb-2">Syllabus & PDF Indexing</h3>
              <p className="text-neutral-400 text-xs leading-relaxed">
                Upload course syllabi, lecture notes, or notices. CampusGPT queries deep inside documents for instant summaries.
              </p>
            </div>
            <div className="mt-6 flex gap-2">
              <span className="px-2.5 py-1 rounded-full bg-[#1c1c20] text-[10px] font-mono text-neutral-300 border border-white/10">Syllabus.pdf</span>
              <span className="px-2.5 py-1 rounded-full bg-[#1c1c20] text-[10px] font-mono text-neutral-300 border border-white/10">Notes.pdf</span>
            </div>
          </motion.div>

          {/* FEATURE 4: ATTENDANCE ANALYTICS (Span 2 cols) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            whileHover={{ y: -4 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="md:col-span-2 bg-[#121215] border border-white/15 rounded-3xl p-7 flex flex-col justify-between hover:border-white/35 transition-all group shadow-lg"
          >
            <div>
              <div className="w-10 h-10 rounded-2xl bg-[#1c1c20] border border-white/15 flex items-center justify-center text-white mb-5 group-hover:bg-white group-hover:text-black transition-colors">
                <i className="fa-solid fa-user-check text-base" />
              </div>
              <span className="text-xs font-mono text-neutral-400 uppercase tracking-widest">Attendance</span>
              <h3 className="text-2xl font-semibold text-white mt-1 mb-2">Smart Attendance Tracking</h3>
              <p className="text-neutral-400 text-sm leading-relaxed max-w-md">
                Monitor current session attendance, track safe absence margins, and receive automatic alerts before falling below mandatory criteria.
              </p>
            </div>
            <div className="mt-8 space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-neutral-400">Current Average Attendance</span>
                <span className="text-emerald-400 font-bold">88.5% (Safe)</span>
              </div>
              <div className="w-full h-2.5 rounded-full bg-[#1c1c22] overflow-hidden p-0.5 border border-white/10">
                <div className="h-full rounded-full bg-emerald-400 w-[88.5%]" />
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 5 — HOW CAMPUSGPT WORKS (4-Step Workflow)
          ========================================================================= */}
      <section id="how-it-works" className="relative z-10 w-full max-w-5xl mx-auto px-4 py-20 scroll-mt-24">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.7 }}
          className="text-center mb-14"
        >
          <div className="inline-block px-3 py-1 rounded-full bg-[#1c1c1e] border border-white/10 text-xs font-semibold text-neutral-300 mb-3 uppercase tracking-wider">
            Architecture
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-semibold text-white tracking-tight">
            How CampusGPT Operates
          </h2>
          <p className="text-neutral-400 text-sm sm:text-base max-w-xl mx-auto mt-2">
            Four streamlined steps connecting university data with conversational intelligence.
          </p>
        </motion.div>

        {/* 4 STEPS GRID */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              step: "01",
              title: "CONNECT",
              desc: "Link official campus credentials and institute department portal.",
              icon: "fa-solid fa-link"
            },
            {
              step: "02",
              title: "INDEX",
              desc: "Vector engine ingests timetables, syllabi, notices, and course files.",
              icon: "fa-solid fa-database"
            },
            {
              step: "03",
              title: "ASK",
              desc: "Ask natural queries via conversational web or mobile interface.",
              icon: "fa-solid fa-message"
            },
            {
              step: "04",
              title: "RESOLVE",
              desc: "Receive verified answers with source citations in under 300ms.",
              icon: "fa-solid fa-bolt"
            }
          ].map((item, index) => (
            <motion.div
              key={item.step}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-[#121215] border border-white/15 rounded-2xl p-6 flex flex-col justify-between hover:border-white/30 transition-all group"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="font-display text-2xl text-white/40 font-bold group-hover:text-white transition-colors">
                    {item.step}
                  </span>
                  <div className="w-8 h-8 rounded-full bg-[#1a1a1e] border border-white/10 flex items-center justify-center text-xs text-neutral-300">
                    <i className={item.icon} />
                  </div>
                </div>
                <h3 className="text-base font-semibold text-white tracking-wider mb-2 font-mono">
                  {item.title}
                </h3>
                <p className="text-xs text-neutral-400 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* =========================================================================
          SECTION 6 — CAMPUS INTELLIGENCE / DATA CATEGORIES
          ========================================================================= */}
      <section className="relative z-10 w-full max-w-4xl mx-auto px-4 py-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="bg-[#101013] border border-white/15 rounded-3xl p-8 sm:p-12 shadow-2xl"
        >
          <span className="text-xs font-mono uppercase tracking-widest text-neutral-400 block mb-2">
            Institutional Index
          </span>
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-semibold text-white mb-4">
            Unified Knowledge Across Every Department
          </h2>
          <p className="text-xs sm:text-sm text-neutral-400 max-w-lg mx-auto mb-8 leading-relaxed">
            CampusGPT indexes academic schedules, syllabus documents, attendance registries, and faculty directories into one searchable vector space.
          </p>

          {/* CHIPS GRID */}
          <div className="flex flex-wrap justify-center gap-2.5 max-w-2xl mx-auto">
            {INTELLIGENCE_CHIPS.map((chip, idx) => (
              <motion.div
                key={idx}
                whileHover={{ scale: 1.05 }}
                className="px-4 py-2 rounded-full bg-[#18181c] border border-white/10 text-xs font-mono text-neutral-300 hover:text-white hover:border-white/30 transition-all cursor-default flex items-center gap-2"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-white/40" />
                <span>{chip.label}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* =========================================================================
          SECTION 7 — FINAL CTA (Clean Monochrome, NO hero strands here!)
          ========================================================================= */}
      <section className="relative z-10 w-full max-w-4xl mx-auto px-4 py-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="bg-gradient-to-b from-[#141418] to-[#0c0c0e] border border-white/20 rounded-3xl p-10 sm:p-16 shadow-[0_0_60px_rgba(255,255,255,0.06)] flex flex-col items-center justify-center relative overflow-hidden"
        >
          <div className="inline-block px-3.5 py-1 rounded-full bg-[#202025] border border-white/15 text-xs font-mono text-white mb-4 uppercase tracking-wider">
            Ready to upgrade your campus?
          </div>
          <h2 className="font-display text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-semibold text-white tracking-wider uppercase mb-4">
            Your Campus. One AI Assistant.
          </h2>
          <p className="text-neutral-400 text-sm sm:text-base max-w-md mx-auto mb-8 leading-relaxed font-normal">
            Everything students and faculty need. One intelligent place to ask.
          </p>

          <SpecularButton
            onClick={() => handleNav("auth")}
            size="lg"
            radius={28}
            tint="#ffffff"
            tintOpacity={1}
            textColor="#000000"
            lineColor="#ffffff"
            baseColor="#e0e0e0"
            intensity={1.2}
            shineSize={12}
            shineFade={35}
            thickness={1.5}
            speed={0.4}
            followMouse={true}
            proximity={260}
            className="font-semibold text-base sm:text-lg shadow-[0_0_35px_rgba(255,255,255,0.45)] hover:shadow-[0_0_55px_rgba(255,255,255,0.7)] transition-all cursor-pointer"
          >
            <span>Get Started</span>
            <i className="fa-solid fa-arrow-right text-sm ml-1" />
          </SpecularButton>
        </motion.div>
      </section>

      {/* =========================================================================
          SECTION 8 — FOOTER (Minimal Premium Footer)
          ========================================================================= */}
      <footer className="relative z-10 w-full max-w-6xl mx-auto px-6 py-12 border-t border-white/10 shrink-0 text-neutral-400 text-xs">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 mb-10">
          {/* BRAND COLUMN */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2.5 text-white font-semibold text-sm">
              <div className="w-7 h-7 rounded-full bg-white text-black flex items-center justify-center text-xs font-black">
                <i className="fa-solid fa-graduation-cap" />
              </div>
              <span>Campus<span className="font-light text-neutral-400">GPT</span></span>
            </div>
            <p className="text-neutral-400 leading-relaxed text-[11px]">
              The Intelligent Campus Operating System for modern universities.
            </p>
          </div>

          {/* NAVIGATION LINKS */}
          <div className="space-y-2">
            <h4 className="text-white font-mono text-xs uppercase tracking-wider mb-3">Navigation</h4>
            <ul className="space-y-2 text-[11px]">
              <li>
                <a href="#home" className="hover:text-white transition-colors">Home</a>
              </li>
              <li>
                <button onClick={() => handleNav("auth")} className="hover:text-white transition-colors cursor-pointer">Services</button>
              </li>
              <li>
                <button onClick={() => handleNav("auth")} className="hover:text-white transition-colors cursor-pointer">Sign In</button>
              </li>
            </ul>
          </div>

          {/* RESOURCES */}
          <div className="space-y-2">
            <h4 className="text-white font-mono text-xs uppercase tracking-wider mb-3">Resources</h4>
            <ul className="space-y-2 text-[11px]">
              <li>
                <a
                  href="https://github.com/IshanWankhede/CampusGPT"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors flex items-center gap-1.5"
                >
                  <i className="fa-brands fa-github" />
                  <span>GitHub Repository</span>
                </a>
              </li>
              <li>
                <a
                  href="mailto:ishan.wankhede7@gmail.com"
                  className="hover:text-white transition-colors flex items-center gap-1.5"
                >
                  <i className="fa-solid fa-envelope" />
                  <span>Contact Support</span>
                </a>
              </li>
            </ul>
          </div>

          {/* SYSTEM METRICS */}
          <div className="space-y-2">
            <h4 className="text-white font-mono text-xs uppercase tracking-wider mb-3">System Metrics</h4>
            <div className="space-y-1.5 text-[11px] font-mono text-neutral-400">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>All Systems Operational</span>
              </div>
              <div>RAG Pipeline: 99.9% Uptime</div>
              <div>Vector Latency: &lt; 280ms</div>
            </div>
          </div>
        </div>

        {/* BOTTOM COPYRIGHT LINE */}
        <div className="pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-neutral-500">
          <div>© {new Date().getFullYear()} CampusGPT. All rights reserved.</div>
          <div>Built for the modern campus experience.</div>
        </div>
      </footer>
    </div>
  );
};

export { LandingPage };
export default LandingPage;
