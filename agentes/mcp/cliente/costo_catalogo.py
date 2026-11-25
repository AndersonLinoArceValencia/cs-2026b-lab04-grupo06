"""E6: costo de contexto del catálogo (≈ caracteres / 4 tokens) a partir de la traza.
Uso: python agentes/mcp/cliente/costo_catalogo.py [traza.jsonl ...]"""

import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def costo(traza: pathlib.Path) -> dict:
    for linea in open(traza, encoding="utf-8"):
        m = json.loads(linea)["msg"]
        tools = (m.get("result") or {}).get("tools")
        if tools:
            return {t["name"]: round(len(json.dumps(t, ensure_ascii=False)) / 4) for t in tools}
    return {}


if __name__ == "__main__":
    for arg in sys.argv[1:] or [RAIZ / "trazas/mcp_trafico.jsonl"]:
        c = costo(pathlib.Path(arg))
        print(f"{pathlib.Path(arg).name}: total ≈ {sum(c.values())} tokens")
        for nombre, tokens in c.items():
            print(f"  {nombre:<18} ≈ {tokens} tokens")
