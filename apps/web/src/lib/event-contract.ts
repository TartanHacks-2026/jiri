import { z } from "zod";

const baseInbound = z.object({
  type: z.string(),
  ts: z.number().int().nonnegative(),
  sessionId: z.string().min(1),
  traceId: z.string().optional(),
  payload: z.unknown(),
});

const planStepSchema = z.object({
  id: z.string(),
  label: z.string(),
  status: z.enum(["pending", "active", "done", "error"]),
});

const toolSchema = z.object({
  name: z.string(),
  description: z.string(),
  server: z.string(),
  status: z.enum(["available", "installing", "ready", "error"]),
  tags: z.array(z.string()).optional(),
});

const artifactSchema = z.object({
  id: z.string(),
  kind: z.enum(["file", "link", "text", "receipt"]),
  title: z.string(),
  url: z.string().url().optional(),
  content: z.string().optional(),
  meta: z.record(z.string(), z.unknown()).optional(),
});

const receiptSchema = z.object({
  id: z.string(),
  title: z.string(),
  status: z.enum(["success", "warning", "error"]),
  details: z.string().optional(),
  ts: z.number().int().nonnegative().optional(),
});

const sessionStartedEvent = baseInbound.extend({
  type: z.literal("session.started"),
  payload: z.object({
    mode: z.enum(["live", "replay"]),
    userId: z.string().optional(),
  }),
});

const sessionStateEvent = baseInbound.extend({
  type: z.literal("session.state"),
  payload: z.object({
    state: z.enum(["idle", "listening", "routing", "executing", "complete", "error"]),
    message: z.string().optional(),
  }),
});

const asrPartialEvent = baseInbound.extend({
  type: z.literal("asr.partial"),
  payload: z.object({
    text: z.string(),
  }),
});

const asrFinalEvent = baseInbound.extend({
  type: z.literal("asr.final"),
  payload: z.object({
    text: z.string(),
    confidence: z.number().min(0).max(1).optional(),
  }),
});

const agentPlanEvent = baseInbound.extend({
  type: z.literal("agent.plan"),
  payload: z.object({
    goal: z.string(),
    steps: z.array(planStepSchema),
  }),
});

const toolsDiscoveredEvent = baseInbound.extend({
  type: z.literal("mcp.tools.discovered"),
  payload: z.object({
    tools: z.array(toolSchema),
  }),
});

const toolCallStartedEvent = baseInbound.extend({
  type: z.literal("mcp.toolcall.started"),
  payload: z.object({
    tool: z.string(),
    callId: z.string(),
    input: z.record(z.string(), z.unknown()).optional(),
  }),
});

const toolCallResultEvent = baseInbound.extend({
  type: z.literal("mcp.toolcall.result"),
  payload: z.object({
    tool: z.string(),
    callId: z.string(),
    durationMs: z.number().nonnegative(),
    output: z.record(z.string(), z.unknown()).optional(),
  }),
});

const toolCallErrorEvent = baseInbound.extend({
  type: z.literal("mcp.toolcall.error"),
  payload: z.object({
    tool: z.string(),
    callId: z.string(),
    durationMs: z.number().nonnegative().optional(),
    error: z.object({
      code: z.string(),
      message: z.string(),
    }),
  }),
});

const artifactCreatedEvent = baseInbound.extend({
  type: z.literal("artifact.created"),
  payload: z.object({
    artifact: artifactSchema,
  }),
});

const receiptCreatedEvent = baseInbound.extend({
  type: z.literal("receipt.created"),
  payload: z.object({
    receipt: receiptSchema,
  }),
});

const sessionEndedEvent = baseInbound.extend({
  type: z.literal("session.ended"),
  payload: z.object({
    reason: z.enum(["user", "system", "error"]),
  }),
});

const errorEvent = baseInbound.extend({
  type: z.literal("error"),
  payload: z.object({
    code: z.string(),
    message: z.string(),
    recoverable: z.boolean(),
  }),
});

const heartbeatEvent = baseInbound.extend({
  type: z.literal("heartbeat"),
  payload: z.object({
    seq: z.number().int().nonnegative(),
  }),
});

export const jiriInboundEventSchema = z.discriminatedUnion("type", [
  sessionStartedEvent,
  sessionStateEvent,
  asrPartialEvent,
  asrFinalEvent,
  agentPlanEvent,
  toolsDiscoveredEvent,
  toolCallStartedEvent,
  toolCallResultEvent,
  toolCallErrorEvent,
  artifactCreatedEvent,
  receiptCreatedEvent,
  sessionEndedEvent,
  errorEvent,
  heartbeatEvent,
]);

const baseOutbound = z.object({
  type: z.enum(["start_session", "stop_session", "user_text", "audio_chunk", "ping"]),
  ts: z.number().int().nonnegative(),
  sessionId: z.string().min(1),
  payload: z.unknown(),
});

const startSessionMessage = baseOutbound.extend({
  type: z.literal("start_session"),
  payload: z.object({
    client: z.literal("web"),
    replay: z.boolean().default(false),
  }),
});

const stopSessionMessage = baseOutbound.extend({
  type: z.literal("stop_session"),
  payload: z.object({
    reason: z.enum(["user", "system"]),
  }),
});

const userTextMessage = baseOutbound.extend({
  type: z.literal("user_text"),
  payload: z.object({
    text: z.string().min(1),
  }),
});

const audioChunkMessage = baseOutbound.extend({
  type: z.literal("audio_chunk"),
  payload: z.object({
    encoding: z.enum(["pcm16", "g711"]),
    sampleRate: z.number().int().positive(),
    dataBase64: z.string().min(1),
  }),
});

const pingMessage = baseOutbound.extend({
  type: z.literal("ping"),
  payload: z.object({
    seq: z.number().int().nonnegative(),
  }),
});

export const jiriOutboundMessageSchema = z.discriminatedUnion("type", [
  startSessionMessage,
  stopSessionMessage,
  userTextMessage,
  audioChunkMessage,
  pingMessage,
]);

export type JiriInboundEvent = z.infer<typeof jiriInboundEventSchema>;
export type JiriOutboundMessage = z.infer<typeof jiriOutboundMessageSchema>;
export type PlanStep = z.infer<typeof planStepSchema>;
export type ToolInfo = z.infer<typeof toolSchema>;
export type Artifact = z.infer<typeof artifactSchema>;
export type Receipt = z.infer<typeof receiptSchema>;

export function parseInboundEvent(input: unknown): JiriInboundEvent | null {
  const parsed = jiriInboundEventSchema.safeParse(input);
  if (!parsed.success) {
    return null;
  }

  return parsed.data;
}

export function parseOutboundMessage(input: unknown): JiriOutboundMessage | null {
  const parsed = jiriOutboundMessageSchema.safeParse(input);
  if (!parsed.success) {
    return null;
  }

  return parsed.data;
}
