"""Servicio de aplicación de RF-02 (consultar el historial de clasificaciones).

La escritura del historial ocurre en ClasificacionService (RF-01 y RF-02 comparten
el flujo de POST /predict). Este servicio cubre las consultas y la verificación humana.

Casos de uso:
  - listar(user_id, skip, limit): historial paginado de la empresa del usuario.
  - obtener(user_id, prediction_id): un registro por ID; distingue encontrado de ausente.
  - verificar(user_id, prediction_id, categoria): guarda la categoría confirmada por un humano.
"""
from typing import Dict

from app import config
from app.services.exceptions import EntradaInvalida, RecursoNoEncontrado, UsuarioSinEmpresa

LIMITE_MAXIMO = 100


class HistorialService:
    def __init__(self, repo):
        self.repo = repo

    def _company_id(self, user_id: str) -> int:
        company_id = self.repo.get_company_id_for_user(user_id)
        if company_id is None:
            raise UsuarioSinEmpresa()
        return company_id

    @staticmethod
    def _validar_id(prediction_id: int) -> None:
        if prediction_id is None or prediction_id <= 0:
            raise EntradaInvalida("El ID de la predicción debe ser un entero positivo.")

    def listar(self, user_id: str, skip: int = 0, limit: int = 50) -> Dict:
        if skip < 0:
            raise EntradaInvalida("El parámetro 'skip' no puede ser negativo.")
        if not 1 <= limit <= LIMITE_MAXIMO:
            raise EntradaInvalida(f"El parámetro 'limit' debe estar entre 1 y {LIMITE_MAXIMO}.")
        company_id = self._company_id(user_id)
        return self.repo.get_company_history(company_id, skip, limit)

    def obtener(self, user_id: str, prediction_id: int):
        self._validar_id(prediction_id)
        company_id = self._company_id(user_id)
        log = self.repo.get_prediction_by_id(prediction_id, company_id)
        if log is None:
            raise RecursoNoEncontrado()
        return log

    def verificar(self, user_id: str, prediction_id: int, categoria: str):
        self._validar_id(prediction_id)
        if categoria not in config.CLASSES:
            raise EntradaInvalida(
                f"Categoría no válida. Use una de: {', '.join(config.CLASSES)}."
            )
        company_id = self._company_id(user_id)
        log = self.repo.verify_prediction(prediction_id, company_id, categoria)
        if log is None:
            raise RecursoNoEncontrado()
        return log
