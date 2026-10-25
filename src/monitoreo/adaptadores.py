"""Patrón Adapter y Factory para proveedores externos de telemetría GPS.

Aísla el dominio de los formatos dispares e incompatibles de los SDKs
de los distintos concesionarios operadores del SIT (Dependency Inversion Principle).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict
from src.monitoreo.externos import GPSOperadorASDK, GPSOperadorBSDK


@dataclass
class DatosTelemetria:
    """Modelo canónico unificado de lectura de telemetría GPS."""
    latitud: float
    longitud: float
    velocidad_kmh: float
    id_unidad: str


class IProveedorGPS(ABC):
    """Puerto formal (Target) para la obtención de posición y telemetría de unidades."""

    @abstractmethod
    def obtener_posicion(self, id_bus: str) -> DatosTelemetria:
        """Obtiene la posición canónica del bus o eleva TimeoutError tras reintentos agotados."""
        raise NotImplementedError


class GPSOperadorAAdapter(IProveedorGPS):
    """Adaptador para el Concesionario A (Arequipa Bus).
    
    Traduce respuestas en formato diccionario con grados decimales a DatosTelemetria.
    """

    def __init__(self, sdk: Optional[GPSOperadorASDK] = None):
        self.sdk = sdk or GPSOperadorASDK()

    def obtener_posicion(self, id_bus: str) -> DatosTelemetria:
        resp = self.sdk.obtener_posicion(id_bus)
        if resp.get("ok"):
            return DatosTelemetria(
                latitud=resp["lat"],
                longitud=resp["lon"],
                velocidad_kmh=resp["velocidad_kmh"],
                id_unidad=resp.get("id_unidad", id_bus)
            )
        raise ValueError(f"Respuesta inválida del Operador A para unidad {id_bus}")


class GPSOperadorBAdapter(IProveedorGPS):
    """Adaptador para el Concesionario B (Consorcio Cono Norte / Tranvía).
    
    Traduce respuestas en formato tupla (status, microgrados, cm/s) a DatosTelemetria.
    """

    def __init__(self, sdk: Optional[GPSOperadorBSDK] = None):
        self.sdk = sdk or GPSOperadorBSDK()

    def obtener_posicion(self, id_bus: str) -> DatosTelemetria:
        codigo, lat_micro, lon_micro, speed_cm = self.sdk.query_location(int(id_bus))
        if codigo == 200:
            return DatosTelemetria(
                latitud=lat_micro / 1_000_000.0,
                longitud=lon_micro / 1_000_000.0,
                velocidad_kmh=speed_cm * 0.036,
                id_unidad=id_bus
            )
        raise ValueError(f"Error {codigo} al consultar telemetría del Operador B")


class FabricaProveedoresGPS:
    """Fábrica y registro de adaptadores de telemetría (Factory sin Singleton)."""

    def __init__(self, proveedores: Optional[Dict[str, IProveedorGPS]] = None):
        self._proveedores: Dict[str, IProveedorGPS] = proveedores or {
            "OPERADOR_A": GPSOperadorAAdapter(),
            "OPERADOR_B": GPSOperadorBAdapter(),
        }

    def registrar(self, operador: str, proveedor: IProveedorGPS) -> None:
        """Registra un nuevo adaptador de operador en tiempo de ejecución (OCP)."""
        self._proveedores[operador] = proveedor

    def obtener_proveedor(self, operador: str) -> IProveedorGPS:
        """Retorna el adaptador correspondiente al operador especificado."""
        if operador not in self._proveedores:
            raise ValueError(f"Operador GPS no soportado: {operador}")
        return self._proveedores[operador]
