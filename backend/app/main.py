"""Punto de entrada del backend FastAPI."""
import logging
import psycopg2
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import config
from app.model_loader import get_model
from app.routes import router
from app.database import engine, Base
from app import models
from app.services.exceptions import ErrorNegocio

# ─── Logging ─────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Lifespan: precarga el modelo al arrancar ───
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando backend de clasificación de residuos...")
    
    yield
    logger.info("Apagando backend...")

Base.metadata.create_all(bind=engine)

# ─── App ─────────────────────────────────────────
app = FastAPI(
    title="Clasificación de Residuos API",
    description=(
        "API para clasificar residuos en 5 categorías "
        "(biológicos, cartón, metal, papel, plástico) "
        "mediante una CNN con transfer learning."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS  ───────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST","PATCH","OPTIONS"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────
app.include_router(router)


# ─── Manejadores de errores  ───
@app.exception_handler(ErrorNegocio)
async def negocio_handler(request: Request, exc: ErrorNegocio):
    """Traduce los errores de la capa de servicios a HTTP (400/403/404/409/500)."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    """Entrada con formato inválido (falta un campo, tipo incorrecto, ID no entero)."""
    return JSONResponse(
        status_code=400,
        content={"detail": "Solicitud inválida. Verifique los datos enviados."},
    )


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    logger.exception("Excepción no manejada")
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno. Intente de nuevo."},
    )


# ─── OpenAPI: la validación responde 400 (no 422); se quita el 422 automático de /docs ───
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    schema = get_openapi(title=app.title, version=app.version,
                         description=app.description, routes=app.routes)
    for operaciones in schema.get("paths", {}).values():
        for operacion in operaciones.values():
            operacion.get("responses", {}).pop("422", None)
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


# ─── Root informativo ────────────────────────────
@app.get("/", tags=["Sistema"])
async def root():
    return {
        "app": "Clasificación de Residuos API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": ["/health", "/model-info", "/predict", "/history", "/predict/{id}", "/stats"],
    }


# ─── Ejecución directa ───────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)