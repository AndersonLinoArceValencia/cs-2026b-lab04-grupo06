"""Versión ingenua del servicio de monitoreo de RutaSIT (antes del refactor).

Esta versión funciona para el flujo crítico de HU-01 (consultar tiempo de llegada),
pero concentra múltiples responsabilidades en un solo método y clase:
- Verificación manual de estados mediante if/elif
- Acoplamiento directo a SDKs de proveedores con interfaces incompatibles
- Algoritmos de cálculo de ETA mezclados con condicionales
- Reintentos implementados con bucles for y try/except manuales
- Emisión de notificaciones "a mano" concatenando strings en una lista
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from src.monitoreo.externos import GPSOperadorASDK, GPSOperadorBSDK, ServicioWebPushExterno


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
    operador: str  # "OPERADOR_A" o "OPERADOR_B"


@dataclass
class Viaje:
    id_viaje: str
    bus: Bus
    paradero_destino: Paradero
    estado: str  # "PROGRAMADO", "EN_RUTA", "DETENIDO", "DESVIADO", "FINALIZADO"
    distancia_km: float = 0.0


class ServicioMonitoreoSIT:
    """Servicio monolítico e ingenuo de monitoreo y cálculo de ETA."""

    def __init__(self, gps_a: Optional[GPSOperadorASDK] = None, gps_b: Optional[GPSOperadorBSDK] = None, web_push: Optional[ServicioWebPushExterno] = None):
        self.gps_a = gps_a or GPSOperadorASDK()
        self.gps_b = gps_b or GPSOperadorBSDK()
        self.web_push = web_push or ServicioWebPushExterno()
        self.eventos: List[str] = []

    def consultar_tiempo_llegada(self, viaje: Viaje, tipo_algoritmo: str = "LINEAL") -> Dict[str, Any]:
        """Flujo crítico: valida estado, consulta GPS con reintentos, calcula ETA y emite eventos."""
        # 1. Validación de estado del viaje (Olor: if/elif sobre estado que viola State)
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

        # 2. Validación de datos de entrada
        if viaje.distancia_km <= 0.0:
            raise ValueError("La distancia al paradero debe ser mayor a 0 km")

        # 3. Consulta de telemetría GPS con reintentos (Olor: acoplamiento a SDKs y reintentos en el servicio)
        aprobado = False
        lat, lon, velocidad = None, None, None

        if viaje.bus.operador == "OPERADOR_A":
            for intento in range(3):
                try:
                    resp = self.gps_a.obtener_posicion(viaje.bus.id_bus)
                    if resp.get("ok"):
                        lat = resp["lat"]
                        lon = resp["lon"]
                        velocidad = resp["velocidad_kmh"]
                        aprobado = True
                        break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False
            if not aprobado:
                self.eventos.append(f"alerta:gps_timeout:{viaje.bus.id_bus}")
                raise TimeoutError("No se pudo obtener la posición GPS del Operador A tras 3 intentos")

        elif viaje.bus.operador == "OPERADOR_B":
            for intento in range(3):
                try:
                    codigo, lat_micro, lon_micro, speed_cm = self.gps_b.query_location(int(viaje.bus.id_bus))
                    if codigo == 200:
                        lat = lat_micro / 1_000_000.0
                        lon = lon_micro / 1_000_000.0
                        velocidad = speed_cm * 0.036  # Conversión cm/s a km/h
                        aprobado = True
                        break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False
            if not aprobado:
                self.eventos.append(f"alerta:gps_timeout:{viaje.bus.id_bus}")
                raise TimeoutError("No se pudo obtener la posición GPS del Operador B tras 3 intentos")
        else:
            raise ValueError(f"Operador GPS no soportado: {viaje.bus.operador}")

        # 4. Cálculo de ETA según algoritmo (Olor: if/elif que viola Strategy y Open/Closed)
        if tipo_algoritmo == "LINEAL":
            v = velocidad if velocidad > 5.0 else 15.0  # Velocidad mínima base
            eta_min = int(round((viaje.distancia_km / v) * 60))
        elif tipo_algoritmo == "HORA_PUNTA":
            # Aplica reducción de velocidad por tráfico denso y suma demora fija en paraderos
            v = (velocidad * 0.6) if velocidad > 5.0 else 10.0
            eta_min = int(round((viaje.distancia_km / v) * 60)) + 4
        elif tipo_algoritmo == "PARADAS_INTERMEDIAS":
            # Agrega 2 minutos por cada 2 km de tramo intermedio
            v = velocidad if velocidad > 5.0 else 18.0
            paradas = int(viaje.distancia_km // 2)
            eta_min = int(round((viaje.distancia_km / v) * 60)) + (paradas * 2)
        else:
            raise ValueError(f"Algoritmo de ETA no soportado: {tipo_algoritmo}")

        # 5. Emisión manual de eventos (Olor: notificaciones 'a mano' sin Observer)
        self.eventos.append(f"pasajero:bus_{viaje.bus.id_bus}:ETA_{eta_min}_min")
        self.eventos.append(f"control:flota:bus_{viaje.bus.id_bus}:lat_{lat:.5f}:lon_{lon:.5f}")

        # 6. Despacho directo a servicio externo
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
            "latitud": lat,
            "longitud": lon,
            "algoritmo": tipo_algoritmo
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
