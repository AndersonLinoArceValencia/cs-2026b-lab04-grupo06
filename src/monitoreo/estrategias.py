"""Patrón Strategy y Factory para algoritmos de cálculo de tiempo estimado de llegada (ETA).

Permite incorporar nuevas políticas o algoritmos de estimación (Open/Closed Principle)
sin modificar la lógica de orquestación del ServicioMonitoreoSIT.
"""

from abc import ABC, abstractmethod
from typing import Dict, Type


class IEstrategiaETA(ABC):
    """Interfaz común (Strategy) para el cálculo de tiempo de llegada."""

    @abstractmethod
    def calcular_eta(self, distancia_km: float, velocidad_kmh: float) -> int:
        """Calcula el tiempo estimado en minutos a partir de distancia y velocidad."""
        raise NotImplementedError


class ETALinealStrategy(IEstrategiaETA):
    """Estrategia estándar: cálculo cinemático básico considerando velocidad mínima base."""

    def calcular_eta(self, distancia_km: float, velocidad_kmh: float) -> int:
        v = velocidad_kmh if velocidad_kmh > 5.0 else 15.0
        return int(round((distancia_km / v) * 60))


class ETAHoraPuntaStrategy(IEstrategiaETA):
    """Estrategia para congestión: penalización de velocidad al 60% y demora en paraderos."""

    def calcular_eta(self, distancia_km: float, velocidad_kmh: float) -> int:
        v = (velocidad_kmh * 0.6) if velocidad_kmh > 5.0 else 10.0
        return int(round((distancia_km / v) * 60)) + 4


class ETAParadasIntermediasStrategy(IEstrategiaETA):
    """Estrategia con paraderos intermedios: suma 2 min por cada 2 km de tramo."""

    def calcular_eta(self, distancia_km: float, velocidad_kmh: float) -> int:
        v = velocidad_kmh if velocidad_kmh > 5.0 else 18.0
        paradas = int(distancia_km // 2)
        return int(round((distancia_km / v) * 60)) + (paradas * 2)


class FabricaEstrategiasETA:
    """Fábrica y registro de estrategias de cálculo de ETA (Factory sin Singleton)."""

    def __init__(self):
        self._estrategias: Dict[str, Type[IEstrategiaETA]] = {
            "LINEAL": ETALinealStrategy,
            "HORA_PUNTA": ETAHoraPuntaStrategy,
            "PARADAS_INTERMEDIAS": ETAParadasIntermediasStrategy,
        }

    def registrar(self, tipo: str, estrategia_cls: Type[IEstrategiaETA]) -> None:
        """Permite registrar nuevas estrategias en tiempo de ejecución (OCP)."""
        self._estrategias[tipo] = estrategia_cls

    def crear(self, tipo: str) -> IEstrategiaETA:
        """Instancia la estrategia asociada al identificador solicitado."""
        if tipo not in self._estrategias:
            raise ValueError(f"Algoritmo de ETA no soportado: {tipo}")
        return self._estrategias[tipo]()
