# Dedalus SDK & MCP Server

Integration using the official [Dedalus Labs](https://dedaluslabs.ai) SDK and MCP framework for AI-powered tool execution.

## Overview

**Dedalus** consists of two main components:

1. **Dedalus Client** (`dedalus.py`) - A wrapper around the official Dedalus Labs SDK for interacting with LLMs (Claude, GPT, etc.)
2. **Dedalus MCP Server** (`mcp_server.py`) - A Model Context Protocol server built with `dedalus_mcp` for registering and executing tools

This implementation follows the official Dedalus Labs patterns documented at [docs.dedaluslabs.ai](https://docs.dedaluslabs.ai/dmcp/server/overview)

## Quick Start

### 1. Get your Dedalus Labs API key

Sign up at [dedaluslabs.ai](https://dedaluslabs.ai) and get your API key.

### 2. Set up your environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Dedalus API key
# DEDALUS_API_KEY=your-actual-api-key
```

### 3. Install dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 4. Run the demo

```bash
# Full demo
python dedalus_demo.py

# Run MCP server standalone
python mcp_server.py

# Run SDK client standalone
python dedalus.py
```

## Usage Examples

### Using the Dedalus Client

```python
from dedalus import DedalusClient

# Initialize client
client = DedalusClient(api_key="your-api-key")

# Simple chat
response = await client.chat(
    "Hello! How can you help me?",
    system_prompt="You are a helpful assistant."
)
print(response)

# Chat with local MCP server
response = await client.run_with_local_mcp(
    "Use the log_hello tool to greet me",
    mcp_url="http://localhost:8000/mcp"
)
print(response)

# Chat with hosted MCP server (marketplace)
response = await client.run(
    "Search for authentication docs",
    mcp_servers=["your-org/your-server"]
)
```

### Creating an MCP Server

```python
from dedalus_mcp import MCPServer, tool

# Define tools with @tool decorator
@tool(description="Add two numbers")
def add(a: int, b: int) -> int:
    return a + b

@tool(description="Log a custom message")
def log_message(message: str) -> str:
    print(f"📝 {message}")
    return message

# Create server
server = MCPServer("my-calculator")
server.collect(add)
server.collect(log_message)

# Serve
if __name__ == "__main__":
    import asyncio
    asyncio.run(server.serve())
```

### Integrated Usage (SDK + Local MCP Server)

```python
from dedalus import DedalusClient
from mcp_server import create_dedalus_mcp_server

# Start MCP server (in production, run as separate process)
# Terminal 1: python mcp_server.py

# Use SDK with local MCP server
client = DedalusClient()

# The SDK automatically discovers and uses tools from the MCP server
response = await client.run_with_local_mcp(
    "Please add 5 and 3 using the add_numbers tool, then log the result",
    mcp_url="http://localhost:8000/mcp"
)
print(response)
```

## Available MCP Tools

The demo MCP server includes these tools:

### 1. `log_hello`
- **Description**: Logs 'hello' to the console
- **Parameters**: None
- **Returns**: Hello message

### 2. `log_message`
- **Description**: Logs a custom message to the console
- **Parameters**: 
  - `message` (string): The message to log
- **Returns**: The logged message with timestamp

### 3. `get_server_info`
- **Description**: Get information about the MCP server
- **Parameters**: None
- **Returns**: Server info (name, version, status, timestamp)

### 4. `add_numbers`
- **Description**: Add two numbers together
- **Parameters**:
  - `a` (integer): First number
  - `b` (integer): Second number
- **Returns**: Sum of the two numbers

## Architecture

```
┌──────────────────────────────────────────┐
│          Dedalus Labs SDK                │
│  (AsyncDedalus + DedalusRunner)          │
│                                          │
│  - Model routing (Claude, GPT, etc.)     │
│  - MCP discovery & connection            │
│  - Tool execution orchestration          │
└────────────────┬─────────────────────────┘
                 │
                 │ HTTP/MCP Protocol
                 ▼
┌──────────────────────────────────────────┐
│      MCP Server (dedalus_mcp)            │
│      Built with @tool decorators         │
│                                          │
│  - Tool registration (collect)           │
│  - JSON Schema generation                │
│  - Tool execution handlers               │
└──────────────────────────────────────────┘

Flow:
1. Client sends request with mcp_servers list
2. SDK discovers tools from MCP server(s)
3. LLM sees tools in context
4. LLM decides to call tool
5. SDK routes call to MCP server
6. Server executes tool and returns result
7. SDK returns final response to user
```

## File Structure

```
jiri/
├── dedalus.py          # Main SDK for GPT-5 integration
├── mcp_server.py       # MCP server with tool implementations
├── dedalus_demo.py     # Complete integration demo
└── DEDALUS_README.md   # This file
```

## Adding Custom Tools

With Dedalus Labs MCP framework, adding tools is simple using the `@tool` decorator:

```python
from dedalus_mcp import MCPServer, tool

# 1. Define your tool with @tool decorator
# Type hints automatically become JSON Schema
@tool(description="Process a user's data")
def process_data(param1: str, param2: int) -> dict[str, str]:
    """Your tool implementation"""
    return {
        "result": f"Processed {param1} with {param2}"
    }

# For async operations
@tool(description="Fetch data from API")
async def fetch_api_data(endpoint: str) -> dict[str, Any]:
    """Async tool implementation"""
    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint)
        return response.json()

# 2. Add to your server
server = MCPServer("my-server")
server.collect(process_data)
server.collect(fetch_api_data)

# That's it! The SDK automatically discovers these tools
# when connecting to your MCP server
```

**Key Benefits:**
- Type hints → JSON Schema (automatic)
- No manual parameter definitions
- Works with sync and async functions
- Automatic tool discovery by SDK

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEDALUS_API_KEY` | Your Dedalus Labs API key | Yes |
| `OPENAI_API_KEY` | Your OpenAI API key (if using OpenAI models directly) | Optional |

## Testing

Run the individual components:

```bash
# Test SDK only
python dedalus.py

# Test MCP Server only
python mcp_server.py

# Test full integration
python dedalus_demo.py
```

## Notes

- Default model is `anthropic/claude-sonnet-4-20250514` (Claude Sonnet 4)
- Supports multiple providers: Anthropic, OpenAI, Google, etc.
- MCP server uses official `dedalus_mcp` framework
- Type hints automatically generate JSON Schema
- Works with both sync and async tool functions
- Local and hosted MCP servers are supported

## Supported Models

The Dedalus Labs SDK supports models from multiple providers:

- **Anthropic**: `anthropic/claude-sonnet-4-20250514`, `anthropic/claude-opus-4-...`
- **OpenAI**: `openai/gpt-4o`, `openai/gpt-4-turbo`
- **Google**: `google/gemini-2.0-flash-exp`
- And more...

Check [Dedalus Labs documentation](https://docs.dedaluslabs.ai) for full model list.

## Troubleshooting

**Error: "Dedalus API key is required"**
- Make sure `DEDALUS_API_KEY` is set in your `.env` file or environment
- Get your API key from [dedaluslabs.ai](https://dedaluslabs.ai)

**MCP server not connecting**
- Ensure the MCP server is running: `python mcp_server.py`
- Check the URL is correct (default: `http://localhost:8000/mcp`)
- Verify no firewall blocking the connection

**Tools not being discovered**
- Make sure tools are decorated with `@tool`
- Ensure `server.collect(tool_function)` is called
- Check server logs for registration confirmation

**LLM not calling tools**
- Tools are automatically available when MCP server is connected
- Try more explicit prompts: "Use the log_hello tool to greet me"
- Check that tool descriptions are clear and actionable

## Additional Resources

- **Dedalus Labs**: [dedaluslabs.ai](https://dedaluslabs.ai)
- **Documentation**: [docs.dedaluslabs.ai](https://docs.dedaluslabs.ai)
- **MCP Server Guide**: [docs.dedaluslabs.ai/dmcp/server/overview](https://docs.dedaluslabs.ai/dmcp/server/overview)
- **Quickstart**: [docs.dedaluslabs.ai/dmcp/quickstart](https://docs.dedaluslabs.ai/dmcp/quickstart)
- **Examples**: [docs.dedaluslabs.ai/dmcp/examples](https://docs.dedaluslabs.ai/dmcp/examples)

## What's Next?

1. **Explore more tools**: Add resources, prompts, and complex tool chains
2. **Deploy your MCP server**: Host on Dedalus marketplace for easy discovery
3. **Build production apps**: Use with any LLM provider through unified SDK
4. **Monitor usage**: Track tool calls and optimize performance

## License

MIT License - Part of the Jiri project

---

Built with ❤️ using [Dedalus Labs](https://dedaluslabs.ai)
