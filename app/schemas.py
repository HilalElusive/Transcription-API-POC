"""Modèles Pydantic pour l'API de transcription de courriers.

Ces schémas définissent le contrat public du service et restent séparés
des routes et du fournisseur IA afin d'être réutilisables par les clients,
la documentation et les tests.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RequestType(str, Enum):
    PASSEPORT = "passeport"
    CARTE_IDENTITE = "carte_identite"
    ETAT_CIVIL = "etat_civil"
    URBANISME = "urbanisme"
    RECLAMATION = "reclamation"
    AUTRE = "autre"


class Operation(str, Enum):
    DEMANDE = "demande"
    RENOUVELLEMENT = "renouvellement"
    MODIFICATION = "modification"
    RECLAMATION = "reclamation"
    AUTRE = "autre"


class Channel(str, Enum):
    MAIL = "mail"
    EMAIL = "email"
    GUICHET = "guichet"
    AUTRE = "autre"


class TranscriptionRequest(BaseModel):
    """Entrée de /transcribe.

    L'image peut être fournie via une référence S3, pratique pour les
    traitements en production, par lots ou asynchrones.
    """
    s3_bucket: Optional[str] = Field(None, description="Nom du bucket S3")
    s3_key: Optional[str] = Field(None, description="Clé de l'objet S3")


class TranscriptionExtracted(BaseModel):
    """Contenu extrait du courrier par le fournisseur IA.

    C'est le seul modèle transmis au LLM comme response_format.
    Il contient uniquement des champs déductibles depuis l'image,
    jamais de métadonnées système.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "subject": "Demande de renouvellement de passeport",
                "descriptionHtml": "<p>Jean Dupont...</p>",
                "contactName": "Jean Dupont",
                "contactEmail": "jean.dupont@gmail.com",
                "contactPhone": "+33612345678",
                "addressLine": "12, rue des chênes",
                "postalCode": "75015",
                "city": "Paris",
                "requestType": "passeport",
                "operation": "renouvellement",
                "channel": "mail",
                "language": "fr",
                "handwritingDetected": True,
                "confidence": 0.98,
                "notes": "Écriture manuscrite détectée – vérification humaine recommandée.",
            }
        }
    )

    subject: str = Field(..., description="Objet court extrait du courrier")
    descriptionHtml: str = Field(..., description="Transcription complète en HTML")
    contactName: Optional[str] = None
    contactEmail: Optional[EmailStr] = None
    contactPhone: Optional[str] = Field(None, description="Format E.164 si possible")
    addressLine: Optional[str] = None
    postalCode: Optional[str] = None
    city: Optional[str] = None
    requestType: RequestType = RequestType.AUTRE
    operation: Operation = Operation.AUTRE
    channel: Channel = Channel.MAIL
    language: str = Field("fr", description="Code langue ISO 639-1")
    handwritingDetected: bool = True
    confidence: float = Field(..., ge=0.0, le=1.0, description="De 0.0 à 1.0")
    notes: Optional[str] = None


class TranscriptionResponse(TranscriptionExtracted):
    """Réponse publique de l'API.

    Contenu extrait plus métadonnées système.
    """

    processedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Date et heure de traitement côté serveur",
    )
    servedByPod: Optional[str] = Field(
        default=None,
        description="Hostname du pod/conteneur ayant traité la requête",
    )