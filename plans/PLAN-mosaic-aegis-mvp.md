# PLAN: Mosaic Aegis MVP (Voice Pipe)

> **Goal:** Create a high-fidelity, low-latency "Voice-In → AI-Response → Voice-Out" loop using Azure Voice Live and Python FastAPI.
> **Philosophy:** "Speed is the Feature." Prove the <200ms latency hypothesis before adding complexity.

## 1. Project Overview

- **Type:** BACKEND (Python 3.13 Async) + Voice Integration
- **Core Loop:**
  1.  **User speaks** (Simulated or via WebSocket)
  2.  **Azure Voice Live** processes audio stream
  3.  **FastAPI Bridge** receives text/intent
  4.  **Mock Tool Executor** returns result (instant)
  5.  **Azure TTS** speaks response
- **Success Criteria:**
  - End-to-End Latency (Voice End to Audio Start) < 500ms (Target: 300ms)
  - Successful tool execution (Mock "GetWeather" or "BookRide") via voice command.

## 2. Tech Stack

| Component           | Technology              | Rationale                                                |
| :------------------ | :---------------------- | :------------------------------------------------------- |
| **Runtime**         | **Python 3.13**         | Latest async features, low overhead.                     |
| **API Framework**   | **FastAPI + Uvicorn**   | High-performance ASGI, native WebSocket support.         |
| **Voice Engine**    | **Azure AI Speech SDK** | Best-in-class generic VAD and natural voice.             |
| **Orchestration**   | **Dedalus (Lite/Mock)** | Lightweight shim for tool execution (no full vault yet). |
| **Dependency Mgmt** | **uv**                  | Fast package resolution and environment management.      |

## 3. File Structure

```
mosaic-aegis/
├── .env.example                # Azure keys, config
├── pyproject.toml              # Dependencies (managed by uv)
├── README.md                   # Setup instructions
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entrypoint
│   ├── config.py               # Settings management
│   ├── bridge/
│   │   ├── __init__.py
│   │   └── voice_client.py     # Azure Voice Live Wrapper
│   └── tools/
│       ├── __init__.py
│       └── mock_executor.py    # Hardcoded tools (Proof of Concept)
└── tests/
    ├── __init__.py
    └── latency_test.py         # Script to measure E2E speed
```

## 4. Task Breakdown

### Phase 1: Foundation Setup

- [ ] **Initialize Project**: Create `pyproject.toml` with `uv`, setup git, create scaffold. <!-- best_agent: backend-specialist -->
- [ ] **Config & Env**: Implement `src/config.py` using `pydantic-settings` to load Azure keys. <!-- best_agent: backend-specialist -->
- [ ] **FastAPI Skeleton**: Create `src/main.py` with health check and WebSocket endpoint. <!-- best_agent: backend-specialist -->
- [ ] **Dependency Install**: Install `fastapi`, `uvicorn`, `azure-cognitiveservices-speech`, `python-dotenv`. <!-- best_agent: backend-specialist -->

### Phase 2: The Voice Bridge (Critical Path)

- [ ] **Azure Client Wrapper**: Implement `VoiceLiveClient` in `src/bridge/voice_client.py`. Focus on `start_continuous_recognition`. <!-- best_agent: backend-specialist -->
- [ ] **WebSocket Handler**: Implement the async loop in FastAPI to stream audio chunks to/from Azure. <!-- best_agent: backend-specialist -->
- [ ] **VAD Integration**: Configure Azure Speech SDK to detect "Speech End" events using Semantic VAD. <!-- best_agent: backend-specialist -->
- [ ] **Echo Test**: Verify audio sent is recognized and text is returned (Latency checkpoint 1). <!-- best_agent: backend-specialist -->

### Phase 3: Tool Execution (Mock)

- [ ] **Mock Tools**: Create `src/tools/mock_executor.py` with `get_weather` and `book_ride` functions. <!-- best_agent: backend-specialist -->
- [ ] **Intent Routing**: Connect Azure "Intent Recognized" event to Mock Executor. <!-- best_agent: backend-specialist -->
- [ ] **Synthesize Response**: Take tool output and trigger Azure TTS (Text-to-Speech) generation. <!-- best_agent: backend-specialist -->

### Phase 4: Verification & Polish

- [ ] **Latency Script**: Create `tests/latency_test.py` to simulate a user request and measure time-to-first-audio-byte. <!-- best_agent: test-engineer -->
- [ ] **Error Handling**: Graceful failure if Azure disconnects or tool fails. <!-- best_agent: backend-specialist -->
- [ ] **Documentation**: Update `README.md` with instructions to run the local server. <!-- best_agent: documentation-specialist -->

## 5. Phase X: Verification Checklist

### Automated Checks

- [ ] **Linting**: `ruff check .` passes with no errors.
- [ ] **Type Checking**: `mypy src/` passes.
- [ ] **Latency**: `tests/latency_test.py` shows Avg Response < 500ms.

### Manual Verification

- [ ] **Voice Check**: Speak "What's the weather?" -> System replies.
- [ ] **Interrupt Check**: Speak while system is talking -> System stops (if VAD enabled).
- [ ] **Environment**: `.env` is not committed used `.env.example`.

---

## 6. Risks & Mitigations

- **Risk:** Azure VAD is too slow.
  - **Mitigation:** Fallback to local VAD (Silero) running in own process if needed (Phase 2 extension).
- **Risk:** Python Async Loop blocking.
  - **Mitigation:** Ensure all Azure SDK calls are run in `executor` or use async-native libraries where possible.
