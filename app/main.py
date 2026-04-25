import logging
from fastapi import FastAPI, File, HTTPException, UploadFile
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
from app.config import settings
from app.schemas import TranscriptionResponse
from app.transcription import transcribe_letter

logging.basicConfig(
    level=settings.log_level,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "msg": "%(message)s"}',
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Letter Transcription API",
    description="Transcribe handwritten letters to structured JSON",
    version="0.1.0",
)

# Métriques métier pour suivre les transcriptions et la confiance du modèle
TRANSCRIPTIONS_TOTAL = Counter(
    "transcriptions_total",
    "Total transcriptions processed",
    ["status", "request_type"],
)
TRANSCRIPTION_CONFIDENCE = Histogram(
    "transcription_confidence",
    "Distribution of confidence scores",
    buckets=[0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0],
)

# Métriques HTTP exposées automatiquement sur /metrics
Instrumentator().instrument(app).expose(app)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}


@app.post("/transcribe", response_model=TranscriptionResponse, tags=["transcription"])
async def transcribe(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()
    if len(image_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image exceeds 5MB limit")

    try:
        result = transcribe_letter(image_bytes)
        TRANSCRIPTIONS_TOTAL.labels(status="success", request_type=result.requestType.value).inc()
        TRANSCRIPTION_CONFIDENCE.observe(result.confidence)
        return result
    except Exception as e:
        logger.exception("Transcription failed")
        TRANSCRIPTIONS_TOTAL.labels(status="error", request_type="unknown").inc()
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")