"""Auditor básico de servidores MCP: revisa el catálogo ANTES de conectarlo a un host.
Uso: python agentes/mcp/cliente/auditar.py <servidor.py>
(código de salida 1 si hay hallazgos altos)

Reglas del recurso del laboratorio + dos reglas nuevas del grupo 06 (E7):
  R5  herramienta de escritura sin destructiveHint explícito.
  R6  parámetro de texto sin maxLength en una herramienta de escritura (permite volcar datos).
"""

import asyncio
import re
import sys

from mcp import Client, StdioServerParameters

REGLAS = [  # (severidad, patrón en la descripción, explicación)
    (
        "ALTA",
        r"<\s*important\s*>|ignora|ignore (all|previous)"
        r"|no (le )?(menciones|digas)|do not (tell|mention)",
        "instrucciones ocultas dirigidas al modelo",
    ),
    (
        "ALTA",
        r"\.env\b|id_rsa|\.ssh|credencial|password|contraseña|token|api[_ ]?key",
        "pide secretos o credenciales",
    ),
    ("ALTA", r"curl |wget |\| *sh\b|https?://", "comandos o URL externas en la descripción"),
    (
        "MEDIA",
        r"(lee|read).{0,40}(archivo|file|recurso|resource)",
        "pide leer datos ajenos a su función",
    ),
]
PARAMS_SOSPECHOSOS = {"contexto", "context", "notas", "notes", "extra", "metadata", "debug"}


def _reglas_descripcion(t) -> list[tuple[str, str, str]]:
    desc = t.description or ""
    hallazgos = [
        (sev, t.name, motivo) for sev, patron, motivo in REGLAS if re.search(patron, desc, re.I)
    ]
    if len(desc) > 400:
        hallazgos.append(("BAJA", t.name, f"descripción muy larga ({len(desc)} caracteres)"))
    return hallazgos


def _reglas_parametros(t) -> list[tuple[str, str, str]]:
    props = t.input_schema.get("properties", {})
    motivo = "parámetro genérico '{}' que podría usarse para filtrar datos"
    return [("MEDIA", t.name, motivo.format(p)) for p in sorted(set(props) & PARAMS_SOSPECHOSOS)]


def _es_texto_libre(esquema: dict) -> bool:
    return esquema.get("type") == "string" and not {"maxLength", "enum"} & set(esquema)


def _reglas_escritura(t) -> list[tuple[str, str, str]]:
    """R5 y R6 (nuevas, grupo 06): solo aplican a herramientas que escriben."""
    a = t.annotations
    if a is None:
        return [("BAJA", t.name, "sin anotaciones (¿solo lectura? ¿destructiva?)")]
    if a.read_only_hint:
        return []
    hallazgos = []
    if a.destructive_hint is None:  # R5: sin la pista, el host debe asumir lo peor
        hallazgos.append(("MEDIA", t.name, "escritura sin destructiveHint explícito"))
    for nombre, esquema in t.input_schema.get("properties", {}).items():
        if _es_texto_libre(esquema):  # R6: texto sin límite permite volcar contexto o secretos
            hallazgos.append(
                ("MEDIA", t.name, f"texto libre '{nombre}' sin maxLength en una escritura")
            )
    return hallazgos


def revisar_herramienta(t) -> list[tuple[str, str, str]]:
    """Aplica todas las reglas a una herramienta del catálogo (función pura, fácil de probar)."""
    return _reglas_descripcion(t) + _reglas_parametros(t) + _reglas_escritura(t)


async def auditar(ruta):
    hallazgos = []
    async with Client(StdioServerParameters(command=sys.executable, args=[ruta])) as c:
        for t in (await c.list_tools()).tools:
            hallazgos += revisar_herramienta(t)
        print(f"Servidor: {c.server_info.name}")
    for h in hallazgos or [("OK", "-", "sin hallazgos")]:
        print(f"  [{h[0]:<5}] {h[1]:<22} {h[2]}")
    return any(h[0] == "ALTA" for h in hallazgos)


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(auditar(sys.argv[1])) else 0)
