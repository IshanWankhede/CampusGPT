import { jsx, jsxs } from "react/jsx-runtime";
import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import DriftWall from "./DriftWall";
import { FcGoogle } from "react-icons/fc";
import StarBorder from "./StarBorder";
const campusWallItems = [
  { image: "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=800&auto=format&fit=crop", title: "Collaborative AI Lab" },
  { image: "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=800&auto=format&fit=crop", title: "Campus Quadrangle" },
  { image: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=800&auto=format&fit=crop", title: "Semantic RAG Search" },
  { image: "https://images.unsplash.com/photo-1532094349884-543bc11b234d?q=80&w=800&auto=format&fit=crop", title: "Neural Computations" },
  { image: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=800&auto=format&fit=crop", title: "Secure Data Core" },
  { image: "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?q=80&w=800&auto=format&fit=crop", title: "Central Research Library" },
  { image: "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=800&auto=format&fit=crop", title: "Interactive Lecture Hub" },
  { image: "https://images.unsplash.com/photo-1562774053-701939374585?q=80&w=800&auto=format&fit=crop", title: "Faculty & Department Portal" },
  { image: "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=800&auto=format&fit=crop", title: "Robotics Workshop" },
  { image: "https://images.unsplash.com/photo-1509062522246-3755977927d7?q=80&w=800&auto=format&fit=crop", title: "Automated Timetables" },
  { image: "https://images.unsplash.com/photo-1571260899304-425eee4c7efc?q=80&w=800&auto=format&fit=crop", title: "Smart Academic Advising" },
  { image: "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?q=80&w=800&auto=format&fit=crop", title: "Predictive Exam Analytics" },
  { image: "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?q=80&w=800&auto=format&fit=crop", title: "Institutional Governance" },
  { image: "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?q=80&w=800&auto=format&fit=crop", title: "Curriculum Repository" },
  { image: "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=800&auto=format&fit=crop", title: "Campus Discovery Hub" }
];
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function InlineOtp({ value, onChange, disabled, status, onComplete }) {
  const digits = value.padEnd(6, " ").slice(0, 6).split("");
  const inputRefs = useRef([]);
  return /* @__PURE__ */ jsxs("div", { className: "flex gap-2", children: digits.map((digit, index) =>
    /* @__PURE__ */ jsx("input", {
      ref: (element) => {
        inputRefs.current[index] = element;
      },
      value: digit.trim(),
      maxLength: 1,
      inputMode: "numeric",
      disabled,
      onChange: (event) => {
        const entered = event.target.value.replace(/\D/g, "");
        const next = entered.slice(-1);
        const nextValue = `${value.slice(0, index)}${next}${value.slice(index + 1)}`.slice(0, 6);
        onChange(nextValue);
        if (next) {
          if (nextValue.length === 6) {
            onComplete(nextValue);
          } else {
            window.requestAnimationFrame(() => inputRefs.current[index + 1]?.focus());
          }
        }
      },
      onKeyDown: (event) => {
        if (event.key === "Backspace" && !digits[index] && index > 0) {
          inputRefs.current[index - 1]?.focus();
        }
      },
      className: `w-10 h-11 text-center text-lg font-semibold bg-[#141416] text-white rounded-[10px] border transition-colors ${
        status === "success" ? "border-green-500/60 bg-green-500/10 shadow-[0_0_14px_rgba(34,197,94,0.16)]" :
        status === "error" ? "border-red-500/60 bg-red-500/10 animate-[shake_0.35s_ease-in-out]" :
        "border-white/10 focus:border-white/40"
      }`,
      key: index
    }, index)
  ) });
}

const AuthScreen = ({
  onSelectRole,
  onNavigate = (_s) => {
  },
  onBackToLanding
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register, sendOtp, verifyOtp } = useAuth();
  const [authMode, setAuthMode] = useState("login");
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginCollege, setLoginCollege] = useState("VIT");
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [loginRole, setLoginRole] = useState("student");
  const [forgotSent, setForgotSent] = useState(false);
  const [signupName, setSignupName] = useState("");
  const [signupCollege, setSignupCollege] = useState("VIT");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupRole, setSignupRole] = useState("student");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupConfirmPassword, setSignupConfirmPassword] = useState("");
  const [showSignupPassword, setShowSignupPassword] = useState(false);
  const [showSignupConfirmPassword, setShowSignupConfirmPassword] = useState(false);
  const [requestError, setRequestError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [otp, setOtp] = useState("");
  const [otpStatus, setOtpStatus] = useState("");
  const [otpError, setOtpError] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [otpSending, setOtpSending] = useState(false);
  const [resendSeconds, setResendSeconds] = useState(0);
  const [emailVerified, setEmailVerified] = useState(false);
  const validSignupEmail = emailPattern.test(signupEmail.trim());
  useEffect(() => {
    if (!resendSeconds) return undefined;
    const timer = setInterval(() => setResendSeconds((seconds) => Math.max(0, seconds - 1)), 1000);
    return () => clearInterval(timer);
  }, [resendSeconds]);
  const handleSignupEmailChange = (event) => {
    const nextEmail = event.target.value;
    setSignupEmail(nextEmail);
    setOtp("");
    setOtpStatus("");
    setOtpError("");
    setOtpSent(false);
    setEmailVerified(false);
  };
  const handleSendSignupOtp = async () => {
    setOtpSending(true);
    setOtpError("");
    try {
      await sendOtp(signupEmail.trim(), "EMAIL_VERIFY");
      setOtpSent(true);
      setResendSeconds(60);
    } catch (error) {
      setOtpError(error.message);
    } finally {
      setOtpSending(false);
    }
  };
  const handleVerifySignupOtp = async (code) => {
    setOtpError("");
    try {
      await verifyOtp(signupEmail.trim(), code, "EMAIL_VERIFY");
      setOtpStatus("success");
      setEmailVerified(true);
    } catch (error) {
      setOtpStatus("error");
      setOtpError(error.message);
      setTimeout(() => {
        setOtp("");
        setOtpStatus("");
      }, 600);
    }
  };
  const handleBack = () => {
    if (onBackToLanding) {
      onBackToLanding();
      return;
    }
    if (typeof onNavigate === "function") {
      onNavigate("landing");
    }
  };
  const handleGoogleSignIn = () => {
    console.log("Initiating Google SSO sign-in...");
  };
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setRequestError("");
    setSubmitting(true);
    try {
      await login(loginEmail.trim(), loginPassword);
      navigate("/app", { replace: true });
    } catch (error) {
      setRequestError(error.message);
    } finally {
      setSubmitting(false);
    }
  };
  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setRequestError("");
    if (!emailVerified) {
      setRequestError("Please verify your email before creating an account.");
      return;
    }
    if (signupPassword !== signupConfirmPassword) {
      setRequestError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      await register(signupName.trim(), signupEmail.trim(), signupPassword, signupRole.toUpperCase());
      await login(signupEmail.trim(), signupPassword);
      navigate("/app", { replace: true });
    } catch (error) {
      setRequestError(error.message);
    } finally {
      setSubmitting(false);
    }
  };
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.07,
        delayChildren: 0.05
      }
    }
  };
  const itemVariants = {
    hidden: { opacity: 0, y: 22 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.85,
        ease: [0.22, 1, 0.36, 1]
      }
    }
  };
  const buttonGlowStyle = {
    boxShadow: "0 0 0 1px rgba(255,255,255,0.15), 0 0 22px rgba(255,255,255,0.32), 0 0 44px rgba(255,255,255,0.12)"
  };
  return /* @__PURE__ */ jsxs(
    "div",
    {
      id: "auth-screen",
      className: "w-full min-h-screen min-h-[100dvh] bg-black text-white flex flex-col min-[900px]:flex-row overflow-x-hidden selection:bg-white/20 font-sans-ui",
      children: [
        /* @__PURE__ */ jsx("div", { className: "w-full min-[900px]:w-[48%] min-[900px]:min-w-[420px] min-[900px]:min-h-[100dvh] flex flex-col justify-center items-center p-[clamp(24px,5vw,64px)] relative z-20 order-2 min-[900px]:order-1 overflow-y-auto", children: /* @__PURE__ */ jsxs(
          motion.div,
          {
            variants: containerVariants,
            initial: "hidden",
            animate: "visible",
            className: "w-full max-w-[440px] my-auto flex flex-col",
            children: [
              /* @__PURE__ */ jsxs(motion.div, { variants: itemVariants, className: "mb-6 flex items-center justify-between", children: [
                /* @__PURE__ */ jsxs(
                  "button",
                  {
                    onClick: handleBack,
                    className: "flex items-center gap-2.5 text-xs text-[var(--muted)] hover:text-white transition-colors group cursor-pointer",
                    title: "Return to home page",
                    children: [
                      /* @__PURE__ */ jsx("div", { className: "w-8 h-8 rounded-full bg-[#1c1c1e] border border-white/15 flex items-center justify-center text-white shadow-sm group-hover:border-white/30 transition-colors", children: /* @__PURE__ */ jsx("i", { className: "fa-solid fa-graduation-cap text-xs" }) }),
                      /* @__PURE__ */ jsxs("span", { className: "font-semibold text-white tracking-tight text-sm", children: [
                        "Campus",
                        /* @__PURE__ */ jsx("span", { className: "font-light text-neutral-400", children: "GPT" })
                      ] })
                    ]
                  }
                ),
                /* @__PURE__ */ jsxs(
                  "button",
                  {
                    onClick: handleBack,
                    className: "text-[11px] text-[var(--muted)] hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer",
                    children: [
                      /* @__PURE__ */ jsx("i", { className: "fa-solid fa-arrow-left text-[10px]" }),
                      /* @__PURE__ */ jsx("span", { children: "Back" })
                    ]
                  }
                )
              ] }),
              /* @__PURE__ */ jsx(
                motion.h1,
                {
                  variants: itemVariants,
                  className: "text-2xl sm:text-3xl font-semibold text-white tracking-tight",
                  children: authMode === "login" ? "Welcome Back" : "Create Your Account"
                }
              ),
              /* @__PURE__ */ jsx(
                motion.p,
                {
                  variants: itemVariants,
                  className: "text-sm text-[var(--muted)] mt-1.5 leading-relaxed",
                  children: authMode === "login" ? "Sign in to access your campus dashboard" : "Join CampusGPT with your official university credentials"
                }
              ),
              /* @__PURE__ */ jsx(motion.div, { variants: itemVariants, className: "mt-5 mb-6", children: /* @__PURE__ */ jsxs("div", { className: "inline-flex p-1 rounded-full bg-[#1a1a1c] border border-white/10 shadow-inner", children: [
                /* @__PURE__ */ jsx(
                  "button",
                  {
                    type: "button",
                    id: "tab-sign-in",
                    onClick: () => {
                      setRequestError("");
                      setAuthMode("login");
                    },
                    className: `px-5 py-2 rounded-full text-xs font-medium transition-all cursor-pointer ${authMode === "login" ? "bg-white text-black font-semibold shadow-sm" : "text-[var(--muted)] hover:text-white"}`,
                    children: "Sign In"
                  }
                ),
                /* @__PURE__ */ jsx(
                  "button",
                  {
                    type: "button",
                    id: "tab-sign-up",
                    onClick: () => {
                      setRequestError("");
                      setAuthMode("signup");
                    },
                    className: `px-5 py-2 rounded-full text-xs font-medium transition-all cursor-pointer ${authMode === "signup" ? "bg-white text-black font-semibold shadow-sm" : "text-[var(--muted)] hover:text-white"}`,
                    children: "Sign Up"
                  }
                )
              ] }) }),
              requestError && /* @__PURE__ */ jsx("p", { role: "alert", className: "text-xs text-red-400 mb-4", children: requestError }),
              /* @__PURE__ */ jsx(AnimatePresence, { mode: "wait", children: authMode === "login" ? (
                /* ================= LOGIN FORM ================= */
                /* @__PURE__ */ jsxs(
                  motion.form,
                  {
                    variants: containerVariants,
                    initial: "hidden",
                    animate: "visible",
                    exit: { opacity: 0, y: -10, transition: { duration: 0.2 } },
                    onSubmit: handleLoginSubmit,
                    className: "space-y-4 w-full",
                    children: [
                      /* College Selection Dropdown */
                      <motion.div variants={itemVariants}>
                        <label 
                          htmlFor="login-college-select" 
                          className="block text-xs font-medium text-neutral-400 mb-1.5 pl-0.5"
                        >
                          College / Institute
                        </label>
                        <StarBorder className="w-full" color="white" speed="5s" thickness={1} backgroundColor="#141416" borderColor="rgba(255, 255, 255, 0.1)">
                          <div className="relative">
                            <select
                              id="login-college-select"
                              value={loginCollege}
                              onChange={(e) => setLoginCollege(e.target.value)}
                              className="w-full bg-transparent text-white rounded-[13px] px-4 py-3.5 text-sm appearance-none focus:outline-none transition-all cursor-pointer pr-10"
                            >
                              <option value="COEP" className="bg-[#141416] text-white">
                                COEP (College of Engineering Pune)
                              </option>
                              <option value="PICT" className="bg-[#141416] text-white">
                                PICT (Pune Institute of Computer Technology)
                              </option>
                              <option value="VIT" className="bg-[#141416] text-white">
                                VIT (Vishwakarma Institute of Technology)
                              </option>
                            </select>
                            
                            {/* Dropdown Chevron Arrow */}
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none text-xs flex items-center">
                              <i className="fa-solid fa-chevron-down text-[11px]" />
                            </div>
                          </div>
                        </StarBorder>
                      </motion.div>,
                      <motion.div variants={itemVariants}>
                        <label className="block text-xs font-medium text-[var(--muted)] mb-1.5 pl-0.5">Campus Email</label>
                        <StarBorder className="w-full" color="white" speed="5s" thickness={1} backgroundColor="#141416" borderColor="rgba(255, 255, 255, 0.1)">
                          <div className="relative">
                            <input
                              id="login-email-input"
                              type="email"
                              required
                              value={loginEmail}
                              onChange={(e) => setLoginEmail(e.target.value)}
                              placeholder="name@campus.edu"
                              className="w-full bg-transparent text-white rounded-[13px] px-4 py-3.5 text-sm placeholder:text-[#8e8e8e] focus:outline-none transition-all pr-10"
                            />
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-500 pointer-events-none text-xs">
                              <i className="fa-regular fa-envelope" />
                            </div>
                          </div>
                        </StarBorder>
                      </motion.div>,
                      <motion.div variants={itemVariants}>
                        <div className="flex items-center justify-between mb-1.5 pl-0.5">
                          <label className="text-xs font-medium text-[var(--muted)]">Password</label>
                          <button
                            type="button"
                            onClick={() => navigate("/auth/forgot-password")}
                            className="text-xs text-[var(--muted)] hover:text-white transition-colors cursor-pointer"
                          >
                            Forgot password?
                          </button>
                        </div>
                        <StarBorder className="w-full" color="white" speed="5s" thickness={1} backgroundColor="#141416" borderColor="rgba(255, 255, 255, 0.1)">
                          <div className="relative">
                            <input
                              id="login-password-input"
                              type={showLoginPassword ? "text" : "password"}
                              required
                              value={loginPassword}
                              onChange={(e) => setLoginPassword(e.target.value)}
                              placeholder="••••••••••••"
                              className="w-full bg-transparent text-white rounded-[13px] px-4 py-3.5 pr-11 text-sm placeholder:text-[#8e8e8e] focus:outline-none transition-all font-mono"
                            />
                            <button
                              type="button"
                              onClick={() => setShowLoginPassword(!showLoginPassword)}
                              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-white transition-colors p-1 cursor-pointer"
                              title={showLoginPassword ? "Hide password" : "Show password"}
                            >
                              <i className={`fa-solid ${showLoginPassword ? "fa-eye-slash" : "fa-eye"} text-xs`} />
                            </button>
                          </div>
                        </StarBorder>
                        {forgotSent && (
                          <motion.div
                            initial={{ opacity: 0, y: -4 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-[11px] text-emerald-400 mt-2 pl-0.5 flex items-center gap-1.5"
                          >
                            <i className="fa-solid fa-circle-check text-[10px]" />
                            <span>Password reset link sent to your registered email</span>
                          </motion.div>
                        )}
                      </motion.div>,
                      <motion.div variants={itemVariants} className="pt-2 grid grid-cols-3 gap-2.5">
                        <button
                          type="submit"
                          id="submit-sign-in-btn"
                          style={buttonGlowStyle}
                          className="col-span-2 w-full bg-white hover:bg-neutral-100 text-black font-semibold text-sm py-3.5 px-4 rounded-full transition-all active:scale-[0.99] cursor-pointer flex items-center justify-center gap-2"
                        >
                          <span>{submitting ? "Signing In..." : "Sign In"}</span>
                          <i className="fa-solid fa-arrow-right text-xs" />
                        </button>

                        <div className="col-span-1">
                          <button
                            type="button"
                            id="google-sign-in-btn"
                            onClick={handleGoogleSignIn}
                            aria-label="Continue with Google"
                            title="Continue with Google"
                            className="w-full h-full py-3.5 rounded-full border border-white/10 bg-[#141416] hover:bg-[#1e1e24] hover:border-white/30 text-white transition-all flex items-center justify-center cursor-pointer shadow-md active:scale-[0.98]"
                          >
                            <FcGoogle className="w-5 h-5 flex-shrink-0" />
                          </button>
                        </div>
                      </motion.div>,
                      <motion.div variants={itemVariants}>
                        <p className="text-xs text-[var(--muted)] text-center mt-3">
                          Don't have an account?{" "}
                          <button
                            type="button"
                            onClick={() => setAuthMode("signup")}
                            className="text-white hover:underline font-medium cursor-pointer ml-1"
                          >
                            Sign up
                          </button>
                        </p>
                      </motion.div>
                    ]
                  },
                  "login-form"
                )
              ) : (
                /* ================= SIGNUP FORM ================= */
                /* @__PURE__ */ jsxs(
                  motion.form,
                  {
                    variants: containerVariants,
                    initial: "hidden",
                    animate: "visible",
                    exit: { opacity: 0, y: -10, transition: { duration: 0.2 } },
                    onSubmit: handleSignupSubmit,
                    className: "space-y-3.5 w-full",
                    children: [
                      <motion.div variants={itemVariants}>
                        <label className="block text-xs font-medium text-[var(--muted)] mb-1.5 pl-0.5">Full Name</label>
                        <StarBorder className="w-full" color="white" speed="5s" thickness={1} backgroundColor="#141416" borderColor="rgba(255, 255, 255, 0.1)">
                          <div className="relative">
                            <input
                              id="signup-name-input"
                              type="text"
                              required
                              value={signupName}
                              onChange={(e) => setSignupName(e.target.value)}
                              placeholder="xyz"
                              className="w-full bg-transparent text-white rounded-[13px] px-4 py-3.5 text-sm placeholder:text-[#8e8e8e] focus:outline-none transition-all pr-10"
                            />
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-500 pointer-events-none text-xs">
                              <i className="fa-regular fa-user" />
                            </div>
                          </div>
                        </StarBorder>
                      </motion.div>,

                      /* College Selection Dropdown */
                      <motion.div variants={itemVariants}>
                        <label 
                          htmlFor="signup-college-select" 
                          className="block text-xs font-medium text-neutral-400 mb-1.5 pl-0.5"
                        >
                          College / Institute
                        </label>
                        <StarBorder className="w-full" color="white" speed="5s" thickness={1} backgroundColor="#141416" borderColor="rgba(255, 255, 255, 0.1)">
                          <div className="relative">
                            <select
                              id="signup-college-select"
                              value={signupCollege}
                              onChange={(e) => setSignupCollege(e.target.value)}
                              className="w-full bg-transparent text-white rounded-[13px] px-4 py-3.5 text-sm appearance-none focus:outline-none transition-all cursor-pointer pr-10"
                            >
                              <option value="COEP" className="bg-[#141416] text-white">
                                COEP (College of Engineering Pune)
                              </option>
                              <option value="PICT" className="bg-[#141416] text-white">
                                PICT (Pune Institute of Computer Technology)
                              </option>
                              <option value="VIT" className="bg-[#141416] text-white">
                                VIT (Vishwakarma Institute of Technology)
                              </option>
                            </select>
                            
                            {/* Dropdown Chevron Arrow */}
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none text-xs flex items-center">
                              <i className="fa-solid fa-chevron-down text-[11px]" />
                            </div>
                          </div>
                        </StarBorder>
                      </motion.div>,
                      <motion.div variants={itemVariants}>
                        <label className="block text-xs font-medium text-[var(--muted)] mb-1.5 pl-0.5">University Email</label>
                        <StarBorder className="w-full" color="white" speed="5s" thickness={1} backgroundColor="#141416" borderColor="rgba(255, 255, 255, 0.1)">
                          <div className="relative">
                            <input
                              id="signup-email-input"
                              type="email"
                              required
                              value={signupEmail}
                              onChange={handleSignupEmailChange}
                              placeholder="xyz@gmail.com"
                              className="w-full bg-transparent text-white rounded-[13px] px-4 py-3.5 text-sm placeholder:text-[#8e8e8e] focus:outline-none transition-all pr-10"
                            />
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-500 pointer-events-none text-xs">
                              <i className="fa-regular fa-envelope" />
                            </div>
                          </div>
                        </StarBorder>
                        {authMode === "signup" && validSignupEmail && !otpSent ? (
                          <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} className="mt-2">
                            <button
                              type="button"
                              disabled={otpSending}
                              onClick={handleSendSignupOtp}
                              className="rounded-full border border-white/15 bg-[#141416] px-3.5 py-1.5 text-[11px] text-neutral-300 hover:text-white hover:border-white/35 transition-colors disabled:opacity-50"
                            >
                              {otpSending ? "Sending..." : "Verify Email"}
                            </button>
                          </motion.div>
                        ) : null}
                        {authMode === "signup" && validSignupEmail && otpSent ? (
                          <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} className="mt-2 space-y-1.5">
                            <div className="flex items-center justify-between text-[10px] text-neutral-500">
                              <span>Code sent to {signupEmail}</span>
                              {!emailVerified && resendSeconds === 0 ? (
                                <button type="button" onClick={handleSendSignupOtp} className="text-white hover:text-neutral-300 underline">
                                  Resend code
                                </button>
                              ) : !emailVerified ? (
                                <span>Resend in {resendSeconds}s</span>
                              ) : null}
                            </div>
                            <InlineOtp value={otp} onChange={setOtp} disabled={emailVerified} status={otpStatus} onComplete={handleVerifySignupOtp} />
                            {otpStatus === "success" ? (
                              <p className="text-[10px] text-green-400"><i className="fa-solid fa-check mr-1" />Email verified</p>
                            ) : otpError ? (
                              <p className="text-[10px] text-red-400">{otpError}</p>
                            ) : null}
                          </motion.div>
                        ) : null}
                      </motion.div>,
                      /* @__PURE__ */ jsxs(motion.div, { variants: itemVariants, children: [
                        /* @__PURE__ */ jsx("label", { className: "block text-xs font-medium text-[var(--muted)] mb-1.5 pl-0.5", children: "Select University Role" }),
                        /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-2 gap-2 p-1 rounded-[14px] bg-[#141416] border border-white/10", children: [
                          /* @__PURE__ */ jsxs(
                            "button",
                            {
                              type: "button",
                              id: "role-pill-student",
                              onClick: () => setSignupRole("student"),
                              className: `py-2.5 px-4 rounded-xl text-xs font-medium transition-all flex items-center justify-center gap-2 cursor-pointer ${signupRole === "student" ? "bg-white text-black font-semibold shadow-sm" : "text-neutral-400 hover:text-white"}`,
                              children: [
                                /* @__PURE__ */ jsx("i", { className: "fa-solid fa-user-graduate text-xs" }),
                                /* @__PURE__ */ jsx("span", { children: "Student" })
                              ]
                            }
                          ),
                          /* @__PURE__ */ jsxs(
                            "button",
                            {
                              type: "button",
                              id: "role-pill-faculty",
                              onClick: () => setSignupRole("faculty"),
                              className: `py-2.5 px-4 rounded-xl text-xs font-medium transition-all flex items-center justify-center gap-2 cursor-pointer ${signupRole === "faculty" ? "bg-white text-black font-semibold shadow-sm" : "text-neutral-400 hover:text-white"}`,
                              children: [
                                /* @__PURE__ */ jsx("i", { className: "fa-solid fa-chalkboard-user text-xs" }),
                                /* @__PURE__ */ jsx("span", { children: "Faculty" })
                              ]
                            }
                          )
                        ] }),
                        /* @__PURE__ */ jsx("p", { className: "text-[10px] text-neutral-500 mt-1 pl-1", children: "* Administrator clearance accounts are provisioned directly by campus IT." })
                      ] }),
                      <motion.div variants={itemVariants}>
                        <label className="block text-xs font-medium text-[var(--muted)] mb-1.5 pl-0.5">Password</label>
                        <StarBorder className="w-full" color="white" speed="5s" thickness={1} backgroundColor="#141416" borderColor="rgba(255, 255, 255, 0.1)">
                          <div className="relative">
                            <input
                              id="signup-password-input"
                              type={showSignupPassword ? "text" : "password"}
                              required
                              value={signupPassword}
                              onChange={(e) => setSignupPassword(e.target.value)}
                              placeholder="••••••••••••"
                              className="w-full bg-transparent text-white rounded-[13px] px-4 py-3.5 pr-11 text-sm placeholder:text-[#8e8e8e] focus:outline-none transition-all font-mono"
                            />
                            <button
                              type="button"
                              onClick={() => setShowSignupPassword(!showSignupPassword)}
                              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-white transition-colors p-1 cursor-pointer"
                              title={showSignupPassword ? "Hide password" : "Show password"}
                            >
                              <i className={`fa-solid ${showSignupPassword ? "fa-eye-slash" : "fa-eye"} text-xs`} />
                            </button>
                          </div>
                        </StarBorder>
                      </motion.div>,
                      <motion.div variants={itemVariants}>
                        <label className="block text-xs font-medium text-[var(--muted)] mb-1.5 pl-0.5">Confirm Password</label>
                        <StarBorder className="w-full" color="white" speed="5s" thickness={1} backgroundColor="#141416" borderColor="rgba(255, 255, 255, 0.1)">
                          <div className="relative">
                            <input
                              id="signup-confirm-password-input"
                              type={showSignupConfirmPassword ? "text" : "password"}
                              required
                              value={signupConfirmPassword}
                              onChange={(e) => setSignupConfirmPassword(e.target.value)}
                              placeholder="••••••••••••"
                              className="w-full bg-transparent text-white rounded-[13px] px-4 py-3.5 pr-11 text-sm placeholder:text-[#8e8e8e] focus:outline-none transition-all font-mono"
                            />
                            <button
                              type="button"
                              onClick={() => setShowSignupConfirmPassword(!showSignupConfirmPassword)}
                              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-white transition-colors p-1 cursor-pointer"
                              title={showSignupConfirmPassword ? "Hide password" : "Show password"}
                            >
                              <i className={`fa-solid ${showSignupConfirmPassword ? "fa-eye-slash" : "fa-eye"}`} />
                            </button>
                          </div>
                        </StarBorder>
                      </motion.div>,
                      <motion.div variants={itemVariants} className="pt-2 grid grid-cols-3 gap-2.5">
                        <button
                          type="submit"
                          id="submit-create-account-btn"
                          style={buttonGlowStyle}
                          className="col-span-2 w-full bg-white hover:bg-neutral-100 text-black font-semibold text-sm py-3.5 px-4 rounded-full transition-all active:scale-[0.99] cursor-pointer flex items-center justify-center gap-2"
                        >
                          <span>{submitting ? "Creating Account..." : "Create Account"}</span>
                          <i className="fa-solid fa-arrow-right text-xs" />
                        </button>

                        <div className="col-span-1">
                          <button
                            type="button"
                            id="google-sign-up-btn"
                            onClick={handleGoogleSignIn}
                            aria-label="Continue with Google"
                            title="Continue with Google"
                            className="w-full h-full py-3.5 rounded-full border border-white/10 bg-[#141416] hover:bg-[#1e1e24] hover:border-white/30 text-white transition-all flex items-center justify-center cursor-pointer shadow-md active:scale-[0.98]"
                          >
                            <FcGoogle className="w-5 h-5 flex-shrink-0" />
                          </button>
                        </div>
                      </motion.div>,
                      <motion.div variants={itemVariants}>
                        <p className="text-xs text-[var(--muted)] text-center mt-3">
                          Already have an account?{" "}
                          <button
                            type="button"
                            onClick={() => setAuthMode("login")}
                            className="text-white hover:underline font-medium cursor-pointer ml-1"
                          >
                            Sign in
                          </button>
                        </p>
                      </motion.div>
                    ]
                  },
                  "signup-form"
                )
              ) })
            ]
          }
        ) }),
        /* @__PURE__ */ jsxs("div", { className: "w-full min-[900px]:w-[52%] h-[420px] min-[500px]:h-[480px] min-[900px]:h-auto min-[900px]:min-h-[100dvh] relative overflow-hidden bg-[#060010] flex flex-col justify-center items-center order-1 min-[900px]:order-2 border-b min-[900px]:border-b-0 min-[900px]:border-l border-white/10", children: [
          /* @__PURE__ */ jsx("div", { className: "absolute inset-0 w-full h-full", children: /* @__PURE__ */ jsx(
            DriftWall,
            {
              items: campusWallItems,
              columns: 5,
              tileWidth: 190,
              tileHeight: 126,
              gap: 16,
              tilt: 16,
              turn: -14,
              perspective: 1200,
              depth: 120,
              speed: 38,
              direction: "up",
              variance: 0.45,
              parallax: 0.6,
              lift: 64,
              fade: 0.6,
              dim: 0.55,
              overlayColor: "#060010"
            }
          ) }),
          /* @__PURE__ */ jsx(
            "div",
            {
              className: "pointer-events-none absolute left-0 top-0 bottom-0 z-10 hidden min-[900px]:block w-24",
              style: {
                background: "linear-gradient(to right, #000000 0%, rgba(0,0,0,0.85) 35%, transparent 100%)"
              }
            }
          ),
          /* @__PURE__ */ jsx(
            "div",
            {
              className: "pointer-events-none absolute bottom-0 inset-x-0 z-10 block min-[900px]:hidden h-16",
              style: {
                background: "linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.85) 65%, #000000 100%)"
              }
            }
          )
        ] })
      ]
    }
  );
};
export {
  AuthScreen
};
