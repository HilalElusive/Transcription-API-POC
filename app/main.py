import hashlib
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, HTTPException, UploadFile
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from app import repository
from app.config import settings
from app.database import engine, init_db
from app.metrics import (TRANSCRIBED_TEXT_LENGTH, TRANSCRIPTION_CONFIDENCE, TRANSCRIPTIONS_TOTAL, )
from app.schemas import TranscriptionResponse
from app.transcription import transcribe_letter
import os
import socket

SERVED_BY_POD = os.environ.get("HOSTNAME") or socket.gethostname()

logging.basicConfig(
    level=settings.log_level,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "msg": "%(message)s"}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema")
    init_db()
    yield


app = FastAPI(
    title="Letter Transcription API",
    description="Transcribe handwritten letters to structured JSON",
    version="0.3.0",
    lifespan=lifespan,
)

# Métriques HTTP sur /metrics
Instrumentator().instrument(app).expose(app)


@app.get("/health/live", tags=["infra"])
def health_live():
    """Vie : processus actif ?"""
    return {"status": "ok"}


@app.get("/health/ready", tags=["infra"])
def health_ready():
    """Prêt : base accessible ?"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {e}")


@app.get("/health", tags=["infra"])
def health():
    return health_live()


@app.post("/transcribe", response_model=TranscriptionResponse, tags=["transcription"])
async def transcribe(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()
    image_size = len(image_bytes)

    if image_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image exceeds 5MB limit")

    image_hash = hashlib.sha256(image_bytes).hexdigest()
    logger.info(
        "Received transcription request",
        extra={"image_hash": image_hash, "image_size_bytes": image_size},
    )

    request_start = time.perf_counter()
    try:
        result = transcribe_letter(image_bytes)
    except Exception as e:
        elapsed_ms = int((time.perf_counter() - request_start) * 1000)
        logger.exception("Transcription failed")
        TRANSCRIPTIONS_TOTAL.labels(status="error", request_type="unknown").inc()
        repository.save_error(
            image_hash=image_hash,
            image_size_bytes=image_size,
            error_message=str(e),
            openai_model=settings.openai_model,
            processing_time_ms=elapsed_ms,
        )
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

    # Métriques métier
    TRANSCRIPTIONS_TOTAL.labels(
        status="success", request_type=result.response.requestType.value
    ).inc()
    TRANSCRIPTION_CONFIDENCE.observe(result.response.confidence)
    TRANSCRIBED_TEXT_LENGTH.observe(len(result.response.descriptionHtml))

    # Sauvegarde sans bloquer la réponse.
    repository.save_success(
        image_hash=image_hash,
        image_size_bytes=image_size,
        response=result.response,
        openai_model=result.model,
        tokens_input=result.tokens_input,
        tokens_output=result.tokens_output,
        processing_time_ms=result.duration_ms,
    )

    response = result.response
    response.servedByPod = SERVED_BY_POD
    return response