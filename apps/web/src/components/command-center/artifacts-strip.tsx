"use client";

import { AnimatePresence, motion } from "framer-motion";
import { FileBadge2, Link as LinkIcon, ReceiptText, ScrollText } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Artifact, Receipt } from "@/lib/event-contract";

interface ArtifactsStripProps {
  artifacts: Artifact[];
  receipts: Receipt[];
}

function ArtifactIcon({ kind }: { kind: Artifact["kind"] }) {
  if (kind === "file") {
    return <FileBadge2 className="h-4 w-4 text-primary" />;
  }
  if (kind === "link") {
    return <LinkIcon className="h-4 w-4 text-accent" />;
  }
  if (kind === "receipt") {
    return <ReceiptText className="h-4 w-4 text-warning" />;
  }

  return <ScrollText className="h-4 w-4 text-muted-foreground" />;
}

function receiptVariant(status: Receipt["status"]): "success" | "warning" | "danger" {
  if (status === "success") {
    return "success";
  }
  if (status === "warning") {
    return "warning";
  }

  return "danger";
}

export function ArtifactsStrip({ artifacts, receipts }: ArtifactsStripProps) {
  return (
    <Card className="border-accent/20">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm uppercase tracking-[0.16em] text-muted-foreground">
          Artifacts + Receipts
        </CardTitle>
      </CardHeader>
      <CardContent className="grid gap-3 lg:grid-cols-2">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Artifacts</p>
          <AnimatePresence initial={false}>
            {artifacts.length === 0 ? (
              <motion.div
                key="artifact-empty"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-lg border border-dashed border-border/70 p-3 text-sm text-muted-foreground"
              >
                No artifacts yet.
              </motion.div>
            ) : (
              artifacts
                .slice(-8)
                .reverse()
                .map((artifact) => (
                  <motion.div
                    key={artifact.id}
                    initial={{ opacity: 0, y: 12, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ duration: 0.2 }}
                    className="rounded-lg border border-success/35 bg-success/5 px-3 py-2"
                  >
                    <div className="flex items-center gap-2">
                      <ArtifactIcon kind={artifact.kind} />
                      <p className="text-sm text-foreground">{artifact.title}</p>
                    </div>
                    {artifact.content ? (
                      <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">{artifact.content}</p>
                    ) : null}
                    {artifact.url ? (
                      <a
                        className="mt-1 inline-block text-xs text-accent underline-offset-4 hover:underline"
                        href={artifact.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open artifact
                      </a>
                    ) : null}
                  </motion.div>
                ))
            )}
          </AnimatePresence>
        </div>

        <div className="space-y-2">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Action receipts</p>
          <AnimatePresence initial={false}>
            {receipts.length === 0 ? (
              <motion.div
                key="receipt-empty"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-lg border border-dashed border-border/70 p-3 text-sm text-muted-foreground"
              >
                Receipts will appear after tool execution.
              </motion.div>
            ) : (
              receipts
                .slice(-8)
                .reverse()
                .map((receipt) => (
                  <motion.div
                    key={receipt.id}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.22 }}
                    className="rounded-lg border border-border/65 bg-background/40 px-3 py-2"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm text-foreground">{receipt.title}</p>
                      <Badge variant={receiptVariant(receipt.status)}>{receipt.status}</Badge>
                    </div>
                    {receipt.details ? (
                      <p className="mt-1 text-xs text-muted-foreground">{receipt.details}</p>
                    ) : null}
                  </motion.div>
                ))
            )}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
}
