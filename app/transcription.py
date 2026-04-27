import base64
import logging
import time
from dataclasses import dataclass
from openai import OpenAI
from app.config import settings
from app.metrics import OPENAI_CALL_DURATION, OPENAI_TOKENS_INPUT, OPENAI_TOKENS_OUTPUT
from app.schemas import TranscriptionExtracted, TranscriptionResponse

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """Tu es un assistant spécialisé dans la transcription
de courriers manuscrits adressés à une mairie française.

Pour chaque image, tu extrais :
- les coordonnées de l'expéditeur,
- la transcription complète du courrier en HTML,
- l'objet, le type de demande, l'opération demandée,
- une estimation de confiance entre 0.0 et 1.0.

Si une information n'est pas présente ou illisible, retourne null pour
ce champ. Ne jamais inventer. La confiance reflète ta certitude
globale sur la transcription.
"""


@dataclass
class TranscriptionResult:
    """Wraps the response with operational metadata captured during the call."""
    response: TranscriptionResponse
    duration_ms: int
    tokens_input: int
    tokens_output: int
    model: str


def transcribe_letter(image_bytes: bytes) -> TranscriptionResult:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    logger.info("Calling OpenAI Vision", extra={"model": settings.openai_model})

    start = time.perf_counter()
    try:
        completion = client.beta.chat.completions.parse(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Transcris ce courrier manuscrit."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                    ],
                },
            ],
            response_format=TranscriptionExtracted,
        )
        duration = time.perf_counter() - start
        OPENAI_CALL_DURATION.labels(model=settings.openai_model, status="success").observe(duration)
    except Exception:
        duration = time.perf_counter() - start
        OPENAI_CALL_DURATION.labels(model=settings.openai_model, status="error").observe(duration)
        raise

    parsed = completion.choices[0].message.parsed
    usage = completion.usage
    tokens_input = usage.prompt_tokens if usage else 0
    tokens_output = usage.completion_tokens if usage else 0

    OPENAI_TOKENS_INPUT.labels(model=settings.openai_model).inc(tokens_input)
    OPENAI_TOKENS_OUTPUT.labels(model=settings.openai_model).inc(tokens_output)

    logger.info(
        "Transcription successful",
        extra={"confidence": parsed.confidence, "request_type": parsed.requestType.value, "tokens_input": tokens_input, "tokens_output": tokens_output, "duration_ms": int(duration * 1000), },
    )

    return TranscriptionResult(
        response=TranscriptionResponse(**parsed.model_dump()),
        duration_ms=int(duration * 1000),
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        model=settings.openai_model,
    )