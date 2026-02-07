# Quick Start Guide: Testing Siri-to-App Handoff

> **Goal:** Test the handoff feature locally (backend) and understand iOS integration steps.

---

## 🚀 Backend Testing (Local)

### Step 1: Start Services (Simplified)

Since ChromaDB is optional for testing handoff, let's test the API directly:

```bash
# Option A: Run without Docker (fastest for testing)
cd /Users/nihal/Desktop/Repos/jiri
uv sync
uv run uvicorn jiri.main:app --reload --port 8000

# Option B: Fix docker-compose to skip ChromaDB
# (Edit docker-compose.yml to comment out chroma service dependency)
```

### Step 2: Test Handoff Detection

**Test 1: Voice-only interaction (no handoff)**
```bash
curl -X POST http://localhost:8000/turn \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "",
    "user_text": "what is the weather",
    "client": "shortcut",
    "meta": {"voice": true}
  }'
```

**Expected Response:**
```json
{
  "session_id": "uuid-here",
  "reply_text": "I don't have access to weather data yet...",
  "end_conversation": false,
  "handoff_to_app": false,
  "deep_link_url": null,
  "debug": {...}
}
```

---

**Test 2: Handoff trigger (visual action)**
```bash
curl -X POST http://localhost:8000/turn \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "",
    "user_text": "book an uber",
    "client": "shortcut",
    "meta": {"voice": true}
  }'
```

**Expected Response:**
```json
{
  "session_id": "uuid-here",
  "reply_text": "I can help with that. Opening the app for you...",
  "end_conversation": false,
  "handoff_to_app": true,
  "deep_link_url": "jiri://continue?session_id=uuid-here",
  "debug": {
    "tool_trace": ["Complex action requires UI: 'book'"],
    ...
  }
}
```

✅ **Success:** `handoff_to_app` is `true` and `deep_link_url` is populated!

---

### Step 3: Test Session History Endpoint

```bash
# Use the session_id from the previous response
curl -X GET http://localhost:8000/session/{session_id}/history
```

**Expected Response:**
```json
{
  "session_id": "uuid-here",
  "messages": [
    {"role": "user", "content": "book an uber"},
    {"role": "assistant", "content": "I can help with that. Opening the app for you..."}
  ],
  "created_at": "2026-02-06T22:30:00"
}
```

---

## 📱 iOS Integration (Next Steps)

### Prerequisites
- Xcode 15+
- Physical iOS device (Siri doesn't work in Simulator)
- Backend running and accessible (use ngrok for testing)

### Setup Steps

1. **Expose Backend via ngrok**
   ```bash
   ngrok http 8000
   # Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
   ```

2. **Add iOS Files to Xcode**
   - Open your iOS project in Xcode
   - Drag `ios-starter/JiriConversationIntent.swift` into project
   - Drag `ios-starter/JiriApp.swift` into project
   - Ensure "Copy items if needed" is checked

3. **Configure Backend URL**
   Edit `JiriConversationIntent.swift` line 33:
   ```swift
   let backendURL = URL(string: "https://YOUR-NGROK-URL.ngrok.io/turn")!
   ```

4. **Add URL Scheme**
   - Select project → Target → Info
   - Add URL Type:
     - **Identifier:** `com.yourcompany.jiri`
     - **URL Schemes:** `jiri`

5. **Build and Run**
   - Connect physical iPhone
   - Build and run app
   - Wait 5 minutes for Siri indexing

6. **Test with Siri**
   ```
   Say: "Hey Siri, talk to Jiri"
   Siri: "What do you want to say?"
   Say: "Book an Uber"
   Expected: App launches automatically!
   ```

---

## 🧪 Trigger Patterns

The backend will trigger handoff for these patterns:

### Visual Triggers
- "show me..."
- "open..."
- "display..."
- "let me see..."
- "I want to see..."

### Complex Actions
- "book..." (rides, appointments)
- "order..." (food, products)
- "buy..." / "purchase..."
- "customize..."
- "choose from..."

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend not starting | Run `uv run uvicorn jiri.main:app --reload` directly |
| ChromaDB error | Skip it - not needed for handoff testing |
| Siri doesn't recognize phrase | Re-install app, wait 5 min for indexing |
| App doesn't open | Check URL scheme is exactly `jiri` (lowercase) |
| Session not restored | Verify `/session/{id}/history` endpoint works |

---

## 📝 What's Working Now

✅ Backend detects handoff triggers  
✅ Deep link URL generated  
✅ Session history endpoint  
✅ iOS starter code provided  

## 🔜 What's Next

- [ ] Build full iOS app UI
- [ ] Add voice input in-app (Speech framework)
- [ ] Integrate Azure Voice Live for TTS
- [ ] Add visual feedback (waveform, transcript)
