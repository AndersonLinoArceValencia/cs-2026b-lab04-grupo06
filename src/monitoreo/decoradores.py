"""Patrón Decorator para responsabilidades transversales en RutaSIT Arequipa.

Proporciona capacidades transversales (caché de cómputo de ETA y reintentos de telemetría)
sin modificar la implementación concreta de las estrategias ni de los adaptadores.
"""

from typing import Dict, Tuple
from src.monitoreo.estrategias import IEstrategiaETA
from src.monitoreo.adaptadores import IProveedorGPS, DatosTelemetria


class CacheETADecorator(IEstrategiaETA):
    """DECORATOR: Memoriza cálculos de ETA para distancias y velocidades idénticas."""

    def __init__(self, estrategia_base: IEstrategiaETA):
        self._estrategia_base = estrategia_base
        self._cache: Dict[Tuple[float, float], int] = {}
        self.llamadas_reales: int = 0

    def calcular_eta(self, distancia_km: float, velocidad_kmh: float) -> int:
        clave = (round(distancia_km, 2), round(velocidad_kmh, 1))
        if clave not in self._cache:
            self.llamadas_reales += 1
            self._cache[clave] = self._estrategia_base.calcular_eta(distancia_km, velocidad_kmh)
        return self._cache[clave]

    def limpiar_cache(self) -> None:
        self._cache.clear()


class ReintentoGPSDecorator(IProveedorGPS):
    """DECORATOR: Añade política de reintentos configurables sobre cualquier proveedor GPS."""

    def __init__(self, proveedor_base: IProveedorGPS, max_intentos: int = 3):
        self._proveedor_base = proveedor_base
        self.max_intentos = max_intentos
        self.intentos_realizados: int = 0

    def obtener_posicion(self, id_bus: str) -> DatosTelemetria:
        ultimo_error = None
        for intento in range(self.max_intentos):
            try:
                self.intentos_realizados += 1
                return self._proveedor_base.obtener_posicion(id_bus)
            except TimeoutError as e:
                ultimo_error = e
                if intento == self.max_intentos - 1:
                    raise TimeoutError(f"No se pudo obtener la posición GPS tras {self.max_intentos} intentos") from e
        if ultimo_error:
            raise ultimo_error
