"""Pruebas unitarias de la capa de servicios (RF-01, RF-02, RF-03).

Se sustituye el repositorio real por uno simulado (MagicMock) y el modelo de IA por
un predictor falso: ninguna prueba abre una conexión a la base de datos ni carga
TensorFlow. Ejecutar desde backend/:  python -m pytest tests -v
"""
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services import ClasificacionService, EstadisticasService, HistorialService
from app.services.exceptions import (
    EntradaInvalida, ErrorInferencia, ErrorPersistencia, RecursoNoEncontrado, UsuarioSinEmpresa,
)

USER = "11111111-1111-1111-1111-111111111111"
COMPANY = 7

RESULTADO_MODELO = {
    "clase": "plastic", "clase_etiqueta": "Plástico", "confianza": 0.91,
    "probabilidades": {"biological": 0.01, "cardboard": 0.02, "metal": 0.03,
                       "paper": 0.03, "plastic": 0.91},
    "color_disposicion": "blanco", "advertencia": False,
    "modelo": "MobileNetV2", "tiempo_inferencia_ms": 120,
}


def repo_con_empresa(company_id=COMPANY):
    repo = MagicMock()
    repo.get_company_id_for_user.return_value = company_id
    return repo


# ─── RF-01: clasificar (y registrar en el historial, RF-02) ───
class TestClasificacionService:
    def test_clasificacion_valida_guarda_y_retorna_id_real(self):
        repo = repo_con_empresa()
        repo.create_prediction_log.return_value = SimpleNamespace(id=42)
        service = ClasificacionService(repo, predictor=lambda img: dict(RESULTADO_MODELO))

        r = service.clasificar(USER, imagen=object())

        assert r["clase"] == "plastic" and r["id_prediccion"] == 42 and "timestamp" in r
        repo.create_prediction_log.assert_called_once_with(
            company_id=COMPANY, user_id=USER, clase_predicha="plastic",
            confianza=0.91, tiempo_inferencia=120, advertencia_activada=False,
        )

    def test_no_se_guarda_la_imagen(self):
        repo = repo_con_empresa()
        repo.create_prediction_log.return_value = SimpleNamespace(id=1)
        ClasificacionService(repo, lambda img: dict(RESULTADO_MODELO)).clasificar(USER, object())
        campos = repo.create_prediction_log.call_args.kwargs
        assert not any("imag" in k for k in campos)

    def test_usuario_sin_empresa_no_infiere_ni_guarda(self):
        repo = repo_con_empresa(None)
        predictor = MagicMock()
        with pytest.raises(UsuarioSinEmpresa):
            ClasificacionService(repo, predictor).clasificar(USER, object())
        predictor.assert_not_called()
        repo.create_prediction_log.assert_not_called()

    def test_fallo_del_modelo_no_guarda(self):
        repo = repo_con_empresa()
        predictor = MagicMock(side_effect=RuntimeError("boom"))
        with pytest.raises(ErrorInferencia):
            ClasificacionService(repo, predictor).clasificar(USER, object())
        repo.create_prediction_log.assert_not_called()

    def test_fallo_al_guardar_no_retorna_exito(self):
        repo = repo_con_empresa()
        repo.create_prediction_log.side_effect = Exception("BD caída")
        with pytest.raises(ErrorPersistencia):
            ClasificacionService(repo, lambda img: dict(RESULTADO_MODELO)).clasificar(USER, object())


# ─── RF-02: consultar el historial ───
class TestHistorialService:
    def test_listar_filtra_por_empresa(self):
        repo = repo_con_empresa()
        repo.get_company_history.return_value = {"total": 0, "records": []}
        assert HistorialService(repo).listar(USER, 0, 10) == {"total": 0, "records": []}
        repo.get_company_history.assert_called_once_with(COMPANY, 0, 10)

    @pytest.mark.parametrize("skip,limit", [(-1, 10), (0, 0), (0, 101)])
    def test_listar_rechaza_paginacion_invalida(self, skip, limit):
        repo = repo_con_empresa()
        with pytest.raises(EntradaInvalida):
            HistorialService(repo).listar(USER, skip, limit)
        repo.get_company_history.assert_not_called()

    def test_obtener_existente(self):
        repo = repo_con_empresa()
        registro = SimpleNamespace(id=5, clase_predicha="metal")
        repo.get_prediction_by_id.return_value = registro
        assert HistorialService(repo).obtener(USER, 5) is registro
        repo.get_prediction_by_id.assert_called_once_with(5, COMPANY)
        # La consulta solo lee: no se invoca ninguna escritura.
        repo.create_prediction_log.assert_not_called()
        repo.verify_prediction.assert_not_called()

    def test_obtener_ausente(self):
        repo = repo_con_empresa()
        repo.get_prediction_by_id.return_value = None
        with pytest.raises(RecursoNoEncontrado):
            HistorialService(repo).obtener(USER, 999999)

    @pytest.mark.parametrize("pid", [0, -3])
    def test_obtener_id_invalido(self, pid):
        repo = repo_con_empresa()
        with pytest.raises(EntradaInvalida):
            HistorialService(repo).obtener(USER, pid)
        repo.get_prediction_by_id.assert_not_called()

    def test_obtener_sin_empresa(self):
        with pytest.raises(UsuarioSinEmpresa):
            HistorialService(repo_con_empresa(None)).obtener(USER, 5)

    def test_verificar_categoria_invalida_no_escribe(self):
        repo = repo_con_empresa()
        with pytest.raises(EntradaInvalida):
            HistorialService(repo).verificar(USER, 5, "vidrio")
        repo.verify_prediction.assert_not_called()

    def test_verificar_valida(self):
        repo = repo_con_empresa()
        repo.verify_prediction.return_value = SimpleNamespace(categoria_confirmada="paper")
        log = HistorialService(repo).verificar(USER, 5, "paper")
        assert log.categoria_confirmada == "paper"
        repo.verify_prediction.assert_called_once_with(5, COMPANY, "paper")


# ─── RF-03: panel estadístico ───
class TestEstadisticasService:
    def test_resumen_calcula_porcentajes(self):
        repo = repo_con_empresa()
        repo.get_prediction_stats.return_value = {
            "total_consultas": 4, "confianza_promedio_global": 0.8,
            "tiempo_inferencia_promedio_ms": 100.0, "total_advertencias_baja_confianza": 1,
            "distribucion_clases": [{"clase": "metal", "cantidad": 3},
                                    {"clase": "paper", "cantidad": 1}],
        }
        r = EstadisticasService(repo).resumen(USER)
        assert [f["porcentaje"] for f in r["distribucion_clases"]] == [75.0, 25.0]
        repo.get_prediction_stats.assert_called_once_with(COMPANY)

    def test_resumen_sin_datos(self):
        repo = repo_con_empresa()
        repo.get_prediction_stats.return_value = {
            "total_consultas": 0, "confianza_promedio_global": 0.0,
            "tiempo_inferencia_promedio_ms": 0.0, "total_advertencias_baja_confianza": 0,
            "distribucion_clases": [],
        }
        assert EstadisticasService(repo).resumen(USER)["distribucion_clases"] == []

    def test_resumen_sin_empresa(self):
        repo = repo_con_empresa(None)
        with pytest.raises(UsuarioSinEmpresa):
            EstadisticasService(repo).resumen(USER)
        repo.get_prediction_stats.assert_not_called()
