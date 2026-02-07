code_patterns.md: Engineering Standards for Mosaic Aegis
1. Core Principles
Asynchronous Everywhere: Use async/await for all I/O-bound tasks (Voice WebSockets, MCP tool calls, DB queries) to prevent event loop blocking.

Zero-Trust Tooling: Secrets must be injected at the Proxy level. Agents should never handle raw API keys or tokens in their context.

Fail-Safe Defaults: Every tool execution must have a timeout and a structured error response that the agent can use to trigger the Discovery Meta-Tool.

Contextual Integrity: All RAG-retrieved context must be validated for timestamp relevance to prevent the agent from acting on stale user preferences.

2. Performance Patterns
2.1. Azure Voice Live WebSocket Bridge
Maintaining sub-200ms latency is critical. Use non-blocking queues for audio chunk buffering.

Python
import asyncio
from azure.ai.voicelive import VoiceLiveClient

async def audio_bridge(client_ws, azure_client: VoiceLiveClient):
    """
    Optimized bridge between iOS audio stream and Azure Voice Live.
    """
    async for chunk in client_ws:
        if chunk.is_audio:
            # Non-blocking forward to Azure
            await azure_client.send_audio(chunk.data)
        
        # Concurrent check for Azure responses/tool calls
        response = await azure_client.receive_event()
        if response.type == "tool_call":
            asyncio.create_task(handle_mcp_call(response))
2.2. uvx for Dynamic Discovery
When a tool is discovered via Awesome-MCP, use uvx for ephemeral, high-speed execution without bloating the main environment.

Python
import subprocess

def dynamic_mcp_run(server_name: str, args: list):
    """
    Executes a newly discovered MCP server in an isolated env.
    """
    command = ["uvx", server_name] + args
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
3. Agentic & RAG Patterns
3.1. The "Memory Augmentor" Wrapper
Always wrap agent intents with a RAG retrieval step to inject user-specific behavioral history.

Python
class ContextAugmentor:
    def __init__(self, vector_db):
        self.db = vector_db

    async def enrich_prompt(self, user_id: str, current_query: str) -> str:
        # Retrieve top-k behavioral preferences from ChromaDB
        past_preferences = await self.db.query(user_id, current_query, n=3)
        return f"User Preferences: {past_preferences}\nQuery: {current_query}"
3.2. Structured Tool Outputs
All MCP tools must return a standardized JSON schema so the Conway Decision Engine can parse confidence scores reliably.

4. Architecture Patterns
4.1. The Secure Gateway Proxy
The Dedalus SDK acts as the root. All tool calls from Azure are intercepted here for credential injection.

4.2. Strategy Factory for Fallbacks
Use a Factory pattern to decide between "Local Tool Execution" and "Registry Discovery" when an intent is received.

Python
class IntentResolver:
    @staticmethod
    def get_handler(intent: str, available_tools: list):
        if intent in available_tools:
            return LocalExecutionHandler()
        return AwesomeMCPDiscoveryHandler()
5. Error Handling & Safety
5.1. The "Human-in-the-Loop" Decorator
High-stakes tools (Payments, Deletion, Security) must be wrapped in an approval gate.

Python
def requires_approval(func):
    async def wrapper(*args, **kwargs):
        # Trigger Siri/Agentuity approval UI
        approved = await request_user_confirmation(func.__name__)
        if not approved:
            return "Action cancelled by user."
        return await func(*args, **kwargs)
    return wrapper
5.2. Semantic VAD Guard
Ensure the backend ignores audio input if the "Agent Speaking" state is active, unless an "Interrupt" threshold is met.

6. Documentation Standards
Docstrings: Use Google Style docstrings for all FastAPI endpoints.

Traceability: Every tool call must log its trace_id to TimescaleDB for post-mortem debugging in Agentuity.

Logging: Use loguru with JSON formatting for cloud-native observability.