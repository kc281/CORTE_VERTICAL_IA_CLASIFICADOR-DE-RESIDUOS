from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# 1. Tabla de Empresas
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones (una empresa tiene muchos miembros y muchas predicciones)
    members = relationship("CompanyMember", back_populates="company")
    predictions = relationship("PredictionLog", back_populates="company")

# 2. Tabla de Miembros (Usuarios dentro de una empresa)
class CompanyMember(Base):
    __tablename__ = "company_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) # ID que genera Supabase Auth
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role = Column(String, default="admin")

    company = relationship("Company", back_populates="members")

# 3. Tabla de Predicciones (Ahora vinculada a una empresa y un usuario)
class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    clase_predicha = Column(String, index=True)
    confianza = Column(Float)
    tiempo_inferencia = Column(Integer)
    advertencia_activada = Column(Boolean, default=False)
    
    # --- NUEVOS CAMPOS MULTI-EMPRESA ---
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(String, nullable=False) 
    categoria_confirmada = Column(String, nullable=True) 

    company = relationship("Company", back_populates="predictions")

    __table_args__ = (
        CheckConstraint('confianza >= 0.0 AND confianza <= 1.0', name='check_confianza_rango'),
    )