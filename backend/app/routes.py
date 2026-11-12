"""Endpoints del API (Capa de Controladores)."""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel # <-- NUEVO IMPORT

from app import config
from app.model_loader import predict as predict_model
from app.schemas import HealthResponse, ModelInfoResponse, PredictionResponse
from app.utils import validate_image
from app.database import get_db
from app.auth import get_current_user
from app import crud

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")

@router.get("/model-info", response_model=ModelInfoResponse, tags=["Sistema"])
async def model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        modelo=config.MODEL_NAME, clases=config.CLASSES,
        clases_etiquetas=config.CLASSES_LABELS_ES, input_size=config.INPUT_SIZE, version="1.0.0",
    )

@router.post("/predict", response_model=PredictionResponse, tags=["Clasificación"])
async def predict_endpoint(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> PredictionResponse:
    
    image = await validate_image(file)

    try:
        result = predict_model(image)
    except Exception:
        logger.exception("Error durante la inferencia")
        raise HTTPException(status_code=500, detail="Ocurrió un error interno en la IA.")

    result["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Buscar empresa del usuario
    user_uuid = current_user["user_id"]
    company_id = crud.get_company_id_for_user(db, user_uuid)
    
    if not company_id:
        raise HTTPException(status_code=403, detail="El usuario no está asociado a ninguna empresa.")

    try:
        crud.create_prediction_log(
            db=db, company_id=company_id, user_id=user_uuid,
            clase_predicha=result["clase"], confianza=result["confianza"],
            tiempo_inferencia=result["tiempo_inferencia_ms"], advertencia_activada=result["advertencia"]
        )
    except Exception as e:
        logger.error(f"La predicción fue exitosa, pero falló el guardado: {e}")

    return PredictionResponse(**result)

@router.get("/stats", tags=["Estadísticas"])
async def get_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_uuid = current_user["user_id"]
    company_id = crud.get_company_id_for_user(db, user_uuid)
    
    if not company_id:
        raise HTTPException(status_code=403, detail="El usuario no está asociado a ninguna empresa.")

    try:
        return crud.get_prediction_stats(db, company_id)
    except Exception:
        logger.exception("Error obteniendo estadísticas")
        raise HTTPException(status_code=500, detail="Error al calcular las estadísticas.")

@router.get("/company-info", tags=["Empresas"])
async def get_company_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retorna el nombre de la empresa del usuario autenticado."""
    user_uuid = current_user["user_id"]
    company_id = crud.get_company_id_for_user(db, user_uuid)
    
    if not company_id:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asociada.")

    company = crud.get_company_details(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")

    return {"company_name": company.name, "company_id": company.id}

@router.get("/predict/{prediction_id}", tags=["Clasificación"])
async def get_prediction_by_id(
    prediction_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_uuid = current_user["user_id"]
    company_id = crud.get_company_id_for_user(db, user_uuid)
    
    log = crud.get_prediction_by_id(db, prediction_id, company_id)
    if not log:
        raise HTTPException(status_code=404, detail="Registro no encontrado o no pertenece a su empresa")
    return log


class CompanyCreate(BaseModel):
    name: str

@router.post("/register-company", tags=["Empresas"])
async def register_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Crea una empresa y asocia al usuario autenticado como administrador."""
    user_uuid = current_user["user_id"]
    
    # Verificar si el usuario ya tiene empresa para evitar duplicados
    existing_company = crud.get_company_id_for_user(db, user_uuid)
    if existing_company:
        raise HTTPException(status_code=400, detail="El usuario ya pertenece a una empresa.")

    try:
        new_company = crud.create_company_and_member(db, company_data.name, user_uuid)
        return {"message": "Empresa creada exitosamente", "company_id": new_company.id}
    except Exception:
        logger.exception("Error creando empresa")
        raise HTTPException(status_code=500, detail="Error al registrar la empresa.")

@router.get("/history", tags=["Historial"])
async def get_history(
    skip: int = 0, 
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene el historial paginado de clasificaciones de la empresa."""
    user_uuid = current_user["user_id"]
    company_id = crud.get_company_id_for_user(db, user_uuid)
    
    if not company_id:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asociada.")

    return crud.get_company_history(db, company_id, skip, limit)

from pydantic import BaseModel

class VerifyPredictionRequest(BaseModel):
    categoria_correcta: str

@router.patch("/predict/{prediction_id}/verify", tags=["Historial"])
async def verify_prediction(
    prediction_id: int,
    request: VerifyPredictionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Permite a un usuario corregir o confirmar la clasificación de la IA."""
    user_uuid = current_user["user_id"]
    company_id = crud.get_company_id_for_user(db, user_uuid)
    
    if not company_id:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asociada.")

    log = crud.verify_prediction(db, prediction_id, company_id, request.categoria_correcta)
    
    if not log:
        raise HTTPException(status_code=404, detail="Registro no encontrado o no pertenece a su empresa.")
        
    return {"message": "Predicción verificada correctamente", "categoria_confirmada": log.categoria_confirmada}