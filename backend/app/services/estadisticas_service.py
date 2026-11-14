"""Servicio de aplicación de RF-03 (panel estadístico).

Caso de uso: resumen(user_id)
  - Verifica la empresa del usuario y calcula, SOLO con sus registros:
    total de consultas, distribución por categoría, confianza promedio,
    tiempo de inferencia promedio y total de advertencias de baja confianza.
  - Agrega el porcentaje de cada categoría sobre el total.
"""
import logging
from typing import Dict

from app.services.exceptions import ErrorConsulta, UsuarioSinEmpresa

logger = logging.getLogger(__name__)


class EstadisticasService:
    def __init__(self, repo):
        self.repo = repo

    def resumen(self, user_id: str) -> Dict:
        company_id = self.repo.get_company_id_for_user(user_id)
        if company_id is None:
            raise UsuarioSinEmpresa()

        try:
            stats = self.repo.get_prediction_stats(company_id)
        except Exception as exc:
            logger.exception("Error obteniendo estadísticas")
            raise ErrorConsulta() from exc

        total = stats["total_consultas"]
        stats["distribucion_clases"] = [
            {**fila, "porcentaje": round(fila["cantidad"] * 100 / total, 2) if total else 0.0}
            for fila in stats["distribucion_clases"]
        ]
        return stats
