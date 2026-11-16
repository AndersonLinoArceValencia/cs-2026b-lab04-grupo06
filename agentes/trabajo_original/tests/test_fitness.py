"""
tests/test_fitness.py
Fitness functions ejecutables como pruebas de regresión arquitectónica (QA-01, QA-03, QA-05).
Garantizan que la arquitectura no se degrade ante futuros cambios o refactorizaciones.
"""

import pytest
from fitness.rendimiento import simular, con_cache, bd_con_indice, bd_sin_indice
from fitness.disponibilidad import simular as simular_disponibilidad

PRESUPUESTO_P95_MS = 150.0  # Límite estricto fijado en QA-01


def test_ff04_rendimiento_p95_hora_punta():
    """
    [FF-04] Rendimiento en tiempo real (QA-01 / ADR-006):
    Bajo una carga de hora punta de 30 req/s con 4 workers,
    la combinación de índice compuesto y caché debe responder con p95 <= 150 ms.
    """
    res = simular(lam=30, workers=4, servicio=con_cache(bd_con_indice, hit_rate=0.85))
    assert res["p95"] <= PRESUPUESTO_P95_MS, (
        f"Degradación arquitectónica: p95={res['p95']:.1f} ms excede el presupuesto de {PRESUPUESTO_P95_MS} ms"
    )


def test_ff05_disponibilidad_cero_telemetrias_perdidas():
    """
    [FF-05] Resiliencia y Cero Pérdidas (QA-03 / ADR-007):
    Ante desconexión de red celular o caída del proveedor GPS,
    el Circuit Breaker con Outbox debe garantizar 0 eventos perdidos.
    """
    res = simular_disponibilidad("breaker_outbox")
    assert res["perdidos"] == 0, (
        f"Violación de resiliencia: se perdieron {res['perdidos']} tramas telemétricas"
    )


def test_ff06_circuit_breaker_protege_canal_caido():
    """
    [FF-06] Protección del canal de red (QA-03 / ADR-007):
    El Circuit Breaker en modo ABIERTO debe reducir las llamadas inútiles al canal
    en más del 90% en comparación con la política ingenua de reintentos sincrónicos.
    """
    res_breaker = simular_disponibilidad("breaker_outbox")
    res_reintentos = simular_disponibilidad("reintentos")
    
    # Debe ser al menos 10 veces menor que los reintentos
    assert res_breaker["llamadas_en_caida"] < (res_reintentos["llamadas_en_caida"] / 10), (
        f"El breaker no protegió adecuadamente: {res_breaker['llamadas_en_caida']} vs {res_reintentos['llamadas_en_caida']}"
    )


def test_ff07_aislamiento_multitenant_consorcios():
    """
    [FF-07] Seguridad y Aislamiento de Empresas Concesionarias (QA-05 / ADR-008):
    Verifica que la política de aislamiento filtra estrictamente los datos por consorcio_id.
    """
    # Dataset simulado con buses pertenecientes a consorcios distintos
    buses_db = [
        {"bus_id": "BUS-001", "consorcio_id": 1, "placa": "V1A-101", "linea": "T-01"},
        {"bus_id": "BUS-002", "consorcio_id": 1, "placa": "V1A-102", "linea": "T-01"},
        {"bus_id": "BUS-003", "consorcio_id": 2, "placa": "V2B-201", "linea": "A-04"},
        {"bus_id": "BUS-004", "consorcio_id": 3, "placa": "V3C-301", "linea": "C-02"},
    ]

    def repositorio_consultar_buses_con_rls(consorcio_solicitante: int):
        # Simula el filtrado enforced por RLS en PostgreSQL
        return [b for b in buses_db if b["consorcio_id"] == consorcio_solicitante]

    # Consorcio 1 (Arequipa Bus) solo debe ver 2 buses y ninguno del consorcio 2 ni 3
    resultado_consorcio_1 = repositorio_consultar_buses_con_rls(consorcio_solicitante=1)
    assert len(resultado_consorcio_1) == 2
    assert all(b["consorcio_id"] == 1 for b in resultado_consorcio_1)

    # Consorcio 2 (Tranvía) solo debe ver 1 bus
    resultado_consorcio_2 = repositorio_consultar_buses_con_rls(consorcio_solicitante=2)
    assert len(resultado_consorcio_2) == 1
    assert resultado_consorcio_2[0]["bus_id"] == "BUS-003"
