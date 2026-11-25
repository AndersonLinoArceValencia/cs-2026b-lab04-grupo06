"""E6: latencia por método (traza final) y costo de contexto por herramienta (v1 vs v3)."""

import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "cliente"))
from costo_catalogo import costo  # noqa: E402
from traza_mcp import cargar, metricas  # noqa: E402


def main():
    m = metricas(cargar(RAIZ / "trazas/mcp_trafico_v3.jsonl"))
    metodos = list(m["latencia_ms"])
    medias = [sum(v) / len(v) for v in m["latencia_ms"].values()]
    v1 = costo(RAIZ / "trazas/mcp_trafico_v1.jsonl")
    v3 = costo(RAIZ / "trazas/mcp_trafico_v3.jsonl")
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.2))
    barras = a.bar(metodos, medias, color=["#888888", "#2f6db5", "#2f6db5", "#2e8b57"])
    a.set_yscale("log")
    a.set_ylim(1, max(medias) * 6)
    a.set_ylabel("Latencia media (ms, escala log)")
    a.set_title("Latencia por método JSON-RPC (stdio)")
    for r, v, n in zip(barras, medias, m["latencia_ms"].values(), strict=True):
        etiqueta = f"{v:.1f} ms\n({len(n)})"
        a.text(r.get_x() + r.get_width() / 2, v * 1.15, etiqueta, ha="center", fontsize=8)
    nombres = list(v1)
    y = range(len(nombres))
    for desp, datos, nombre, color in ((0.2, v1, "v1", "#c0392b"), (-0.2, v3, "v3", "#2e8b57")):
        etiqueta = f"{nombre} ({sum(datos.values())} tokens)"
        b.barh([i + desp for i in y], [datos[n] for n in nombres], 0.4, label=etiqueta, color=color)
    b.set_yticks(list(y), nombres)
    b.set_xlabel("Tokens aproximados (caracteres / 4)")
    b.set_title("Contexto que ocupa cada herramienta")
    b.legend()
    fig.tight_layout()
    fig.savefig(RAIZ / "img/metricas_mcp.png", dpi=150)


if __name__ == "__main__":
    main()
