"""Repositorio de acceso a datos .
Encapsula todas las consultas y escrituras a la base de datos.
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models

logger = logging.getLogger(__name__)


def create_prediction_log(
    db: Session, 
    clase_predicha: str, 
    confianza: float, 
    tiempo_inferencia: int, 
    advertencia_activada: bool
) -> models.PredictionLog:
    """Guarda un registro de predicción en la base de datos."""
    try:
        db_log = models.PredictionLog(
            clase_predicha=clase_predicha,
            confianza=confianza,
            tiempo_inferencia=tiempo_inferencia,
            advertencia_activada=advertencia_activada
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log) # Refresca para obtener el ID generado
        return db_log
    except Exception as e:
        db.rollback()
        logger.error(f"Error al guardar la predicción en BD: {e}")
        raise e


def get_prediction_stats(db: Session) -> dict:
    """Retorna las métricas agregadas de la base de datos para el módulo estadístico."""
    
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

    # 3. Conteo de advertencias 
    total_advertencias = db.query(func.count(models.PredictionLog.id)).filter(
        models.PredictionLog.advertencia_activada == True
    ).scalar()

    # 4. Formatear y retornar
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