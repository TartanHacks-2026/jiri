"use client";

import { AnimatePresence, motion } from "framer-motion";
import { AlertTriangle, CheckCircle2, LoaderCircle, Sparkles } from "lucide-react";


import { formatTime } from "@/lib/utils";
import type { TraceLine } from "@/store/command-center-store";

interface TracePanelProps {
  trace: TraceLine[];
}

function TraceIcon({ type }: { type: TraceLine["type"] }) {
  if (type === "started") {
    return <LoaderCircle className="h-4 w-4 animate-spin text-accent" />;
  }
  if (type === "result") {
    return (
      <motion.div
        initial={{ rotate: 0 }}
        animate={{ rotate: 360 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <CheckCircle2 className="h-4 w-4 text-success" />
      </motion.div>
    );
  }
  if (type === "error") {
    return <AlertTriangle className="h-4 w-4 text-danger" />;
  }

  return <Sparkles className="h-4 w-4 text-muted-foreground" />;
}

function lineClasses(type: TraceLine["type"]) {
  if (type === "result") {
    return "border-success/40 bg-success/5";
  }
  if (type === "error") {
    return "border-danger/40 bg-danger/5";
  }
  if (type === "started") {
    return "border-accent/40 bg-accent/5";
  }

  return "border-border/65 bg-background/45";
}

export function TracePanel({ trace }: TracePanelProps) {
  const items = trace.slice(-18).reverse();

  return (
    <div className="space-y-3">
      <h3 className="text-sm uppercase tracking-[0.16em] text-muted-foreground">
        Tool Trace
      </h3>
      <div className="space-y-2">
        <AnimatePresence initial={false}>
          {items.length === 0 ? (
            <motion.div
              key="trace-empty"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="rounded-lg border border-dashed border-border/70 p-4 text-sm text-muted-foreground"
            >
              Waiting for tool events from backend or replay.
            </motion.div>
          ) : (
            items.map((item) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: 14, scale: 0.98 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.22 }}
                className={`rounded-lg border px-3 py-2 ${lineClasses(item.type)}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2">
                    <TraceIcon type={item.type} />
                    <div>
                      <p className="text-sm text-foreground">{item.title}</p>
                      {item.subtitle ? (
                        <p className="font-mono text-xs text-muted-foreground">{item.subtitle}</p>
                      ) : null}
                    </div>
                  </div>
                  <span className="font-mono text-[10px] uppercase tracking-wide text-muted-foreground">
                    {formatTime(item.ts)}
                  </span>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
