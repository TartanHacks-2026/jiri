"""SmartRouter — the main orchestrator.

Replaces the two-phase (Discovery → Execution) architecture with a single
execution pass that uses an LRU tool cache. The agent discovers new tools
on-demand via ``discover_tools`` and only triggers a re-run when new servers
are found.

Flow per turn:
  1. Build messages from conversation history + new user input.
  2. Execute with cached MCP servers + ``discover_tools`` always available.
  3. If ``discover_tools`` was called → add new servers to LRU → re-run
     with expanded server set.
  4. Post-run: touch used servers in LRU, mark failures, record metrics,
     update conversation history.
"""

from __future__ import annotations

import sys
from typing import AsyncIterator, Dict, List

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
You are a helpful assistant with access to external tool servers.

{cache_status}

🚨 MANDATORY DISCOVERY PROTOCOL 🚨

CRITICAL RULE: If you don't currently have a tool for a request, you MUST call discover_tools FIRST.
NEVER say "I don't have access" or "I can't help" without trying discover_tools first!

STEP 1: Check if your CURRENT servers (listed above) can handle this EXACT request.
   - Stock server can ONLY get stock data
   - Weather server can ONLY get weather data  
   - Each server has ONE specific capability
   - If unsure or capability missing → GO TO STEP 2

STEP 2: ALWAYS call discover_tools with 2-3 specific queries for the capability needed:
   
   REQUEST EXAMPLES → discover_tools QUERIES:
   - "MSFT stock price" → discover_tools(["stock market data", "financial quotes", "equity prices"])
   - "Weather in NYC" → discover_tools(["weather data", "forecasts", "current conditions"])
   - "Elon Musk tweets" → discover_tools(["twitter", "X API", "social media", "tweets"])
   - "Latest tech news" → discover_tools(["news", "current events", "headlines"])
   - "My calendar events" → discover_tools(["calendar", "scheduling", "events"])
   - "Find restaurants" → discover_tools(["places", "locations", "restaurant search"])
   - "Fetch website data" → discover_tools(["web scraping", "HTTP fetch", "webpage content"])

STEP 3: After discovering, use the newly found tool to answer the question.

🚫 NEVER:
- Use a tool for something it can't do (stocks ≠ weather ≠ tweets)
- Say "I don't have access" without calling discover_tools first
- Answer with suggestions like "try visiting X.com" - discover a tool instead!

✅ ONLY answer from your knowledge for: basic math, general facts, reasoning (no real-time data).\
"""


class SmartRouter:
    """Provider-agnostic agent router with LRU tool caching."""

    def __init__(
        self,
        dedalus_client,      # Dedalus (sync) for embeddings
        runner,              # DedalusRunner (async) for agent
        config: RouterConfig,
    ):
        self._dedalus = dedalus_client
        self._runner = runner
        self._agent = runner  # Alias for code that uses _agent
        self._config = config

        # Sub-systems
        self._registry = ToolRegistry(
            self._dedalus,  # Pass sync client directly
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
        if results:
            descs = [f"- {r['description']} (score: {r['score']})" for r in results]
            return "Found these capabilities:\n" + "\n".join(descs)
        return "No matching tools found for those queries."
    
    def _select_best_server(self, user_query: str, cached_urls: List[str]) -> List[str]:
        """Select the most relevant server from cache for this query.
        
        Returns a list with 0-1 URLs (single server or empty).
        """
        if not cached_urls:
            return []
        
        if len(cached_urls) == 1:
            return cached_urls
        
        # Search registry to find which cached server best matches the query
        self._log(f"  [Selecting best server from cache for query: '{user_query[:50]}...']")
        results = self._registry.search([user_query])
        
        # Find first result that's in our cache
        for r in results:
            if r["url"] in cached_urls:
                self._log(f"  [Best match from cache: {r['url']} (score: {r['score']})]")
                return [r["url"]]
        
        # No semantic match, use most recent
        self._log(f"  [No semantic match, using most recent: {cached_urls[-1]}]")
        return [cached_urls[-1]]
    
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
    # Turn handling
    # ------------------------------------------------------------------

    async def handle_turn(self, user_input: str) -> str:
        """Process a single user turn. Returns the assistant response."""

        # Track discoveries at instance level to avoid closure issues
        self._newly_discovered: List[str] = []

        # --- discover_tools as instance method reference ---
        def discover_tools(queries: list[str]) -> str:
            """Search for tool servers that provide the capabilities described in the queries.
            Each query should be a short natural-language description of a capability you need.
            Call this with multiple queries if the task requires different capabilities.
            Example: discover_tools(["stock market data", "text translation"])"""
            return self._discover_tools_impl(queries)
        
        # Set the function name for Dedalus serialization
        discover_tools.__name__ = "discover_tools"

        # Build messages
        messages = self._history.append_user(user_input)

        # Active servers (healthy subset of cache)
        cached_urls = self._cache.get_urls()
        active_urls = self._health.filter_healthy(cached_urls)
        
        if cached_urls and not active_urls:
            self._log(f"  [All {len(cached_urls)} cached servers are unhealthy - starting fresh]")
        
        # The agent can see all servers in instructions and will intelligently choose the right one
        instructions = self._build_instructions(active_urls)

        # --- Execution run ---
        self._log(f"  [Running with {len(active_urls) if active_urls else 0} MCP servers, max_steps={self._config.max_steps}]")
        if active_urls:
            self._log(f"  [Active servers: {', '.join(active_urls)}]")
        self._log(f"  [Tools available to agent: discover_tools]")
        self._log(f"  [DEBUG: model={self._config.execution_model}, tools={[t.__name__ for t in [discover_tools]]}, mcp_servers={active_urls if active_urls else None}]")
        self._log(f"  [DEBUG: messages count={len(messages)}, instructions length={len(instructions)} chars]")
        
        try:
            result = await self._agent.run(
                messages=messages,
                model=self._config.execution_model,
                tools=[discover_tools],
                mcp_servers=active_urls if active_urls else None,
                instructions=instructions,
                max_steps=self._config.max_steps,
            )
            self._log(f"  [Execution completed: steps_used={result.steps_used if hasattr(result, 'steps_used') else 'unknown'}]")
            
            # Log if discover_tools was called this run
            if not self._newly_discovered and active_urls:
                self._log(f"  [⚠️  discover_tools was NOT called - agent used existing servers]")
                
        except Exception as e:
            # Even on error, try to evict problematic servers
            self._log(f"  [❌ Execution error: {e}]")
            if active_urls:
                self._log(f"  [Marking all active servers as unhealthy due to error]")
                for url in active_urls:
                    self._health.mark_unhealthy(url)
                    self._cache.evict(url)
            # Rollback the failed user query to prevent contamination
            self._log(f"  [Rolling back failed user query from history]")
            self._history.rollback_last_user()
            raise

        # --- Check if discovery happened → re-run with new servers ---
        if self._newly_discovered:
            self._log(f"  [Discovered {len(self._newly_discovered)} new tool(s): {', '.join(self._newly_discovered)}]")
            # Rebuild with ALL healthy cached servers - agent will choose the right one
            active_urls = self._health.filter_healthy(self._cache.get_urls())
            self._log(f"  [Re-running with {len(active_urls)} active servers: {active_urls}]")
            instructions = self._build_instructions(active_urls)
            
            try:
                self._log(f"  [Calling runner.run with mcp_servers={active_urls}]")
                result = await self._agent.run(
                    messages=messages,  # original messages, not first run's output
                    model=self._config.execution_model,
                    tools=[discover_tools],
                    mcp_servers=active_urls if active_urls else None,
                    instructions=instructions,
                    max_steps=self._config.max_steps,
                )
                self._log(f"  [Re-run completed successfully]")
            except Exception as e:
                self._log(f"  [❌ Re-run error during execution: {type(e).__name__}: {e}]")
                # The error might be from a specific server - mark all as unhealthy for now
                for url in self._newly_discovered:
                    self._log(f"  [Marking {url} as unhealthy due to re-run failure]")
                    self._health.mark_unhealthy(url)
                    self._cache.evict(url)
                # Rollback the failed user query to prevent contamination
                self._log(f"  [Rolling back failed user query from history]")
                self._history.rollback_last_user()
                raise

        # Check for handoff messages BEFORE post-run processing
        # This indicates the MCP server didn't respond properly
        if hasattr(result, 'final_output'):
            output = result.final_output
            self._log(f"  [final_output type: {type(output)}]")
            
            if isinstance(output, str) and '__DEDALUS_HANDOFF__' in output:
                self._log(f"  [⚠️  WARNING: Got raw handoff message - MCP tool execution failed]")
                self._log(f"  [Marking newly discovered servers as unhealthy and rolling back]")
                # Mark newly discovered servers as unhealthy (they're the ones that failed)
                for url in self._newly_discovered:
                    self._health.mark_unhealthy(url)
                    self._cache.evict(url)
                # Rollback the failed query
                self._history.rollback_last_user()
                return "The tool server didn't respond properly. The server may be experiencing issues or requires authentication."

        # --- Post-run processing ---
        self._post_run(result, active_urls)

        # Debug: log result attributes
        self._log(f"  [Result attributes: {dir(result)}]")
        
        # Extract final output
        if hasattr(result, 'final_output'):
            output = result.final_output
            
            # Check if output is a dict (assistant message)
            if isinstance(output, dict):
                if 'content' in output:
                    content = output['content']
                    if isinstance(content, str) and '__DEDALUS_HANDOFF__' not in content:
                        return content
                return str(output)
            
            return output
        
        # Fallback: try to get from messages
        if hasattr(result, 'messages') and result.messages:
            self._log(f"  [Trying to extract from messages]")
            last_msg = result.messages[-1]
            if isinstance(last_msg, dict) and last_msg.get('role') == 'assistant':
                return last_msg.get('content', str(last_msg))
        
        return "No response generated"

    async def handle_turn_stream(self, user_input: str) -> AsyncIterator[str]:
        """Process a turn with streaming output.

        If discovery is triggered, the discovery run is non-streaming.
        Only the final execution run is streamed.
        """
        # Reset discoveries for this turn
        self._newly_discovered: List[str] = []

        def discover_tools(queries: list[str]) -> str:
            """Search for tool servers that provide the capabilities described in the queries.
            Each query should be a short natural-language description of a capability you need.
            Call this with multiple queries if the task requires different capabilities.
            Example: discover_tools(["stock market data", "text translation"])"""
            return self._discover_tools_impl(queries)
        
        discover_tools.__name__ = "discover_tools"

        messages = self._history.append_user(user_input)
        active_urls = self._health.filter_healthy(self._cache.get_urls())
        instructions = self._build_instructions(active_urls)

        # Probe run (non-streaming) — may trigger discovery
        result = await self._agent.run(
            messages=messages,
            model=self._config.execution_model,
            tools=[discover_tools],
            mcp_servers=active_urls if active_urls else None,
            instructions=instructions,
            max_steps=self._config.max_steps,
        )

        if self._newly_discovered:
            self._log(f"  [Discovered {len(self._newly_discovered)} new tool(s): {', '.join(self._newly_discovered)}]")
            active_urls = self._health.filter_healthy(self._cache.get_urls())
            instructions = self._build_instructions(active_urls)
            # Stream the re-run with original messages
            collected: List[str] = []
            async for chunk in self._agent.run_stream(
                messages=messages,  # original messages, not first run's output
                model=self._config.execution_model,
                tools=[discover_tools],
                mcp_servers=active_urls if active_urls else None,
                instructions=instructions,
                max_steps=self._config.max_steps,
            ):
                collected.append(chunk)
                yield chunk

            # Update history from collected output
            # (streaming doesn't return a RunResult, so we reconstruct minimally)
            full_output = "".join(collected)
            self._history.update(
                result.messages + [{"role": "assistant", "content": full_output}]
            )
        else:
            # No discovery — just yield the full result
            yield result.final_output
            self._post_run(result, active_urls)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _post_run(self, result, active_urls: List[str]) -> None:
        """LRU touch, health tracking, metrics, history update."""
        # Check if any MCP tools returned errors
        has_server_error = False
        if result.mcp_results:
            for mr in result.mcp_results:
                if mr.is_error:
                    self._log(f"  [MCP tool error: {mr.tool_name} - {mr.error if hasattr(mr, 'error') else 'unknown error'}]")
                    has_server_error = True

        # If tools were executed successfully, touch all active servers
        # (we don't know which specific server each tool came from)
        if not has_server_error and result.mcp_results:
            for url in active_urls:
                self._cache.touch(url)
                self._metrics.record_tool_use(url)
                self._log(f"  [✓ Server {url} used successfully]")

        # Update conversation history - but filter out server errors
        # to prevent poisoning future discovery attempts
        if has_server_error:
            # Don't add the failed attempt to history, mark all active servers as unhealthy
            self._log(f"  [Skipping history update due to MCP tool error]")
            for url in active_urls:
                self._log(f"  [Marking {url} as unhealthy due to tool error]")
                self._health.mark_unhealthy(url)
                self._cache.evict(url)
            # CRITICAL: Rollback the user's question from history since we can't answer it
            self._log(f"  [Rolling back failed user query from history to prevent contamination]")
            self._history.rollback_last_user()
        else:
            self._history.update(result.messages)

    def _build_instructions(self, active_urls: List[str]) -> str:
        """Generate agent instructions reflecting current cache state."""
        if active_urls:
            # Show servers with their capabilities AND keywords
            server_info = []
            for url in active_urls:
                # Find server info in registry
                for entry in self._config.registry:
                    if entry["url"] == url:
                        desc = entry.get('description', 'Unknown')
                        keywords = entry.get('keywords', [])
                        kw_str = f" (covers: {', '.join(keywords[:5])})" if keywords else ""
                        server_info.append(f"  - {url}: {desc}{kw_str}")
                        break
            
            if server_info:
                status = f"CONNECTED SERVERS:\n" + "\n".join(server_info) + "\n\nIMPORTANT: These servers ONLY handle their specific capabilities. For ANY other capability, you MUST call discover_tools."
            else:
                status = f"You have {len(active_urls)} tool server(s) connected."
        else:
            status = "You have NO tool servers connected yet."
        return _AGENT_INSTRUCTIONS.format(cache_status=status)

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    @property
    def cache_contents(self) -> List[str]:
        return self._cache.get_urls()

    @property
    def history_turns(self) -> int:
        return self._history.turn_count