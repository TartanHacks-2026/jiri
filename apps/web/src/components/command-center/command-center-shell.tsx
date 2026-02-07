"use client";

import { motion } from "framer-motion";
import { AlertTriangle } from "lucide-react";

import { ArtifactsStrip } from "@/components/command-center/artifacts-strip";
import { FloatingModule } from "@/components/command-center/floating-module";
import { JarvisOrb } from "@/components/command-center/jarvis-orb";
import { MarketplaceSheet } from "@/components/command-center/marketplace-sheet";
import { PlanCard } from "@/components/command-center/plan-card";
import { StateRail } from "@/components/command-center/state-rail";
import { TechLines } from "@/components/command-center/tech-lines";
import { TopStatusBar } from "@/components/command-center/top-status-bar";
import { TracePanel } from "@/components/command-center/trace-panel";
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
  const isFocused = useFocusMode({ idleTimeout: 2000 });

  // Determine active modules for tech lines
  const activeModules = [];
  if (trace.length > 0) activeModules.push("trace");
  if (tools.length > 0) activeModules.push("tools");
  if (planGoal || planSteps.length > 0) activeModules.push("plan");

  return (
    <>
      {/* Top Status Bar (Fixed) */}
      <div className="fixed left-0 right-0 top-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto max-w-[1440px] px-3 py-2 md:px-6">
          <TopStatusBar
            connectionStatus={connectionStatus}
            sessionId={sessionId}
            onStartLive={startLive}
            onStop={stopLive}
            onRunDemo={runReplay}
            onOpenMarketplace={() => setMarketplaceOpen(true)}
          />
        </div>
      </div>

      {/* Error Banner */}
      {lastError && (
        <div className="fixed left-0 right-0 top-16 z-40 px-3 md:px-6">
          <div className="mx-auto max-w-[1440px]">
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger"
            >
              <AlertTriangle className="h-4 w-4" />
              {lastError}
            </motion.div>
          </div>
        </div>
      )}

      {/* Main Radial Layout */}
      <div className="relative h-screen w-screen overflow-hidden pt-16">
        {/* Tech Lines (Background Layer) */}
        <TechLines activeModules={activeModules} orbCenter={{ x: "50%", y: "50%" }} />

        {/* Central Orb */}
        <JarvisOrb
          className="absolute left-1/2 top-1/2 z-10 -translate-x-1/2 -translate-y-1/2"
          transcript={transcript.map((t) => ({ role: t.role, text: t.text }))}
          partialTranscript={partialTranscript}
          isListening={connectionStatus === "connected"}
          isThinking={phase === "thinking"}
        />

        {/* Floating Modules (Radial Positioning) */}

        {/* Trace Panel (Right) */}
        <FloatingModule position="trace" isFocused={isFocused} className="w-[420px]">
          <TracePanel trace={trace} />
        </FloatingModule>

        {/* Tools Quick View (Left) */}
        <FloatingModule position="tools" isFocused={isFocused} className="w-[320px]">
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

        {/* Plan Card (Bottom Right) */}
        {(planGoal || planSteps.length > 0) && (
          <FloatingModule position="plan" isFocused={isFocused} className="w-[380px]">
            <PlanCard goal={planGoal} steps={planSteps} />
          </FloatingModule>
        )}

        {/* Artifacts (Bottom Left) */}
        {(artifacts.length > 0 || receipts.length > 0) && (
          <FloatingModule position="artifacts" isFocused={isFocused} className="w-[380px]">
            <ArtifactsStrip artifacts={artifacts} receipts={receipts} />
          </FloatingModule>
        )}

        {/* State Rail (Bottom Center) */}
        <FloatingModule position="stateRail" isFocused={isFocused} className="w-[300px]">
          <StateRail phase={phase} phaseMessage={phaseMessage} />
        </FloatingModule>
      </div>

      {/* Marketplace Sheet (Overlay) */}
      <MarketplaceSheet open={marketplaceOpen} tools={tools} onClose={() => setMarketplaceOpen(false)} />
    </>
  );
}
