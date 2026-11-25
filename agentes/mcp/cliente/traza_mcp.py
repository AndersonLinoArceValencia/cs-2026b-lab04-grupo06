"""Convierte el tráfico JSON-RPC capturado por el espía en un diagrama de secuencia Mermaid
y en una tabla de métricas (mensajes, métodos, errores, latencia)."""

import collections
import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def cargar(archivo=RAIZ / "trazas/mcp_trafico.jsonl"):
    return [json.loads(linea) for linea in open(archivo, encoding="utf-8")]


def _peticion(m: dict, aprobar) -> list[str]:
    params = m.get("params") or {}
    nombre = params.get("name") or params.get("uri") or ""
    lineas = [f"    A->>U: ¿apruebas {nombre}?", "    U-->>A: sí"] if nombre in aprobar else []
    return lineas + [f"    A->>S: {m['method']} {nombre}".rstrip()]


def _respuesta(m: dict, metodo: str | None) -> str:
    r = m.get("result", {})
    if "error" in m or r.get("isError"):
        return "    S--xA: error (isError=true)"
    if metodo == "server/discover":
        return f"    S-->>A: versiones {', '.join(r.get('supportedVersions', []))} + capacidades"
    if "tools" in r:
        return f"    S-->>A: {len(r['tools'])} herramientas con esquema"
    return "    S-->>A: resultado (resultType=complete)"


def a_mermaid(eventos, aprobar=("reportar_desvio",)) -> str:
    lineas = [
        "sequenceDiagram",
        "    autonumber",
        "    actor U as Humano",
        "    participant A as Agente (host MCP)",
        "    participant S as Servidor MCP rutasit",
    ]
    pendientes = {}
    for e in eventos:
        m = e["msg"]
        if e["dir"] == "host->servidor" and "method" in m:
            pendientes[m.get("id")] = m["method"]
            lineas += _peticion(m, aprobar)
        elif e["dir"] == "servidor->host" and "id" in m:
            lineas.append(_respuesta(m, pendientes.get(m["id"])))
    return "\n".join(lineas)


def metricas(eventos) -> dict:
    envios = {
        e["msg"]["id"]: e for e in eventos if e["dir"] == "host->servidor" and "id" in e["msg"]
    }
    lat = collections.defaultdict(list)
    errores = 0
    for e in eventos:
        m = e["msg"]
        if e["dir"] == "servidor->host" and m.get("id") in envios:
            ida = envios[m["id"]]
            lat[ida["msg"]["method"]].append(round((e["t"] - ida["t"]) * 1000, 1))
            errores += bool(m.get("result", {}).get("isError") or "error" in m)
    return {
        "mensajes": len(eventos),
        "errores": errores,
        "latencia_ms": dict(lat),
        "bytes": sum(len(json.dumps(e["msg"])) for e in eventos),
    }


if __name__ == "__main__":
    ev = cargar()
    (RAIZ / "trazas/mcp_trafico.mmd").write_text(a_mermaid(ev), encoding="utf-8")
    print(json.dumps(metricas(ev), ensure_ascii=False, indent=1))
