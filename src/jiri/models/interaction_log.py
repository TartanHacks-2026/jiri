"""InteractionLog model for voice interaction tracking.

Stores every voice interaction for:
- Analytics and debugging
- Latency monitoring
- Tool usage patterns
- Agentuity visualization

Corresponds to the TimescaleDB hypertable defined in init.sql.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Double, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from jiri.models.base import Base


class InteractionLog(Base):
    """Model for logging voice interactions.

    This table is a TimescaleDB hypertable partitioned by time
    for efficient time-series queries.

    Attributes:
        id: Auto-incrementing primary key.
        time: Timestamp of the interaction (partition key).
        user_id: UUID of the user.
        session_id: UUID of the voice session.
        intent: Detected intent from speech.
        tool_called: Name of MCP tool executed (if any).
        input_text: Transcribed user speech.
        result_summary: Summary of tool/response result.
        latency_ms: End-to-end latency in milliseconds.
        success_score: 0.0-1.0 score of interaction success.
        trace_id: Unique trace ID for debugging.
    """

    __tablename__ = "interaction_logs"

    # Primary key (composite with time for hypertable)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        server_default=func.now(),
        index=True,
    )

    # User identification
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    session_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    # Interaction details
    intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tool_called: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metrics
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    success_score: Mapped[float | None] = mapped_column(Double, nullable=True)

    # Tracing
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index("idx_interaction_logs_user_id", "user_id", "time"),
        Index("idx_interaction_logs_session_id", "session_id", "time"),
    )

    def __repr__(self) -> str:
        return (
            f"InteractionLog(id={self.id}, user_id={self.user_id}, "
            f"intent={self.intent}, tool={self.tool_called})"
        )
