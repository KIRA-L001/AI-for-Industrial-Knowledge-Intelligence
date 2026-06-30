"use client";

import { useEffect, useState } from "react";

const SLIDES = ["/auth/slide-1.svg", "/auth/slide-2.svg", "/auth/slide-3.svg"];

const INTERVAL_MS = 5000;

/**
 * Auto-sliding crossfade background for the auth visual panel.
 * Cycles through the slide images and exposes pagination dots + a caption.
 * Purely decorative; respects prefers-reduced-motion.
 */
export function AuthSlideshow() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;
    const id = setInterval(() => setIndex((i) => (i + 1) % SLIDES.length), INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  return (
    <>
      {/* Crossfading images */}
      <div className="absolute inset-0 z-0">
        {SLIDES.map((src, i) => (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            key={src}
            src={src}
            alt=""
            aria-hidden
            className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-1000 ease-in-out ${
              i === index ? "opacity-100" : "opacity-0"
            }`}
          />
        ))}
        {/* legibility scrim — light, only darkens the bottom for the text/dots */}
        <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-transparent" />
        <div className="absolute inset-0 bg-background/15" />
      </div>

      {/* Pagination dots (bottom-right, like the reference) */}
      <div className="absolute bottom-10 right-10 flex items-center gap-2">
        {SLIDES.map((src, i) => (
          <button
            key={src}
            onClick={() => setIndex(i)}
            aria-label={`Go to slide ${i + 1}`}
            className={`h-1.5 rounded-full transition-all duration-300 ${
              i === index ? "w-6 bg-foreground/90" : "w-2 bg-foreground/35 hover:bg-foreground/60"
            }`}
          />
        ))}
      </div>
    </>
  );
}
