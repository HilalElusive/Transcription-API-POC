"""Data access layer for Transcription records.
   Matches FastAPI's dependency-injection style.
"""
import logging
import time
from typing import Optional

from app.database import get_session
from app.metrics import DB_OPERATION_DURATION, DB_WRITE_ERRORS
from app.models import Transcription
from app.schemas import TranscriptionResponse

logger = logging.getLogger(__name__)


def save_success(
    image_hash: str,
    image_size_bytes: int,
    response: TranscriptionResponse,
    openai_model: str,
    tokens_input: int,
    tokens_output: int,
    processing_time_ms: int,
) -> Optional[Transcription]:
    """Persist a successful transcription. Returns None on DB failure (resilient)."""
    start = time.perf_counter()
    try:
        with get_session() as session:
            record = Transcription(
                image_hash=image_hash,
                image_size_bytes=image_size_bytes,
                subject=response.subject,
                request_type=response.requestType.value,
                operation=response.operation.value,
                confidence=response.confidence,
                full_response=response.model_dump(mode="json"),
                status="success",
                openai_model=openai_model,
                openai_tokens_input=tokens_input,
                openai_tokens_output=tokens_output,
                processing_time_ms=processing_time_ms,
            )
            session.add(record)
            session.flush()
            DB_OPERATION_DURATION.labels(operation="insert_success").observe(
                time.perf_counter() - start
            )
            return record
    except Exception:
        logger.exception("DB write failed for successful transcription")
        DB_WRITE_ERRORS.labels(operation="insert_success").inc()
        return None


def save_error(
    image_hash: str,
    image_size_bytes: int,
    error_message: str,
    openai_model: str,
    processing_time_ms: int,
) -> Optional[Transcription]:
    """Persist a failed transcription attempt for postmortem visibility."""
    start = time.perf_counter()
    try:
        with get_session() as session:
            record = Transcription(
                image_hash=image_hash,
                image_size_bytes=image_size_bytes,
                status="error",
                error_message=error_message[:5000],
                openai_model=openai_model,
                processing_time_ms=processing_time_ms,
            )
            session.add(record)
            session.flush()
            DB_OPERATION_DURATION.labels(operation="insert_error").observe(
                time.perf_counter() - start
            )
            return record
    except Exception:
        logger.exception("DB write failed for error transcription")
        DB_WRITE_ERRORS.labels(operation="insert_error").inc()
        return None