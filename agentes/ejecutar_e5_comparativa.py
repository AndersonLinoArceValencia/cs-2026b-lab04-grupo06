"""Comparativa E5: Agente único frente a Actor-Crítico en ISSUE-02."""
import pathlib
import shutil
import json
import sys

RAIZ = pathlib.Path(__file__).parent
sys.path.insert(0, str(RAIZ))

from agente.nucleo import Agente
from agente.herramientas import Herramientas
from agente.modelos import ModeloGrabado
from agente.politica import Politica

# -------------------------------------------------------------
# 1. EJECUCIÓN CON AGENTE ÚNICO
# -------------------------------------------------------------
print("======================================================")
print("EJECUTANDO VARIANTE 1: AGENTE ÚNICO (ISSUE-02)")
print("======================================================")
shutil.rmtree(RAIZ / "trabajo_unico", ignore_errors=True)
shutil.copytree(RAIZ / "trabajo_original", RAIZ / "trabajo_unico")
h_unico = Herramientas(RAIZ / "trabajo_unico")

traza_unico = RAIZ / "trazas" / "agente_unico_issue2.jsonl"
agente_unico = Agente(
    "agente_unico",
    ModeloGrabado(str(RAIZ / "trayectorias" / "ejecutor_issue2_unico.json")),
    h_unico,
    Politica(max_pasos=12),
    "Resuelve ISSUE-02.md en el repositorio de RutaSIT Arequipa: corregir falsos positivos de desvío en curvas.",
    str(traza_unico)
)
res_unico = agente_unico.ejecutar()
ctx_unico = len(json.dumps(agente_unico.historial, ensure_ascii=False))

ev_unico = [json.loads(l) for l in open(traza_unico, encoding="utf-8")]
acc_permitidas_u = sum(1 for e in ev_unico if e["tipo"] == "accion" and not e["bloqueada"])
acc_bloqueadas_u = sum(1 for e in ev_unico if e["tipo"] == "accion" and e["bloqueada"])

print(f"Resultado Agente Único:\n{res_unico}")
print(f"Rondas: 1 | Acciones permitidas: {acc_permitidas_u} | Bloqueadas: {acc_bloqueadas_u} | Contexto final: {ctx_unico} chars")

# -------------------------------------------------------------
# 2. EJECUCIÓN CON ORQUESTADOR ACTOR-CRÍTICO
# -------------------------------------------------------------
print("\n======================================================")
print("EJECUTANDO VARIANTE 2: ORQUESTADOR ACTOR-CRÍTICO (ISSUE-02)")
print("======================================================")
shutil.rmtree(RAIZ / "trabajo", ignore_errors=True)
shutil.copytree(RAIZ / "trabajo_original", RAIZ / "trabajo")
h_multi = Herramientas(RAIZ / "trabajo")

# Planificador
planificador = Agente(
    "planificador",
    ModeloGrabado(str(RAIZ / "trayectorias" / "planificador.json")),
    h_multi,
    Politica(herramientas_permitidas=set(), max_pasos=2),
    "Planifica cómo resolver ISSUE-02.md en el repositorio de RutaSIT Arequipa.",
    str(RAIZ / "trazas" / "planificador.jsonl")
)
plan = planificador.ejecutar()
print(f"\nPLANIFICADOR:\n{plan}\n")

agentes_multi, retro = [planificador], ""
MAX_RONDAS = 2

for ronda in range(1, MAX_RONDAS + 1):
    def tray(nombre, r): return f"trayectorias/{nombre}{'' if r == 1 else f'_r{r}'}.json"
    ejecutor = Agente(
        "ejecutor",
        ModeloGrabado(str(RAIZ / tray("ejecutor", ronda))),
        h_multi,
        Politica(max_pasos=12),
        f"Resuelve ISSUE-02.md siguiendo este plan:\n{plan}\n{retro}Herramientas: {h_multi.catalogo()}",
        str(RAIZ / f"trazas/ejecutor{'' if ronda == 1 else f'_r{ronda}'}.jsonl")
    )
    resumen = ejecutor.ejecutar()
    revisor = Agente(
        "revisor",
        ModeloGrabado(str(RAIZ / tray("revisor", ronda))),
        h_multi,
        Politica(herramientas_permitidas={"ver_cambios", "leer_archivo", "buscar", "ejecutar_pruebas"}, max_pasos=8),
        f"Revisa el cambio del ejecutor. Responde APROBADO... o CAMBIOS SOLICITADOS...\nResumen:\n{resumen}",
        str(RAIZ / f"trazas/revisor{'' if ronda == 1 else f'_r{ronda}'}.jsonl")
    )
    veredicto = revisor.ejecutar()
    agentes_multi += [ejecutor, revisor]
    print(f"--- RONDA {ronda}\nEJECUTOR: {resumen}\nREVISOR: {veredicto}\n")
    if not veredicto.startswith("CAMBIOS SOLICITADOS"):
        break
    retro = f"El revisor solicitó cambios:\n{veredicto}\n"

ctx_multi_total = sum(len(json.dumps(a.historial, ensure_ascii=False)) for a in agentes_multi)
ev_multi_total = []
for n in ["planificador", "ejecutor", "revisor", "ejecutor_r2", "revisor_r2"]:
    f = RAIZ / "trazas" / f"{n}.jsonl"
    if f.exists():
        ev_multi_total += [json.loads(l) for l in open(f, encoding="utf-8")]

acc_permitidas_m = sum(1 for e in ev_multi_total if e["tipo"] == "accion" and not e["bloqueada"])
acc_bloqueadas_m = sum(1 for e in ev_multi_total if e["tipo"] == "accion" and e["bloqueada"])

# Diagrama Mermaid de la trayectoria multiagente completa
from agente.traza import a_mermaid
ev_mermaid = []
for n in ["planificador", "ejecutor", "revisor", "ejecutor_r2", "revisor_r2"]:
    f = RAIZ / "trazas" / f"{n}.jsonl"
    if f.exists():
        r = int(n.split("_r")[1]) if "_r" in n else 1
        ev_mermaid += [dict(json.loads(l), ronda=r) for l in open(f, encoding="utf-8")]

(RAIZ / "trazas" / "trayectoria.mmd").write_text(a_mermaid(ev_mermaid), encoding="utf-8")

print("======================================================")
print("TABLA COMPARATIVA E5: AGENTE ÚNICO VS. ACTOR-CRÍTICO")
print("======================================================")
print(f"| Métrica | Agente Único | Actor-Crítico (Orquestado) |")
print(f"| :--- | :--- | :--- |")
print(f"| Rondas totales | 1 | {ronda} |")
print(f"| Acciones ejecutadas (permitidas) | {acc_permitidas_u} | {acc_permitidas_m} |")
print(f"| Acciones bloqueadas | {acc_bloqueadas_u} | {acc_bloqueadas_m} |")
print(f"| Contexto acumulado total | {ctx_unico} caracteres | {ctx_multi_total} caracteres |")
print(f"| ¿Revisor detectó fallas ocultas? | No (sin revisor) | Sí: División por cero (ZeroDivisionError) y rutas de 1 waypoint |")
