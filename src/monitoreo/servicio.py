"""Servicio de monitoreo y cálculo de ETA refactorizado (E2: Strategy + Adapter + Factory).

Elimina condicionales if/elif para proveedores GPS (Adapter) y algoritmos de ETA (Strategy),
orquestando los componentes mediante inyección de fábricas desacopladas (Factory).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from src.monitoreo.externos import GPSOperadorASDK, GPSOperadorBSDK, ServicioWebPushExterno
from src.monitoreo.estados import (
    EstadoViajeState,
    ProgramadoState,
    EnRutaState,
    DetenidoState,
    DesviadoState,
    FinalizadoState,
    TransicionInvalidaError,
    crear_estado_desde_string,
)
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


class Viaje:
    """Entidad principal de viaje que delega su ciclo de vida al patrón State."""

    def __init__(
        self,
        id_viaje: str,
        bus: Bus,
        paradero_destino: Paradero,
        estado: Any = "EN_RUTA",
        distancia_km: float = 0.0
    ):
        self.id_viaje = id_viaje
        self.bus = bus
        self.paradero_destino = paradero_destino
        self.distancia_km = distancia_km
        self.motivo_contingencia: Optional[str] = None

        if isinstance(estado, EstadoViajeState):
            self._estado = estado
        elif isinstance(estado, str):
            self._estado = crear_estado_desde_string(estado)
        else:
            self._estado = crear_estado_desde_string(str(estado))

    @property
    def estado(self) -> str:
        """Propiedad de compatibilidad que retorna el nombre en texto del estado."""
        return self._estado.nombre

    @property
    def estado_obj(self) -> EstadoViajeState:
        return self._estado

    def cambiar_a(self, nuevo_estado: EstadoViajeState) -> None:
        self._estado = nuevo_estado

    def iniciar_recorrido(self) -> None:
        self._estado.iniciar_recorrido(self)

    def registrar_detencion(self, motivo: str) -> None:
        self._estado.registrar_detencion(self, motivo)

    def registrar_desvio(self, motivo: str) -> None:
        self._estado.registrar_desvio(self, motivo)

    def reanudar_recorrido(self) -> None:
        self._estado.reanudar_recorrido(self)

    def retornar_a_ruta(self) -> None:
        self._estado.retornar_a_ruta(self)

    def finalizar_recorrido(self) -> None:
        self._estado.finalizar_recorrido(self)

    def validar_disponibilidad_eta(self, eventos: List[str]) -> None:
        self._estado.validar_disponibilidad_eta(self, eventos)


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
        # 1. Validación de estado delegada al objeto State (polimorfismo sin if/elif)
        viaje.validar_disponibilidad_eta(self.eventos)

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
