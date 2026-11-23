import importlib
import os
from datetime import datetime

import pytest

from src.monitoreo.dominio import Coordenada

MODULO_NOMBRE = os.environ.get("MODULO", "src.monitoreo.llegada")
COORD_AQP = Coordenada(-16.4090, -71.5375)


def cargar_modulo():
    return importlib.import_module(MODULO_NOMBRE)


def test_bus_en_camino_estrategia_lineal():
    mod = cargar_modulo()
    ahora = datetime(2026, 11, 23, 8, 0)
    res = mod.estimar_hora_llegada(
        ubicacion_gps=COORD_AQP,
        km_bus=2.0,
        km_paradero=5.0,
        velocidad_kmh=30.0,
        hora_actual=ahora,
        estrategia="LINEAL",
    )
    assert res.estado == "EN_CAMINO"
    assert res.minutos_eta == 6
    assert res.hora_estimada == datetime(2026, 11, 23, 8, 6)


def test_bus_ya_paso_el_paradero():
    mod = cargar_modulo()
    ahora = datetime(2026, 11, 23, 8, 15)
    res = mod.estimar_hora_llegada(
        ubicacion_gps=COORD_AQP,
        km_bus=6.2,
        km_paradero=5.0,
        velocidad_kmh=25.0,
        hora_actual=ahora,
    )
    assert res.estado == "YA_PASO"
    assert res.minutos_eta is None
    assert res.hora_estimada is None


def test_gps_sin_datos():
    mod = cargar_modulo()
    ahora = datetime(2026, 11, 23, 8, 20)
    res = mod.estimar_hora_llegada(
        ubicacion_gps=None,
        km_bus=2.0,
        km_paradero=5.0,
        velocidad_kmh=20.0,
        hora_actual=ahora,
    )
    assert res.estado == "SIN_GPS"
    assert res.minutos_eta is None
    assert res.hora_estimada is None


def test_hora_punta_reutiliza_estrategia():
    mod = cargar_modulo()
    ahora = datetime(2026, 11, 23, 18, 0)
    res = mod.estimar_hora_llegada(
        ubicacion_gps=COORD_AQP,
        km_bus=1.0,
        km_paradero=4.0,
        velocidad_kmh=30.0,
        hora_actual=ahora,
        estrategia="HORA_PUNTA",
    )
    assert res.estado == "EN_CAMINO"
    assert res.minutos_eta == 14
    assert res.hora_estimada == datetime(2026, 11, 23, 18, 14)


def test_bus_en_el_mismo_paradero():
    mod = cargar_modulo()
    ahora = datetime(2026, 11, 23, 9, 0)
    res = mod.estimar_hora_llegada(
        ubicacion_gps=COORD_AQP,
        km_bus=5.0,
        km_paradero=5.0,
        velocidad_kmh=20.0,
        hora_actual=ahora,
    )
    assert res.estado == "EN_CAMINO"
    assert res.minutos_eta == 0
    assert res.hora_estimada == ahora


@pytest.mark.parametrize("velocidad", [-5.0, 150.0])
def test_velocidad_fuera_de_rango_lanza_error(velocidad):
    mod = cargar_modulo()
    with pytest.raises(ValueError, match="velocidad"):
        mod.estimar_hora_llegada(
            ubicacion_gps=COORD_AQP,
            km_bus=1.0,
            km_paradero=4.0,
            velocidad_kmh=velocidad,
            hora_actual=datetime(2026, 11, 23, 8, 0),
        )


def test_coordenada_fuera_de_arequipa_lanza_error():
    mod = cargar_modulo()
    with pytest.raises(ValueError, match="Arequipa"):
        mod.estimar_hora_llegada(
            ubicacion_gps=Coordenada(0.0, 0.0),
            km_bus=1.0,
            km_paradero=4.0,
            velocidad_kmh=25.0,
            hora_actual=datetime(2026, 11, 23, 8, 0),
        )
