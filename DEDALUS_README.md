# Dedalus SDK + MCP

Simple integration of Dedalus Labs SDK with MCP tools.

## Files

- **`dedalus.py`** - Client with integrated MCP tools
- **`mcp_server.py`** - MCP tool definitions

## Setup

```bash
# 1. Add API key to .env
DEDALUS_API_KEY=your-key-here

# 2. Install
uv sync

# 3. Run
uv run python dedalus.py
```

## Usage

### Interactive Chat
```bash
uv run python dedalus.py
```

### In Code
```python
from dedalus import DedalusClient

client = DedalusClient()

# Simple chat
response = await client.chat("Hello!")

# Tools used automatically
response = await client.chat("Add 5 and 3")  # Uses add_numbers tool

# Disable tools
response = await client.chat("Add 5 and 3", use_tools=False)
```

## Available Tools

- `log_hello` - Logs hello
- `log_message(message)` - Logs custom message
- `add_numbers(a, b)` - Adds two numbers
- `get_server_info` - Server info

## Add Your Own Tool

In `mcp_server.py`:

```python
@tool(description="Your tool")
def my_tool(param: str) -> str:
    return f"Result: {param}"
```

In `dedalus.py`:

```python
# Add to _load_tools()
from mcp_server import my_tool
self.tools["my_tool"] = my_tool

# Add to tools_desc in _chat_with_tools()
"- my_tool(param): Your tool description",
```

That's it!
