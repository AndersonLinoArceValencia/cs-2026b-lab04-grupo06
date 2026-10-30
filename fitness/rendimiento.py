"""
fitness/rendimiento.py
Núcleo de simulación de rendimiento (cola M/G/c) para RutaSIT Arequipa.
Evalúa el escenario QA-01: 50,000 consultas de tiempo de llegada en hora punta (lambda = 15..50 req/s)
con 4 workers y diferentes combinaciones de tácticas de diseño.
"""

import heapq
import random
import statistics
import matplotlib.pyplot as plt


def bd_sin_indice(rnd: random.Random) -> float:
    """Consulta de llegada escaneando tablas de posiciones y rutas (media ~75 ms)."""
    return rnd.lognormvariate(-2.6, 0.45)


def bd_con_indice(rnd: random.Random) -> float:
    """Consulta con índice compuesto (linea_id, parada_id) (media ~18 ms)."""
    return rnd.lognormvariate(-4.0, 0.35)


def con_cache(servicio_bd, hit_rate: float = 0.85):
    """
    Táctica: Maintain copies of data (Caché en memoria con TTL de 10s).
    Si hay acierto (hit), respuesta en ~2 ms. En caso de fallo (miss), consulta BD.
    """
    def _servicio(rnd: random.Random) -> float:
        if rnd.random() < hit_rate:
            return rnd.uniform(0.001, 0.003)
        return servicio_bd(rnd)
    return _servicio


def simular(lam: float, workers: int, servicio, segundos: float = 120, semilla: int = 42):
    """Simula una cola M/G/c con llegadas Poisson y tiempos de servicio dados."""
    rnd = random.Random(semilla)
    t = 0.0
    llegadas = []
    while t < segundos:
        t += rnd.expovariate(lam)
        llegadas.append(t)

    libres = [0.0] * workers
    heapq.heapify(libres)
    respuestas = []

    for llegada in llegadas:
        libre = heapq.heappop(libres)
        inicio = max(llegada, libre)
        fin = inicio + servicio(rnd)
        heapq.heappush(libres, fin)
        respuestas.append((fin - llegada) * 1000.0)  # Convertir a ms

    respuestas.sort()
    n = len(respuestas)
    p = lambda q: respuestas[int(q * (n - 1))] if n > 0 else 0.0

    return {
        "n": n,
        "p50": p(0.50),
        "p95": p(0.95),
        "p99": p(0.99),
        "media": statistics.mean(respuestas) if n > 0 else 0.0,
        "max": respuestas[-1] if n > 0 else 0.0
    }


def generar_grafico_comparativo(ruta_salida: str = "fitness/simulacion_p95.png"):
    """Genera gráfico comparativo de p95 vs tasa de llegada y sensibilidad de caché."""
    lambdas = [5, 10, 15, 20, 25, 30, 35, 40]
    
    # 1. Sin tácticas (BD sin índice, 4 workers)
    p95_sin = []
    for l in lambdas:
        r = simular(lam=l, workers=4, servicio=bd_sin_indice, segundos=90)
        p95_sin.append(r["p95"])

    # 2. Solo Índice (4 workers)
    p95_indice = []
    for l in lambdas:
        r = simular(lam=l, workers=4, servicio=bd_con_indice, segundos=90)
        p95_indice.append(r["p95"])

    # 3. Índice + Caché (hit rate 85%, 4 workers)
    p95_cache = []
    for l in lambdas:
        r = simular(lam=l, workers=4, servicio=con_cache(bd_con_indice, 0.85), segundos=90)
        p95_cache.append(r["p95"])

    # 4. Escalar a 8 workers sin caché (doble costo)
    p95_8workers = []
    for l in lambdas:
        r = simular(lam=l, workers=8, servicio=bd_con_indice, segundos=90)
        p95_8workers.append(r["p95"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Panel izquierdo: Comparativa de tácticas
    ax1.plot(lambdas, p95_sin, 'r-o', label="Sin tácticas (4 workers)")
    ax1.plot(lambdas, p95_8workers, 'orange', linestyle='--', marker='s', label="Escalar a 8 workers (sin caché)")
    ax1.plot(lambdas, p95_indice, 'b-^', label="Táctica: Solo Índice (4 workers)")
    ax1.plot(lambdas, p95_cache, 'g-d', linewidth=2.5, label="Táctica: Índice + Caché (4 workers)")
    ax1.axhline(y=150, color='darkred', linestyle=':', label="Presupuesto QA-01 (150 ms)")
    ax1.set_yscale('log')
    ax1.set_xlabel('Tasa de llegada λ (req/s)')
    ax1.set_ylabel('Latencia p95 (ms, escala log)')
    ax1.set_title('RutaSIT: Rendimiento p95 según Tácticas')
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    ax1.legend(loc='upper left', fontsize=9)

    # Panel derecho: Sensibilidad a la tasa de aciertos de caché (a 30 req/s)
    hit_rates = [0.10, 0.30, 0.50, 0.70, 0.80, 0.85, 0.90, 0.95]
    p95_sensibilidad = []
    for hr in hit_rates:
        r = simular(lam=30, workers=4, servicio=con_cache(bd_con_indice, hr), segundos=90)
        p95_sensibilidad.append(r["p95"])

    ax2.plot([hr * 100 for hr in hit_rates], p95_sensibilidad, 'm-o', linewidth=2)
    ax2.axhline(y=150, color='darkred', linestyle=':', label="Límite QA-01 (150 ms)")
    ax2.set_xlabel('Tasa de aciertos de caché (%)')
    ax2.set_ylabel('Latencia p95 (ms)')
    ax2.set_title('Punto de Sensibilidad: Hit Rate de Caché (λ=30 req/s)')
    ax2.grid(True, ls="--", alpha=0.5)
    ax2.legend(loc='upper right', fontsize=9)

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=200)
    plt.close()
    print(f"Gráfico guardado en: {ruta_salida}")


if __name__ == "__main__":
    print("=== Simulación RutaSIT Arequipa (λ = 30 req/s, 4 workers) ===")
    sin = simular(lam=30, workers=4, servicio=bd_sin_indice)
    print(f"Sin tácticas:               p50={sin['p50']:.1f}ms, p95={sin['p95']:.1f}ms, media={sin['media']:.1f}ms")

    ind = simular(lam=30, workers=4, servicio=bd_con_indice)
    print(f"Solo índice:                p50={ind['p50']:.1f}ms, p95={ind['p95']:.1f}ms, media={ind['media']:.1f}ms")

    cache = simular(lam=30, workers=4, servicio=con_cache(bd_con_indice, 0.85))
    print(f"Índice + Caché (85% hit):   p50={cache['p50']:.1f}ms, p95={cache['p95']:.1f}ms, media={cache['media']:.1f}ms")

    w8 = simular(lam=30, workers=8, servicio=bd_con_indice)
    print(f"Escalar a 8 workers:        p50={w8['p50']:.1f}ms, p95={w8['p95']:.1f}ms, media={w8['media']:.1f}ms")

    generar_grafico_comparativo()
