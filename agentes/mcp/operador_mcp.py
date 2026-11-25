"""E4: el agente del Lab 10, sin cambios en su núcleo, usando el servidor rutasit por MCP.
Uso: python agentes/mcp/operador_mcp.py   (pasa por el espía y deja la traza JSON-RPC)"""

import pathlib
import shutil
import sys

from mcp import StdioServerParameters

MCP_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(MCP_DIR.parent))  # carpeta agentes/ (framework del Lab 10)
from agente.herramientas_mcp import HerramientasMCP  # noqa: E402
from agente.modelos import ModeloGrabado  # noqa: E402
from agente.nucleo import Agente  # noqa: E402
from agente.politica import Politica  # noqa: E402

shutil.rmtree(MCP_DIR / "reportes", ignore_errors=True)
(MCP_DIR / "trazas/mcp_trafico.jsonl").unlink(missing_ok=True)

h = HerramientasMCP(
    StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_DIR / "cliente/espia.py"), str(MCP_DIR / "servidor_mcp/rutasit_mcp.py")],
    )
)
print("Herramientas descubiertas por MCP:", ", ".join(h.catalogo()))
print("Requieren aprobación (según anotaciones):", h.herramientas_de_escritura())


def aprobador(accion, args):  # humano en el circuito
    print(f"\n[APROBACIÓN] {accion}({args['id_bus']}): {args['descripcion'][:60]!r}...")
    respuesta = (
        input("¿Aprueba el registro? (s/n): ").strip().lower() if sys.stdin.isatty() else "s"
    )
    print(f"  → respuesta del operador humano: {respuesta}")
    return respuesta == "s"


politica = Politica(
    herramientas_permitidas=set(h.catalogo()),
    max_pasos=8,
    requieren_aprobacion=h.herramientas_de_escritura(),
)
politica.aprobar = aprobador
agente = Agente(
    "operador",
    ModeloGrabado(MCP_DIR / "trayectorias/operador.json"),
    h,
    politica,
    "El centro de control pregunta: ¿qué buses circulan en la ruta R-01, cuánto tarda el siguiente "
    "en llegar a Plaza de Armas a las 07:30 del 25/11/2026 y hay alguno desviado? Si hay un desvío "
    f"confirmado, repórtalo.\nHerramientas: {h.catalogo()}",
    MCP_DIR / "trazas/operador.jsonl",
)
print("\nRESPUESTA:\n" + agente.ejecutar())
for e in agente.eventos:
    if e["tipo"] == "accion":
        print(f"  paso {e['paso']}: {e['accion']:<17} {e['estado']:<11} {e['observacion'][:78]!r}")
h.cerrar()
