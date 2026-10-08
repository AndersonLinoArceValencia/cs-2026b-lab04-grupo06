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

    def consultar_eta(self, paradero: Paradero, servicio_monitoreo: 'ServicioMonitoreoSIT') -> Optional[int]:
        return servicio_monitoreo.solicitar_eta(self, paradero)

@dataclass
class Bus:
    id_bus: str
    placa: str
    capacidad: int
    _ubicacion_actual: Optional[Coordenada] = None

    def actualizar_ubicacion(self, coord: Coordenada) -> None:
        self._ubicacion_actual = coord

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
    
    def cambiar_estado(self, nuevo_estado: EstadoViaje) -> None:
        self.estado = nuevo_estado

    def calcular_tiempo_llegada(self, destino: Paradero) -> Optional[int]:
        if self.estado == EstadoViaje.EN_RUTA:
            ubicacion_bus = self.bus._ubicacion_actual
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
    def __init__(self, proveedor_gps: IProveedorGPS, servicio_mapas: IServicioMapas):
        self.proveedor_gps = proveedor_gps
        self.servicio_mapas = servicio_mapas

    def solicitar_eta(self, pasajero: Pasajero, paradero: Paradero) -> Optional[int]:
        viajes = paradero.obtener_viajes_proximos()
        
        if not viajes:
            return None # O lanzar error "No hay buses disponibles"
            
        tiempos = []
        for viaje in viajes:
            if viaje.estado == EstadoViaje.EN_RUTA:
                eta = viaje.calcular_tiempo_llegada(paradero)
                if eta is not None:
                    tiempos.append(eta)
            elif viaje.estado in (EstadoViaje.DESVIADO, EstadoViaje.DETENIDO):
                self.procesar_alerta_desvio(viaje)
                
        return min(tiempos) if tiempos else None

    def procesar_alerta_desvio(self, viaje: Viaje) -> None:
        # Emitir evento asíncrono o notificar a operaciones
        print(f"Alerta: Viaje {viaje.id_viaje} reportado como {viaje.estado.value}.")
