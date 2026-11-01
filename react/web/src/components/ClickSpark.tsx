"use client";

import { useEffect, useRef } from "react";

const EASINGS: Record<string, (t: number) => number> = {
  linear: (t) => t,
  "ease-in": (t) => t * t,
  "ease-out": (t) => 1 - Math.pow(1 - t, 3),
  "ease-in-out": (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  spring: (t) => 1 + 2.4 * Math.pow(t - 1, 3) + 1.4 * Math.pow(t - 1, 2),
};

export function ClickSpark({ children }: { children: React.ReactNode }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const settings = {
      colors: ["#059669", "#34D399", "#065F46"],
      radius: 30,
      count: 8,
      width: 2,
      duration: 500,
      ease: EASINGS["ease-out"],
    };

    const bursts: any[] = [];
    let raf = 0;

    function resize() {
      if (!canvas) return;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    function onClick(e: MouseEvent) {
      if (!canvas) return;
      const burst: any = { x: e.clientX, y: e.clientY, time: performance.now(), sparks: [] };
      for (let i = 0; i < settings.count; i++) {
        const angle = ((Math.PI * 2) / settings.count) * i;
        burst.sparks.push({
          angle,
          velocity: settings.radius * (0.6 + Math.random() * 0.8),
          color: settings.colors[Math.floor(Math.random() * settings.colors.length)],
        });
      }
      bursts.push(burst);
      if (bursts.length > 32) bursts.shift();
    }
    window.addEventListener("click", onClick);

    function draw() {
      if (!canvas || !ctx) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const now = performance.now();
      for (let b = bursts.length - 1; b >= 0; b--) {
        const burst = bursts[b];
        const elapsed = now - burst.time;
        if (elapsed > settings.duration) { bursts.splice(b, 1); continue; }
        const t = elapsed / settings.duration;
        const eased = settings.ease(t);
        for (const spark of burst.sparks) {
          const dist = spark.velocity * eased;
          const x = burst.x + Math.cos(spark.angle) * dist;
          const y = burst.y + Math.sin(spark.angle) * dist;
          ctx.save();
          ctx.globalAlpha = 1 - t;
          ctx.strokeStyle = spark.color;
          ctx.lineWidth = settings.width;
          ctx.beginPath();
          ctx.moveTo(burst.x, burst.y);
          ctx.lineTo(x, y);
          ctx.stroke();
          ctx.restore();
        }
      }
      raf = requestAnimationFrame(draw);
    }
    raf = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("click", onClick);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <>
      {children}
      <canvas ref={canvasRef} style={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 2147483000 }} />
    </>
  );
}
