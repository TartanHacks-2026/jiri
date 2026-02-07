🎯 Project Overview
App: Mosaic Aegis Goal: A high-fidelity, voice-first agentic bridge connecting Apple's ecosystem (Siri) to the infinite tool capabilities of the Model Context Protocol (MCP), featuring dynamic tool discovery and self-improving capabilities. Stack: Python 3.13, FastAPI, Azure AI Voice Live API, Dedalus SDK, TimescaleDB, ChromaDB, Docker. Current Phase: Phase 1 - Foundation & The Voice Pipe

🧠 How I Should Think
Prioritize Latency: In a voice-first application, responsiveness is paramount. Optimize WebSocket handling and tool execution paths to maintain sub-200ms latency.

Zero-Trust by Default: Recognize the security sensitivity of API keys and personal data. Use the Dedalus Secure Vault pattern to ensure the agent never "sees" raw credentials.

Graceful Fallbacks: If a requested tool is missing, trigger the "Discovery" meta-tool to search the Awesome-MCP registry rather than failing the user request.

Context-Aware Reasoning: Leverage RAG (ChromaDB) to recall user history and preferences (e.g., "I prefer UberXL") before executing any tool to ensure personalized alignment.

Safety-First Autonomy: Always implement a manual override for high-stakes actions. When in doubt about a decision's impact, pause and ask the user for confirmation via voice.

📁 Context Files
Refer to these for details (load only when needed):

agent_docs/tech_design.md: Full architecture, Azure Voice Live integration, and secure proxy logic.

agent_docs/product_requirements.md: High-level vision, user stories, and "self-improving" rationale.

agent_docs/code_patterns.md: Standards for WebSocket loops, MCP tool definitions, and RAG implementation.

🔄 Current State (Update This!)
Last Updated: February 6, 2026 Working On: Initialization of the FastAPI backend and Azure Voice Live WebSocket integration. Recently Completed: System architecture design and tech stack finalization. Blocked By: None.

🚀 Roadmap
Phase 1: Foundation & The Voice Pipe
[ ] Initialize Python 3.13 project structure with uv.

[ ] Set up FastAPI backend with Azure Voice Live WebSocket bridge.

[ ] Implement Siri Shortcut for audio capture and metadata forwarding.

[ ] Connect Dedalus MCP Gateway with "Core" tools (Calendar, Uber).

Phase 2: Discovery & Intelligence
[ ] Implement registry_search meta-tool for Awesome-MCP lookup.

[ ] Connect TimescaleDB for event logging and ChromaDB for preference-based RAG.

[ ] Build "Self-Healing" logic for dynamic MCP tool loading and session updates.

Phase 3: Experience & Polish
[ ] Integrate Agentuity for real-time thought-trace visualization and debugging.

[ ] Implement "Semantic VAD" for natural conversation pacing.

[ ] Execute adversarial testing (e.g., prompt injection) to validate the Secure Vault.

⚠️ What NOT To Do
Do NOT pass raw API keys or secrets into the LLM's context window.

Do NOT allow the agent to install third-party MCP servers without a security check or user notification.

Do NOT hard-code tool schemas; use the Dedalus runner to dynamically aggregate MCP capabilities.

Do NOT ignore Semantic VAD; ensure the agent does not interrupt the user mid-sentence.