import { useLayoutEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import "./CampusFeatureSpread.css";

const FEATURES = [
  { label: "01 // AI ASSISTANT", visual: "Ask CampusGPT", detail: "DBMS is in Room 402 at 10:00 AM", spread: [-0.39, -0.25, -8] },
  { label: "02 // ATTENDANCE", visual: "88.5%", detail: "Above required 75%", spread: [-0.13, -0.31, 5] },
  { label: "03 // TIMETABLE", visual: "MON  TUE  WED  THU", detail: "09:00  ·  10:00  ·  11:00", spread: [0.13, -0.31, -5] },
  { label: "04 // ASSIGNMENTS", visual: "Coursework", detail: "Pending  ·  Submitted  ·  Graded", spread: [0.39, -0.24, 7] },
  { label: "05 // DOCUMENTS & RAG", visual: "Course files", detail: "Syllabus.pdf  ·  Indexed", spread: [-0.39, 0.25, 6] },
  { label: "06 // ANALYTICS", visual: "Attendance overview", detail: "▂ ▄ ▃ ▆ ▅ █ ▇", spread: [-0.13, 0.31, -6] },
  { label: "07 // CAMPUS LIFE", visual: "Campus, connected", detail: "One place for every update", spread: [0.13, 0.31, 5] },
  { label: "08 // STUDY SPACES", visual: "Your next study spot", detail: "Library · Open until 9 PM", spread: [0.39, 0.24, -7] },
];

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

export default function CampusFeatureSpread() {
  const sectionRef = useRef(null);

  useLayoutEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    const section = sectionRef.current;
    if (!section) return undefined;

    const context = gsap.context(() => {
      const cards = gsap.utils.toArray("[data-feature-card]", section);
      const cardContents = gsap.utils.toArray("[data-feature-card-content]", section);
      const cardArtContents = gsap.utils.toArray(".feature-spread-card-content", section);
      const heading = section.querySelector(".feature-spread-heading");
      const subtitle = section.querySelector(".feature-spread-subtitle");
      const headingMotion = section.querySelector(".feature-spread-copy-motion");
      const hint = section.querySelector(".feature-spread-hint");
      const media = gsap.matchMedia();
      let mouseMove;
      let parallaxSetters = [];
      let floatTweens = [];

      const resetParallax = () => {
        if (mouseMove) window.removeEventListener("mousemove", mouseMove);
        mouseMove = null;
        floatTweens.forEach((tween) => tween.kill());
        floatTweens = [];
        parallaxSetters.forEach((setter) => {
          setter.x.tween.kill();
          setter.y.tween.kill();
          setter.rotationX.tween.kill();
          setter.rotationY.tween.kill();
        });
        gsap.set([...cardContents, headingMotion], {
          x: 0,
          y: 0,
          rotationX: 0,
          rotationY: 0,
        });
        gsap.set(cardArtContents, { y: 0 });
        parallaxSetters = [];
      };

      const enableParallax = () => {
        if (mouseMove) return;
        const targets = [...cardContents, headingMotion];
        targets.forEach((target) => gsap.set(target, { transformPerspective: 900, transformStyle: "preserve-3d" }));
        parallaxSetters = targets.map((target) => ({
          x: gsap.quickTo(target, "x", { duration: 0.55, ease: "power3.out" }),
          y: gsap.quickTo(target, "y", { duration: 0.55, ease: "power3.out" }),
          rotationX: gsap.quickTo(target, "rotationX", { duration: 0.55, ease: "power3.out" }),
          rotationY: gsap.quickTo(target, "rotationY", { duration: 0.55, ease: "power3.out" }),
        }));
        cards.forEach((card, index) => {
          floatTweens.push(gsap.to(cardArtContents[index], {
            y: index % 2 ? -5 : 5,
            duration: 2.8 + index * 0.16,
            delay: index * 0.12,
            ease: "sine.inOut",
            repeat: -1,
            yoyo: true,
          }));
        });
        mouseMove = (event) => {
          const rawMouseX = clamp(((event.clientX / innerWidth) - 0.5) * 2, -1, 1);
          const rawMouseY = clamp(((event.clientY / innerHeight) - 0.5) * 2, -1, 1);

          cards.forEach((card, index) => {
            const [spreadX, spreadY] = FEATURES[index].spread;
            const depth = 0.78 + Math.min(0.42, Math.hypot(spreadX, spreadY) * 0.55) + (index % 3) * 0.06;
            const setter = parallaxSetters[index];
            setter.x(rawMouseX * 14 * depth);
            setter.y(rawMouseY * 14 * depth);
            setter.rotationX(-rawMouseY * 3.2 * depth);
            setter.rotationY(rawMouseX * 3.2 * depth);
          });

          const headingSetter = parallaxSetters[parallaxSetters.length - 1];
          headingSetter.x(rawMouseX * 6);
          headingSetter.y(rawMouseY * 6);
          headingSetter.rotationX(-rawMouseY * 0.8);
          headingSetter.rotationY(rawMouseX * 0.8);
        };
        window.addEventListener("mousemove", mouseMove, { passive: true });
      };

      media.add("(min-width: 900px) and (pointer: fine) and (prefers-reduced-motion: no-preference)", () => {
        cards.forEach((card) => gsap.set(card, {
          xPercent: -50,
          yPercent: -50,
          x: Number(card.dataset.stackX),
          y: Number(card.dataset.stackY),
          rotation: Number(card.dataset.stackRotation),
          scale: Number(card.dataset.stackScale),
        }));
        gsap.set([heading, subtitle], { autoAlpha: 0.12, scale: 0.97 });
        gsap.set(hint, { autoAlpha: 1 });

        const timeline = gsap.timeline({
          scrollTrigger: {
            trigger: section,
            start: "top top",
            end: "+=150%",
            pin: true,
            pinSpacing: "margin",
            scrub: true,
            invalidateOnRefresh: true,
            onLeave: enableParallax,
            onEnterBack: resetParallax,
            onLeaveBack: resetParallax,
          },
        });
        cards.forEach((card, index) => {
          const [x, y, rotation] = FEATURES[index].spread;
          timeline.to(card, {
            x: () => clamp(x * section.clientWidth, -section.clientWidth * 0.43, section.clientWidth * 0.43),
            y: () => y * section.clientHeight,
            rotation,
            scale: 0.92,
            ease: "none",
          }, 0);
        });
        timeline.to([heading, subtitle], { autoAlpha: 1, scale: 1, ease: "none" }, 0.3);
        timeline.to(hint, { autoAlpha: 0, ease: "none" }, 0);

        return () => {
          resetParallax();
          timeline.scrollTrigger?.kill();
          timeline.kill();
        };
      });

      media.add("(max-width: 899px) and (prefers-reduced-motion: no-preference), (pointer: coarse) and (prefers-reduced-motion: no-preference)", () => {
        gsap.set([heading, subtitle], { clearProps: "opacity,visibility,transform" });
        gsap.set(hint, { autoAlpha: 0 });
        gsap.from(cards, {
          autoAlpha: 0,
          y: 24,
          stagger: 0.07,
          duration: 0.5,
          ease: "power2.out",
          scrollTrigger: { trigger: section, start: "top 80%", once: true },
        });
      });

      media.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set([heading, subtitle], { clearProps: "opacity,visibility,transform" });
        gsap.set(hint, { autoAlpha: 0 });
        gsap.set(cards, { clearProps: "all" });
        gsap.set([...cardContents, headingMotion], { clearProps: "all" });
        gsap.set(cardArtContents, { clearProps: "all" });
      });

      return () => {
        resetParallax();
        media.revert();
      };
    }, section);

    const refreshFrame = requestAnimationFrame(() => ScrollTrigger.refresh());
    return () => {
      cancelAnimationFrame(refreshFrame);
      context.revert();
    };
  }, []);

  return (
    <section id="capabilities" className="feature-spread" ref={sectionRef}>
      <div className="feature-spread-stage">
        <div className="feature-spread-copy">
          <div className="feature-spread-copy-motion">
            <h2 className="feature-spread-heading">
              <span>One AI.</span> Every part
              <br />
              of your campus, in
              <br />
              <span>one place.</span>
            </h2>
            <p className="feature-spread-subtitle">
              Attendance, timetables, assignments, documents, and an AI that actually
              knows your campus — unified into one experience.
            </p>
          </div>
        </div>
        <div className="feature-spread-cards">
          {FEATURES.map((feature, index) => {
            const stack = [[-12, -10, -8, 0.94], [7, -5, 6, 1.02], [-5, 9, -4, 0.98], [12, 4, 8, 0.96],
              [-14, 5, -9, 0.91], [5, -12, 5, 1.04], [13, 10, -6, 0.95], [-8, -3, 4, 0.99]][index];
            return (
              <article
                className="feature-spread-card"
                data-feature-card
                data-stack-x={stack[0]}
                data-stack-y={stack[1]}
                data-stack-rotation={stack[2]}
                data-stack-scale={stack[3]}
                key={feature.label}
              >
                <div className="feature-spread-card-motion" data-feature-card-content>
                  <div className="feature-spread-card-content">
                    <div className="feature-card-art">
                      <strong>{feature.visual}</strong>
                      <span>{feature.detail}</span>
                    </div>
                    <small>{feature.label}</small>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
        <div className="feature-spread-hint">
          <span>SCROLL TO SPREAD</span>
          <i className="fa-solid fa-chevron-down" />
        </div>
      </div>
    </section>
  );
}
