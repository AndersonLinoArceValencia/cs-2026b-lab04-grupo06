"""Prueba que reproduce el ISSUE-03: Falla o falta de validación ante trama GPS corrupta con datos nulos."""
import pytest
from src.monitoreo.adaptadores import GPSOperadorAAdapter


class MockGPSOperadorASDKCorrupto:
    """Simula pérdida de señal satelital o trama corrupta donde el hardware reporta None en coordenadas."""

    def obtener_posicion(self, id_bus: str):
        return {
            "ok": True,
            "id_unidad": id_bus,
            "lat": None,
            "lon": None,
            "velocidad_kmh": None,
        }


def test_trama_gps_con_coordenadas_nulas_debe_lanzar_error_controlado():
    """Verifica que el adaptador valide que las coordenadas sean numéricas y no None.
    
    BUG (ISSUE-03): Actualmente el adaptador acepta la trama con 'ok': True e instancia
    DatosTelemetria con latitud=None y longitud=None sin validar, propagando datos corruptos
    que provocan caídas con TypeError en el cálculo de distancias y geocercas del servicio.
    Debe lanzar ValueError indicando que las coordenadas o la trama son inválidas.
    """
    sdk_mock = MockGPSOperadorASDKCorrupto()
    adaptador = GPSOperadorAAdapter(sdk_mock)

    with pytest.raises(ValueError) as excinfo:
        telemetria = adaptador.obtener_posicion("BUS-01")
        # Si el adaptador no valida y permite coordenadas None, la prueba falla explícitamente:
        if telemetria.latitud is None or telemetria.longitud is None:
            raise AssertionError("El adaptador no validó coordenadas nulas y retornó DatosTelemetria corrupto")

    assert "coordenada" in str(excinfo.value).lower() or "trama" in str(excinfo.value).lower()
