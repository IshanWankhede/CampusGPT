import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { useNavigate } from "react-router-dom";

const NAV_ITEMS = [
  {
    id: "home",
    label: "Home",
    icon: "fa-solid fa-house",
    action: "home",
    ariaLabel: "Go to Home section",
  },
  {
    id: "dashboard",
    label: "Dashboard",
    icon: "fa-solid fa-table-cells-large",
    action: "auth",
    ariaLabel: "Go to Dashboard — Sign In required",
  },
  {
    id: "services",
    label: "Services",
    icon: "fa-solid fa-grip",
    action: "services",
    ariaLabel: "View Capabilities & Services section",
  },
  {
    id: "dashboard",
    label: "Dashboard",
    icon: "fa-solid fa-table-cells-large",
    action: "auth",
    ariaLabel: "Go to Dashboard — Sign In required",
  },
  {
    id: "contact",
    label: "Contact",
    icon: "fa-solid fa-envelope",
    action: "mailto",
    ariaLabel: "Contact us via email",
  },
  {
    id: "github",
    label: "GitHub",
    icon: "fa-brands fa-github",
    action: "github",
    ariaLabel: "CampusGPT GitHub Repository",
  },
];

export default function FloatingNav({ onNavigate }) {
  const [activeId, setActiveId] = useState("home");
  const [hoveredId, setHoveredId] = useState(null);
  const navigate = useNavigate();

  const handleClick = (item) => {
    setActiveId(item.id);

    if (item.action === "home") {
      if (window.__lenis) {
        window.__lenis.scrollTo(0, { duration: 1.2 });
      } else {
        document.getElementById("landing-screen")?.scrollIntoView({ behavior: "smooth" });
      }
      return;
    }

    if (item.action === "services" || item.id === "services") {
      const el = document.getElementById("capabilities") || document.getElementById("services");
      if (el) {
        if (window.__lenis) {
          window.__lenis.scrollTo(el, { duration: 1.2, offset: -40 });
        } else {
          el.scrollIntoView({ behavior: "smooth" });
        }
      } else if (onNavigate) {
        onNavigate("services");
      }
      return;
    }

    if (item.action === "github") {
      window.open("https://github.com/IshanWankhede/CampusGPT", "_blank", "noopener,noreferrer");
      return;
    }

    if (item.action === "mailto") {
      window.location.href = "mailto:ishan.wankhede7@gmail.com";
      return;
    }

    if (item.action === "auth") {
      if (onNavigate) {
        onNavigate("auth");
      } else {
        navigate("/auth");
      }
    }
  };

  return (
    <nav
      role="navigation"
      aria-label="Main Navigation"
      className="flex items-center gap-1 p-1.5 rounded-full border border-black/15 bg-white shadow-[0_8px_30px_rgba(0,0,0,0.15)]"
    >
      {NAV_ITEMS.map((item) => {
        const isActive = activeId === item.id;
        const isHovered = hoveredId === item.id;

        return (
          <button
            key={item.id}
            onClick={() => handleClick(item)}
            onMouseEnter={() => setHoveredId(item.id)}
            onMouseLeave={() => setHoveredId(null)}
            aria-label={item.ariaLabel}
            aria-current={isActive ? "page" : undefined}
            className={[
              "relative flex items-center rounded-full transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black/50 cursor-pointer select-none",
              isActive
                ? "text-white gap-2 px-4 py-2"
                : "text-black justify-center w-9 h-9",
            ].join(" ")}
            style={{
              transform: !isActive && isHovered ? "scale(1.08)" : "scale(1)",
              transition: "transform 0.15s ease, color 0.2s ease",
            }}
          >
            {isActive && (
              <motion.div
                layoutId="active-nav-indicator"
                className="absolute inset-0 rounded-full bg-black shadow-[0_2px_10px_rgba(0,0,0,0.25)] z-0"
                transition={{
                  type: "spring",
                  stiffness: 380,
                  damping: 30,
                }}
              />
            )}

            <span className="relative z-10 flex items-center gap-2">
              <i className={`${item.icon} text-sm`} aria-hidden="true" />
              <AnimatePresence mode="wait">
                {isActive && (
                  <motion.span
                    key="label"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.15 }}
                    className="text-[13px] font-medium whitespace-nowrap"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </span>
          </button>
        );
      })}
    </nav>
  );
}
