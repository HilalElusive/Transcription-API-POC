import base64
import logging
from openai import OpenAI
from app.config import settings
from app.schemas import TranscriptionResponse, TranscriptionExtracted

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


def transcribe_letter(image_bytes: bytes) -> TranscriptionResponse:
    """Transcribe a handwritten letter image to structured JSON."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    logger.info("Calling OpenAI Vision", extra={"model": settings.openai_model})

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

    result = completion.choices[0].message.parsed
    logger.info(
        "Transcription successful",
        extra={"confidence": result.confidence, "request_type": result.requestType},
    )
    return TranscriptionResponse(**result.model_dump())