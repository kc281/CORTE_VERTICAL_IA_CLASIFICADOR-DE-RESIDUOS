"""Endpoints del API (capa de controladores).

Cada endpoint solo recibe HTTP, valida el formato de la entrada y delega en un
servicio de aplicación (app/services). Las reglas de negocio viven en los servicios
y el SQL en el repositorio (app/crud.py).

    RF-01 Clasificar residuo ........ POST  /predict                 -> ClasificacionService.clasificar
    RF-02 Historial de consultas .... (escritura en POST /predict)   -> ClasificacionService.clasificar
                                      GET   /history                 -> HistorialService.listar
                                      GET   /predict/{prediction_id} -> HistorialService.obtener
                                      PATCH /predict/{id}/verify     -> HistorialService.verificar
    RF-03 Panel estadístico ......... GET   /stats                   -> EstadisticasService.resumen

Los errores de negocio (app/services/exceptions.py) se traducen a HTTP en app/main.py.
"""
from fastapi import APIRouter, Depends, File, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import config
from app.auth import get_current_user
from app.crud import PredictionRepository
from app.database import get_db
from app.model_loader import predict as predict_model
from app.schemas import ErrorResponse, HealthResponse, ModelInfoResponse, PredictionResponse
from app.services import (
    ClasificacionService, EmpresaService, EstadisticasService, HistorialService,
)
from app.utils import validate_image

router = APIRouter()


# ─── Errores documentados en el contrato (se muestran en /docs) ───
def _err(descripcion: str) -> dict:
    return {"model": ErrorResponse, "description": descripcion}


E400 = {400: _err("Entrada inválida (formato, tipo o valor fuera de rango).")}
E401 = {401: _err("Token ausente, inválido o expirado.")}
E403 = {403: _err("El usuario no está asociado a ninguna empresa.")}
E404 = {404: _err("Registro no encontrado o no pertenece a su empresa.")}
E500 = {500: _err("Error interno (no expone detalles técnicos).")}


# ─── Inyección de dependencias: sesión -> repositorio -> servicio ───
def get_repository(db: Session = Depends(get_db)) -> PredictionRepository:
    return PredictionRepository(db)


def get_clasificacion_service(repo=Depends(get_repository)) -> ClasificacionService:
    return ClasificacionService(repo, predict_model)


def get_historial_service(repo=Depends(get_repository)) -> HistorialService:
    return HistorialService(repo)


def get_estadisticas_service(repo=Depends(get_repository)) -> EstadisticasService:
    return EstadisticasService(repo)


def get_empresa_service(repo=Depends(get_repository)) -> EmpresaService:
    return EmpresaService(repo)


# ─── Sistema ─────────────────────────────────────
@router.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")


@router.get("/model-info", response_model=ModelInfoResponse, tags=["Sistema"])
async def model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        modelo=config.MODEL_NAME, clases=config.CLASSES,
        clases_etiquetas=config.CLASSES_LABELS_ES, input_size=config.INPUT_SIZE, version="1.0.0",
    )


# ─── RF-01 (+ escritura RF-02): clasificar un residuo ───
@router.post(
    "/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED,
    tags=["RF-01 Clasificación"],
    responses={**E400, **E401, **E403,
               413: _err("La imagen supera el tamaño máximo (5 MB)."), **E500},
)
async def predict_endpoint(
    file: UploadFile = File(...),
    service: ClasificacionService = Depends(get_clasificacion_service),
    current_user: dict = Depends(get_current_user),
) -> PredictionResponse:
    image = await validate_image(file)
    return PredictionResponse(**service.clasificar(current_user["user_id"], image))


# ─── RF-02: consultar el historial ───
@router.get("/history", tags=["RF-02 Historial"], responses={**E400, **E401, **E403, **E500})
async def get_history(
    skip: int = 0,
    limit: int = 50,
    service: HistorialService = Depends(get_historial_service),
    current_user: dict = Depends(get_current_user),
):
    """Historial paginado de clasificaciones de la empresa (más reciente primero)."""
    return service.listar(current_user["user_id"], skip, limit)


@router.get("/predict/{prediction_id}", tags=["RF-02 Historial"],
            responses={**E400, **E401, **E403, **E404, **E500})
async def get_prediction_by_id(
    prediction_id: int,
    service: HistorialService = Depends(get_historial_service),
    current_user: dict = Depends(get_current_user),
):
    """Un registro del historial por su ID."""
    return service.obtener(current_user["user_id"], prediction_id)


class VerifyPredictionRequest(BaseModel):
    categoria_correcta: str


@router.patch("/predict/{prediction_id}/verify", tags=["RF-02 Historial"],
              responses={**E400, **E401, **E403, **E404, **E500})
async def verify_prediction(
    prediction_id: int,
    request: VerifyPredictionRequest,
    service: HistorialService = Depends(get_historial_service),
    current_user: dict = Depends(get_current_user),
):
    """Permite a un usuario corregir o confirmar la clasificación de la IA."""
    log = service.verificar(current_user["user_id"], prediction_id, request.categoria_correcta)
    return {"message": "Predicción verificada correctamente", "categoria_confirmada": log.categoria_confirmada}


# ─── RF-03: panel estadístico ───
@router.get("/stats", tags=["RF-03 Estadísticas"], responses={**E401, **E403, **E500})
async def get_stats(
    service: EstadisticasService = Depends(get_estadisticas_service),
    current_user: dict = Depends(get_current_user),
):
    return service.resumen(current_user["user_id"])


# ─── Soporte: empresas ───
class CompanyCreate(BaseModel):
    name: str


@router.post("/register-company", tags=["Empresas"],
             responses={**E400, **E401, 409: _err("El usuario ya pertenece a una empresa."), **E500})
async def register_company(
    company_data: CompanyCreate,
    service: EmpresaService = Depends(get_empresa_service),
    current_user: dict = Depends(get_current_user),
):
    """Crea una empresa y asocia al usuario autenticado como administrador."""
    return service.registrar(current_user["user_id"], company_data.name)


@router.get("/company-info", tags=["Empresas"], responses={**E401, **E403, **E404})
async def get_company_info(
    service: EmpresaService = Depends(get_empresa_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna el nombre de la empresa del usuario autenticado."""
    return service.informacion(current_user["user_id"])
