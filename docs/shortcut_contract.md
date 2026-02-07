# Siri Shortcut API Contract

> **Endpoint:** `POST /turn`  
> **Purpose:** Power the "Dictate → POST → Speak → Repeat" loop for Jarvis-like voice assistant

## Request Schema

```json
{
  "session_id": "string-or-empty",
  "user_text": "string",
  "user_id": "optional-string",
  "client": "shortcut",
  "meta": {
    "timezone": "America/New_York",
    "device": "iphone",
    "voice": true,
    "app_version": "optional"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `session_id` | No | Empty for new session, reuse for continuity |
| `user_text` | **Yes** | Transcribed speech from Siri |
| `user_id` | No | Optional user identifier |
| `client` | No | Default: "shortcut" |
| `meta` | No | Device metadata |

## Response Schema

```json
{
  "session_id": "uuid-string",
  "reply_text": "spoken response",
  "end_conversation": false,
  "debug": {
    "tool_trace": [],
    "latency_ms": 150,
    "mode": "agent"
  }
}
```

| Field | Always Present | Description |
|-------|----------------|-------------|
| `session_id` | **Yes** | UUID for session continuity |
| `reply_text` | **Yes** | 1-3 sentence speakable response |
| `end_conversation` | Yes | `true` if user said stop/end/goodbye |
| `debug` | Yes | Tool traces and latency info |

---

## Siri Shortcut Build Guide

### Create Shortcut: "Jarvis"

#### A) Initialize Session
1. **Text** → Empty string → Set Variable `SessionID`

#### B) Main Loop (Repeat 20 Times)

```
2. Repeat (20 Times)
   │
   ├── 2.1 Dictate Text
   │       Prompt: "What do you want to do?"
   │       → Variable: UserText
   │
   ├── 2.2 If (UserText is empty)
   │       → Stop this Shortcut
   │
   ├── 2.3 If (UserText contains "stop" OR "end" OR "goodbye")
   │       → Speak "Got it — ending."
   │       → Stop this Shortcut
   │
   ├── 2.4 Dictionary (Payload)
   │       session_id: SessionID
   │       user_text: UserText
   │       client: "shortcut"
   │       meta: {voice: true, timezone: "America/New_York", device: "iphone"}
   │
   ├── 2.5 Get Contents of URL
   │       URL: https://YOUR_DOMAIN/turn
   │       Method: POST
   │       Body: JSON (Payload)
   │       Headers: Content-Type: application/json
   │       → Variable: Resp
   │
   ├── 2.6 Get Dictionary Value from Resp
   │       session_id → NewSessionID
   │       reply_text → ReplyText
   │       end_conversation → EndFlag
   │
   ├── 2.7 Set Variable SessionID = NewSessionID
   │
   ├── 2.8 Speak Text: ReplyText
   │
   └── 2.9 If (EndFlag is true)
           → Stop this Shortcut

End Repeat
```

---

## Test with Curl

```bash
# First turn (new session)
curl -X POST http://localhost:8000/turn \
  -H "Content-Type: application/json" \
  -d '{"session_id":"","user_text":"hello","client":"shortcut","meta":{"voice":true}}'

# Subsequent turn (with session)
curl -X POST http://localhost:8000/turn \
  -H "Content-Type: application/json" \
  -d '{"session_id":"<SESSION_ID>","user_text":"what can you do","client":"shortcut","meta":{"voice":true}}'

# End conversation
curl -X POST http://localhost:8000/turn \
  -H "Content-Type: application/json" \
  -d '{"session_id":"<SESSION_ID>","user_text":"stop","client":"shortcut","meta":{"voice":true}}'
```

---

## Rules

1. **session_id** must always be returned (new UUID if request had empty)
2. **reply_text** must never be empty
3. **end_conversation** = `true` when user says: stop, end, goodbye, cancel
4. **Replies are speakable**: max 2-3 sentences, no markdown or URLs
5. **Fallback always works**: if agent/MCP fails, returns helpful demo response
