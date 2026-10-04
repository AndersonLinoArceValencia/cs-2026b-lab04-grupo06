"""
Gráfico de la matriz de decisión ponderada de RutaSIT Arequipa (E2, paso 5).

Los pesos y puntajes son los mismos de docs/architecture/matriz-decision.md.
Si cambian, se editan aquí y se vuelve a ejecutar el script.

Requisitos:
    pip install matplotlib

Ejecutar desde la raíz del repositorio:
    python docs/architecture/diagramas/matriz.py

Genera docs/architecture/diagramas/img/matriz-decision.png
"""

from pathlib import Path

import matplotlib.pyplot as plt

criterios = [
    ("Rendimiento en tiempo real", 0.25),
    ("Tiempo de entrega", 0.25),
    ("Costo en 1 VPS", 0.20),
    ("Simplicidad operativa", 0.15),
    ("Modificabilidad", 0.15),
]

# Puntaje de 1 a 5 en el mismo orden de "criterios"
alternativas = {
    "A. Monolito en capas": [3, 4, 4, 5, 2],
    "B. Microservicios": [4, 1, 1, 1, 5],
    "C. Monolito modular asíncrono": [5, 4, 5, 4, 4],
}

colores = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"]

pesos = [p for _, p in criterios]
assert abs(sum(pesos) - 1.0) < 1e-9, "Los pesos deben sumar 100 %"

nombres = list(alternativas)
totales = [sum(p * s for p, s in zip(pesos, alternativas[n])) for n in nombres]

fig, ax = plt.subplots(figsize=(10, 4.8))

# Barras apiladas: cada tramo es el aporte (peso x puntaje) de un criterio
izquierda = [0.0] * len(nombres)
for i, (criterio, peso) in enumerate(criterios):
    aportes = [peso * alternativas[n][i] for n in nombres]
    ax.barh(nombres, aportes, left=izquierda, color=colores[i],
            edgecolor="white", label=f"{criterio} ({peso:.0%})")
    izquierda = [a + b for a, b in zip(izquierda, aportes)]

for y, total in enumerate(totales):
    ax.text(total + 0.05, y, f"{total:.2f}", va="center", fontsize=12, fontweight="bold")

ax.set_xlim(0, 5.3)
ax.set_xlabel("Total ponderado (máximo 5)")
ax.set_title("RutaSIT Arequipa: matriz de decisión ponderada")
ax.invert_yaxis()
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=False, fontsize=9)

ganador = nombres[totales.index(max(totales))]
ax.get_yticklabels()[nombres.index(ganador)].set_fontweight("bold")

salida = Path("docs/architecture/diagramas/img/matriz-decision.png")
salida.parent.mkdir(parents=True, exist_ok=True)
fig.tight_layout()
fig.savefig(salida, dpi=200, bbox_inches="tight")
print(f"Ganador: {ganador} ({max(totales):.2f}). Imagen en {salida}")
