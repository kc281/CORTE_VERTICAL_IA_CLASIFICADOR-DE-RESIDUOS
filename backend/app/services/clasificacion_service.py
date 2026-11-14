"""Servicio de aplicación de RF-01 (clasificar un residuo) y escritura de RF-02.

Caso de uso: clasificar(user_id, imagen)
  1. Verificar que el usuario pertenezca a una empresa (aislamiento multiempresa).
  2. Ejecutar la inferencia del modelo (5 categorías).
     Regla: si la confianza es < 0.60 se activa la advertencia (la marca el predictor
     con config.LOW_CONFIDENCE_THRESHOLD).
  3. Registrar en el historial (RF-02): fecha, categoría, confianza, tiempo y advertencia.
     Regla de privacidad (Ley 1581 de 2012): NUNCA se guarda la imagen.
  4. Retornar el resultado solo después de confirmar la escritura.
"""
import logging
from datetime import datetime, timezone
from typing import Callable, Dict

from app.services.exceptions import ErrorInferencia, ErrorPersistencia, UsuarioSinEmpresa

logger = logging.getLogger(__name__)


class ClasificacionService:
    def __init__(self, repo, predictor: Callable[[object], Dict]):
        # repo: objeto con get_company_id_for_user y create_prediction_log
        # predictor: función imagen -> dict (app.model_loader.predict en producción)
        self.repo = repo
        self.predictor = predictor

    def clasificar(self, user_id: str, imagen) -> Dict:
        company_id = self.repo.get_company_id_for_user(user_id)
        if company_id is None:
            raise UsuarioSinEmpresa()

        try:
            resultado = self.predictor(imagen)
        except Exception as exc:
            logger.exception("Error durante la inferencia")
            raise ErrorInferencia() from exc

        try:
            log = self.repo.create_prediction_log(
                company_id=company_id,
                user_id=user_id,
                clase_predicha=resultado["clase"],
                confianza=resultado["confianza"],
                tiempo_inferencia=resultado["tiempo_inferencia_ms"],
                advertencia_activada=resultado["advertencia"],
            )
        except Exception as exc:
            logger.exception("La inferencia fue exitosa, pero falló el guardado del historial")
            raise ErrorPersistencia() from exc

        return {
            **resultado,
            "id_prediccion": log.id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
