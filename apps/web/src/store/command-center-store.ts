import { create } from "zustand";

import type {
  Artifact,
  JiriInboundEvent,
  PlanStep,
  Receipt,
  ToolInfo,
} from "@/lib/event-contract";

export type ConnectionStatus = "disconnected" | "connected" | "degraded" | "replay";
export type SessionPhase = "idle" | "listening" | "routing" | "executing" | "complete" | "error";

export interface TranscriptLine {
  id: string;
  ts: number;
  role: "user" | "assistant" | "system";
  text: string;
}

export interface TraceLine {
  id: string;
  ts: number;
  type: "started" | "result" | "error" | "info";
  title: string;
  subtitle?: string;
  tool?: string;
  callId?: string;
  durationMs?: number;
}

interface CommandCenterState {
  sessionId: string;
  mode: "idle" | "live" | "replay";
  connectionStatus: ConnectionStatus;
  phase: SessionPhase;
  phaseMessage: string;
  partialTranscript: string;
  transcript: TranscriptLine[];
  planGoal: string;
  planSteps: PlanStep[];
  tools: ToolInfo[];
  trace: TraceLine[];
  artifacts: Artifact[];
  receipts: Receipt[];
  lastError?: string;
  marketplaceOpen: boolean;
  setMarketplaceOpen: (open: boolean) => void;
  setSessionId: (sessionId: string) => void;
  setMode: (mode: "idle" | "live" | "replay") => void;
  setConnectionStatus: (status: ConnectionStatus) => void;
  addLocalUserText: (text: string) => void;
  addAssistantText: (text: string) => void;
  ingestEvent: (event: JiriInboundEvent) => void;
  reset: () => void;
}

const MAX_LINES = 120;

function boundedPush<T>(list: T[], value: T) {
  const updated = [...list, value];
  if (updated.length > MAX_LINES) {
    return updated.slice(updated.length - MAX_LINES);
  }

  return updated;
}

const initialState = {
  sessionId: "-",
  mode: "idle" as const,
  connectionStatus: "disconnected" as const,
  phase: "idle" as const,
  phaseMessage: "Standby",
  partialTranscript: "",
  transcript: [] as TranscriptLine[],
  planGoal: "Awaiting planner output",
  planSteps: [] as PlanStep[],
  tools: [] as ToolInfo[],
  trace: [] as TraceLine[],
  artifacts: [] as Artifact[],
  receipts: [] as Receipt[],
  lastError: undefined,
  marketplaceOpen: false,
};

export const useCommandCenterStore = create<CommandCenterState>((set, get) => ({
  ...initialState,
  setMarketplaceOpen: (open) => set({ marketplaceOpen: open }),
  setSessionId: (sessionId) => set({ sessionId }),
  setMode: (mode) => set({ mode }),
  setConnectionStatus: (connectionStatus) => set({ connectionStatus }),
  addLocalUserText: (text) => {
    const now = Date.now();
    set({
      transcript: boundedPush(get().transcript, {
        id: `local-user-${now}`,
        role: "user",
        text,
        ts: now,
      }),
    });
  },
  addAssistantText: (text) => {
    const now = Date.now();
    set({
      transcript: boundedPush(get().transcript, {
        id: `local-assistant-${now}`,
        role: "assistant",
        text,
        ts: now,
      }),
    });
  },
  ingestEvent: (event) => {
    switch (event.type) {
      case "session.started": {
        set({
          mode: event.payload.mode,
          sessionId: event.sessionId,
          phase: "listening",
          phaseMessage: "Session started",
          lastError: undefined,
        });
        break;
      }
      case "session.state": {
        set({
          phase: event.payload.state,
          phaseMessage: event.payload.message ?? event.payload.state,
        });
        break;
      }
      case "asr.partial": {
        set({ partialTranscript: event.payload.text });
        break;
      }
      case "asr.final": {
        const line: TranscriptLine = {
          id: `asr-${event.ts}`,
          role: "user",
          text: event.payload.text,
          ts: event.ts,
        };
        set({
          partialTranscript: "",
          transcript: boundedPush(get().transcript, line),
        });
        break;
      }
      case "agent.plan": {
        set({ planGoal: event.payload.goal, planSteps: event.payload.steps });
        break;
      }
      case "mcp.tools.discovered": {
        set({ tools: event.payload.tools });
        break;
      }
      case "mcp.toolcall.started": {
        const trace: TraceLine = {
          id: `trace-start-${event.payload.callId}-${event.ts}`,
          ts: event.ts,
          type: "started",
          title: `Calling ${event.payload.tool}`,
          subtitle: event.payload.callId,
          tool: event.payload.tool,
          callId: event.payload.callId,
        };

        set({
          phase: "executing",
          phaseMessage: `Executing ${event.payload.tool}`,
          trace: boundedPush(get().trace, trace),
        });
        break;
      }
      case "mcp.toolcall.result": {
        const trace: TraceLine = {
          id: `trace-result-${event.payload.callId}-${event.ts}`,
          ts: event.ts,
          type: "result",
          title: `${event.payload.tool} succeeded`,
          subtitle: `${event.payload.durationMs.toFixed(0)}ms`,
          tool: event.payload.tool,
          callId: event.payload.callId,
          durationMs: event.payload.durationMs,
        };

        set({
          trace: boundedPush(get().trace, trace),
          receipts: boundedPush(get().receipts, {
            id: `receipt-${event.payload.callId}-${event.ts}`,
            title: `${event.payload.tool} completed`,
            status: "success",
            details: `Completed in ${event.payload.durationMs.toFixed(0)}ms`,
            ts: event.ts,
          }),
          phaseMessage: `${event.payload.tool} done`,
        });
        break;
      }
      case "mcp.toolcall.error": {
        const trace: TraceLine = {
          id: `trace-error-${event.payload.callId}-${event.ts}`,
          ts: event.ts,
          type: "error",
          title: `${event.payload.tool} failed`,
          subtitle: event.payload.error.message,
          tool: event.payload.tool,
          callId: event.payload.callId,
          durationMs: event.payload.durationMs,
        };

        set({
          phase: "error",
          phaseMessage: event.payload.error.message,
          lastError: event.payload.error.message,
          trace: boundedPush(get().trace, trace),
          receipts: boundedPush(get().receipts, {
            id: `receipt-error-${event.payload.callId}-${event.ts}`,
            title: `${event.payload.tool} failed`,
            status: "error",
            details: `${event.payload.error.code}: ${event.payload.error.message}`,
            ts: event.ts,
          }),
        });
        break;
      }
      case "artifact.created": {
        set({
          artifacts: boundedPush(get().artifacts, event.payload.artifact),
        });
        break;
      }
      case "receipt.created": {
        set({
          receipts: boundedPush(get().receipts, {
            ...event.payload.receipt,
            ts: event.ts,
          }),
        });
        break;
      }
      case "session.ended": {
        set({
          phase: event.payload.reason === "error" ? "error" : "complete",
          phaseMessage: `Session ended: ${event.payload.reason}`,
        });
        break;
      }
      case "error": {
        const trace: TraceLine = {
          id: `trace-error-global-${event.ts}`,
          ts: event.ts,
          type: "error",
          title: event.payload.code,
          subtitle: event.payload.message,
        };

        set({
          phase: "error",
          phaseMessage: event.payload.message,
          lastError: event.payload.message,
          trace: boundedPush(get().trace, trace),
        });
        break;
      }
      case "heartbeat": {
        // Heartbeats keep connection alive; no UI update needed.
        break;
      }
      default:
        break;
    }
  },
  reset: () => {
    set({
      ...initialState,
      sessionId: get().sessionId,
    });
  },
}));
