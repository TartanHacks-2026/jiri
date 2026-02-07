"use client";

import { useCallback, useRef } from "react";
import { z } from "zod";

import type { JiriOutboundMessage } from "@/lib/event-contract";
import { loadReplayEvents, replayEvents } from "@/lib/replay";
import { JiriStreamClient } from "@/lib/ws-client";
import { useCommandCenterStore } from "@/store/command-center-store";

function now() {
  return Date.now();
}

function makeSessionId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  return `session-${Date.now()}`;
}

const turnResponseSchema = z.object({
  session_id: z.string().min(1),
  reply_text: z.string(),
  end_conversation: z.boolean().default(false),
  debug: z
    .object({
      tool_trace: z.array(z.string()).default([]),
      latency_ms: z.number().int().nonnegative().default(0),
      mode: z.string().default("agent"),
    })
    .default({
      tool_trace: [],
      latency_ms: 0,
      mode: "agent",
    }),
});

function getAgentuityApiBaseUrl() {
  return (process.env.NEXT_PUBLIC_AGENTUITY_API_URL ?? "http://127.0.0.1:3500").replace(/\/$/, "");
}

export function useCommandCenterConnection() {
  const clientRef = useRef<JiriStreamClient | null>(null);
  const replayStopRef = useRef<(() => void) | null>(null);

  const setSessionId = useCommandCenterStore((state) => state.setSessionId);
  const setMode = useCommandCenterStore((state) => state.setMode);
  const setConnectionStatus = useCommandCenterStore((state) => state.setConnectionStatus);
  const ingestEvent = useCommandCenterStore((state) => state.ingestEvent);
  const addLocalUserText = useCommandCenterStore((state) => state.addLocalUserText);
  const addAssistantText = useCommandCenterStore((state) => state.addAssistantText);
  const reset = useCommandCenterStore((state) => state.reset);
  const sessionId = useCommandCenterStore((state) => state.sessionId);

  const send = useCallback((message: JiriOutboundMessage) => {
    if (!clientRef.current) {
      return false;
    }

    clientRef.current.send(message);
    return true;
  }, []);

  const stopReplay = useCallback(() => {
    replayStopRef.current?.();
    replayStopRef.current = null;
  }, []);

  const stopLive = useCallback(() => {
    const activeSessionId = useCommandCenterStore.getState().sessionId;
    const isConnected = useCommandCenterStore.getState().connectionStatus === "connected";
    if (clientRef.current && isConnected && activeSessionId && activeSessionId !== "-") {
      send({
        type: "stop_session",
        ts: now(),
        sessionId: activeSessionId,
        payload: { reason: "user" },
      });
    }

    clientRef.current?.close();
    clientRef.current = null;
    setConnectionStatus("disconnected");
    setMode("idle");
  }, [send, setConnectionStatus, setMode]);

  const startLive = useCallback(() => {
    stopReplay();
    stopLive();

    const wsUrl = process.env.NEXT_PUBLIC_JIRI_WS_URL;
    reset();

    const newSessionId = makeSessionId();
    setSessionId(newSessionId);
    setMode("live");

    if (!wsUrl) {
      setConnectionStatus("degraded");
      ingestEvent({
        type: "session.started",
        ts: now(),
        sessionId: newSessionId,
        payload: {
          mode: "live",
        },
      });
      ingestEvent({
        type: "session.state",
        ts: now(),
        sessionId: newSessionId,
        payload: {
          state: "listening",
          message: "REST fallback active (no WS URL)",
        },
      });
      return;
    }

    const client = new JiriStreamClient({
      wsUrl,
      sseUrl: process.env.NEXT_PUBLIC_JIRI_SSE_URL,
      onEvent: ingestEvent,
      onStatus: setConnectionStatus,
      onError: (message) => {
        ingestEvent({
          type: "error",
          ts: now(),
          sessionId: newSessionId,
          payload: {
            code: "frontend.stream",
            message,
            recoverable: true,
          },
        });
      },
    });

    client.connect();
    clientRef.current = client;

    setTimeout(() => {
      client.send({
        type: "start_session",
        ts: now(),
        sessionId: newSessionId,
        payload: {
          client: "web",
          replay: false,
        },
      });
    }, 120);
  }, [
    ingestEvent,
    reset,
    setConnectionStatus,
    setMode,
    setSessionId,
    stopLive,
    stopReplay,
  ]);

  const sendTurnViaProxy = useCallback(
    async (activeSessionId: string, text: string) => {
      setConnectionStatus("degraded");

      ingestEvent({
        type: "session.state",
        ts: now(),
        sessionId: activeSessionId,
        payload: {
          state: "routing",
          message: "Routing through Agentuity bridge",
        },
      });

      try {
        const response = await fetch(`${getAgentuityApiBaseUrl()}/api/jiri/turn`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            session_id: activeSessionId,
            user_text: text,
            client: "web",
            meta: {
              device: "web",
              voice: false,
              timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
            },
          }),
        });

        const raw = await response.json().catch(() => null);
        if (!response.ok) {
          const errorMessage =
            raw && typeof raw === "object" && "message" in raw ? String(raw.message) : `HTTP ${response.status}`;
          throw new Error(errorMessage);
        }

        const parsed = turnResponseSchema.safeParse(raw);
        if (!parsed.success) {
          throw new Error("Invalid /turn response from Agentuity bridge");
        }

        const turn = parsed.data;
        if (turn.session_id !== activeSessionId) {
          setSessionId(turn.session_id);
        }

        addAssistantText(turn.reply_text);

        ingestEvent({
          type: "receipt.created",
          ts: now(),
          sessionId: turn.session_id,
          payload: {
            receipt: {
              id: `turn-${Date.now()}`,
              title: "Turn processed",
              status: "success",
              details: `${turn.debug.mode} - ${turn.debug.latency_ms}ms`,
            },
          },
        });

        turn.debug.tool_trace.forEach((line, index) => {
          ingestEvent({
            type: "receipt.created",
            ts: now() + index + 1,
            sessionId: turn.session_id,
            payload: {
              receipt: {
                id: `trace-${Date.now()}-${index}`,
                title: "Tool trace",
                status: "warning",
                details: line,
              },
            },
          });
        });

        ingestEvent({
          type: "artifact.created",
          ts: now(),
          sessionId: turn.session_id,
          payload: {
            artifact: {
              id: `artifact-reply-${Date.now()}`,
              kind: "text",
              title: "Assistant reply",
              content: turn.reply_text,
              meta: {
                source: "agentuity-proxy",
              },
            },
          },
        });

        ingestEvent({
          type: "session.state",
          ts: now(),
          sessionId: turn.session_id,
          payload: {
            state: "complete",
            message: "Turn complete",
          },
        });

        if (turn.end_conversation) {
          ingestEvent({
            type: "session.ended",
            ts: now(),
            sessionId: turn.session_id,
            payload: {
              reason: "user",
            },
          });
        }
      } catch (error) {
        ingestEvent({
          type: "error",
          ts: now(),
          sessionId: activeSessionId,
          payload: {
            code: "frontend.agentuity.turn",
            message: error instanceof Error ? error.message : "Agentuity bridge request failed",
            recoverable: true,
          },
        });
      }
    },
    [addAssistantText, ingestEvent, setConnectionStatus, setSessionId],
  );

  const sendUserText = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed) {
        return;
      }

      const state = useCommandCenterStore.getState();
      let activeSessionId = state.sessionId || sessionId;
      if (!activeSessionId || activeSessionId === "-") {
        activeSessionId = makeSessionId();
        setSessionId(activeSessionId);
      }

      if (state.mode === "idle") {
        setMode("live");
      }

      addLocalUserText(trimmed);

      if (state.connectionStatus === "connected" && clientRef.current) {
        send({
          type: "user_text",
          ts: now(),
          sessionId: activeSessionId,
          payload: { text: trimmed },
        });
        return;
      }

      void sendTurnViaProxy(activeSessionId, trimmed);
    },
    [addLocalUserText, send, sendTurnViaProxy, sessionId, setMode, setSessionId],
  );

  const runReplay = useCallback(async () => {
    stopLive();
    stopReplay();

    reset();

    const replaySessionId = `replay-${Date.now()}`;
    setSessionId(replaySessionId);
    setMode("replay");
    setConnectionStatus("replay");

    try {
      const events = await loadReplayEvents();
      replayStopRef.current = replayEvents({
        events,
        onEvent: (event) => {
          ingestEvent({
            ...event,
            sessionId: replaySessionId,
          });
        },
      });
    } catch (error) {
      ingestEvent({
        type: "error",
        ts: now(),
        sessionId: replaySessionId,
        payload: {
          code: "frontend.replay",
          message: error instanceof Error ? error.message : "Replay load failed",
          recoverable: true,
        },
      });
    }
  }, [
    ingestEvent,
    reset,
    setConnectionStatus,
    setMode,
    setSessionId,
    stopLive,
    stopReplay,
  ]);

  return {
    startLive,
    stopLive,
    runReplay,
    sendUserText,
    stopReplay,
  };
}
