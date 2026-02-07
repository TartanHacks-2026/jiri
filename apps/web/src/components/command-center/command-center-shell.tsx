"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Store } from "lucide-react";

import { ArtifactsStrip } from "@/components/command-center/artifacts-strip";
import { FloatingModule } from "@/components/command-center/floating-module";
import { JarvisOrb } from "@/components/command-center/jarvis-orb";
import { MarketplaceSheet } from "@/components/command-center/marketplace-sheet";
import { PlanCard } from "@/components/command-center/plan-card";
import { StateRail } from "@/components/command-center/state-rail";
import { TechLines } from "@/components/command-center/tech-lines";
import { TopStatusBar } from "@/components/command-center/top-status-bar";
import { TracePanel } from "@/components/command-center/trace-panel";
import { VoicePanel } from "@/components/command-center/voice-panel";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCommandCenterConnection } from "@/hooks/use-command-center-connection";
import { useFocusMode } from "@/hooks/useFocusMode";
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
  const isFocused = useFocusMode({ idleTimeout: 3800 });

  const activeModules = ["trace", "tools", "plan"].filter((key) => {
    if (key === "trace") return trace.length > 0;
    if (key === "tools") return tools.length > 0;
    if (key === "plan") return Boolean(planGoal) || planSteps.length > 0;
    return true;
  });

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
          <div className="mx-auto w-full max-w-[1120px]">
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger"
            >
              <AlertTriangle className="h-4 w-4" />
              {lastError}
            </motion.div>
          </div>
        ) : null}

        <div className="relative mx-auto hidden h-[min(780px,calc(100vh-200px))] min-h-[600px] w-full max-w-[1200px] overflow-hidden rounded-2xl border border-border/45 bg-background/35 md:grid md:grid-cols-5 md:grid-rows-5 md:gap-0">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,217,255,0.08),transparent_65%)]" />
          <TechLines activeModules={activeModules} orbCenter={{ x: "50%", y: "50%" }} />

          <JarvisOrb
            className="col-start-3 row-start-3 z-10 place-self-center"
            transcript={transcript.map((t) => ({ role: t.role, text: t.text }))}
            partialTranscript={partialTranscript}
            isListening={connectionStatus === "connected"}
            isThinking={phase === "routing" || phase === "executing"}
          />

          <FloatingModule position="tools" isFocused={isFocused} className="col-start-2 row-start-2 w-[320px] place-self-center">
            <div className="space-y-2">
              <div className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                Active Tools
              </div>
              {tools.length === 0 ? (
                <p className="text-sm text-muted-foreground">No tools discovered</p>
              ) : (
                <div className="space-y-2">
                  {tools.slice(0, 4).map((tool) => (
                    <div
                      key={`${tool.server}-${tool.name}`}
                      className="rounded-lg border border-border/40 bg-background/40 px-2 py-1.5"
                    >
                      <p className="text-xs font-medium text-foreground">{tool.name}</p>
                      <p className="text-[10px] text-muted-foreground">{tool.server}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </FloatingModule>

          <FloatingModule position="trace" isFocused={isFocused} className="col-start-4 row-start-2 w-[420px] max-h-[330px] overflow-auto place-self-center">
            <TracePanel trace={trace} />
          </FloatingModule>

          <FloatingModule position="voice" isFocused={isFocused} className="col-start-2 row-start-4 w-[420px] p-0 place-self-center">
            <VoicePanel
              transcript={transcript}
              partialTranscript={partialTranscript}
              onSendText={sendUserText}
            />
          </FloatingModule>

          <FloatingModule position="plan" isFocused={isFocused} className="col-start-4 row-start-4 w-[380px] place-self-center">
            <PlanCard goal={planGoal} steps={planSteps} />
          </FloatingModule>

          <FloatingModule position="stateRail" isFocused={isFocused} className="col-start-3 row-start-5 w-[320px] place-self-center">
            <StateRail phase={phase} phaseMessage={phaseMessage} />
          </FloatingModule>
        </div>

        <div className="mx-auto grid w-full max-w-[1120px] gap-4 md:hidden">
          <VoicePanel
            transcript={transcript}
            partialTranscript={partialTranscript}
            onSendText={sendUserText}
          />

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

          <div className="space-y-4">
            <TracePanel trace={trace} />
            <PlanCard goal={planGoal} steps={planSteps} />
            <StateRail phase={phase} phaseMessage={phaseMessage} />
          </div>
        </div>

        <div className="mx-auto w-full max-w-[1320px]">
          <ArtifactsStrip artifacts={artifacts} receipts={receipts} />
        </div>
      </div>

      <MarketplaceSheet open={marketplaceOpen} tools={tools} onClose={() => setMarketplaceOpen(false)} />
    </>
  );
}
