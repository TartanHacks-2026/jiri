# PLAN: Siri-to-App Handoff (Warm Handoff Architecture)

> **Goal:** Enable users to start with Siri, interact with Jiri backend, then seamlessly transition to the full iOS app for deeper voice interaction.

## Architecture Overview

```
┌─────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│  Siri   │────▶│  App Intent  │────▶│   Backend   │────▶│  iOS App    │
│ "Hey..."│     │ (Background) │     │  POST /turn │     │ (Foreground)│
└─────────┘     └──────────────┘     └─────────────┘     └─────────────┘
                       │                     │                    │
                       │  1. User speech     │                    │
                       │──────────────────▶  │                    │
                       │                     │                    │
                       │  2. Process + reply │                    │
                       │  ◀──────────────────│                    │
                       │  {action: "open"}   │                    │
                       │                     │                    │
                       │  3. Deep link       │                    │
                       │─────────────────────────────────────────▶│
                       │  jiri://continue?   │                    │
                       │  session_id=123     │                    │
                       │                     │                    │
                       │                     │  4. Resume session │
                       │                     │  ◀──────────────────
```

## User Review Required

> [!IMPORTANT]
> **Assumptions Made:**
> - iOS App will be built with **SwiftUI** (native)
> - Handoff triggers when backend sets `"handoff_to_app": true` in response
> - App supports URL scheme: `jiri://continue?session_id=<UUID>`
> - Biometric auth required if phone is locked

> [!WARNING]
> **Breaking Change:**
> `TurnResponse` schema will add a new optional field:
> ```json
> {
>   "handoff_to_app": false,
>   "deep_link_url": "jiri://continue?session_id=123"
> }
> ```

## Proposed Changes

### Component 1: Backend API Enhancement

#### [MODIFY] [voice_turn.py](file:///Users/nihal/Desktop/Repos/jiri/src/jiri/routers/voice_turn.py)
- Add `handoff_to_app` boolean to `TurnResponse`
- Add `deep_link_url` optional string to `TurnResponse`
- Logic: Set `handoff_to_app=True` when:
  - User intent requires visual confirmation (e.g., "book a ride")
  - Orchestrator determines task is too complex for voice-only

#### [NEW] [handoff_decision.py](file:///Users/nihal/Desktop/Repos/jiri/src/jiri/orchestrator/handoff_decision.py)
- Decision engine: Analyze user intent
- Return `should_handoff: bool`
- Patterns that trigger handoff:
  - "show me", "open", "I want to see"
  - Actions requiring forms (payment, multi-step)

---

### Component 2: iOS App Intent

#### [NEW] ios-app/AppIntents/JiriConversationIntent.swift
- Define `JiriConversationIntent` conforming to `AppIntent`
- Parameters:
  - `userText: String` (what user said)
  - `sessionID: String?` (optional, for continuity)
- Perform:
  1. Send POST to `/turn`
  2. Parse response
  3. If `handoff_to_app == true`:
     - Call `openURL(deep_link_url)`
     - Exit intent
  4. Else:
     - Return dialog response for Siri to speak

#### [NEW] ios-app/AppIntents/JiriAppShortcuts.swift
- Register Siri phrase: "Hey Jiri, let's talk"
- Maps to `JiriConversationIntent`

---

### Component 3: iOS Deep Link Handler

#### [MODIFY] ios-app/JiriApp.swift (SwiftUI App entry)
- Add `.onOpenURL { url in ... }`
- Parse `jiri://continue?session_id=<UUID>`
- Extract `session_id`
- Navigate to `VoiceConversationView(sessionID: ...)`

#### [NEW] ios-app/Views/VoiceConversationView.swift
- Auto-start microphone on appear
- Load session history from backend: `GET /session/{id}/history` (new endpoint)
- Display minimal UI: waveform + transcript
- Continue conversation via WebSocket or repeated `/turn` calls

---

### Component 4: Session History Endpoint

#### [NEW] [session.py](file:///Users/nihal/Desktop/Repos/jiri/src/jiri/routers/session.py)
- `GET /session/{session_id}/history`
- Returns:
  ```json
  {
    "session_id": "uuid",
    "messages": [
      {"role": "user", "content": "Book a ride"},
      {"role": "assistant", "content": "Opening app..."}
    ]
  }
  ```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | Python 3.13, FastAPI |
| iOS App | SwiftUI (iOS 17+) |
| App Intents | Swift, AppIntentsFramework |
| Deep Linking | Universal Links / Custom URL Scheme |
| Session Store | Redis (existing) |

---

## Verification Plan

### Automated Tests
1. **Backend:** Unit test for handoff decision logic
2. **Backend:** Integration test: `/turn` returns `handoff_to_app=true` for visual intents
3. **iOS:** XCTest for deep link parsing

### Manual Verification
1. **Siri Trigger:**
   - Say "Hey Jiri, book an Uber"
   - Verify: Siri speaks initial response
   - Verify: App launches automatically
   - Verify: Session context preserved (conversation visible)

2. **Locked Phone:**
   - Repeat with phone locked
   - Verify: Biometric unlock prompt appears
   - Verify: App opens after auth

3. **Continuity:**
   - In app, send follow-up message
   - Verify: Backend recognizes session
   - Verify: Previous context used in LLM prompt
