"""Módulo de detección de desvíos de ruta para unidades de transporte SIT."""
import math
from dataclasses import dataclass
from typing import List


@dataclass
class CoordenadaGPS:
    lat: float
    lon: float


def distancia_metros(c1: CoordenadaGPS, c2: CoordenadaGPS) -> float:
    """Calcula distancia euclidiana aproximada en metros (Arequipa: ~111,000 m por grado)."""
    dx = (c1.lon - c2.lon) * math.cos(math.radians(-16.4090)) * 111320.0
    dy = (c1.lat - c2.lat) * 110574.0
    return math.hypot(dx, dy)


def evaluar_desvio_ruta(
    posicion: CoordenadaGPS,
    waypoints_ruta: List[CoordenadaGPS],
    umbral_metros: float = 50.0
) -> bool:
    """Evalúa si una unidad está desviada de su ruta.
    
    BUG (ISSUE-02): Compara la distancia del bus únicamente contra los vértices/waypoints
    discretos de la ruta en vez de calcular la distancia ortogonal al segmento de curva.
    En curvas con waypoints espaciados (>100m), esto genera falsos positivos (retorna True).
    """
    if not waypoints_ruta:
        return False
    # Error: evalúa solo contra los waypoints aislados
    dist_minima = min(distancia_metros(posicion, wp) for wp in waypoints_ruta)
    return dist_minima > umbral_metros
