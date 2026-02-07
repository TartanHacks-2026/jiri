#!/bin/bash
# Setup script for Dedalus SDK and MCP Server

set -e

echo "=================================================="
echo "  Dedalus SDK & MCP Server Setup"
echo "=================================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📄 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  Please edit .env and add your DEDALUS_API_KEY"
    echo "   Get your API key from: https://dedaluslabs.ai"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Check if DEDALUS_API_KEY is set
if grep -q "DEDALUS_API_KEY=your_dedalus_api_key_here" .env 2>/dev/null; then
    echo "⚠️  Warning: DEDALUS_API_KEY not set in .env"
    echo "   Please edit .env and add your API key"
    echo ""
fi

# Install dependencies
echo "📦 Installing dependencies..."
if command -v uv &> /dev/null; then
    echo "   Using uv..."
    uv sync
else
    echo "   Using pip..."
    pip install -e .
fi
echo "✓ Dependencies installed"
echo ""

# Summary
echo "=================================================="
echo "  Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your DEDALUS_API_KEY"
echo "  2. Run demo: python dedalus_demo.py"
echo "  3. Start MCP server: python mcp_server.py"
echo "  4. Use SDK: python dedalus.py"
echo ""
echo "Documentation:"
echo "  - README: DEDALUS_README.md"
echo "  - Dedalus Labs: https://dedaluslabs.ai"
echo "  - Docs: https://docs.dedaluslabs.ai"
echo ""
echo "=================================================="
