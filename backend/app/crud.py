"""Repositorio de acceso a datos."""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models

logger = logging.getLogger(__name__)

def get_company_id_for_user(db: Session, user_id: str) -> int:
    member = db.query(models.CompanyMember).filter(models.CompanyMember.user_id == user_id).first()
    return member.company_id if member else None

def create_prediction_log(
    db: Session, company_id: int, user_id: str, clase_predicha: str, 
    confianza: float, tiempo_inferencia: int, advertencia_activada: bool
) -> models.PredictionLog:
    try:
        db_log = models.PredictionLog(
            company_id=company_id, user_id=user_id, clase_predicha=clase_predicha,
            confianza=confianza, tiempo_inferencia=tiempo_inferencia, advertencia_activada=advertencia_activada
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        db.rollback()
        logger.error(f"Error al guardar la predicción en BD: {e}")
        raise e

def get_prediction_stats(db: Session, company_id: int) -> dict:
    """Retorna métricas SOLO de la empresa especificada."""
    
    # 1. Conteo por clase (Filtrado por empresa)
    conteo_clases = db.query(
        models.PredictionLog.clase_predicha, 
        func.count(models.PredictionLog.id).label("cantidad")
    ).filter(models.PredictionLog.company_id == company_id).group_by(models.PredictionLog.clase_predicha).all()

    # 2. Métricas globales (Filtrado por empresa)
    metricas_globales = db.query(
        func.count(models.PredictionLog.id).label("total_consultas"),
        func.avg(models.PredictionLog.confianza).label("confianza_promedio"),
        func.avg(models.PredictionLog.tiempo_inferencia).label("tiempo_promedio")
    ).filter(models.PredictionLog.company_id == company_id).first()

    # 3. Conteo de advertencias (Filtrado por empresa)
    total_advertencias = db.query(func.count(models.PredictionLog.id)).filter(
        models.PredictionLog.advertencia_activada == True,
        models.PredictionLog.company_id == company_id
    ).scalar()

    return {
        "total_consultas": metricas_globales.total_consultas or 0,
        "confianza_promedio_global": round(float(metricas_globales.confianza_promedio or 0), 4),
        "tiempo_inferencia_promedio_ms": round(float(metricas_globales.tiempo_promedio or 0), 2),
        "total_advertencias_baja_confianza": total_advertencias or 0,
        "distribucion_clases": [{"clase": row.clase_predicha, "cantidad": row.cantidad} for row in conteo_clases]
    }

def get_prediction_by_id(db: Session, prediction_id: int, company_id: int):
    """Busca una predicción por ID, asegurando que pertenezca a la empresa."""
    return db.query(models.PredictionLog).filter(
        models.PredictionLog.id == prediction_id,
        models.PredictionLog.company_id == company_id
    ).first()

def create_company_and_member(db: Session, company_name: str, user_id: str):
    """Crea una empresa y asocia al usuario como administrador."""
    try:
        # 1. Crear la empresa
        new_company = models.Company(name=company_name, status="active")
        db.add(new_company)
        db.commit()
        db.refresh(new_company)

        # 2. Asociar al usuario como admin
        new_member = models.CompanyMember(
            user_id=user_id, 
            company_id=new_company.id, 
            role="admin"
        )
        db.add(new_member)
        db.commit()
        return new_company
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear la empresa: {e}")
        raise e

def get_company_history(db: Session, company_id: int, skip: int = 0, limit: int = 50):
    """Retorna el historial de predicciones de una empresa con paginación."""
    # Contamos el total para saber cuántas páginas hay
    total = db.query(models.PredictionLog).filter(models.PredictionLog.company_id == company_id).count()
    
    # Traemos los registros ordenados del más reciente al más antiguo
    records = db.query(models.PredictionLog).filter(
        models.PredictionLog.company_id == company_id
    ).order_by(models.PredictionLog.fecha.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "records": records}

def verify_prediction(db: Session, prediction_id: int, company_id: int, categoria_correcta: str):
    """Actualiza la categoría confirmada de una predicción, asegurando el aislamiento por empresa."""
    log = db.query(models.PredictionLog).filter(
        models.PredictionLog.id == prediction_id,
        models.PredictionLog.company_id == company_id
    ).first()
    
    if log:
        log.categoria_confirmada = categoria_correcta
        db.commit()
        db.refresh(log)
    return log