🛠️ Technical Design Document: Mosaic Aegis MVPExecutive SummarySystem: Mosaic Aegis (Voice-First Agentic Bridge)Version: 1.0Architecture Pattern: Event-Driven Voice Bridge / Discovery-Enabled OrchestrationEstimated Effort: 4-6 Person-weeks (Optimized for Hackathon speed)Architecture OverviewHigh-Level ArchitectureThe system utilizes a modular design to separate voice ingress, tool orchestration, and long-term context.Code snippetgraph TB
    A[Siri / App Intents] --> B[FastAPI Backend]
    B <--> C[Azure Voice Live API]
    B --> D[Dedalus MCP Gateway]
    
    D --> E1[Core MCP Servers]
    D --> E2[Dynamic Awesome-MCP Discovery]
    
    B -.-> G1[TimescaleDB - Event Logs]
    B -.-> G2[ChromaDB - User RAG]
    B -.-> G3[Redis - Session State]

    subgraph "Voice Processing"
        C
    end
    
    subgraph "Orchestration Layer"
        D
        E1
        E2
    end
    
    subgraph "Context Layer"
        G1
        G2
        G3
    end
Tech Stack Decision🧠 Core EngineRuntime: Python 3.13 (Native support for modern async/await).Voice Orchestration: Azure AI Speech SDK (Voice Live API).Agentic Framework: Dedalus Labs SDK + MCP Python SDK.Real-time API: FastAPI + WebSockets (Uvicorn).🗄️ Persistence & ContextDatabase: TimescaleDB (For structured, time-stamped interaction history).Vector Store: ChromaDB (For preference-based RAG and semantic tool search).State/Cache: Redis (For locking session intent and Semantic VAD flags).Containerization: Docker (Essential for sandboxing dynamic MCP tool execution).📱 Frontend & MonitoringWorkbench: Agentuity (For real-time thought-trace visualization).Mobile Bridge: Apple Shortcuts / App Intents (Swift-based "Hidden" app).Component DesignVoice Bridge (Layer 1)File: src/bridge/voice_live.pyResponsibility: Maintain a full-duplex WebSocket with Azure and handle Semantic VAD.Logic: Stream G.711 audio from iOS; detect tool-call intents in the event stream.Dedalus Orchestrator (Layer 2)File: src/orchestrator/gateway.pyResponsibility: Execute tool calls via a Secure Vault proxy.Logic: Intercept tool calls, inject .env secrets, and return only data results to the LLM.Dynamic Discovery (Layer 3)File: src/discovery/registry.pyResponsibility: Query awesome-mcp registry and dynamically register new clients.Logic: Triggered by TOOL_NOT_FOUND errors; uses uvx for ephemeral tool spin-up.Personalization Engine (Layer 4)File: src/memory/rag_manager.pyResponsibility: Fetch top-K behavioral preferences from ChromaDB to augment the system prompt.Database SchemaSQL-- Interaction Event Log
CREATE TABLE interaction_logs (
    time TIMESTAMPTZ NOT NULL,
    user_id UUID NOT NULL,
    intent VARCHAR(50),
    tool_called VARCHAR(50),
    result_summary TEXT,
    success_score DOUBLE PRECISION
);
SELECT create_hypertable('interaction_logs', 'time');

-- Tool Discovery Registry (Cache)
CREATE TABLE tool_registry (
    tool_name VARCHAR(50) PRIMARY KEY,
    mcp_manifest_url TEXT,
    last_discovered TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
Feature Implementation: Secure Vault ProxyBusiness LogicThe Secure Vault ensures that the AI context never possesses raw API keys. The DedalusRunner handles the secret injection locally.Pythonfrom dedalus_labs import DedalusRunner

class SecureVaultProxy:
    def __init__(self, secrets_map: dict):
        self.secrets = secrets_map

    async def execute_tool(self, tool_name, params):
        # Injects local secrets into the tool call if needed
        if tool_name in ["book_uber", "send_gmail"]:
            params["api_key"] = self.secrets.get(f"{tool_name.upper()}_KEY")
            
        # Execute via standardized MCP call
        result = await mcp_gateway.call(tool_name, **params)
        
        # Scrub any accidentally returned secrets from the result
        return self.sanitize(result)
Performance OptimizationLatency Management:Region Pinning: Host the FastAPI backend in eastus2 to minimize latency with Azure Voice Live servers.Semantic VAD: Use Azure's native VAD to avoid round-trip audio processing for "silence" detection.Discovery Speed:Use Redis to cache the capability-to-MCP-manifest mappings from Awesome-MCP to avoid repetitive API lookups.Development WorkflowAI-Assisted Development StrategyPhasePrimary ToolPurposeVoice WebSocketClaude Sonnet 3.5Handling asynchronous bidirectional audio streamsMCP IntegrationCursor + DedalusMapping standard tool definitions into Azure JSONRAG ImplementationGitHub CopilotWriting vectorized search queries for ChromaDBSiri IntentsXcode + GPT-4oGenerating Swift App Intents boilerplateTesting StrategyFunctional Unit Tests:Verify the registry_search tool correctly identifies a new MCP for a "missing" capability.Validate that the Secure Vault successfully scrubs keys from log outputs.Experience Guardrails:Echo Testing: Measure latency from "Voice End" to "Agent Start" (Target: <300ms).Injection Testing: Attempt to "trick" the agent into revealing its hidden .env tokens via voice.Cost Analysis (Monthly)ServiceTierCostAzure AI SpeechVoice Live (Standard)$150 (Est. usage)Compute (AWS)t3.large (Backend + DB)$80LLM InferenceGPT-4o / Claude 3.5$100Total$330/moMigration & Scaling PathPhase 1 (MVP): Siri Shortcut bridge, local MCP servers, hardcoded RAG.Phase 2 (Growth): Full iOS App with App Intents, dynamic uvx tool loading, multi-user DB.Phase 3 (Scale): Distributed MCP workers, custom-trained voice model for lower TTS latency.