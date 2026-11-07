"""Endpoints del API """
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends
from sqlalchemy.orm import Session

from app import config
from app.model_loader import predict as predict_model
from app.schemas import (
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
)
from app.utils import validate_image
from app.database import get_db
from app import crud  # <-- Importamos el repositorio

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")


@router.get("/model-info", response_model=ModelInfoResponse, tags=["Sistema"])
async def model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        modelo=config.MODEL_NAME,
        clases=config.CLASSES,
        clases_etiquetas=config.CLASSES_LABELS_ES,
        input_size=config.INPUT_SIZE,
        version="1.0.0",
    )


@router.post("/predict", response_model=PredictionResponse, tags=["Clasificación"])
async def predict_endpoint(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
) -> PredictionResponse:
    
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

    # 4) Persistencia 
    try:
        crud.create_prediction_log(
            db=db,
            clase_predicha=result["clase"],
            confianza=result["confianza"],
            tiempo_inferencia=result["tiempo_inferencia_ms"],
            advertencia_activada=result["advertencia"]
        )
    except Exception:
        # Si falla la Base de Datos, el resultado del usuario se ve
        logger.error("La predicción fue exitosa, pero falló el guardado en BD.")

    return PredictionResponse(**result)


@router.get("/stats", tags=["Estadísticas"])
async def get_stats(db: Session = Depends(get_db)):
    """Obtiene las métricas estadísticas desde el repositorio."""
    try:
        return crud.get_prediction_stats(db)
    except Exception:
        logger.exception("Error obteniendo estadísticas")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al calcular las estadísticas en la base de datos."
        )


@router.get("/predict/{prediction_id}", tags=["Clasificación"])
async def get_prediction_by_id(prediction_id: int, db: Session = Depends(get_db)):
    """Recupera el registro de una predicción específica por su ID."""
    log = crud.get_prediction_by_id(db, prediction_id)
    if not log:
        # Aquí ocurre la prueba de calidad: en lugar de fallar, responde con un 404 controlado
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Registro no encontrado"
        )
    return log
