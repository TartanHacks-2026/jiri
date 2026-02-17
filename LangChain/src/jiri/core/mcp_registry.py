"""MCP Registry - CRUD operations for MCP Server management."""

import os
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jiri.core.models.mcp import MCPServer


class MCPRegistry:
    """
    Manages the registry of MCP servers stored in the database.

    Provides async CRUD operations and integration with ChromaDB
    for semantic tool discovery.
    """

    def __init__(self, db_session: AsyncSession, chroma_client=None):
        """
        Initialize the registry.

        Args:
            db_session: SQLAlchemy async session for database operations
            chroma_client: Optional ChromaDB client for semantic embeddings
        """
        self.db = db_session
        self.chroma = chroma_client
        self._collection_name = "mcp_tools"

    async def add(
        self,
        slug: str,
        name: str,
        description: str,
        url: Optional[str] = None,
        config: Optional[dict] = None,
    ) -> MCPServer:
        """
        Add a new MCP server to the registry.

        Also embeds the description into ChromaDB for semantic search.
        """
        mcp = MCPServer(
            slug=slug,
            name=name,
            description=description,
            url=url,
            is_active=True,
            config=config,
        )
        self.db.add(mcp)
        await self.db.commit()
        await self.db.refresh(mcp)

        # Embed in ChromaDB if available
        if self.chroma:
            try:
                collection = self.chroma.get_or_create_collection(self._collection_name)
                collection.add(
                    ids=[slug],
                    documents=[description],
                    metadatas=[{"name": name, "url": url or "", "slug": slug}],
                )
            except Exception as e:
                print(f"ChromaDB embedding failed: {e}")

        return mcp

    async def remove(self, slug: str) -> bool:
        """Remove an MCP server from the registry."""
        result = await self.db.execute(select(MCPServer).where(MCPServer.slug == slug))
        mcp = result.scalar_one_or_none()

        if mcp:
            await self.db.delete(mcp)
            await self.db.commit()

            # Remove from ChromaDB
            if self.chroma:
                try:
                    collection = self.chroma.get_collection(self._collection_name)
                    collection.delete(ids=[slug])
                except Exception:
                    pass

            return True
        return False

    async def list_active(self) -> list[MCPServer]:
        """List all active MCP servers."""
        result = await self.db.execute(select(MCPServer).where(MCPServer.is_active == True))
        return list(result.scalars().all())

    async def list_active_slugs(self) -> list[str]:
        """Get slugs of all active MCP servers for DedalusRunner."""
        servers = await self.list_active()
        return [s.slug for s in servers]

    async def get(self, slug: str) -> Optional[MCPServer]:
        """Get a specific MCP server by slug."""
        result = await self.db.execute(select(MCPServer).where(MCPServer.slug == slug))
        return result.scalar_one_or_none()

    async def set_active(self, slug: str, active: bool) -> bool:
        """Enable or disable an MCP server."""
        mcp = await self.get(slug)
        if mcp:
            mcp.is_active = active
            await self.db.commit()
            return True
        return False

    def find_relevant_tools(self, query: str, n_results: int = 3) -> list[dict]:
        """
        Semantic search for relevant MCP tools using ChromaDB.

        Returns list of dicts with slug, name, description, and similarity score.
        """
        if not self.chroma:
            return []

        try:
            collection = self.chroma.get_collection(self._collection_name)
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            tools = []
            if results and results.get("ids"):
                for i, id_ in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i] if results.get("distances") else 1.0
                    # Convert distance to similarity (assuming L2 distance)
                    similarity = max(0, 1 - distance)
                    tools.append(
                        {
                            "slug": id_,
                            "name": results["metadatas"][0][i].get("name", ""),
                            "description": results["documents"][0][i]
                            if results.get("documents")
                            else "",
                            "similarity": similarity,
                        }
                    )
            return tools
        except Exception as e:
            print(f"ChromaDB query failed: {e}")
            return []
