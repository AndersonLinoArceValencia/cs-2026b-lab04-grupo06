"""Prueba que reproduce el ISSUE-01: Tiempo de llegada (ETA) negativo si el bus pasó el paradero."""
import pytest
from src.monitoreo.estrategias import ETALinealStrategy, ETAHoraPuntaStrategy, ETAParadasIntermediasStrategy


def test_eta_lineal_no_debe_ser_negativo_si_bus_rebaso_paradero():
    estrategia = ETALinealStrategy()
    # Si el bus ya pasó el paradero por 500m (distancia negativa), el ETA debe ser 0 min
    eta = estrategia.calcular_eta(distancia_km=-0.5, velocidad_kmh=15.0)
    assert eta == 0, f"Se esperaba ETA=0 pero se obtuvo {eta} (negativo)"


def test_eta_hora_punta_no_debe_ser_negativo_con_distancia_negativa():
    estrategia = ETAHoraPuntaStrategy()
    # Con distancia negativa severa (-2.0 km), el ETA no debe ser negativo
    eta = estrategia.calcular_eta(distancia_km=-2.0, velocidad_kmh=15.0)
    assert eta == 0, f"Se esperaba ETA=0 pero se obtuvo {eta} (negativo)"


def test_eta_paradas_intermedias_cero_con_distancia_cero_o_negativa():
    estrategia = ETAParadasIntermediasStrategy()
    assert estrategia.calcular_eta(distancia_km=0.0, velocidad_kmh=20.0) == 0
    assert estrategia.calcular_eta(distancia_km=-1.0, velocidad_kmh=20.0) == 0
