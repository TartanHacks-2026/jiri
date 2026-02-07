# PLAN: Mosaic Aegis - Orchestration Pipeline

> **Goal:** The central nervous system. Connects the Voice Bridge (Azure) to the Model Brain (LLM) and Tool Hands (Dedalus).
> **Role:** "The Orchestrator" - Managing session flow, routing intents, and ensuring security.

## 1. Overview

- **Scope:** Intent Recognition, Dedalus Gateway integration, Semantic Routing, and Response Synthesis logic.
- **Project Type:** BACKEND / LOGIC
- **Output:** A robust `OrchestratorService` that handles the `Audio -> Text -> Action -> Audio` loop.

## 2. Tech Stack

| Component   | Tech                      | Rationale                                                                  |
| :---------- | :------------------------ | :------------------------------------------------------------------------- |
| **Logic**   | **Dedalus Gateway**       | Secure proxy for executing MCP tools.                                      |
| **Routing** | **Semantic Router**       | Determine if input needs a tool or just chat.                              |
| **State**   | **Redis FSM**             | Finite State Machine for conversation (Listening -> Thinking -> Speaking). |
| **LLM**     | **OpenAI / Azure OpenAI** | The decision-making reasoning engine.                                      |

## 3. File Structure

```
mosaic-aegis/
├── src/
│   ├── orchestrator/
│   │   ├── pipeline.py         # Main event loop
│   │   ├── router.py           # Intent classifier
│   │   ├── dedalus_client.py   # Secure Gateway integration
│   │   └── synthesis.py        # Text-to-Speech formatter
│   └── state/
│       └── session_fsm.py      # Redis-backed state machine
└── tests/
    └── test_pipeline.py        # Mocked end-to-end tests
```

## 4. Task Breakdown

### Phase 1: Core Routing Logic

- [ ] **Session FSM**: Implement Redis-backed state machine (`IDLE`, `LISTENING`, `PROCESSING`, `SPEAKING`). <!-- best_agent: backend-specialist -->
- [ ] **Intent Classifier**: Implement simple router: `Is this a command?` vs `Is this chitchat?`. <!-- best_agent: backend-specialist -->
- [ ] **Secure Proxy Client**: Implement `DedalusClient` to forward tool calls to the Secure Vault. <!-- best_agent: security-auditor -->

### Phase 2: Pipeline Integration

- [ ] **Voice-to-Action**: Connect `VoiceClient` text output -> `Router` -> `DedalusClient`. <!-- best_agent: backend-specialist -->
- [ ] **Action-to-Voice**: Connect `ToolResult` -> `LLM Summarizer` -> `VoiceClient.speak()`. <!-- best_agent: backend-specialist -->
- [ ] **Interruption Logic**: Handle `VoiceClient.stop_speaking()` when user barge-in is detected. <!-- best_agent: backend-specialist -->

### Phase 3: Advanced Flow

- [ ] **Multi-Turn**: Handle clarifying questions from tools (e.g., "Which Uber type?"). <!-- best_agent: backend-specialist -->
- [ ] **Context Awareness**: Inject `MemoryManager` context into the decision prompt. <!-- best_agent: backend-specialist -->

## 5. Phase X: Verification

- [ ] **Routing Accuracy**: "Book an Uber" -> triggers Tool. "Hello" -> triggers Chat.
- [ ] **Security**: API Keys are NOT present in the LLM context (verified via logs).
- [ ] **State Integrity**: System correctly resets to `IDLE` after speaking.
- [ ] **Latency**: Pipeline processing time (Text-in to Text-out) < 800ms.
