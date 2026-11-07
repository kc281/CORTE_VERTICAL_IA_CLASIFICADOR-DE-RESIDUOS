from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, CheckConstraint 
from datetime import datetime
from app.database import Base

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    clase_predicha = Column(String, index=True)
    confianza = Column(Float)
    tiempo_inferencia = Column(Integer)
    advertencia_activada = Column(Boolean, default=False)

    
    __table_args__ = (
        CheckConstraint('confianza >= 0.0 AND confianza <= 1.0', name='check_confianza_rango'),
    )