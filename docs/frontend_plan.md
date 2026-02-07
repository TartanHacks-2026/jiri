# Jiri Command Center Frontend Plan

## 1) One-Page UI Spec

### Product Intent
A single-screen Command Center that lets judges instantly see the full agent loop: **Voice -> Transcript -> Plan -> Tool Discovery -> Tool Execution -> Artifacts**. If backend streaming fails, the same UI runs from replay logs.

### Visual Direction
- Theme: **Signal Ops / Future Lab (2026)**
- Tone: Clean, high-contrast, data-rich, not game-like
- Core effects: soft gradients, subtle glow edges, glass panels, restrained motion
- No heavy 3D; depth is created with layered cards + parallax-lite motion

### Layout (Desktop)
- **Top bar**: Jiri logo, session ID, connection pills (`Connected`, `Degraded`, `Replay`), Run Demo button
- **Main split (2 columns)**
- **Left column (Voice + Conversation)**
  - Voice control card (mic button stub, start/stop session)
  - Live transcript stream (partial/final)
  - Agent plan card (current objective + steps)
  - State rail (`Listening`, `Routing`, `Executing`, `Complete`)
- **Right column (Execution Surface)**
  - Tool Trace timeline (tool started/result/error)
  - Tool Marketplace launcher + slide-over sheet
  - Marketplace list with skeleton loading and install/enable states
- **Bottom strip (Artifacts + Receipts)**
  - Artifact cards: files, links, previews
  - Action receipts: confirmations, approvals, completion logs

### Mobile Behavior
- Single-column stack
- Sticky top status and bottom artifacts drawer
- Marketplace opens full-screen sheet

### Animation Moments (Framer Motion)
- State rail transitions with shared layout animation and progress pulse
- New trace events slide/fade in with tiny glow bloom
- Marketplace sheet spring slide-in; skeleton shimmer while loading
- Artifact cards scale/fade in and success pulse ring on creation
- Respect `prefers-reduced-motion`

### Core User Flows
1. **Live Session Flow**
- User taps Start -> WS connects -> transcript and events stream -> trace + artifacts update live.
2. **Degraded Flow**
- WS disconnects -> SSE fallback attempted -> status becomes `Degraded` if fallback active.
3. **Replay Flow**
- User taps Run Demo -> loads `/public/demo/demo_run.jsonl` -> replays with event timing -> status `Replay`.
4. **Tool Discovery Flow**
- `mcp.tools.discovered` events populate marketplace -> user inspects tools and availability.

## 2) Event Contract (Frontend <-> Backend)

### Event Envelope (Inbound)
All inbound events must match:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "JiriInboundEvent",
  "type": "object",
  "required": ["type", "ts", "sessionId", "payload"],
  "properties": {
    "type": { "type": "string" },
    "ts": { "type": "integer", "minimum": 0 },
    "sessionId": { "type": "string", "minLength": 1 },
    "traceId": { "type": "string" },
    "payload": { "type": "object" }
  },
  "additionalProperties": false
}
```

### Inbound `type` values and payload schemas
- `session.started`: `{ "mode": "live|replay", "userId?": "string" }`
- `session.state`: `{ "state": "idle|listening|routing|executing|complete|error", "message?": "string" }`
- `asr.partial`: `{ "text": "string" }`
- `asr.final`: `{ "text": "string", "confidence?": "number" }`
- `agent.plan`: `{ "goal": "string", "steps": [{ "id": "string", "label": "string", "status": "pending|active|done|error" }] }`
- `mcp.tools.discovered`: `{ "tools": [{ "name": "string", "description": "string", "server": "string", "status": "available|installing|ready|error" }] }`
- `mcp.toolcall.started`: `{ "tool": "string", "input": {}, "callId": "string" }`
- `mcp.toolcall.result`: `{ "tool": "string", "callId": "string", "durationMs": "number", "output": {} }`
- `mcp.toolcall.error`: `{ "tool": "string", "callId": "string", "durationMs?": "number", "error": { "code": "string", "message": "string" } }`
- `artifact.created`: `{ "artifact": { "id": "string", "kind": "file|link|text|receipt", "title": "string", "url?": "string", "content?": "string", "meta?": {} } }`
- `receipt.created`: `{ "receipt": { "id": "string", "title": "string", "status": "success|warning|error", "details?": "string" } }`
- `session.ended`: `{ "reason": "user|system|error" }`
- `error`: `{ "code": "string", "message": "string", "recoverable": "boolean" }`
- `heartbeat`: `{ "seq": "number" }`

### Outbound Message Format (Client -> Backend)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "JiriOutboundMessage",
  "type": "object",
  "required": ["type", "ts", "sessionId", "payload"],
  "properties": {
    "type": {
      "enum": ["start_session", "stop_session", "user_text", "audio_chunk", "ping"]
    },
    "ts": { "type": "integer", "minimum": 0 },
    "sessionId": { "type": "string", "minLength": 1 },
    "payload": { "type": "object" }
  },
  "additionalProperties": false
}
```

Payloads:
- `start_session`: `{ "client": "web", "replay": false }`
- `stop_session`: `{ "reason": "user" }`
- `user_text`: `{ "text": "string" }`
- `audio_chunk`: `{ "encoding": "pcm16|g711", "sampleRate": 16000, "dataBase64": "string" }` (stub-ready)
- `ping`: `{ "seq": "number" }`

## 3) Proposed File/Folder Structure

```text
apps/web/
  public/demo/demo_run.jsonl
  src/app/
    layout.tsx
    page.tsx
    globals.css
  src/components/command-center/
    command-center-shell.tsx
    top-status-bar.tsx
    voice-panel.tsx
    state-rail.tsx
    plan-card.tsx
    trace-panel.tsx
    marketplace-sheet.tsx
    artifacts-strip.tsx
    logo-jiri.tsx
  src/components/ui/                 # shadcn/ui
  src/lib/
    event-contract.ts                # zod schemas + TS types
    replay.ts                        # json/jsonl parser + timed playback
    ws-client.ts                     # ws + sse fallback connector
    utils.ts
  src/store/
    command-center-store.ts          # zustand state/actions
  src/hooks/
    use-command-center-connection.ts
  .env.example
  package.json
  tailwind.config.ts
  postcss.config.js
  components.json
```

## 4) Implementation Steps (Ordered)

### MVP First
1. Scaffold Next.js App Router + TypeScript + Tailwind in `apps/web`.
2. Install and configure shadcn/ui, Framer Motion, Zustand, Zod.
3. Build static page shell with 3-pane layout and reusable cards.
4. Define Zod event contract and typed store actions.
5. Implement WS connector (`NEXT_PUBLIC_JIRI_WS_URL`) + SSE fallback status handling.
6. Render live transcript, plan, trace, tools, artifacts from store updates.
7. Implement Replay Mode using local demo log with timed dispatch.

### “Insane” Polish Pass
8. Add branded Jiri logo + strong visual system tokens (color, glow, spacing, typography).
9. Add motion choreography (state rail, trace entries, marketplace sheet, artifact pulse).
10. Add skeleton/loading, empty/error/degraded states and robust validation to ignore malformed events.
11. Final responsiveness + accessibility pass (keyboard/focus/reduced motion).
12. Validate build/lint/types and document local run + demo log generation.
