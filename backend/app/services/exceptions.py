"""Excepciones de negocio de la capa de servicios.

Los servicios no conocen HTTP: comunican el resultado del caso de uso con estas
excepciones. `app/main.py` las traduce a respuestas HTTP con un único manejador,
usando el atributo `status_code` y el mensaje (`detail`) de cada una.
"""


class ErrorNegocio(Exception):
    """Base de los errores esperados del dominio (distinguibles de un fallo interno)."""

    status_code = 400
    detail = "Solicitud inválida."

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class EntradaInvalida(ErrorNegocio):
    status_code = 400
    detail = "Los datos de entrada no son válidos."


class UsuarioSinEmpresa(ErrorNegocio):
    status_code = 403
    detail = "El usuario no está asociado a ninguna empresa."


class RecursoNoEncontrado(ErrorNegocio):
    status_code = 404
    detail = "Registro no encontrado o no pertenece a su empresa."


class Conflicto(ErrorNegocio):
    status_code = 409
    detail = "El recurso ya existe."


class ErrorInferencia(ErrorNegocio):
    status_code = 500
    detail = "Ocurrió un error interno en la IA."


class ErrorPersistencia(ErrorNegocio):
    status_code = 500
    detail = "No se pudo guardar el registro de la clasificación."


class ErrorConsulta(ErrorNegocio):
    status_code = 500
    detail = "Error al calcular las estadísticas."
