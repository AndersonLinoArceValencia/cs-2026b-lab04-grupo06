"""Servicio de monitoreo y cálculo de ETA refactorizado (E2: Strategy + Adapter + Factory).

Elimina condicionales if/elif para proveedores GPS (Adapter) y algoritmos de ETA (Strategy),
orquestando los componentes mediante inyección de fábricas desacopladas (Factory).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from src.monitoreo.externos import GPSOperadorASDK, GPSOperadorBSDK, ServicioWebPushExterno
from src.monitoreo.adaptadores import (
    DatosTelemetria,
    IProveedorGPS,
    GPSOperadorAAdapter,
    GPSOperadorBAdapter,
    FabricaProveedoresGPS,
)
from src.monitoreo.estrategias import (
    IEstrategiaETA,
    FabricaEstrategiasETA,
)


@dataclass
class Coordenada:
    latitud: float
    longitud: float


@dataclass
class Paradero:
    id_paradero: str
    nombre: str
    latitud: float
    longitud: float


@dataclass
class Bus:
    id_bus: str
    placa: str
    operador: str  # "OPERADOR_A", "OPERADOR_B", etc.


@dataclass
class Viaje:
    id_viaje: str
    bus: Bus
    paradero_destino: Paradero
    estado: str  # "PROGRAMADO", "EN_RUTA", "DETENIDO", "DESVIADO", "FINALIZADO"
    distancia_km: float = 0.0


class ServicioMonitoreoSIT:
    """Servicio de monitoreo que delega en Strategy, Adapter y Factory."""

    def __init__(
        self,
        gps_a: Optional[GPSOperadorASDK] = None,
        gps_b: Optional[GPSOperadorBSDK] = None,
        web_push: Optional[ServicioWebPushExterno] = None,
        fabrica_gps: Optional[FabricaProveedoresGPS] = None,
        fabrica_eta: Optional[FabricaEstrategiasETA] = None,
    ):
        # Si se inyectan SDKs específicos (como en pruebas), se adaptan en la fábrica
        if fabrica_gps is not None:
            self.fabrica_gps = fabrica_gps
        else:
            proveedores = {
                "OPERADOR_A": GPSOperadorAAdapter(gps_a),
                "OPERADOR_B": GPSOperadorBAdapter(gps_b),
            }
            self.fabrica_gps = FabricaProveedoresGPS(proveedores)

        self.fabrica_eta = fabrica_eta or FabricaEstrategiasETA()
        self.web_push = web_push or ServicioWebPushExterno()
        self.eventos: List[str] = []

    def consultar_tiempo_llegada(self, viaje: Viaje, tipo_algoritmo: str = "LINEAL") -> Dict[str, Any]:
        """Flujo crítico refactorizado: delega telemetría a Adapter y cálculo a Strategy."""
        # 1. Validación de estado (State será aplicado en E3)
        if viaje.estado != "EN_RUTA":
            if viaje.estado == "PROGRAMADO":
                raise ValueError("El viaje está en estado PROGRAMADO y aún no inicia recorrido")
            elif viaje.estado == "DETENIDO":
                self.eventos.append(f"alerta:contingencia:viaje_{viaje.id_viaje}_detenido")
                raise ValueError("El viaje está DETENIDO por contingencia en la vía")
            elif viaje.estado == "DESVIADO":
                self.eventos.append(f"alerta:desvio:viaje_{viaje.id_viaje}_fuera_de_ruta")
                raise ValueError("El viaje está DESVIADO de su ruta oficial")
            elif viaje.estado == "FINALIZADO":
                raise ValueError("El viaje ya ha FINALIZADO")
            else:
                raise ValueError(f"Estado de viaje no reconocido: {viaje.estado}")

        if viaje.distancia_km <= 0.0:
            raise ValueError("La distancia al paradero debe ser mayor a 0 km")

        # 2. Obtención de telemetría mediante Factory y Adapter (sin if/elif por operador)
        proveedor: IProveedorGPS = self.fabrica_gps.obtener_proveedor(viaje.bus.operador)
        try:
            telemetria: DatosTelemetria = proveedor.obtener_posicion(viaje.bus.id_bus)
        except TimeoutError:
            self.eventos.append(f"alerta:gps_timeout:{viaje.bus.id_bus}")
            raise

        # 3. Cálculo de ETA mediante Factory y Strategy (sin if/elif por algoritmo)
        estrategia: IEstrategiaETA = self.fabrica_eta.crear(tipo_algoritmo)
        eta_min: int = estrategia.calcular_eta(viaje.distancia_km, telemetria.velocidad_kmh)

        # 4. Emisión de eventos y notificación externa
        self.eventos.append(f"pasajero:bus_{viaje.bus.id_bus}:ETA_{eta_min}_min")
        self.eventos.append(f"control:flota:bus_{viaje.bus.id_bus}:lat_{telemetria.latitud:.5f}:lon_{telemetria.longitud:.5f}")

        self.web_push.enviar_alerta(
            canal="pasajeros",
            titulo=f"Bus {viaje.bus.placa} aproximándose",
            cuerpo=f"Tiempo estimado: {eta_min} min al paradero {viaje.paradero_destino.nombre}"
        )

        return {
            "id_viaje": viaje.id_viaje,
            "id_bus": viaje.bus.id_bus,
            "eta_minutos": eta_min,
            "distancia_km": viaje.distancia_km,
            "estado": viaje.estado,
            "operador": viaje.bus.operador,
            "latitud": telemetria.latitud,
            "longitud": telemetria.longitud,
            "algoritmo": tipo_algoritmo,
        }

    def explicar_retraso(self, motivo: str, minutos_retraso: int) -> str:
        """Explicación simple con condicionales para pasajeros (a refactorizar con IA en E5)."""
        if minutos_retraso <= 0:
            return "El bus se encuentra operando dentro del itinerario normal."
        if "tráfico" in motivo.lower() or "congestión" in motivo.lower():
            return f"Retraso de aprox. {minutos_retraso} min debido a congestión vehicular en la vía."
        elif "choque" in motivo.lower() or "accidente" in motivo.lower():
            return f"Retraso de aprox. {minutos_retraso} min por atención de incidente vial reportado."
        elif "desvío" in motivo.lower() or "obra" in motivo.lower():
            return f"Retraso de aprox. {minutos_retraso} min por desvío temporal de ruta debido a obras."
        else:
            return f"Retraso estimado de {minutos_retraso} min por contingencia operativa en ruta."
