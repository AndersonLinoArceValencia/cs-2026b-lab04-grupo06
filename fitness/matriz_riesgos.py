"""
fitness/matriz_riesgos.py
Genera el gráfico de la matriz de probabilidad e impacto (ATAM-lite) para RutaSIT Arequipa.
"""

import matplotlib.pyplot as plt
import numpy as np


def generar_matriz_riesgos(ruta_salida: str = "fitness/matriz_riesgos.png"):
    fig, ax = plt.subplots(figsize=(7, 6))

    # Definir malla de fondo con gradiente de criticidad
    x = np.linspace(0.5, 5.5, 100)
    y = np.linspace(0.5, 5.5, 100)
    X, Y = np.meshgrid(x, y)
    Z = X * Y

    # Mapa de calor de riesgo
    cax = ax.imshow(Z, origin='lower', extent=[0.5, 5.5, 0.5, 5.5], cmap='YlOrRd', alpha=0.35, aspect='auto')

    # Líneas divisorias de zonas
    ax.axvline(x=3.5, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=3.5, color='gray', linestyle='--', alpha=0.5)

    # Hallazgos de RutaSIT
    puntos = [
        {"id": "S1", "nombre": "S1: Hit rate de caché", "p": 4.0, "i": 2.5, "color": "blue", "offset": (0.1, 0.1)},
        {"id": "T1", "nombre": "T1: Consistencia 10s", "p": 3.0, "i": 2.0, "color": "darkblue", "offset": (0.1, -0.2)},
        {"id": "R1", "nombre": "R1: Cache stampede", "p": 2.5, "i": 4.0, "color": "darkred", "offset": (0.1, 0.1)},
        {"id": "R2", "nombre": "R2: Apagón red 4G (Crítico)", "p": 4.5, "i": 4.5, "color": "red", "offset": (-1.8, 0.15)},
        {"id": "NR1", "nombre": "NR1: Aislamiento IA", "p": 1.5, "i": 1.5, "color": "green", "offset": (0.1, 0.1)},
        {"id": "R3", "nombre": "R3: Fuga multitenant", "p": 1.5, "i": 4.5, "color": "purple", "offset": (0.1, -0.25)},
    ]

    for pt in puntos:
        ax.scatter(pt["p"], pt["i"], color=pt["color"], s=120, edgecolors='black', linewidth=1.5, zorder=5)
        ax.text(pt["p"] + pt["offset"][0], pt["i"] + pt["offset"][1], pt["nombre"], fontsize=9, fontweight='bold', zorder=6)

    # Textos de zonas
    ax.text(1.2, 5.1, "ZONA MODERADA", fontsize=9, color='darkorange', fontweight='bold')
    ax.text(4.0, 5.1, "ZONA CRÍTICA (ALTO RIESGO)", fontsize=9, color='darkred', fontweight='bold')
    ax.text(1.2, 0.8, "ZONA ACEPTABLE", fontsize=9, color='darkgreen', fontweight='bold')

    ax.set_xlabel('Probabilidad de Ocurrencia (1 a 5)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Impacto Técnico / Operativo (1 a 5)', fontsize=10, fontweight='bold')
    ax.set_title('RutaSIT Arequipa: Matriz de Riesgos ATAM-lite', fontsize=12, fontweight='bold', pad=12)

    ax.set_xlim(0.8, 5.4)
    ax.set_ylim(0.8, 5.4)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=200)
    plt.close()
    print(f"Matriz de riesgos guardada en: {ruta_salida}")


if __name__ == "__main__":
    generar_matriz_riesgos()
