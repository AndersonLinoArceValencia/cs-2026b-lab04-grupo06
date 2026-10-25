"""Pruebas de caracterización para el flujo crítico de RutaSIT (HU-01: Consultar tiempo de llegada).

Siguiendo el Paso 2 de la guía:
- Prueban únicamente comportamiento observable (retornos, excepciones, eventos emitidos).
- No acopladas a la estructura interna.
- Utilizan fixture parametrizado (inicia con 'src.monitoreo.antes.servicio' y en E2 sumará 'src.monitoreo.servicio').
- 11 casos de prueba cubriendo éxito, reintentos, algoritmos alternativos y errores límite.
"""

import importlib
import pytest
from src.monitoreo.externos import GPSOperadorASDK, GPSOperadorBSDK, ServicioWebPushExterno


@pytest.fixture(params=["src.monitoreo.antes.servicio", "src.monitoreo.servicio"])
def m(request):
    """Carga dinámicamente el módulo a probar: evalúa tanto la versión antes como la refactorizada."""
    return importlib.import_module(request.param)


def crear_viaje(m, id_viaje="V-101", id_bus="B-01", placa="V7A-100", operador="OPERADOR_A", estado="EN_RUTA", distancia_km=5.0):
    bus = m.Bus(id_bus=id_bus, placa=placa, operador=operador)
    paradero = m.Paradero(id_paradero="P-01", nombre="Plaza de Armas", latitud=-16.3988, longitud=-71.5369)
    return m.Viaje(id_viaje=id_viaje, bus=bus, paradero_destino=paradero, estado=estado, distancia_km=distancia_km)


# 1. Caso de éxito estándar con Operador A y algoritmo lineal
def test_exito_operador_a_algoritmo_lineal(m):
    servicio = m.ServicioMonitoreoSIT()
    viaje = crear_viaje(m, operador="OPERADOR_A", distancia_km=5.0)

    resultado = servicio.consultar_tiempo_llegada(viaje, tipo_algoritmo="LINEAL")

    # 5 km a 30 km/h = 10 minutos
    assert resultado["eta_minutos"] == 10
    assert resultado["estado"] == "EN_RUTA"
    assert resultado["operador"] == "OPERADOR_A"
    assert any("pasajero:bus_B-01:ETA_10_min" in e for e in servicio.eventos)
    assert any("control:flota:bus_B-01" in e for e in servicio.eventos)
    assert len(servicio.web_push.notificaciones_enviadas) == 1


# 2. Caso de éxito con Operador B (formato disímil en microgrados y cm/s)
def test_exito_operador_b_algoritmo_lineal(m):
    servicio = m.ServicioMonitoreoSIT()
    # id_bus numérico como string ("202")
    viaje = crear_viaje(m, id_bus="202", placa="V9B-200", operador="OPERADOR_B", distancia_km=5.0)

    resultado = servicio.consultar_tiempo_llegada(viaje, tipo_algoritmo="LINEAL")

    # 833 cm/s ~ 30 km/h -> 5 km toma 10 minutos
    assert resultado["eta_minutos"] == 10
    assert resultado["operador"] == "OPERADOR_B"
    assert round(resultado["latitud"], 4) == -16.4090
    assert round(resultado["longitud"], 4) == -71.5375


# 3. Algoritmo alternativo: Hora punta (congestión)
def test_algoritmo_hora_punta(m):
    servicio = m.ServicioMonitoreoSIT()
    viaje = crear_viaje(m, operador="OPERADOR_A", distancia_km=6.0)

    # 30 km/h * 0.6 = 18 km/h. 6 km a 18 km/h = 20 min + 4 min demora fija = 24 min
    resultado = servicio.consultar_tiempo_llegada(viaje, tipo_algoritmo="HORA_PUNTA")
    assert resultado["eta_minutos"] == 24
    assert resultado["algoritmo"] == "HORA_PUNTA"


# 4. Algoritmo alternativo: Paradas intermedias
def test_algoritmo_paradas_intermedias(m):
    servicio = m.ServicioMonitoreoSIT()
    viaje = crear_viaje(m, operador="OPERADOR_A", distancia_km=6.0)

    # 6 km a 30 km/h = 12 min. 6 // 2 = 3 paradas * 2 min = 6 min extra -> 18 min
    resultado = servicio.consultar_tiempo_llegada(viaje, tipo_algoritmo="PARADAS_INTERMEDIAS")
    assert resultado["eta_minutos"] == 18
    assert resultado["algoritmo"] == "PARADAS_INTERMEDIAS"


# 5. Reintento exitoso ante fallas temporales de GPS
def test_reintento_exitoso_tras_fallas_gps(m):
    gps_a = GPSOperadorASDK(fallas=2)  # Falla las 2 primeras veces con TimeoutError
    servicio = m.ServicioMonitoreoSIT(gps_a=gps_a)
    viaje = crear_viaje(m, operador="OPERADOR_A", distancia_km=5.0)

    resultado = servicio.consultar_tiempo_llegada(viaje)
    assert resultado["eta_minutos"] == 10
    assert gps_a.intentos == 3  # Tuvo éxito en el tercer intento


# 6. Agotamiento de reintentos ante falla persistente de GPS
def test_falla_tras_tres_timeouts_gps(m):
    gps_a = GPSOperadorASDK(fallas=3)  # Falla los 3 intentos
    servicio = m.ServicioMonitoreoSIT(gps_a=gps_a)
    viaje = crear_viaje(m, operador="OPERADOR_A")

    with pytest.raises(TimeoutError) as exc_info:
        servicio.consultar_tiempo_llegada(viaje)
    
    assert "tras 3 intentos" in str(exc_info.value)
    assert any("alerta:gps_timeout:B-01" in e for e in servicio.eventos)


# 7. Rechazo si el viaje no está en estado EN_RUTA
@pytest.mark.parametrize("estado_invalido,mensaje_esperado", [
    ("PROGRAMADO", "aún no inicia"),
    ("DETENIDO", "está DETENIDO"),
    ("DESVIADO", "está DESVIADO"),
    ("FINALIZADO", "ha FINALIZADO")
])
def test_error_viaje_no_en_ruta(m, estado_invalido, mensaje_esperado):
    servicio = m.ServicioMonitoreoSIT()
    viaje = crear_viaje(m, estado=estado_invalido)

    with pytest.raises(ValueError) as exc_info:
        servicio.consultar_tiempo_llegada(viaje)
    
    assert mensaje_esperado in str(exc_info.value)
    if estado_invalido in ("DETENIDO", "DESVIADO"):
        assert len(servicio.eventos) > 0  # Registra evento de contingencia o desvío


# 8. Rechazo si el estado del viaje es desconocido
def test_error_estado_desconocido(m):
    servicio = m.ServicioMonitoreoSIT()
    viaje = crear_viaje(m, estado="CANCELADO_SIN_REGISTRO")

    with pytest.raises(ValueError) as exc_info:
        servicio.consultar_tiempo_llegada(viaje)
    assert "no reconocido" in str(exc_info.value)


# 9. Validación de distancia mayor a cero
def test_error_distancia_invalida(m):
    servicio = m.ServicioMonitoreoSIT()
    viaje = crear_viaje(m, distancia_km=0.0)

    with pytest.raises(ValueError) as exc_info:
        servicio.consultar_tiempo_llegada(viaje)
    assert "mayor a 0 km" in str(exc_info.value)


# 10. Rechazo de operador o algoritmo no soportado
def test_error_operador_o_algoritmo_no_soportado(m):
    servicio = m.ServicioMonitoreoSIT()
    viaje_invalido = crear_viaje(m, operador="OPERADOR_DESCONOCIDO")

    with pytest.raises(ValueError) as exc_op:
        servicio.consultar_tiempo_llegada(viaje_invalido)
    assert "Operador GPS no soportado" in str(exc_op.value)

    viaje_valido = crear_viaje(m, operador="OPERADOR_A")
    with pytest.raises(ValueError) as exc_alg:
        servicio.consultar_tiempo_llegada(viaje_valido, tipo_algoritmo="MACHINE_LEARNING_V3")
    assert "Algoritmo de ETA no soportado" in str(exc_alg.value)


# 11. Explicación de motivos de retraso
def test_explicar_retraso_motivos(m):
    servicio = m.ServicioMonitoreoSIT()

    exp_normal = servicio.explicar_retraso("ninguno", 0)
    assert "itinerario normal" in exp_normal

    exp_trafico = servicio.explicar_retraso("fuerte congestión en Av. Ejército", 15)
    assert "congestión vehicular" in exp_trafico and "15 min" in exp_trafico

    exp_accidente = servicio.explicar_retraso("accidente leve en puente Grau", 20)
    assert "incidente vial" in exp_accidente and "20 min" in exp_accidente

    exp_desvio = servicio.explicar_retraso("desvío por obras de asfaltado", 12)
    assert "desvío temporal" in exp_desvio and "12 min" in exp_desvio
