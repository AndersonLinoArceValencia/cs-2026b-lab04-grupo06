from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from src.monitoreo.dominio import Coordenada
from src.monitoreo.estrategias import FabricaEstrategiasETA

LAT_MIN_AQP = -16.65
LAT_MAX_AQP = -16.15
LON_MIN_AQP = -71.80
LON_MAX_AQP = -71.30
VELOCIDAD_MAX_KMH = 120.0


@dataclass(frozen=True)
class ResultadoLlegada:
    estado: str
    minutos_eta: Optional[int]
    hora_estimada: Optional[datetime]


def _validar_coordenada_arequipa(coord: Coordenada) -> None:
    en_lat = LAT_MIN_AQP <= coord.latitud <= LAT_MAX_AQP
    en_lon = LON_MIN_AQP <= coord.longitud <= LON_MAX_AQP
    if not (en_lat and en_lon):
        raise ValueError("Coordenada GPS fuera del rango geografico de Arequipa")


def _validar_velocidad(velocidad_kmh: float) -> None:
    if velocidad_kmh < 0.0 or velocidad_kmh > VELOCIDAD_MAX_KMH:
        raise ValueError("La velocidad debe estar entre 0 y 120 km/h")


def estimar_hora_llegada(
    ubicacion_gps: Optional[Coordenada],
    km_bus: float,
    km_paradero: float,
    velocidad_kmh: float,
    hora_actual: datetime,
    estrategia: str = "LINEAL",
) -> ResultadoLlegada:
    if ubicacion_gps is None:
        return ResultadoLlegada(estado="SIN_GPS", minutos_eta=None, hora_estimada=None)

    _validar_coordenada_arequipa(ubicacion_gps)
    _validar_velocidad(velocidad_kmh)

    if km_bus > km_paradero:
        return ResultadoLlegada(estado="YA_PASO", minutos_eta=None, hora_estimada=None)

    distancia_km = km_paradero - km_bus
    fabrica = FabricaEstrategiasETA()
    minutos = fabrica.crear(estrategia).calcular_eta(distancia_km, velocidad_kmh)
    hora_estimada = hora_actual + timedelta(minutes=minutos)
    return ResultadoLlegada(estado="EN_CAMINO", minutos_eta=minutos, hora_estimada=hora_estimada)
