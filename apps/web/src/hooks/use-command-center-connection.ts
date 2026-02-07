"use client";

import { useCallback, useRef } from "react";

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

export function useCommandCenterConnection() {
  const clientRef = useRef<JiriStreamClient | null>(null);
  const replayStopRef = useRef<(() => void) | null>(null);

  const setSessionId = useCommandCenterStore((state) => state.setSessionId);
  const setMode = useCommandCenterStore((state) => state.setMode);
  const setConnectionStatus = useCommandCenterStore((state) => state.setConnectionStatus);
  const ingestEvent = useCommandCenterStore((state) => state.ingestEvent);
  const addLocalUserText = useCommandCenterStore((state) => state.addLocalUserText);
  const reset = useCommandCenterStore((state) => state.reset);
  const sessionId = useCommandCenterStore((state) => state.sessionId);

  const send = useCallback((message: JiriOutboundMessage) => {
    clientRef.current?.send(message);
  }, []);

  const stopReplay = useCallback(() => {
    replayStopRef.current?.();
    replayStopRef.current = null;
  }, []);

  const stopLive = useCallback(() => {
    const activeSessionId = useCommandCenterStore.getState().sessionId;
    if (clientRef.current && activeSessionId && activeSessionId !== "-") {
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
    if (!wsUrl) {
      setConnectionStatus("degraded");
      return;
    }

    reset();

    const newSessionId = makeSessionId();
    setSessionId(newSessionId);
    setMode("live");

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

  const sendUserText = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed) {
        return;
      }

      const activeSessionId = useCommandCenterStore.getState().sessionId || sessionId;
      if (!activeSessionId || activeSessionId === "-") {
        return;
      }

      addLocalUserText(trimmed);

      send({
        type: "user_text",
        ts: now(),
        sessionId: activeSessionId,
        payload: { text: trimmed },
      });
    },
    [addLocalUserText, send, sessionId],
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
