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


def distancia_punto_a_segmento_metros(
    p: CoordenadaGPS,
    a: CoordenadaGPS,
    b: CoordenadaGPS
) -> float:
    """Calcula la distancia mínima en metros desde el punto p al segmento ab."""
    dx = (b.lon - a.lon) * math.cos(math.radians(-16.4090)) * 111320.0
    dy = (b.lat - a.lat) * 110574.0
    longitud_seg_sq = dx * dx + dy * dy
    if longitud_seg_sq == 0.0:
        return distancia_metros(p, a)

    px = (p.lon - a.lon) * math.cos(math.radians(-16.4090)) * 111320.0
    py = (p.lat - a.lat) * 110574.0
    t = max(0.0, min(1.0, (px * dx + py * dy) / longitud_seg_sq))

    proj_x = a.lon + t * (b.lon - a.lon)
    proj_y = a.lat + t * (b.lat - a.lat)
    return distancia_metros(p, CoordenadaGPS(lat=proj_y, lon=proj_x))


def evaluar_desvio_ruta(
    posicion: CoordenadaGPS,
    waypoints_ruta: List[CoordenadaGPS],
    umbral_metros: float = 50.0
) -> bool:
    """Evalúa si una unidad está desviada de su ruta.
    
    Calcula la distancia ortogonal mínima a los segmentos formados por waypoints
    consecutivos, evitando falsos positivos en curvas cerradas.
    """
    if not waypoints_ruta:
        return False
    if len(waypoints_ruta) == 1:
        return distancia_metros(posicion, waypoints_ruta[0]) > umbral_metros

    dist_minima = min(
        distancia_punto_a_segmento_metros(posicion, waypoints_ruta[i], waypoints_ruta[i + 1])
        for i in range(len(waypoints_ruta) - 1)
    )
    return dist_minima > umbral_metros
