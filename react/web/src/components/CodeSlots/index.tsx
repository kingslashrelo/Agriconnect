"use client";

import { useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import "./CodeSlots.css";

type SlotsStatus = "idle" | "typing" | "success" | "error";

interface CodeSlotsProps {
  length?: number;
  status?: SlotsStatus;
  onChange?: (value: string) => void;
  onComplete?: (value: string) => void;
  accentColor?: string;
  inkColor?: string;
  slotColor?: string;
  digitColor?: string;
  dangerColor?: string;
  slotSize?: number;
  gap?: number;
  radius?: number;
  bounce?: number;
  settle?: number;
  rise?: number;
  cascade?: number;
  mask?: boolean;
  caret?: boolean;
  outcome?: "success" | "error" | null;
  disabled?: boolean;
}

export function CodeSlots({
  length = 6,
  status = "idle",
  onChange,
  onComplete,
  accentColor = "#059669",
  inkColor = "#065F46",
  slotColor = "#ffffff",
  digitColor,
  dangerColor = "#dc2626",
  slotSize = 26,
  gap = 4,
  radius = 8,
  bounce = 420,
  settle = 26,
  rise = 14,
  cascade = 0.02,
  mask = false,
  caret = true,
  outcome = null,
  disabled = false,
}: CodeSlotsProps) {
  const [value, setValue] = useState("");
  const [focused, setFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const activeStatus: SlotsStatus = outcome === "error" ? "error" : outcome === "success" ? "success" : status;
  const groupGap = gap + 5;

  const handleChange = (raw: string) => {
    if (disabled) return;
    const next = raw.replace(/\D/g, "").slice(0, length);
    setValue(next);
    onChange?.(next);
    if (next.length === length) onComplete?.(next);
  };

  return (
    <div
      className="code-slots"
      style={{
        ["--slots-accent" as string]: accentColor,
        ["--slots-ink" as string]: inkColor,
        ["--slots-bg" as string]: slotColor,
        ["--slots-digit" as string]: digitColor ?? inkColor,
        ["--slots-danger" as string]: dangerColor,
        ["--slots-size" as string]: `${slotSize}px`,
        ["--slots-gap" as string]: `${gap}px`,
        ["--slots-radius" as string]: `${radius}px`,
      }}
      onClick={() => inputRef.current?.focus()}
    >
      <input
        ref={inputRef}
        className="code-slots-input"
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        inputMode="numeric"
        pattern="[0-9]*"
        autoComplete="one-time-code"
        aria-label="Aadhaar number"
        disabled={disabled}
      />
      {Array.from({ length }).map((_, index) => {
        const char = value[index];
        const isActive = focused && !disabled && value.length === index;
        const grouped = (index + 1) % 4 === 0 && index !== length - 1;
        return (
          <div
            key={index}
            className="code-slots-slot"
            data-status={activeStatus}
            data-active={isActive || undefined}
            data-filled={char ? true : undefined}
            style={grouped ? { marginLeft: groupGap - gap } : undefined}
          >
            <AnimatePresence initial={false} mode="popLayout">
              {char ? (
                <motion.span
                  key={`${index}-${char}`}
                  className="code-slots-digit"
                  initial={{ y: rise, opacity: 0, scale: 0.5 }}
                  animate={{ y: 0, opacity: 1, scale: 1 }}
                  exit={{ y: -rise, opacity: 0, scale: 0.5 }}
                  transition={{ type: "spring", stiffness: bounce, damping: settle, delay: index * cascade }}
                >
                  {mask ? "\u2022" : char}
                </motion.span>
              ) : isActive && caret ? (
                <span className="code-slots-caret" />
              ) : null}
            </AnimatePresence>
          </div>
        );
      })}
      <AnimatePresence>
        {outcome === "success" && (
          <motion.span
            className="code-slots-outcome"
            style={{ color: accentColor }}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
          </motion.span>
        )}
        {outcome === "error" && (
          <motion.span
            className="code-slots-outcome"
            style={{ color: dangerColor }}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </motion.span>
        )}
      </AnimatePresence>
    </div>
  );
}
