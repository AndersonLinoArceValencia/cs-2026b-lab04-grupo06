"""Prueba que reproduce el ISSUE-02: Falso positivo de desvío en curvas cerradas de la ruta."""
import pytest
from src.monitoreo.desvios import CoordenadaGPS, evaluar_desvio_ruta


def test_no_debe_marcar_desvio_si_bus_circula_sobre_curva_entre_waypoints():
    """Simula una curva en la ruta entre waypoint A y waypoint B distanciados ~150 metros.
    
    El bus se encuentra en el punto medio exacto de la curva (sobre la calzada).
    La distancia perpendicular al segmento de ruta es 0m, pero la distancia euclidiana
    a los extremos A y B es ~75m. Con un umbral de 50m, el algoritmo defectuoso
    emite erróneamente True (desviado). Debe ser False.
    """
    wp1 = CoordenadaGPS(lat=-16.400000, lon=-71.530000)
    wp2 = CoordenadaGPS(lat=-16.401000, lon=-71.531000)
    ruta = [wp1, wp2]

    # Punto medio sobre el segmento de carretera
    bus_en_medio = CoordenadaGPS(lat=-16.400500, lon=-71.530500)

    # El bus NO está desviado; está exactamente en el trayecto de la curva
    desviado = evaluar_desvio_ruta(bus_en_medio, ruta, umbral_metros=50.0)
    assert desviado is False, "Falso positivo: el bus está en la curva de la ruta pero se marcó como desviado"


def test_si_debe_marcar_desvio_si_bus_esta_realmente_lejos_de_la_curva():
    wp1 = CoordenadaGPS(lat=-16.400000, lon=-71.530000)
    wp2 = CoordenadaGPS(lat=-16.401000, lon=-71.531000)
    ruta = [wp1, wp2]

    # Bus desviado a una calle paralela a 120 metros
    bus_lejos = CoordenadaGPS(lat=-16.400500, lon=-71.532000)

    desviado = evaluar_desvio_ruta(bus_lejos, ruta, umbral_metros=50.0)
    assert desviado is True, "El bus está fuera de la calzada a >100m y debe reportarse como desviado"
