PRD: Project "Mosaic Aegis"Version: 1.0Objective: To build a proactive, voice-native personal assistant that utilizes Azure Voice Live for real-time interaction, Dedalus for secure tool orchestration, and a self-improving Dynamic Discovery layer to autonomously expand its own capabilities.1. System ArchitectureThe system follows a High-Fidelity Bridge design, linking on-device triggers to cloud-based reasoning and local/hosted tool execution.LayerComponentFunctionLayer 1: EntryApple App Intents / ShortcutsCaptures "Hey Siri" voice input and forwards device context (GPS, Time).Layer 2: ProcessorAzure Voice Live APIHandles real-time, bidirectional voice-to-voice orchestration and VAD.Layer 3: HandsDedalus MCP GatewayExecutes standardized tools (Uber, Calendar) via a Zero-Trust secure proxy.Layer 4: MemoryTimescaleDB & ChromaDBStores long-term event history and vectorized user preferences for RAG.Layer 5: EvolutionAwesome-MCP DiscoveryMeta-tool that searches and installs new MCP servers when a capability is missing.2. Technical Specifications2.1. The Voice-Live BridgeGoal: Provide a natural, low-latency conversation experience.Input: G.711 or PCM audio stream from iOS client.Orchestration: Maintain a persistent WebSocket connection with Azure AI Foundry.VAD Logic: Utilize Semantic Voice Activity Detection to allow for user interruptions while maintaining an instant agent response time ($<200ms$).2.2. The Secure Vault (Zero-Trust Proxy)Goal: Prevent Credential Leakage during tool execution.Logic: The agent generates an intent (e.g., book_ride).Verification: The Dedalus Gateway intercepts the call and injects the locally stored API key (e.g., Uber Token) into the request.Isolation: The model context never sees the raw key, only the "Success/Fail" result.2.3. Dynamic Discovery EngineGoal: Enable "Self-Improving" capabilities.Process: If a user request cannot be fulfilled by current tools, trigger a registry_search tool.Discovery: Query the Awesome-MCP API for a server manifest matching the required functionality.Integration: Dynamically register the new MCP client in the Dedalus Runner and update the Azure session config on-the-fly.3. The RAG & Personalization EngineThe agent uses a Hybrid Memory System to ensure context-aware responses and personalized defaults.3.1. Vectorized Memory (ChromaDB)Content: Past user preferences (e.g., "I prefer aisle seats," "No cilantro in my orders").Retrieval: Every prompt is augmented with the top-3 most relevant behavioral snippets from past interactions.3.2. Event Logging (TimescaleDB)Content: Structured logs of every tool call, result, and user feedback.Improvement: Used to calculate the Inference-to-Action Success Ratio to refine agent behavior over time.4. Implementation StackLanguage: Python 3.13 (Async-first).Frameworks:FastAPI (Backend API & WebSocket server).Azure AI Speech SDK (Voice Live orchestration).Dedalus SDK (MCP Gateway & Secure Vault).Data:TimescaleDB (PostgreSQL extension for event history).ChromaDB (Vector storage for RAG).Infrastructure: Docker (for sandboxing MCP servers).5. Risk & GuardrailsLatency Monitoring: The backend must trigger a "Thinking" audio signal if the Conway Logic (reasoning) takes longer than 500ms.Safety Gate (Manual Override): Any action involving financial transactions or data deletion must present a "Voice Approval" prompt.Discovery Sandbox: All dynamically discovered MCP servers must run in a restricted Docker container to prevent malicious tool behavior.6. Execution Roadmap for the AI AgentModule A: Implement the FastAPI-to-Azure WebSocket bridge and verify low-latency audio echo.Module B: Build the Dedalus Secure Proxy and connect "Core" MCP tools (Calendar, Contacts).Module C: Develop the Discovery Meta-Tool to query and load servers from the Awesome-MCP registry.Module D: Integrate ChromaDB for preference-aware RAG and finalize the Agentuity monitoring dashboard.

### 3. PRD - Product Requirements Document
The high-level vision for judges and sponsors.

```markdown
# PRD: Project "Mosaic Aegis"
**Version:** 1.0 | **Track:** Conway, Dedalus Labs, Polychrome Mosaic

## 1. Problem Statement
Personal assistants are currently reactive, siloed, and high-latency. Users cannot easily add new capabilities, and existing assistants lack a memory of user preferences that actually influences their decisions.

## 2. The Vision
A voice-first "Personal AI Brain" that:
1. **Communicates** via low-latency, natural Azure Voice Live.
2. **Executes** via the universal Model Context Protocol.
3. **Discovers** its own missing features via Awesome-MCP.
4. **Remembers** through a high-velocity RAG memory layer.

## 3. Core Functional Requirements
| Feature | Requirement | Priority |
| :--- | :--- | :--- |
| **Voice Interface** | Bidirectional WebSocket audio with interrupt handling. | P0 |
| **Secure MCP** | Zero-trust credential injection via Dedalus Gateway. | P0 |
| **Discovery** | Auto-lookup of Awesome-MCP servers for failed intents. | P1 |
| **Memory** | User preference RAG using ChromaDB. | P1 |

## 4. User Stories
* "As a user, I want to say 'Hey Siri, book an Uber' and have the agent know my home address and preferred car type without me saying it."
* "As a user, I want the agent to find a new tool if I ask for something it can't currently do (e.g., 'Order me a pizza')."

## 5. Success Metrics (KPIs)
* **Latency:** <250ms Voice-to-Thought response.
* **Success Rate:** % of tools successfully discovered and installed via Awesome-MCP.