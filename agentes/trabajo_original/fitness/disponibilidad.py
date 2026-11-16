"""
fitness/disponibilidad.py
Simulación Monte Carlo de resiliencia y disponibilidad para RutaSIT Arequipa (QA-03).
Evalúa la ingesta de telemetría ante pérdidas de cobertura 4G y caídas temporales de proveedores GPS.
Compara:
  1. Reintentos simples sincrónicos
  2. Circuit Breaker sin persistencia
  3. Circuit Breaker + Outbox transaccional (Táctica seleccionada)
"""

import random
import matplotlib.pyplot as plt


def simular(estrategia: str = "breaker_outbox", eventos_totales: int = 1200, semilla: int = 42):
    """
    Simula el envío de telemetría de 1200 buses durante una ventana con fallas de red.
    Falla transitoria (jitter de señal): 8% de probabilidad de timeout.
    Caída general del enlace (ventana de falla): 15% de los eventos ocurren en zona sin señal.
    """
    rnd = random.Random(semilla)
    
    llamadas_totales = 0
    llamadas_en_caida = 0
    eventos_perdidos = 0
    eventos_procesados = 0
    eventos_encolados_outbox = 0
    
    # Estado del Circuit Breaker
    estado_breaker = "CERRADO"
    fallas_consecutivas = 0
    umbral_falla = 3
    tiempo_recuperacion = 10  # eventos hasta intentar semiabierto
    contador_abierto = 0

    for i in range(eventos_totales):
        # Simular zona sin cobertura celular en la ruta
        en_zona_caida = (300 <= i < 500)  # Ventana de 200 eventos en blackout de red
        falla_transitoria = (rnd.random() < 0.08)
        proveedor_disponible = not (en_zona_caida or falla_transitoria)

        if estrategia == "reintentos":
            # Reintentos sincrónicos agresivos (hasta 3 intentos)
            exito = False
            for intento in range(3):
                llamadas_totales += 1
                if en_zona_caida:
                    llamadas_en_caida += 1
                if proveedor_disponible:
                    exito = True
                    break
            if exito:
                eventos_procesados += 1
            else:
                eventos_perdidos += 1

        elif estrategia == "breaker_simple":
            # Circuit Breaker sin almacenamiento diferido
            if estado_breaker == "ABIERTO":
                contador_abierto += 1
                if contador_abierto >= tiempo_recuperacion:
                    estado_breaker = "SEMIABIERTO"
                else:
                    eventos_perdidos += 1
                    continue

            llamadas_totales += 1
            if en_zona_caida:
                llamadas_en_caida += 1

            if proveedor_disponible:
                eventos_procesados += 1
                fallas_consecutivas = 0
                estado_breaker = "CERRADO"
            else:
                eventos_perdidos += 1
                fallas_consecutivas += 1
                if fallas_consecutivas >= umbral_falla:
                    estado_breaker = "ABIERTO"
                    contador_abierto = 0

        elif estrategia in ("breaker", "breaker_outbox"):
            # Circuit Breaker + Outbox diferido
            if estado_breaker == "ABIERTO":
                contador_abierto += 1
                eventos_encolados_outbox += 1  # No se pierde: va al outbox
                if contador_abierto >= tiempo_recuperacion:
                    estado_breaker = "SEMIABIERTO"
                continue

            llamadas_totales += 1
            if en_zona_caida:
                llamadas_en_caida += 1

            if proveedor_disponible:
                eventos_procesados += 1
                fallas_consecutivas = 0
                estado_breaker = "CERRADO"
            else:
                # Al fallar, se protege en la cola outbox
                eventos_encolados_outbox += 1
                fallas_consecutivas += 1
                if fallas_consecutivas >= umbral_falla:
                    estado_breaker = "ABIERTO"
                    contador_abierto = 0

    if estrategia in ("breaker", "breaker_outbox"):
        eventos_perdidos = 0  # Garantía del Outbox: 0 pérdidas
        eventos_procesados += eventos_encolados_outbox

    return {
        "estrategia": estrategia,
        "eventos_totales": eventos_totales,
        "perdidos": eventos_perdidos,
        "procesados": eventos_procesados,
        "llamadas_en_caida": llamadas_en_caida,
        "llamadas_totales": llamadas_totales,
        "encolados_outbox": eventos_encolados_outbox
    }


def generar_grafico_disponibilidad(ruta_salida: str = "fitness/simulacion_disponibilidad.png"):
    r_reintentos = simular("reintentos")
    r_breaker = simular("breaker_simple")
    r_outbox = simular("breaker_outbox")

    estrategias = ["Reintentos\nSincrónicos", "Circuit Breaker\n(sin cola)", "Circuit Breaker\n+ Outbox (Elegida)"]
    perdidos = [r_reintentos["perdidos"], r_breaker["perdidos"], r_outbox["perdidos"]]
    llamadas_caida = [r_reintentos["llamadas_en_caida"], r_breaker["llamadas_en_caida"], r_outbox["llamadas_en_caida"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Gráfico 1: Eventos de telemetría perdidos
    bars1 = ax1.bar(estrategias, perdidos, color=['#D9534F', '#F0AD4E', '#5CB85C'], width=0.55)
    ax1.set_ylabel('Telemetrías Perdidas (de 1200)')
    ax1.set_title('Eventos de Telemetría Perdidos ante Falla (QA-03)')
    ax1.grid(True, axis='y', ls='--', alpha=0.5)
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 5, f"{int(yval)}", ha='center', fontweight='bold')

    # Gráfico 2: Sobrecarga al proveedor caído (llamadas inútiles)
    bars2 = ax2.bar(estrategias, llamadas_caida, color=['#D9534F', '#5BC0DE', '#5CB85C'], width=0.55)
    ax2.set_ylabel('Llamadas enviadas durante la caída')
    ax2.set_title('Protección del Canal: Llamadas en Caída')
    ax2.grid(True, axis='y', ls='--', alpha=0.5)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 8, f"{int(yval)}", ha='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=200)
    plt.close()
    print(f"Gráfico de disponibilidad guardado en: {ruta_salida}")


if __name__ == "__main__":
    print("=== Simulación de Disponibilidad Monte Carlo: RutaSIT ===")
    for e in ["reintentos", "breaker_simple", "breaker_outbox"]:
        res = simular(e)
        print(f"[{res['estrategia']:<18}] Perdidos: {res['perdidos']:<4} | Llamadas en caída: {res['llamadas_en_caida']:<4} | Outbox: {res['encolados_outbox']:<4}")
    generar_grafico_disponibilidad()
