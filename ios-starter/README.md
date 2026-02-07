# iOS App Intent Setup Guide

> **Starter code for integrating Jiri backend with iOS App Intents**

## Files Provided

| File | Purpose |
|------|---------|
| `JiriConversationIntent.swift` | App Intent for Siri interaction |
| `JiriApp.swift` | Main app with deep link handler |

---

## Setup Instructions

### 1. Add Files to Xcode Project

1. Drag `JiriConversationIntent.swift` and `JiriApp.swift` into your Xcode project
2. Ensure "Copy items if needed" is checked
3. Add to your app target

### 2. Configure URL Scheme

In Xcode:
1. Select your project → Target → Info
2. Expand "URL Types"
3. Click "+" to add new URL type:
   - **Identifier**: `com.yourcompany.jiri`
   - **URL Schemes**: `jiri`
   - **Role**: Editor

### 3. Update Backend URL

In `JiriConversationIntent.swift`, line 33:
```swift
let backendURL = URL(string: "https://your-backend.com/turn")!
```
Replace with your actual backend URL (e.g., ngrok tunnel for dev).

### 4. Register Siri Phrases

The app automatically registers these phrases:
- "Hey Jiri, let's talk"
- "Talk to Jiri"
- "Ask Jiri"

To test:
1. Run app on physical device (Simulator doesn't support Siri)
2. Say one of the phrases
3. Siri will prompt for your input

---

## How It Works

```
┌─────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│  User   │────▶│  Siri        │────▶│ App Intent  │────▶│  Backend    │
│         │     │              │     │             │     │ POST /turn  │
└─────────┘     └──────────────┘     └──────────────┘     └─────────────┘
                                            │                     │
                                            │   Response          │
                                            │◀────────────────────┘
                                            │
                                    {handoff_to_app: true?}
                                            │
                                       Yes  │  No
                                            │
                    ┌───────────────────────┴────────────────┐
                    │                                        │
                    ▼                                        ▼
            Opens App via                            Siri speaks
            jiri://continue?                         reply and ends
            session_id=...
                    │
                    ▼
            App restores session
            Auto-starts voice mode
```

---

## Testing

### 1. Test Siri Phrase
```
Say: "Hey Jiri, let's talk"
Siri: "What do you want to say?"
Say: "What's the weather?"
Expected: Siri speaks backend response
```

### 2. Test Handoff
```
Say: "Hey Jiri, let's talk"
Say: "Book an Uber"
Expected: 
- Siri speaks "Opening the app for you..."
- App launches automatically
- Previous conversation visible
```

### 3. Test Session Continuity
```
1. Trigger handoff (see above)
2. In app, send follow-up: "Make it an UberXL"
3. Backend should recognize context from previous "book an Uber"
```

---

## Customization

### Add More Trigger Patterns

Edit `handoff_decision.py` (backend):
```python
VISUAL_TRIGGERS = [
    "show me",
    "open",
    "your custom trigger",  # Add here
]
```

### Change Siri Phrases

Edit `JiriAppShortcuts` in `JiriConversationIntent.swift`:
```swift
phrases: [
    "Hey Jiri, let's talk",
    "Your custom phrase",  // Add here
]
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Siri doesn't recognize phrase | Re-install app, wait 5 minutes for indexing |
| App doesn't open | Check URL scheme is `jiri` (lowercase) |
| Session not restored | Verify `GET /session/{id}/history` endpoint works |
| "Can't connect to server" | Check backend URL in JiriConversationIntent.swift |

---

## Next Steps

1. **Build UI**: Create `VoiceConversationView.swift` for active voice chat
2. **Add Audio**: Integrate Speech framework for voice input in-app
3. **Polish UX**: Add loading states, error handling, animations
