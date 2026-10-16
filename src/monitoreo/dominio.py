from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

# ==========================================
# Enumeración de Estados
# ==========================================
class EstadoViaje(Enum):
    PROGRAMADO = "PROGRAMADO"
    EN_RUTA = "EN_RUTA"
    DESVIADO = "DESVIADO"
    DETENIDO = "DETENIDO"
    FINALIZADO = "FINALIZADO"

# ==========================================
# Tipos de Datos (Datatypes)
# ==========================================
@dataclass
class Coordenada:
    latitud: float
    longitud: float

# ==========================================
# Interfaces (Puertos para integraciones externas)
# ==========================================
class IProveedorGPS(ABC):
    @abstractmethod
    def obtener_coordenada_actual(self, id_bus: str) -> Coordenada:
        raise NotImplementedError("El adaptador debe implementar obtener_coordenada_actual")

class IServicioMapas(ABC):
    @abstractmethod
    def calcular_eta(self, origen: Coordenada, destino: Coordenada) -> int:
        raise NotImplementedError("El adaptador debe implementar calcular_eta")

class INotificador(ABC):
    @abstractmethod
    def notificar_retraso(self, viaje: "Viaje") -> None:
        raise NotImplementedError("El adaptador debe implementar notificar_retraso")

# ==========================================
# Adaptadores (realizan los puertos; sin integración real en el MVP)
# ==========================================
class ProveedorGPSAdapter(IProveedorGPS):
    def obtener_coordenada_actual(self, id_bus: str) -> Coordenada:
        raise NotImplementedError("Integrar con el proveedor GPS (Redis Streams)")

class ServicioMapasAdapter(IServicioMapas):
    def calcular_eta(self, origen: Coordenada, destino: Coordenada) -> int:
        raise NotImplementedError("Integrar con el servicio de mapas")

class WebPushAdapter(INotificador):
    def notificar_retraso(self, viaje: "Viaje") -> None:
        raise NotImplementedError("Integrar con el servicio Web Push")

# ==========================================
# Clases del Dominio
# ==========================================
@dataclass
class Paradero:
    id_paradero: str
    nombre: str
    ubicacion: Coordenada
    _viajes_proximos: List['Viaje'] = field(default_factory=list)

    def obtener_viajes_proximos(self) -> List['Viaje']:
        return self._viajes_proximos

@dataclass
class Pasajero:
    id_pasajero: str
    ubicacion_actual: Coordenada

@dataclass
class Bus:
    id_bus: str
    placa: str
    capacidad: int
    ubicacion_actual: Optional[Coordenada] = None

    def actualizar_ubicacion(self, coord: Coordenada) -> None:
        self.ubicacion_actual = coord

@dataclass
class Ruta:
    id_ruta: str
    nombre: str
    paraderos: List[Paradero] = field(default_factory=list)

    def obtener_paraderos(self) -> List[Paradero]:
        return self.paraderos

@dataclass
class Viaje:
    id_viaje: str
    estado: EstadoViaje
    hora_inicio_programada: datetime
    bus: Bus
    servicio_mapas: IServicioMapas
    
    def programar(self) -> None:
        self.estado = EstadoViaje.PROGRAMADO

    def cambiar_estado(self, nuevo_estado: EstadoViaje) -> None:
        self.estado = nuevo_estado

    def calcular_tiempo_llegada(self, destino: Paradero) -> Optional[int]:
        if self.estado == EstadoViaje.EN_RUTA:
            ubicacion_bus = self.bus.ubicacion_actual
            if ubicacion_bus:
                return self.servicio_mapas.calcular_eta(ubicacion_bus, destino.ubicacion)
        return None

    def registrar_contingencia(self, motivo: str) -> None:
        # Lógica mínima de contingencia
        if "tráfico" in motivo.lower() or "choque" in motivo.lower():
            self.cambiar_estado(EstadoViaje.DETENIDO)
        else:
            self.cambiar_estado(EstadoViaje.DESVIADO)

# ==========================================
# Servicios de Aplicación (Controlador/Caso de Uso)
# ==========================================
class ServicioMonitoreoSIT:
    def __init__(self, proveedor_gps: IProveedorGPS, notificador: INotificador):
        self.proveedor_gps = proveedor_gps
        self.notificador = notificador

    def solicitar_eta(self, pasajero: Pasajero, paradero: Paradero) -> Optional[int]:
        """Devuelve el menor ETA en minutos, o None si no hay buses o están retrasados."""
        viajes = paradero.obtener_viajes_proximos()

        if not viajes:
            return None  # "No hay buses aproximándose a este paradero"

        tiempos = []
        for viaje in viajes:
            coord = self.proveedor_gps.obtener_coordenada_actual(viaje.bus.id_bus)
            viaje.bus.actualizar_ubicacion(coord)
            eta = viaje.calcular_tiempo_llegada(paradero)
            if eta is not None:
                tiempos.append(eta)
            elif viaje.estado in (EstadoViaje.DESVIADO, EstadoViaje.DETENIDO):
                self.procesar_alerta_desvio(viaje)

        return min(tiempos) if tiempos else None

    def procesar_alerta_desvio(self, viaje: Viaje) -> None:
        self.notificador.notificar_retraso(viaje)

# ==========================================
# Interfaz de usuario
# ==========================================
class AppPasajero:
    def __init__(self, servicio_monitoreo: ServicioMonitoreoSIT, pasajero: Pasajero):
        self.servicio_monitoreo = servicio_monitoreo
        self.pasajero = pasajero

    def consultar_eta(self, paradero: Paradero) -> None:
        eta = self.servicio_monitoreo.solicitar_eta(self.pasajero, paradero)
        self.mostrar_resultado(eta)

    def mostrar_resultado(self, eta: Optional[int]) -> None:
        if eta is None:
            print("No hay buses aproximándose o el bus está retrasado.")
        else:
            print(f"El bus llega en {eta} minutos.")
