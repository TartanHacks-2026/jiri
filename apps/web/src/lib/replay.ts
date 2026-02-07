import { type JiriInboundEvent, parseInboundEvent } from "@/lib/event-contract";

interface ReplayOptions {
  events: JiriInboundEvent[];
  onEvent: (event: JiriInboundEvent) => void;
  onDone?: () => void;
  speed?: number;
}

export async function loadReplayEvents(path = "/demo/demo_run.jsonl") {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Replay file not found: ${path}`);
  }

  const raw = await response.text();
  const trimmed = raw.trim();
  if (!trimmed) {
    return [] as JiriInboundEvent[];
  }

  const candidates: unknown[] = trimmed.startsWith("[")
    ? JSON.parse(trimmed)
    : trimmed
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line) => JSON.parse(line));

  const parsed = candidates
    .map((candidate) => parseInboundEvent(candidate))
    .filter((candidate): candidate is JiriInboundEvent => candidate !== null)
    .sort((a, b) => a.ts - b.ts);

  return parsed;
}

export function replayEvents({ events, onEvent, onDone, speed = 1 }: ReplayOptions) {
  const safeSpeed = speed > 0 ? speed : 1;
  if (events.length === 0) {
    onDone?.();
    return () => undefined;
  }

  const startedAt = events[0].ts;
  const timers: Array<ReturnType<typeof setTimeout>> = [];

  events.forEach((event) => {
    const delay = Math.max(0, (event.ts - startedAt) / safeSpeed);
    const timer = setTimeout(() => onEvent(event), delay);
    timers.push(timer);
  });

  const doneDelay = Math.max(0, (events[events.length - 1].ts - startedAt) / safeSpeed + 60);
  const doneTimer = setTimeout(() => onDone?.(), doneDelay);
  timers.push(doneTimer);

  return () => {
    timers.forEach((timer) => clearTimeout(timer));
  };
}
