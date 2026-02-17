"""SQLAlchemy models for MCP Server Registry."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jiri.core.database import Base


class MCPServer(Base):
    """
    Represents a registered MCP (Model Context Protocol) server.

    Stores metadata about available tools/servers that can be invoked
    by the DedalusRunner during agent turns.
    """

    __tablename__ = "mcp_servers"

    # Primary key: the slug identifier (e.g., "tsion/yahoo-finance-mcp")
    slug: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Human-readable name
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Description for semantic search embedding
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Optional public URL (for self-hosted MCPs; null for Dedalus-managed)
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Whether this MCP is currently active and should be loaded
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Configuration JSON (env vars, arguments, etc.)
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<MCPServer(slug='{self.slug}', active={self.is_active})>"
