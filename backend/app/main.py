"""Punto de entrada del backend FastAPI."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import config
from app.model_loader import get_model
from app.routes import router

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
    try:
        get_model()
        logger.info("Modelo precargado y listo para inferencia.")
    except Exception as exc:
        logger.error(f"No se pudo precargar el modelo: {exc}")
        raise
    yield
    logger.info("Apagando backend...")


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
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────
app.include_router(router)


# ─── Manejadores de errores  ───
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Solicitud inválida. Verifique los datos enviados."},
    )


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    logger.exception("Excepción no manejada")
    return JSONResponse(
        status_code=500,
        content={"error": "Ocurrió un error interno. Intente de nuevo."},
    )


# ─── Root informativo ────────────────────────────
@app.get("/", tags=["Sistema"])
async def root():
    return {
        "app": "Clasificación de Residuos API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": ["/health", "/model-info", "/predict"],
    }


# ─── Ejecución directa ───────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)