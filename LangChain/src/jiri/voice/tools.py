"""Local tool definitions and MCP server loader for Azure Voice Live."""

import os
import json
from pathlib import Path
from typing import Any

from azure.ai.voicelive.models import FunctionTool, MCPServer


# ============================================
# Local Tool Definitions
# ============================================

TOOL_DEFINITIONS: list[FunctionTool] = [
    FunctionTool(
        name="get_current_time",
        description="Get the current date and time",
        parameters={
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone name (e.g., 'America/New_York', 'UTC')",
                }
            },
            "required": [],
        },
    ),
    FunctionTool(
        name="calculate",
        description="Perform basic mathematical calculations",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')",
                }
            },
            "required": ["expression"],
        },
    ),
]


# ============================================
# Local Tool Handlers
# ============================================


def get_current_time(arguments: dict) -> str:
    """Get current time in specified timezone."""
    from datetime import datetime
    import pytz

    tz_name = arguments.get("timezone", "UTC")
    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        return json.dumps(
            {
                "time": now.strftime("%I:%M %p"),
                "date": now.strftime("%B %d, %Y"),
                "timezone": tz_name,
            }
        )
    except Exception as e:
        return json.dumps({"error": str(e)})


def calculate(arguments: dict) -> str:
    """Evaluate a mathematical expression safely."""
    expression = arguments.get("expression", "")
    try:
        # Use compile + restricted eval for safety
        # Only allow basic math operators and numbers
        allowed_chars = set("0123456789+-*/().% ")
        if not all(c in allowed_chars for c in expression):
            return json.dumps({"error": "Invalid characters in expression"})

        # Compile to AST for safety check
        code = compile(expression, "<string>", "eval")

        # Check for forbidden names (no builtins, no imports)
        for name in code.co_names:
            return json.dumps({"error": f"Forbidden name: {name}"})

        # Safe eval with no builtins
        result = eval(code, {"__builtins__": {}}, {})
        return json.dumps({"expression": expression, "result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})


TOOL_HANDLERS: dict[str, Any] = {
    "get_current_time": get_current_time,
    "calculate": calculate,
}


# ============================================
# MCP Server Loader
# ============================================


def load_mcp_servers() -> list[MCPServer]:
    """Load MCP servers from mcp_servers.json."""
    config_path = Path(__file__).parent / "mcp_servers.json"

    if not config_path.exists():
        print(f"Warning: {config_path} not found, no MCP servers loaded")
        return []

    try:
        with open(config_path) as f:
            servers_config = json.load(f)

        mcp_servers = []
        for config in servers_config:
            server = MCPServer(
                server_label=config["server_label"],
                server_url=config["server_url"],
                require_approval=config.get("require_approval", "never"),
                allowed_tools=config.get("allowed_tools"),
            )
            mcp_servers.append(server)
            print(f"✓ Loaded MCP server: {config['server_label']}")

        return mcp_servers
    except Exception as e:
        print(f"Error loading MCP servers: {e}")
        return []
