"""SQLAlchemy ORM models."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Transcription(Base):
    """Persistent record of every transcription attempt, success or failure."""
    __tablename__ = "transcriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    image_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    request_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    operation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    full_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # 'success' | 'error'
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    openai_model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    openai_tokens_input: Mapped[int | None] = mapped_column(Integer, nullable=True)
    openai_tokens_output: Mapped[int | None] = mapped_column(Integer, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )