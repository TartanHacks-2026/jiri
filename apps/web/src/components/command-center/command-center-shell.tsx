"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Store } from "lucide-react";

import { ArtifactsStrip } from "@/components/command-center/artifacts-strip";
import { MarketplaceSheet } from "@/components/command-center/marketplace-sheet";
import { PlanCard } from "@/components/command-center/plan-card";
import { StateRail } from "@/components/command-center/state-rail";
import { TopStatusBar } from "@/components/command-center/top-status-bar";
import { TracePanel } from "@/components/command-center/trace-panel";
import { VoicePanel } from "@/components/command-center/voice-panel";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCommandCenterConnection } from "@/hooks/use-command-center-connection";
import { useCommandCenterStore } from "@/store/command-center-store";
import { useShallow } from "zustand/react/shallow";

export function CommandCenterShell() {
  const {
    sessionId,
    connectionStatus,
    phase,
    phaseMessage,
    transcript,
    partialTranscript,
    planGoal,
    planSteps,
    trace,
    tools,
    artifacts,
    receipts,
    lastError,
    marketplaceOpen,
    setMarketplaceOpen,
  } = useCommandCenterStore(
    useShallow((state) => ({
      sessionId: state.sessionId,
      connectionStatus: state.connectionStatus,
      phase: state.phase,
      phaseMessage: state.phaseMessage,
      transcript: state.transcript,
      partialTranscript: state.partialTranscript,
      planGoal: state.planGoal,
      planSteps: state.planSteps,
      trace: state.trace,
      tools: state.tools,
      artifacts: state.artifacts,
      receipts: state.receipts,
      lastError: state.lastError,
      marketplaceOpen: state.marketplaceOpen,
      setMarketplaceOpen: state.setMarketplaceOpen,
    })),
  );

  const { startLive, stopLive, runReplay, sendUserText } = useCommandCenterConnection();

  return (
    <>
      <div className="relative z-10 mx-auto flex w-full max-w-[1440px] flex-col gap-4 px-3 pb-6 pt-5 md:px-6">
        <TopStatusBar
          connectionStatus={connectionStatus}
          sessionId={sessionId}
          onStartLive={startLive}
          onStop={stopLive}
          onRunDemo={runReplay}
          onOpenMarketplace={() => setMarketplaceOpen(true)}
        />

        {lastError ? (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-2 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger"
          >
            <AlertTriangle className="h-4 w-4" />
            {lastError}
          </motion.div>
        ) : null}

        <div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
          <div className="space-y-4">
            <VoicePanel
              transcript={transcript}
              partialTranscript={partialTranscript}
              onSendText={sendUserText}
            />
            <PlanCard goal={planGoal} steps={planSteps} />
            <StateRail phase={phase} phaseMessage={phaseMessage} />
          </div>

          <div className="space-y-4">
            <Card className="border-accent/20">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm uppercase tracking-[0.16em] text-muted-foreground">
                  Tool Marketplace
                </CardTitle>
                <Button size="sm" variant="secondary" onClick={() => setMarketplaceOpen(true)}>
                  <Store className="mr-1 h-3.5 w-3.5" />
                  Open
                </Button>
              </CardHeader>
              <CardContent className="space-y-2">
                {tools.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No discovered tools yet. Start live or run replay.</p>
                ) : (
                  tools.slice(0, 5).map((tool) => (
                    <div
                      key={`${tool.server}-${tool.name}`}
                      className="rounded-lg border border-border/65 bg-background/45 px-3 py-2"
                    >
                      <p className="text-sm text-foreground">{tool.name}</p>
                      <p className="text-xs text-muted-foreground">{tool.server}</p>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>

            <div className="min-h-[420px]">
              <TracePanel trace={trace} />
            </div>
          </div>
        </div>

        <ArtifactsStrip artifacts={artifacts} receipts={receipts} />
      </div>

      <MarketplaceSheet open={marketplaceOpen} tools={tools} onClose={() => setMarketplaceOpen(false)} />
    </>
  );
}
