"""MCP Discovery and Caching with Dedalus Marketplace Crawler."""

import json
from datetime import datetime, timedelta
from typing import Any

import chromadb
from chromadb.config import Settings

from jiri.core.config import get_settings


class MCPDiscovery:
    """Discovers and caches MCPs from Dedalus Marketplace."""

    def __init__(self):
        self._chroma_client: chromadb.HttpClient | None = None
        self._collection: chromadb.Collection | None = None
        self._cache_ttl = timedelta(hours=24)
        self._last_refresh: datetime | None = None

        # Native Dedalus MCPs - prioritized
        self._native_mcps = [
            "tsion/yahoo-finance-mcp",
            "tsion/uber-mcp",
            "tsion/doordash-mcp",
            "meanerbeaver/webpage-extract",
            "meanerbeaver/git-repo-brief",
            "meanerbeaver/dedalus-marketplace-crawler-ts",
        ]

        # Usage counters (in-memory, should be persisted to DB)
        self._usage_counts: dict[str, int] = {}

    async def connect(self):
        """Connect to ChromaDB."""
        settings = get_settings()
        try:
            self._chroma_client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=Settings(anonymized_telemetry=False),
            )
            self._collection = self._chroma_client.get_or_create_collection(
                name="mcp_registry",
                metadata={"description": "MCP Server Registry with semantic search"},
            )
            print("✓ MCPDiscovery connected to ChromaDB")
        except Exception as e:
            print(f"Warning: ChromaDB connection failed: {e}")
            self._chroma_client = None

    async def refresh_from_marketplace(self) -> list[dict]:
        """Fetch all MCPs from Dedalus Marketplace using the crawler MCP.

        This uses the meanerbeaver/dedalus-marketplace-crawler-ts MCP
        to fetch available MCP servers.
        """
        # For now, return the native MCPs as a starting point
        # In production, this would call the actual crawler MCP
        mcps = [
            {
                "slug": "tsion/yahoo-finance-mcp",
                "name": "Yahoo Finance",
                "description": "Get stock prices, market data, and financial information",
                "tools": ["get_stock_price", "get_market_summary"],
                "category": "finance",
            },
            {
                "slug": "tsion/uber-mcp",
                "name": "Uber",
                "description": "Book rides, estimate fares, and track drivers",
                "tools": ["request_ride", "get_fare_estimate", "track_ride"],
                "category": "transportation",
            },
            {
                "slug": "tsion/doordash-mcp",
                "name": "DoorDash",
                "description": "Order food delivery from local restaurants",
                "tools": ["search_restaurants", "place_order", "track_order"],
                "category": "food",
            },
            {
                "slug": "meanerbeaver/webpage-extract",
                "name": "Webpage Extract",
                "description": "Extract readable content, tables, and metadata from webpages",
                "tools": ["extract_content", "extract_tables", "get_metadata"],
                "category": "utilities",
            },
            {
                "slug": "meanerbeaver/git-repo-brief",
                "name": "Git Repo Brief",
                "description": "Generate structured briefs for public GitHub repositories",
                "tools": ["get_repo_brief", "list_files", "get_readme"],
                "category": "development",
            },
        ]

        # Cache in ChromaDB
        if self._collection:
            for mcp in mcps:
                self._collection.upsert(
                    ids=[mcp["slug"]],
                    documents=[f"{mcp['name']}: {mcp['description']}"],
                    metadatas=[
                        {
                            "slug": mcp["slug"],
                            "name": mcp["name"],
                            "category": mcp["category"],
                            "tools": json.dumps(mcp["tools"]),
                        }
                    ],
                )

        self._last_refresh = datetime.now()
        print(f"✓ Cached {len(mcps)} MCPs from marketplace")
        return mcps

    async def find_relevant_mcps(self, query: str, limit: int = 5) -> list[str]:
        """Find MCPs relevant to a user query using semantic search."""
        if not self._collection:
            # Fall back to native MCPs
            return self._native_mcps[:limit]

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=limit,
            )

            if results["ids"] and results["ids"][0]:
                slugs = results["ids"][0]
                # Prioritize native MCPs
                native_first = [s for s in slugs if s in self._native_mcps]
                others = [s for s in slugs if s not in self._native_mcps]
                return native_first + others

        except Exception as e:
            print(f"Semantic search failed: {e}")

        return self._native_mcps[:limit]

    def get_warm_mcps(self, count: int = 5) -> list[str]:
        """Get the most frequently used MCPs (warm pool)."""
        if not self._usage_counts:
            return self._native_mcps[:count]

        sorted_mcps = sorted(
            self._usage_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return [slug for slug, _ in sorted_mcps[:count]]

    def record_usage(self, slug: str):
        """Record MCP usage for ranking."""
        self._usage_counts[slug] = self._usage_counts.get(slug, 0) + 1

    async def get_mcp_info(self, slug: str) -> dict | None:
        """Get information about a specific MCP."""
        if not self._collection:
            return None

        try:
            result = self._collection.get(ids=[slug])
            if result["metadatas"]:
                meta = result["metadatas"][0]
                return {
                    "slug": meta["slug"],
                    "name": meta["name"],
                    "category": meta["category"],
                    "tools": json.loads(meta["tools"]),
                }
        except Exception:
            pass
        return None

    @property
    def needs_refresh(self) -> bool:
        """Check if cache needs refresh."""
        if self._last_refresh is None:
            return True
        return datetime.now() - self._last_refresh > self._cache_ttl


# Global instance
mcp_discovery = MCPDiscovery()
