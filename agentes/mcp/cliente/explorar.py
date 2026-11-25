"""Host MCP mínimo: descubre las capacidades del servidor rutasit y prueba cada primitiva.
Uso: python agentes/mcp/cliente/explorar.py   (pasa por el espía y deja la traza JSON-RPC)"""

import asyncio
import json
import pathlib
import sys

from mcp import Client, StdioServerParameters
from mcp.types import Implementation

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SERVIDOR = StdioServerParameters(
    command=sys.executable,
    args=[str(RAIZ / "cliente/espia.py"), str(RAIZ / "servidor_mcp/rutasit_mcp.py")],
)


def texto(resultado) -> str:
    return " ".join(getattr(c, "text", "") for c in resultado.content)


async def main():
    (RAIZ / "trazas/mcp_trafico.jsonl").unlink(missing_ok=True)
    async with Client(
        SERVIDOR, client_info=Implementation(name="explorador-lab11", version="1.0")
    ) as c:
        print(f"Servidor: {c.server_info.name} | protocolo {c.protocol_version}")
        print("\nHERRAMIENTAS (las elige el modelo):")
        for h in (await c.list_tools()).tools:
            a = h.annotations
            tipo = "solo lectura" if a and a.read_only_hint else "ESCRITURA"
            print(f"  - {h.name}({', '.join(h.input_schema.get('properties', {}))})  [{tipo}]")
        print("\nRECURSOS (los elige la aplicación):")
        for r in (await c.list_resources()).resources:
            print(f"  - {r.uri}  {r.title}")
        for t in (await c.list_resource_templates()).resource_templates:
            print(f"  - {t.uri_template}  {t.title} (plantilla)")
        print("\nPROMPTS (los elige el usuario):")
        for p in (await c.list_prompts()).prompts:
            print(f"  - {p.name}({', '.join(a.name for a in p.arguments or [])})")

        print("\nPRUEBAS DE USO:")
        r = await c.call_tool(
            "tiempo_llegada",
            {"id_bus": "B-011", "id_paradero": "P-104", "hora_actual": "2026-11-25T07:30"},
        )
        print("  tiempo_llegada →", json.dumps(r.structured_content, ensure_ascii=False))
        r = await c.call_tool("buses_en_ruta", {"id_ruta": "R-09"})
        print("  buses_en_ruta(R-09) → is_error =", r.is_error, "|", texto(r)[:90])
        r = await c.read_resource("rutasit://adr/001")
        print("  read_resource(adr/001) →", r.contents[0].text.splitlines()[0][:80])
        r = await c.get_prompt(
            "aviso_usuarios", {"id_ruta": "R-01", "motivo": "obras en Puente Grau"}
        )
        print("  get_prompt(aviso_usuarios) →", r.messages[0].content.text[:70], "…")


asyncio.run(main())
