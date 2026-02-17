"""SmartRouter — the main orchestrator.

Uses LangGraph with langchain-mcp-adapters for MCP tool execution.
Replaces the previous Dedalus Labs SDK-based architecture with a single
execution pass that uses an LRU tool cache. The agent discovers new tools
on-demand via ``discover_tools`` and only triggers a re-run when new servers
are found.

Flow per turn:
  1. Build messages from conversation history + new user input.
  2. Connect to cached MCP servers via MultiServerMCPClient.
  3. Create a ReAct agent with MCP tools + ``discover_tools``.
  4. If ``discover_tools`` was called → add new servers to LRU → re-run
     with expanded server set.
  5. Post-run: touch used servers in LRU, mark failures, record metrics,
     update conversation history.
"""

from __future__ import annotations

import sys
from typing import AsyncIterator, Dict, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool as langchain_tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from .config import RouterConfig
from .health import HealthTracker
from .history import ConversationHistory
from .metrics import UsageMetrics
from .registry import ToolRegistry
from .tool_cache import ToolCache


# ---------------------------------------------------------------------------
# Instructions template
# ---------------------------------------------------------------------------

_AGENT_INSTRUCTIONS = """\
You are Jiri, a smart AI assistant that can dynamically discover and use external
tool servers to answer questions.

{cache_status}

CRITICAL RULE — NEVER say "I can't" or "I don't have the capability" without
calling discover_tools() first. You can discover tools for ANY capability:
web scraping, fetching URLs, weather, stocks, news, social media, and more.

HOW YOU WORK:
1. Simple conversation ("hi", "explain X", general knowledge) → respond directly.
2. Anything involving real-time data, URLs, web pages, APIs, or external info:
   a. Check if your connected servers (above) can handle it.
   b. If YES → use those tools.
   c. If NO  → call discover_tools() with 2-3 search terms, then use the results.
3. If someone gives you a URL or asks to fetch/scrape/read a page
   → call discover_tools(queries=["web", "fetch", "scrape"]) to find a tool.

RULES:
- ALWAYS try discover_tools() before telling the user you cannot do something.
- NEVER fabricate real-time data. Use tools.
- After discover_tools() succeeds, STOP discovering and answer normally — the tools will load.
- Be concise, friendly, and helpful.\
"""


class SmartRouter:
    """Provider-agnostic agent router with LRU tool caching."""

    def __init__(
        self,
        chat_model,       # LangChain BaseChatModel (e.g. ChatOpenAI)
        embeddings,       # LangChain Embeddings (e.g. OpenAIEmbeddings)
        config: RouterConfig,
    ):
        self._model = chat_model
        self._config = config

        # Sub-systems
        self._registry = ToolRegistry(
            embeddings,
            config.registry,
            similarity_threshold=config.similarity_threshold,
            relative_score_cutoff=config.relative_score_cutoff,
            debug=config.debug,
        )
        self._cache = ToolCache(max_size=config.max_cache_size)
        self._health = HealthTracker(cooldown_seconds=config.health_cooldown_seconds)
        self._metrics = UsageMetrics(metrics_file=config.metrics_file)
        self._history = ConversationHistory(max_turns=config.max_history_turns)
        
        # Track tool discoveries (set per turn)
        self._newly_discovered: List[str] = []
    
    def _log(self, msg: str) -> None:
        """Print debug message to stderr if debug mode is enabled."""
        if self._config.debug:
            print(msg, file=sys.stderr, flush=True)
    
    # ------------------------------------------------------------------
    # Tool Discovery
    # ------------------------------------------------------------------
    
    def _discover_tools_impl(self, queries: List[str]) -> str:
        """Internal implementation of discover_tools."""
        self._discover_call_count += 1

        # Once tools are found, stop immediately — no more searching
        if self._newly_discovered:
            return "STOP. Tools already found and loading. Answer the user now."

        # Allow up to 5 attempts with different keywords, then give up
        if self._discover_call_count > 5:
            return "No tools found after multiple attempts. Answer with your general knowledge."

        self._log(f"  [🔍 discover_tools called with queries: {queries}]")
        results = self._registry.search(queries)
        self._log(f"  [🔍 Found {len(results)} matching tools]")
        for r in results:
            url = r["url"]
            if self._health.is_healthy(url) and url not in self._newly_discovered:
                self._newly_discovered.append(url)
                evicted = self._cache.add(url)
                if evicted:
                    self._log(f"  [Cache evicted: {evicted}]")
        if self._newly_discovered:
            descs = [f"- {r['description']}" for r in results]
            return (
                "SUCCESS: Found and activated these tool servers:\n"
                + "\n".join(descs)
                + "\n\nTools are loading. DO NOT call discover_tools again. Answer the user now."
            )
        return "No matching tools found for those queries. Try different search terms."
    
    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Startup: cache embeddings + preload popular tools."""
        print("Caching registry embeddings...")
        count = self._registry.cache_embeddings()
        print(f"Cached embeddings for {count} tool(s).")

        # Preload from historical usage
        top = self._metrics.get_top_tools(self._config.preload_count)
        if top:
            # Only preload tools still in the registry
            registry_urls = {t["url"] for t in self._config.registry}
            to_preload = [u for u in top if u in registry_urls]
            self._cache.preload(to_preload)
            if to_preload:
                print(f"Preloaded {len(to_preload)} tool(s) from usage history: {', '.join(to_preload)}")

    def shutdown(self) -> None:
        """Flush metrics on exit."""
        self._metrics.flush_session()

    # ------------------------------------------------------------------
    # MCP Client helpers
    # ------------------------------------------------------------------

    def _build_mcp_config(self, urls: List[str]) -> Dict:
        """Build MultiServerMCPClient config from registry URLs."""
        config = {}
        for url in urls:
            # Find server info in registry
            entry = None
            for e in self._config.registry:
                if e["url"] == url:
                    entry = e
                    break
            
            name = entry.get("name", url) if entry else url
            transport = entry.get("transport", "http") if entry else "http"
            
            # Use a sanitised key name
            key = name.replace(" ", "_").lower()

            if transport == "stdio":
                config[key] = {
                    "command": entry.get("command", "python"),
                    "args": entry.get("args", []),
                    "transport": "stdio",
                }
            else:
                config[key] = {
                    "url": url,
                    "transport": transport,
                }
        return config

    # ------------------------------------------------------------------
    # Turn handling
    # ------------------------------------------------------------------

    async def handle_turn(self, user_input: str) -> str:
        """Process a single user turn. Returns the assistant response."""

        # Track discoveries at instance level to avoid closure issues
        self._newly_discovered: List[str] = []
        self._discover_call_count = 0

        # --- discover_tools as a LangChain tool ---
        router_self = self  # capture for closure

        @langchain_tool
        def discover_tools(queries: list[str]) -> str:
            """Search for MCP tool servers that can handle specific capabilities.
            
            Call this when you need external data but don't have a matching server.
            Use 2-3 descriptive search terms per capability.
            
            Examples:
            - discover_tools(queries=["weather", "forecast", "conditions"])
            - discover_tools(queries=["github", "repository", "code search"])
            - discover_tools(queries=["stock market", "financial data"])"""
            return router_self._discover_tools_impl(queries)

        # Build messages
        messages = self._history.append_user(user_input)

        # Active servers (healthy subset of cache)
        cached_urls = self._cache.get_urls()
        active_urls = self._health.filter_healthy(cached_urls)
        
        if cached_urls and not active_urls:
            self._log(f"  [All {len(cached_urls)} cached servers are unhealthy - starting fresh]")
        

        # Build instructions
        instructions = self._build_instructions(active_urls)

        # --- Run agent ---
        response = await self._run_agent(
            messages=messages,
            active_urls=active_urls,
            discover_tools=discover_tools,
            instructions=instructions,
        )

        # --- Check if discovery happened → re-run with new servers ---
        if self._newly_discovered:
            self._log(f"  [Discovered {len(self._newly_discovered)} new tool(s): {', '.join(self._newly_discovered)}]")
            active_urls = self._health.filter_healthy(self._cache.get_urls())
            self._log(f"  [Re-running with {len(active_urls)} active servers: {active_urls}]")
            instructions = self._build_instructions(active_urls)
            
            response = await self._run_agent(
                messages=messages,
                active_urls=active_urls,
                discover_tools=discover_tools,
                instructions=instructions,
            )
            self._log(f"  [Re-run completed successfully]")

        # --- Post-run processing ---
        self._post_run(response, active_urls)

        # Extract final text from response
        return self._extract_response(response)

    async def _run_agent(
        self,
        messages: List[Dict],
        active_urls: List[str],
        discover_tools,
        instructions: str,
    ) -> dict:
        """Run the LangGraph ReAct agent with MCP tools.
        
        If a server fails to connect, removes it and retries with the rest.
        """
        remaining_urls = list(active_urls)

        while True:
            self._log(f"  [Running with {len(remaining_urls)} MCP servers, max_steps={self._config.max_steps}]")
            if remaining_urls:
                self._log(f"  [Active servers: {', '.join(remaining_urls)}]")

            lc_messages = self._to_langchain_messages(messages, instructions)

            try:
                if remaining_urls:
                    mcp_config = self._build_mcp_config(remaining_urls)
                    self._log(f"  [MCP config: {mcp_config}]")

                    mcp_client = MultiServerMCPClient(mcp_config)
                    mcp_tools = await mcp_client.get_tools()
                    self._log(f"  [Loaded {len(mcp_tools)} MCP tools]")

                    all_tools = list(mcp_tools) + [discover_tools]
                    agent = create_react_agent(self._model, all_tools)
                else:
                    agent = create_react_agent(self._model, [discover_tools])

                result = await agent.ainvoke(
                    {"messages": lc_messages},
                    config={"recursion_limit": self._config.max_steps * 2},
                )
                self._log(f"  [Execution completed]")
                return result

            except BaseException as e:
                # Try to identify which server failed
                error_str = str(e)
                failed_url = None

                if isinstance(e, BaseExceptionGroup):
                    for sub in e.exceptions:
                        self._log(f"  [❌ Sub-exception: {type(sub).__name__}: {sub}]")
                        sub_str = str(sub)
                        # Find which URL is in the error
                        for url in remaining_urls:
                            if url in sub_str:
                                failed_url = url
                                break

                if not failed_url:
                    for url in remaining_urls:
                        if url in error_str:
                            failed_url = url
                            break

                if failed_url and len(remaining_urls) > 1:
                    # Remove the failing server and retry with the rest
                    self._log(f"  [⚠️ Server {failed_url} failed — removing and retrying with remaining servers]")
                    self._health.mark_unhealthy(failed_url)
                    self._cache.evict(failed_url)
                    remaining_urls.remove(failed_url)
                    continue  # retry the while loop
                elif failed_url:
                    # Only server left failed — mark unhealthy, fall through to discover-only
                    self._log(f"  [⚠️ Server {failed_url} failed — falling back to discover-tools only]")
                    self._health.mark_unhealthy(failed_url)
                    self._cache.evict(failed_url)
                    remaining_urls.remove(failed_url)
                    continue  # will run with 0 servers (discover_tools only)
                else:
                    # Can't identify failing server — mark all newly discovered as unhealthy
                    self._log(f"  [❌ Execution error: {e}]")
                    if self._newly_discovered:
                        for url in self._newly_discovered:
                            self._health.mark_unhealthy(url)
                            self._cache.evict(url)
                    self._history.rollback_last_user()
                    raise

    async def handle_turn_stream(self, user_input: str) -> AsyncIterator[str]:
        """Process a turn with streaming output.

        If discovery is triggered, the discovery run is non-streaming.
        Only the final execution run is streamed.
        """
        # Reset discoveries for this turn
        self._newly_discovered: List[str] = []
        self._discover_call_count = 0

        router_self = self

        @langchain_tool
        def discover_tools(queries: list[str]) -> str:
            """Search for MCP tool servers that can handle specific capabilities.
            
            Call this when you need external data but don't have a matching server.
            Use 2-3 descriptive search terms per capability.
            
            Examples:
            - discover_tools(queries=["weather", "forecast", "conditions"])
            - discover_tools(queries=["github", "repository", "code search"])
            - discover_tools(queries=["stock market", "financial data"])"""
            return router_self._discover_tools_impl(queries)

        messages = self._history.append_user(user_input)
        active_urls = self._health.filter_healthy(self._cache.get_urls())
        instructions = self._build_instructions(active_urls)

        # Probe run (non-streaming) — may trigger discovery
        result = await self._run_agent(
            messages=messages,
            active_urls=active_urls,
            discover_tools=discover_tools,
            instructions=instructions,
        )

        if self._newly_discovered:
            self._log(f"  [Discovered {len(self._newly_discovered)} new tool(s): {', '.join(self._newly_discovered)}]")
            active_urls = self._health.filter_healthy(self._cache.get_urls())
            instructions = self._build_instructions(active_urls)
            
            # Build streaming config
            lc_messages = self._to_langchain_messages(messages, instructions)
            
            if active_urls:
                mcp_config = self._build_mcp_config(active_urls)
                mcp_client = MultiServerMCPClient(mcp_config)
                mcp_tools = await mcp_client.get_tools()
                all_tools = list(mcp_tools) + [discover_tools]
                agent = create_react_agent(self._model, all_tools)
                
                collected: List[str] = []
                async for event in agent.astream_events(
                    {"messages": lc_messages},
                    config={"recursion_limit": self._config.max_steps * 2},
                    version="v2",
                ):
                    if event["event"] == "on_chat_model_stream":
                        chunk = event["data"]["chunk"]
                        if hasattr(chunk, "content") and isinstance(chunk.content, str) and chunk.content:
                            collected.append(chunk.content)
                            yield chunk.content
            else:
                agent = create_react_agent(self._model, [discover_tools])
                collected: List[str] = []
                async for event in agent.astream_events(
                    {"messages": lc_messages},
                    config={"recursion_limit": self._config.max_steps * 2},
                    version="v2",
                ):
                    if event["event"] == "on_chat_model_stream":
                        chunk = event["data"]["chunk"]
                        if hasattr(chunk, "content") and isinstance(chunk.content, str) and chunk.content:
                            collected.append(chunk.content)
                            yield chunk.content

            # Update history from collected output
            full_output = "".join(collected)
            updated_msgs = messages + [{"role": "assistant", "content": full_output}]
            self._history.update(updated_msgs)
        else:
            # No discovery — yield the full result
            output = self._extract_response(result)
            yield output
            self._post_run(result, active_urls)

    # ------------------------------------------------------------------
    # Message conversion
    # ------------------------------------------------------------------

    def _to_langchain_messages(self, messages: List[Dict], instructions: str) -> list:
        """Convert OpenAI-format dicts to LangChain message objects."""
        lc_messages = [SystemMessage(content=instructions)]
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        return lc_messages

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _post_run(self, result: dict, active_urls: List[str]) -> None:
        """LRU touch, health tracking, metrics, history update."""
        response_messages = result.get("messages", [])
        
        # Check if any tool calls happened (indicates MCP tools were used)
        tool_was_used = False
        has_error = False
        for msg in response_messages:
            if isinstance(msg, ToolMessage):
                tool_was_used = True
                if hasattr(msg, "status") and msg.status == "error":
                    has_error = True
                    self._log(f"  [Tool error: {msg.content[:100]}]")

        # If tools were executed successfully, touch all active servers
        if tool_was_used and not has_error:
            for url in active_urls:
                self._cache.touch(url)
                self._metrics.record_tool_use(url)
                self._log(f"  [✓ Server {url} used successfully]")

        # Update conversation history
        if has_error:
            self._log(f"  [Skipping history update due to tool error]")
            for url in active_urls:
                self._log(f"  [Marking {url} as unhealthy due to tool error]")
                self._health.mark_unhealthy(url)
                self._cache.evict(url)
            self._log(f"  [Rolling back failed user query from history to prevent contamination]")
            self._history.rollback_last_user()
        else:
            # Convert LangChain messages back to dict format for history
            history_msgs = []
            for msg in response_messages:
                if isinstance(msg, HumanMessage):
                    history_msgs.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage) and isinstance(msg.content, str) and msg.content:
                    history_msgs.append({"role": "assistant", "content": msg.content})
                elif isinstance(msg, SystemMessage):
                    history_msgs.append({"role": "system", "content": msg.content})
            self._history.update(history_msgs)

    def _extract_response(self, result: dict) -> str:
        """Extract the final text response from a LangGraph result."""
        response_messages = result.get("messages", [])
        
        # Find the last AI message with text content
        for msg in reversed(response_messages):
            if isinstance(msg, AIMessage) and isinstance(msg.content, str) and msg.content:
                return msg.content
        
        return "No response generated"

    def _build_instructions(self, active_urls: List[str]) -> str:
        """Generate agent instructions reflecting current cache state."""
        if active_urls:
            server_info = []
            for url in active_urls:
                for entry in self._config.registry:
                    if entry["url"] == url:
                        name = entry.get('name', url)
                        desc = entry.get('description', '')
                        keywords = entry.get('keywords', [])
                        kw_str = f" [{', '.join(keywords[:5])}]" if keywords else ""
                        server_info.append(f"  - {name}: {desc}{kw_str}")
                        break
            
            if server_info:
                status = (
                    "YOUR TOOLS ARE ALREADY LOADED for these capabilities:\n"
                    + "\n".join(server_info)
                    + "\n\nYou already have tools for the above — just USE them directly, "
                    "do NOT call discover_tools for these. "
                    "Only call discover_tools if you need a capability NOT listed above."
                )
            else:
                status = f"You have {len(active_urls)} tool server(s) connected."
        else:
            status = "You have NO tool servers connected yet. Call discover_tools() to find tools."
        return _AGENT_INSTRUCTIONS.format(cache_status=status)

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    @property
    def cache_contents(self) -> List[Dict]:
        """Return cached servers with friendly names for the UI."""
        urls = self._cache.get_urls()
        result = []
        for url in urls:
            name = url
            for entry in self._config.registry:
                if entry["url"] == url:
                    name = entry.get("name", url)
                    break
            result.append({"url": url, "name": name})
        return result

    @property
    def history_turns(self) -> int:
        return self._history.turn_count