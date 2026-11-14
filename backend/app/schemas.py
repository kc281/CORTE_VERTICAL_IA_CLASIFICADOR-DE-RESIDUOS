"""Modelos Pydantic de request/response (contrato con el frontend)."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str


class ModelInfoResponse(BaseModel):
    modelo: str
    clases: List[str]
    clases_etiquetas: Dict[str, str]
    input_size: int
    version: str


class PredictionResponse(BaseModel):
    clase: str
    clase_etiqueta: str
    confianza: float = Field(..., ge=0, le=1)
    probabilidades: Dict[str, float]
    color_disposicion: str
    advertencia: bool
    modelo: str
    tiempo_inferencia_ms: int
    timestamp: str
    id_prediccion: Optional[int] = None  # ID real del registro guardado (RF-02)


class ErrorResponse(BaseModel):
    error: str