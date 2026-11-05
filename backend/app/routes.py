"""Endpoints del API con persistencia en Base de Datos."""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import config
from app.model_loader import predict as predict_model
from app.schemas import (
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
)
from app.utils import validate_image
from app.database import get_db
from app import models

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
async def predict_endpoint(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db) # Inyectamos la sesión de la BD
) -> PredictionResponse:
    """
    Recibe una imagen, devuelve la clasificación y guarda el registro en la BD.
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

    # 4) Guardar metadatos en la Base de Datos 
    try:
        db_log = models.PredictionLog(
            clase_predicha=result["clase"],
            confianza=result["confianza"],
            tiempo_inferencia=result["tiempo_inferencia_ms"],
            advertencia_activada=result["advertencia"]
        )
        db.add(db_log)
        db.commit()
    except Exception as e:
        # Si falla la BD, hacemos rollback y registramos el error, 
        
        db.rollback()
        logger.error(f"Error al guardar en la base de datos: {e}")

    return PredictionResponse(**result)


@router.get("/stats", tags=["Estadísticas"])
async def get_stats(db: Session = Depends(get_db)):
    """
    Módulo estadístico: Retorna métricas agregadas de todas las predicciones.
    Utiliza la base de datos para calcular promedios y distribuciones.
    """
    try:
        # 1. Conteo por clase 
        conteo_clases = db.query(
            models.PredictionLog.clase_predicha, 
            func.count(models.PredictionLog.id).label("cantidad")
        ).group_by(models.PredictionLog.clase_predicha).all()

        # 2. Métricas globales 
        metricas_globales = db.query(
            func.count(models.PredictionLog.id).label("total_consultas"),
            func.avg(models.PredictionLog.confianza).label("confianza_promedio"),
            func.avg(models.PredictionLog.tiempo_inferencia).label("tiempo_promedio")
        ).first()

        # 3. Conteo de advertencias (Umbral del 60%)
        total_advertencias = db.query(func.count(models.PredictionLog.id)).filter(
            models.PredictionLog.advertencia_activada == True
        ).scalar()

        # 4. Formatear respuesta
        return {
            "total_consultas": metricas_globales.total_consultas or 0,
            "confianza_promedio_global": round(float(metricas_globales.confianza_promedio or 0), 4),
            "tiempo_inferencia_promedio_ms": round(float(metricas_globales.tiempo_promedio or 0), 2),
            "total_advertencias_baja_confianza": total_advertencias or 0,
            "distribucion_clases": [
                {"clase": row.clase_predicha, "cantidad": row.cantidad} 
                for row in conteo_clases
            ]
        }
    except Exception as e:
        logger.exception("Error obteniendo estadísticas")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al calcular las estadísticas en la base de datos."
        )