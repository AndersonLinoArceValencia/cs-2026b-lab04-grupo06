"""Pruebas unitarias que demuestran la aplicación y beneficios de cada patrón de diseño (E2–E5).

E2: Strategy + Adapter + Factory
- Demostración del Principio Abierto/Cerrado (OCP): extensión de estrategias y adaptadores sin modificar el servicio.
- Aislamiento de adaptadores sin reglas de negocio.
"""

import pytest
from src.monitoreo.servicio import ServicioMonitoreoSIT, Bus, Paradero, Viaje
from src.monitoreo.estrategias import IEstrategiaETA
from src.monitoreo.adaptadores import IProveedorGPS, DatosTelemetria


def crear_viaje(id_viaje="V-999", id_bus="B-99", operador="OPERADOR_A", distancia_km=6.0):
    bus = Bus(id_bus=id_bus, placa="V1A-999", operador=operador)
    paradero = Paradero(id_paradero="P-10", nombre="Av. Dolores", latitud=-16.4200, longitud=-71.5200)
    return Viaje(id_viaje=id_viaje, bus=bus, paradero_destino=paradero, estado="EN_RUTA", distancia_km=distancia_km)


# ==============================================================================
# Pruebas E2: Strategy + Adapter + Factory (Principio Abierto / Cerrado)
# ==============================================================================

def test_open_closed_nueva_estrategia_sin_modificar_servicio():
    """Demuestra OCP: se añade una nueva estrategia de cálculo de ETA (Lluvia Torrencial)

    sin modificar una sola línea de ServicioMonitoreoSIT.
    """
    class ETALluviaTorrencialStrategy(IEstrategiaETA):
        """Nueva estrategia climática: velocidad reducida al 50% y demora por pavimento resbaladizo."""
        def calcular_eta(self, distancia_km: float, velocidad_kmh: float) -> int:
            v_reducida = (velocidad_kmh * 0.5) if velocidad_kmh > 5.0 else 10.0
            return int(round((distancia_km / v_reducida) * 60)) + 8

    servicio = ServicioMonitoreoSIT()
    # 1. Registrar nueva estrategia en tiempo de ejecución
    servicio.fabrica_eta.registrar("LLUVIA_TORRENCIAL", ETALluviaTorrencialStrategy)

    # 2. Ejecutar con viaje de 6 km a 30 km/h (velocidad reducida a 15 km/h -> 24 min + 8 min = 32 min)
    viaje = crear_viaje(distancia_km=6.0)
    resultado = servicio.consultar_tiempo_llegada(viaje, tipo_algoritmo="LLUVIA_TORRENCIAL")

    assert resultado["eta_minutos"] == 32
    assert resultado["algoritmo"] == "LLUVIA_TORRENCIAL"


def test_open_closed_nuevo_operador_gps_sin_modificar_servicio():
    """Demuestra OCP: se añade un nuevo consorcio (Operador C) con su propio SDK y adaptador

    sin alterar el código fuente del servicio principal.
    """
    class GPSOperadorCSDKSimulado:
        """SDK hipotético de un tercer operador que envía velocidad en metros por segundo."""
        def get_fleet_telemetry(self, code: str):
            return {"device": code, "latitude": -16.4300, "longitude": -71.5400, "speed_mps": 10.0}

    class GPSOperadorCAdapter(IProveedorGPS):
        """Adaptador que transforma los datos del Operador C al modelo canónico."""
        def __init__(self, sdk):
            self.sdk = sdk

        def obtener_posicion(self, id_bus: str) -> DatosTelemetria:
            raw = self.sdk.get_fleet_telemetry(id_bus)
            return DatosTelemetria(
                latitud=raw["latitude"],
                longitud=raw["longitude"],
                velocidad_kmh=raw["speed_mps"] * 3.6,  # 10 m/s = 36 km/h
                id_unidad=id_bus
            )

    servicio = ServicioMonitoreoSIT()
    # 1. Registrar nuevo operador en la fábrica
    sdk_c = GPSOperadorCSDKSimulado()
    servicio.fabrica_gps.registrar("OPERADOR_C", GPSOperadorCAdapter(sdk_c))

    # 2. Consultar viaje con bus de Operador C (6 km a 36 km/h = 10 min)
    viaje_c = crear_viaje(id_bus="B-303", operador="OPERADOR_C", distancia_km=6.0)
    resultado = servicio.consultar_tiempo_llegada(viaje_c, tipo_algoritmo="LINEAL")

    assert resultado["eta_minutos"] == 10
    assert resultado["operador"] == "OPERADOR_C"
    assert resultado["latitud"] == -16.4300
    assert resultado["longitud"] == -71.5400


def test_adaptadores_convierten_correctamente_sin_reglas_de_negocio():
    """Verifica que los adaptadores se limitan a transformar datos de red y formato

    sin alterar estados de entidades ni reglas de negocio.
    """
    from src.monitoreo.adaptadores import GPSOperadorAAdapter, GPSOperadorBAdapter
    from src.monitoreo.externos import GPSOperadorASDK, GPSOperadorBSDK

    adapter_a = GPSOperadorAAdapter(GPSOperadorASDK())
    adapter_b = GPSOperadorBAdapter(GPSOperadorBSDK())

    telemetria_a = adapter_a.obtener_posicion("BUS-01")
    telemetria_b = adapter_b.obtener_posicion("202")

    assert isinstance(telemetria_a, DatosTelemetria)
    assert isinstance(telemetria_b, DatosTelemetria)
    assert telemetria_a.velocidad_kmh == 30.0
    assert round(telemetria_b.velocidad_kmh, 1) == 30.0
