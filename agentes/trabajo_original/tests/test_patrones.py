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


# ==============================================================================
# Pruebas E3: Patrón State para el ciclo de vida del Viaje
# ==============================================================================

def test_state_transiciones_validas_ciclo_completo():
    """Valida el ciclo de vida completo del viaje respetando estados-viaje.mmd:
    PROGRAMADO -> EN_RUTA -> DETENIDO -> EN_RUTA -> DESVIADO -> EN_RUTA -> FINALIZADO.
    """
    from src.monitoreo.estados import (
        ProgramadoState,
        EnRutaState,
        DetenidoState,
        DesviadoState,
        FinalizadoState,
    )

    viaje = crear_viaje()
    viaje.cambiar_a(ProgramadoState())
    assert viaje.estado == "PROGRAMADO"
    assert isinstance(viaje.estado_obj, ProgramadoState)

    # 1. Iniciar recorrido
    viaje.iniciar_recorrido()
    assert viaje.estado == "EN_RUTA"
    assert isinstance(viaje.estado_obj, EnRutaState)

    # 2. Registrar contingencia (detención)
    viaje.registrar_detencion("Tráfico pesado en Av. Cayma")
    assert viaje.estado == "DETENIDO"
    assert isinstance(viaje.estado_obj, DetenidoState)
    assert viaje.motivo_contingencia == "Tráfico pesado en Av. Cayma"

    # 3. Reanudar marcha
    viaje.reanudar_recorrido()
    assert viaje.estado == "EN_RUTA"
    assert viaje.motivo_contingencia is None

    # 4. Registrar desvío de ruta
    viaje.registrar_desvio("Obras de asfaltado en calle Mercaderes")
    assert viaje.estado == "DESVIADO"
    assert isinstance(viaje.estado_obj, DesviadoState)

    # 5. Retornar a la ruta
    viaje.retornar_a_ruta()
    assert viaje.estado == "EN_RUTA"

    # 6. Finalizar viaje
    viaje.finalizar_recorrido()
    assert viaje.estado == "FINALIZADO"
    assert isinstance(viaje.estado_obj, FinalizadoState)


def test_state_transicion_invalida_lanza_excepcion():
    """Verifica que transiciones prohibidas por la máquina de estados
    sean rechazadas por construcción mediante TransicionInvalidaError.
    """
    from src.monitoreo.estados import (
        ProgramadoState,
        FinalizadoState,
        TransicionInvalidaError,
    )

    viaje = crear_viaje()
    viaje.cambiar_a(ProgramadoState())

    # No se puede reanudar ni finalizar un viaje que todavía no inicia
    with pytest.raises(TransicionInvalidaError) as exc_info1:
        viaje.reanudar_recorrido()
    assert "No se puede reanudar recorrido desde el estado PROGRAMADO" in str(exc_info1.value)

    with pytest.raises(TransicionInvalidaError) as exc_info2:
        viaje.finalizar_recorrido()
    assert "No se puede finalizar recorrido desde el estado PROGRAMADO" in str(exc_info2.value)

    # Un viaje FINALIZADO es un estado terminal que prohíbe cualquier transición posterior
    viaje.cambiar_a(FinalizadoState())
    with pytest.raises(TransicionInvalidaError) as exc_info3:
        viaje.iniciar_recorrido()
    assert "No se puede iniciar recorrido desde el estado FINALIZADO" in str(exc_info3.value)

    with pytest.raises(TransicionInvalidaError) as exc_info4:
        viaje.registrar_detencion("Avería mecánica")
    assert "No se puede registrar detención desde el estado FINALIZADO" in str(exc_info4.value)


# ==============================================================================
# Pruebas E4: Patrones Observer y Decorator
# ==============================================================================

def test_observer_nuevo_suscriptor_sin_tocar_el_servicio():
    """Demuestra el patrón Observer: se añade un nuevo suscriptor de auditoría municipal

    que escucha eventos en tiempo real sin modificar ServicioMonitoreoSIT.
    """
    from src.monitoreo.eventos import ISuscriptor

    class AuditoriaMunicipalObserver(ISuscriptor):
        def __init__(self):
            self.bitacora = []

        def actualizar(self, tipo_evento: str, datos: dict) -> None:
            if tipo_evento == "ETA_CALCULADO":
                self.bitacora.append(
                    f"AUDITORIA: SIT monitoreó bus {datos['id_bus']} con ETA={datos['eta_minutos']}m"
                )

    servicio = ServicioMonitoreoSIT()
    auditor = AuditoriaMunicipalObserver()

    # 1. Suscripción dinámica
    servicio.publicador.suscribir("ETA_CALCULADO", auditor)

    # 2. Ejecutar flujo crítico
    viaje = crear_viaje(id_bus="B-555", distancia_km=5.0)
    servicio.consultar_tiempo_llegada(viaje)

    # 3. Comprobar que el observador recibió el evento
    assert len(auditor.bitacora) == 1
    assert "AUDITORIA: SIT monitoreó bus B-555 con ETA=10m" in auditor.bitacora[0]


def test_decorator_cache_evita_llamadas_repetidas():
    """Demuestra el patrón Decorator: CacheETADecorator memoriza cálculos idénticos

    reduciendo la carga computacional en consultas consecutivas.
    """
    from src.monitoreo.estrategias import ETALinealStrategy
    from src.monitoreo.decoradores import CacheETADecorator

    estrategia_base = ETALinealStrategy()
    cache_decorator = CacheETADecorator(estrategia_base)

    # Primera llamada: cálculo real (5 km a 30 km/h = 10 min)
    res1 = cache_decorator.calcular_eta(5.0, 30.0)
    assert res1 == 10
    assert cache_decorator.llamadas_reales == 1

    # Segunda y tercera llamada con los mismos argumentos: provienen de caché
    res2 = cache_decorator.calcular_eta(5.0, 30.0)
    res3 = cache_decorator.calcular_eta(5.0, 30.0)
    assert res2 == 10
    assert res3 == 10
    assert cache_decorator.llamadas_reales == 1  # No volvió a invocar la estrategia base

    # Argumentos distintos: provoca cómputo nuevo
    res4 = cache_decorator.calcular_eta(10.0, 30.0)
    assert res4 == 20
    assert cache_decorator.llamadas_reales == 2


def test_decorator_reintentos_gps_sobre_adaptador():
    """Demuestra el patrón Decorator: ReintentoGPSDecorator añade tolerancia a fallos

    sobre cualquier proveedor GPS sin modificar el código del adaptador.
    """
    from src.monitoreo.adaptadores import GPSOperadorAAdapter
    from src.monitoreo.externos import GPSOperadorASDK
    from src.monitoreo.decoradores import ReintentoGPSDecorator

    # SDK que falla las 2 primeras veces
    sdk_inestable = GPSOperadorASDK(fallas=2)
    adaptador_base = GPSOperadorAAdapter(sdk_inestable)
    decorador_reintentos = ReintentoGPSDecorator(adaptador_base, max_intentos=3)

    telemetria = decorador_reintentos.obtener_posicion("BUS-777")

    assert telemetria.id_unidad == "BUS-777"
    assert telemetria.velocidad_kmh == 30.0
    assert decorador_reintentos.intentos_realizados == 3


# ==============================================================================
# Pruebas E5: Componente de IA Aislado (Strategy/Adapter + Decorator + Guardrails)
# ==============================================================================

def test_ia_proveedor_mock_genera_explicacion_valida():
    """Valida la generación de explicaciones en lenguaje natural para el pasajero

    utilizando el adaptador simulado MockLLMAdapter (sin depender de API externa).
    """
    from src.monitoreo.ia import ServicioExplicacionIA, MockLLMAdapter

    servicio_ia = ServicioExplicacionIA(proveedor=MockLLMAdapter())

    # Retraso por congestión
    texto_trafico = servicio_ia.explicar_retraso("Congestión vehicular intensa en Av. Ejército", 15)
    assert "congestión vehicular" in texto_trafico
    assert "15 min" in texto_trafico

    # Sin retraso
    texto_normal = servicio_ia.explicar_retraso("Ninguno", 0)
    assert "itinerario normal" in texto_normal


def test_ia_cache_decorator_evita_llamadas_repetidas():
    """Valida el patrón Decorator: CacheIADecorator evita invocar al modelo

    ante peticiones idénticas de explicación de contingencias.
    """
    from src.monitoreo.ia import ServicioExplicacionIA, MockLLMAdapter, CacheIADecorator

    mock_llm = MockLLMAdapter()
    cache_llm = CacheIADecorator(mock_llm)
    servicio_ia = ServicioExplicacionIA(proveedor=cache_llm, usar_cache=False)

    # 1. Primera consulta: invoca al mock
    res1 = servicio_ia.explicar_retraso("Lluvia y congestión", 10)
    assert cache_llm.llamadas_reales == 1
    assert mock_llm.llamadas == 1

    # 2. Consultas subsecuentes con los mismos datos: resueltas desde caché
    res2 = servicio_ia.explicar_retraso("Lluvia y congestión", 10)
    res3 = servicio_ia.explicar_retraso("Lluvia y congestión", 10)
    assert res1 == res2 == res3
    assert cache_llm.llamadas_reales == 1
    assert mock_llm.llamadas == 1  # No hubo llamadas adicionales al LLM


def test_ia_guardrail_consistencia_bloquea_alucinaciones():
    """Valida Chain of Responsibility: GuardrailConsistenciaTelemetria bloquea respuestas

    del LLM que alucinan incidentes graves no respaldados por la telemetría real.
    """
    import pytest
    from src.monitoreo.ia import (
        ServicioExplicacionIA,
        MockLLMAdapter,
        ViolacionGuardrailError,
    )

    # Simulamos un LLM que alucina que el motor explotó cuando la telemetría solo reportó tráfico
    llm_alucinador = MockLLMAdapter(
        respuesta_forzada="Estimado pasajero: lamentamos informar que el motor de la unidad explotó."
    )
    servicio_ia = ServicioExplicacionIA(proveedor=llm_alucinador, usar_cache=False)

    with pytest.raises(ViolacionGuardrailError) as exc_info:
        servicio_ia.explicar_retraso("Tráfico denso en hora punta", 10)

    assert "Guardrail de Consistencia" in str(exc_info.value)
    assert "alucinó 'motor'" in str(exc_info.value)


def test_ia_guardrail_longitud_y_tono_bloquea_alarmismo():
    """Valida Chain of Responsibility: GuardrailLongitudYTono bloquea respuestas

    que exceden los 250 caracteres o emplean expresiones alarmistas.
    """
    import pytest
    from src.monitoreo.ia import (
        ServicioExplicacionIA,
        MockLLMAdapter,
        ViolacionGuardrailError,
    )

    # 1. Prueba de lenguaje alarmista
    llm_alarmista = MockLLMAdapter(
        respuesta_forzada="¡Alerta máxima! Se ha desatado una catástrofe en la avenida principal."
    )
    servicio_ia1 = ServicioExplicacionIA(proveedor=llm_alarmista, usar_cache=False)

    with pytest.raises(ViolacionGuardrailError) as exc_tono:
        servicio_ia1.explicar_retraso("Accidente menor", 15)
    assert "Guardrail de Tono" in str(exc_tono.value)

    # 2. Prueba de longitud excesiva (> 250 caracteres)
    texto_largo = "Información para pasajeros: " + ("texto de relleno explicativo muy largo " * 8)
    llm_verboso = MockLLMAdapter(respuesta_forzada=texto_largo)
    servicio_ia2 = ServicioExplicacionIA(proveedor=llm_verboso, usar_cache=False)

    with pytest.raises(ViolacionGuardrailError) as exc_len:
        servicio_ia2.explicar_retraso("Demora", 10)
    assert "Guardrail de Longitud" in str(exc_len.value)



