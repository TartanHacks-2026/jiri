"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Bot, ServerCog, Wrench } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { ToolInfo } from "@/lib/event-contract";

interface MarketplaceSheetProps {
  open: boolean;
  tools: ToolInfo[];
  onClose: () => void;
}

function statusVariant(status: ToolInfo["status"]): "success" | "warning" | "secondary" | "danger" {
  if (status === "ready") {
    return "success";
  }
  if (status === "installing") {
    return "warning";
  }
  if (status === "error") {
    return "danger";
  }

  return "secondary";
}

export function MarketplaceSheet({ open, tools, onClose }: MarketplaceSheetProps) {
  return (
    <AnimatePresence>
      {open ? (
        <>
          <motion.button
            type="button"
            aria-label="Close marketplace"
            className="fixed inset-0 z-40 bg-black/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 200, damping: 24 }}
            className="fixed right-0 top-0 z-50 h-full w-full max-w-md border-l border-accent/30 bg-background/95 p-4 backdrop-blur-xl"
          >
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Tool Marketplace
                </h2>
                <p className="text-xs text-muted-foreground">Discovery + capability routing</p>
              </div>
              <Button size="sm" variant="outline" onClick={onClose}>
                Close
              </Button>
            </div>

            <div className="space-y-2 overflow-auto pb-6">
              {tools.length === 0
                ? Array.from({ length: 5 }).map((_, index) => (
                    <Card
                      key={`sk-${index}`}
                      className="overflow-hidden border-border/60 bg-background/40 p-3"
                    >
                      <div className="h-3 w-28 rounded bg-gradient-to-r from-card via-muted/60 to-card bg-[length:220%_100%] animate-shimmer" />
                      <div className="mt-2 h-2.5 w-44 rounded bg-gradient-to-r from-card via-muted/60 to-card bg-[length:220%_100%] animate-shimmer" />
                    </Card>
                  ))
                : tools.map((tool) => (
                    <motion.div
                      key={`${tool.server}-${tool.name}`}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="rounded-lg border border-border/65 bg-card/70 p-3"
                    >
                      <div className="mb-2 flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <Bot className="h-4 w-4 text-accent" />
                          <p className="text-sm font-medium text-foreground">{tool.name}</p>
                        </div>
                        <Badge variant={statusVariant(tool.status)}>{tool.status}</Badge>
                      </div>

                      <p className="mb-2 text-xs text-muted-foreground">{tool.description}</p>

                      <div className="mb-2 flex items-center gap-1 text-[11px] uppercase tracking-wide text-muted-foreground">
                        <ServerCog className="h-3.5 w-3.5" />
                        {tool.server}
                      </div>

                      <Button size="sm" variant="secondary" className="w-full">
                        <Wrench className="mr-1 h-3.5 w-3.5" />
                        {tool.status === "ready" ? "Enabled" : "Inspect"}
                      </Button>
                    </motion.div>
                  ))}
            </div>
          </motion.aside>
        </>
      ) : null}
    </AnimatePresence>
  );
}
