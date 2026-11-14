"""Servicio de soporte: empresas (no es uno de los tres RF, pero los habilita).

Todos los RF exigen que el usuario pertenezca a una empresa; este servicio
registra la empresa y devuelve sus datos.
"""
import logging
from typing import Dict

from app.services.exceptions import (
    Conflicto, EntradaInvalida, ErrorPersistencia, RecursoNoEncontrado, UsuarioSinEmpresa,
)

logger = logging.getLogger(__name__)


class EmpresaService:
    def __init__(self, repo):
        self.repo = repo

    def registrar(self, user_id: str, nombre: str) -> Dict:
        nombre = (nombre or "").strip()
        if not nombre:
            raise EntradaInvalida("El nombre de la empresa es obligatorio.")
        if self.repo.get_company_id_for_user(user_id) is not None:
            raise Conflicto("El usuario ya pertenece a una empresa.")
        try:
            empresa = self.repo.create_company_and_member(nombre, user_id)
        except Exception as exc:
            logger.exception("Error creando empresa")
            raise ErrorPersistencia("Error al registrar la empresa.") from exc
        return {"message": "Empresa creada exitosamente", "company_id": empresa.id}

    def informacion(self, user_id: str) -> Dict:
        company_id = self.repo.get_company_id_for_user(user_id)
        if company_id is None:
            raise UsuarioSinEmpresa()
        empresa = self.repo.get_company_details(company_id)
        if empresa is None:
            raise RecursoNoEncontrado("Empresa no encontrada.")
        return {"company_name": empresa.name, "company_id": empresa.id}
