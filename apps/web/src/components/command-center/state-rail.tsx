"use client";

import { motion } from "framer-motion";

import type { SessionPhase } from "@/store/command-center-store";

interface StateRailProps {
  phase: SessionPhase;
  phaseMessage: string;
}

const STATES: Array<{ key: SessionPhase; label: string }> = [
  { key: "listening", label: "Listening" },
  { key: "routing", label: "Routing" },
  { key: "executing", label: "Executing" },
  { key: "complete", label: "Complete" },
];

export function StateRail({ phase, phaseMessage }: StateRailProps) {
  const activeIndex = Math.max(
    0,
    STATES.findIndex((state) => state.key === phase),
  );

  return (
    <div className="space-y-3">
      <h3 className="text-sm uppercase tracking-[0.16em] text-muted-foreground">
        State Rail
      </h3>
      <div className="space-y-3">
        <div className="grid grid-cols-4 gap-2">
          {STATES.map((state, index) => {
            const isPastOrCurrent = index <= activeIndex;
            const isCurrent = index === activeIndex;

            return (
              <div
                key={state.key}
                className="relative overflow-hidden rounded-lg border border-border/70 bg-background/55 px-1.5 py-2"
              >
                {isCurrent ? (
                  <motion.div
                    layoutId="state-rail-indicator"
                    className="absolute inset-0 rounded-lg border border-accent/40 bg-accent/10"
                    transition={{ type: "spring", stiffness: 240, damping: 22 }}
                  />
                ) : null}
                <div className="relative z-10 text-center">
                  <div
                    className={`mx-auto h-2 w-2 rounded-full ${isPastOrCurrent
                        ? "bg-primary shadow-[0_0_14px_rgba(61,239,199,0.78)]"
                        : "bg-muted"
                      }`}
                  />
                  <div className="mt-1 text-[11px] uppercase tracking-wide text-muted-foreground">
                    {state.label}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <p className="font-mono text-xs text-muted-foreground">{phaseMessage}</p>
      </div>
    </div>
  );
}
