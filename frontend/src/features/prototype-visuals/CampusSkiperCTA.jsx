import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import "./CampusSkiperCTA.css";

const SPRITE_ROWS = 15;
const SPRITE_COLS = 7;

function CrowdCanvas({ src, rows = SPRITE_ROWS, cols = SPRITE_COLS }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;
    const context = canvas.getContext("2d");
    if (!context) {
      console.error("Canvas 2D context is unavailable; the Skiper39 crowd animation cannot render.");
      return undefined;
    }

    const image = new Image();
    const stage = { width: 0, height: 0, pixelRatio: 1, spriteScale: 0.3 };
    const peeps = [];
    const crowd = [];
    const availablePeeps = [];
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let isDisposed = false;

    const createPeep = (index) => {
      const cellWidth = image.naturalWidth / rows;
      const cellHeight = image.naturalHeight / cols;
      const sourceRect = [
        (index % rows) * cellWidth,
        Math.floor(index / rows) * cellHeight,
        cellWidth,
        cellHeight,
      ];
      const peep = {
        sourceRect,
        width: cellWidth * stage.spriteScale,
        height: cellHeight * stage.spriteScale,
        x: 0,
        y: 0,
        anchorY: 0,
        scaleX: 1,
        walk: null,
      };
      peeps.push(peep);
      return peep;
    };

    const draw = () => {
      if (isDisposed) return;
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.save();
      context.scale(stage.pixelRatio, stage.pixelRatio);
      crowd.forEach((peep) => {
        const [sourceX, sourceY, sourceWidth, sourceHeight] = peep.sourceRect;
        context.save();
        context.translate(peep.x, peep.y);
        context.scale(peep.scaleX, 1);
        context.drawImage(
          image,
          sourceX,
          sourceY,
          sourceWidth,
          sourceHeight,
          0,
          0,
          peep.width,
          peep.height,
        );
        context.restore();
      });
      context.restore();
    };

    const resetPeep = (peep) => {
      const direction = Math.random() > 0.5 ? 1 : -1;
      const offsetY = 100 - 250 * gsap.parseEase("power2.in")(Math.random());
      const startY = stage.height - peep.height + offsetY;
      const startX = direction === 1 ? -peep.width : stage.width + peep.width;
      const endX = direction === 1 ? stage.width : 0;

      peep.x = startX;
      peep.y = startY;
      peep.anchorY = startY;
      peep.scaleX = direction;

      return { startY, startX, endX };
    };

    const removeFrom = (items, item) => {
      const index = items.indexOf(item);
      if (index !== -1) items.splice(index, 1);
    };

    const addPeepToCrowd = () => {
      if (isDisposed || !availablePeeps.length) return;
      const peep = availablePeeps.splice(Math.floor(Math.random() * availablePeeps.length), 1)[0];
      const { startY, startX, endX } = resetPeep(peep);
      const timeline = gsap.timeline({
        onComplete: () => {
          removeFrom(crowd, peep);
          availablePeeps.push(peep);
          addPeepToCrowd();
        },
      });

      timeline.timeScale(0.5 + Math.random());
      timeline.fromTo(peep, { x: startX }, { x: endX, duration: 10, ease: "none" }, 0);
      timeline.to(peep, { y: startY - 10, duration: 0.25, repeat: 39, yoyo: true, ease: "none" }, 0);
      peep.walk = timeline;
      crowd.push(peep);
      crowd.sort((a, b) => a.anchorY - b.anchorY);
      if (prefersReducedMotion) timeline.pause(0);
    };

    const resize = () => {
      if (!canvas.clientWidth || !canvas.clientHeight) return;

      stage.width = canvas.clientWidth;
      stage.height = canvas.clientHeight;
      stage.pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
      stage.spriteScale = Math.min(0.42, Math.max(0.18, stage.height / 600));
      canvas.width = Math.round(stage.width * stage.pixelRatio);
      canvas.height = Math.round(stage.height * stage.pixelRatio);

      peeps.forEach((peep) => {
        peep.walk?.kill();
        peep.width = peep.sourceRect[2] * stage.spriteScale;
        peep.height = peep.sourceRect[3] * stage.spriteScale;
      });
      crowd.length = 0;
      availablePeeps.length = 0;
      availablePeeps.push(...peeps);

      if (prefersReducedMotion) {
        peeps.forEach((peep, index) => {
          peep.x = (index / Math.max(1, peeps.length - 1)) * stage.width;
          peep.y = stage.height - peep.height;
          peep.anchorY = peep.y;
          peep.scaleX = 1;
          crowd.push(peep);
        });
        draw();
        return;
      }

      while (availablePeeps.length) {
        const peep = addPeepToCrowd();
        peep?.walk?.progress(Math.random());
      }
    };

    image.onload = () => {
      if (isDisposed) return;
      for (let index = 0; index < rows * cols; index += 1) createPeep(index);
      resize();
      if (!prefersReducedMotion) gsap.ticker.add(draw);
    };
    image.onerror = () => {
      console.error(`Unable to load Skiper39 crowd sprite sheet: ${src}`);
    };
    image.src = src;

    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(canvas);

    return () => {
      isDisposed = true;
      resizeObserver.disconnect();
      gsap.ticker.remove(draw);
      peeps.forEach((peep) => peep.walk?.kill());
      crowd.length = 0;
      availablePeeps.length = 0;
      image.onload = null;
      image.onerror = null;
    };
  }, [src, rows, cols]);

  return <canvas ref={canvasRef} className="skiper39-crowd-canvas" aria-hidden="true" />;
}

export default function CampusSkiperCTA({ onGetStarted }) {
  return (
    <section id="final-cta" className="campus-skiper-cta">
      <CrowdCanvas src="/images/peeps/all-peeps.png" />
      <div className="campus-skiper-card">
        <span className="campus-skiper-eyebrow">READY TO UPGRADE YOUR CAMPUS?</span>
        <h2>
          YOUR CAMPUS. <span>ONE AI</span>
          <br />
          ASSISTANT.
        </h2>
        <p>Everything students and faculty need. One intelligent place to ask.</p>
        <button
          type="button"
          className="campus-skiper-button"
          onClick={onGetStarted}
        >
          Get Started <i className="fa-solid fa-arrow-right" aria-hidden="true" />
        </button>
        <a
          className="campus-skiper-credit"
          href="https://skiper-ui.com"
          target="_blank"
          rel="noreferrer"
        >
          Animation by Skiper UI
        </a>
      </div>
    </section>
  );
}
