"""Endpoints del API """
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app import config
from app.model_loader import predict as predict_model
from app.schemas import (
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
)
from app.utils import validate_image

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health() -> HealthResponse:
    """Health check para verificar disponibilidad del servicio."""
    return HealthResponse(status="ok", version="1.0.0")


@router.get("/model-info", response_model=ModelInfoResponse, tags=["Sistema"])
async def model_info() -> ModelInfoResponse:
    """Información del modelo cargado y de las clases."""
    return ModelInfoResponse(
        modelo=config.MODEL_NAME,
        clases=config.CLASSES,
        clases_etiquetas=config.CLASSES_LABELS_ES,
        input_size=config.INPUT_SIZE,
        version="1.0.0",
    )


@router.post("/predict", response_model=PredictionResponse, tags=["Clasificación"])
async def predict_endpoint(file: UploadFile = File(...)) -> PredictionResponse:
    """
    Recibe una imagen y devuelve la clasificación.

    - Valida formato y tamaño
    - Preprocesa e infiere
    - Devuelve clase, confianza y probabilidades por clase
    """
    # 1) Validar imagen 
    image = await validate_image(file)

    # 2) Inferencia 
    try:
        result = predict_model(image)
    except Exception:
        logger.exception("Error durante la inferencia")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno. Intente de nuevo.",
        )

    # 3) Timestamp 
    result["timestamp"] = datetime.now(timezone.utc).isoformat()

    return PredictionResponse(**result)