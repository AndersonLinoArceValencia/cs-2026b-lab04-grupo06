"""Sistema multiagente con coordinación por gestor (Albada, 2025, cap. 8):
Planificador -> [Ejecutor (actor) <-> Revisor (crítico)] -> Humano.
Cada agente tiene su propia política (mínimo privilegio)."""
import json, shutil, pathlib
from agente.nucleo import Agente
from agente.herramientas import Herramientas
from agente.modelos import ModeloGrabado
from agente.politica import Politica

RAIZ = pathlib.Path(__file__).parent
MAX_RONDAS = 2                                                      # presupuesto del bucle actor-crítico
shutil.rmtree(RAIZ / "trabajo", ignore_errors=True)                 # cada ejecución parte del estado original
shutil.copytree(RAIZ / "trabajo_original", RAIZ / "trabajo")
(RAIZ / "trazas").mkdir(exist_ok=True)
h = Herramientas(RAIZ / "trabajo")

def trayectoria(nombre, ronda):                                     # ejecutor.json, ejecutor_r2.json, ...
    return f"trayectorias/{nombre}{'' if ronda == 1 else f'_r{ronda}'}.json"

planificador = Agente("planificador", ModeloGrabado("trayectorias/planificador.json"), h,
                      Politica(herramientas_permitidas=set(), max_pasos=2),
                      "Planifica cómo resolver ISSUE-27.md en el repositorio de AgroConecta.", "trazas/planificador.jsonl")
plan = planificador.ejecutar()
print(f"PLANIFICADOR:\n{plan}\n")
agentes, retro = [planificador], ""

for ronda in range(1, MAX_RONDAS + 1):
    ejecutor = Agente("ejecutor", ModeloGrabado(trayectoria("ejecutor", ronda)), h, Politica(max_pasos=12),
                      f"Resuelve ISSUE-27.md siguiendo este plan:\n{plan}\n{retro}Herramientas: {h.catalogo()}",
                      f"trazas/ejecutor{'' if ronda == 1 else f'_r{ronda}'}.jsonl")
    resumen = ejecutor.ejecutar()
    revisor = Agente("revisor", ModeloGrabado(trayectoria("revisor", ronda)), h,
                     Politica(herramientas_permitidas={"ver_cambios", "leer_archivo", "buscar", "ejecutar_pruebas"}, max_pasos=8),
                     f"Revisa el cambio del ejecutor. Responde APROBADO... o CAMBIOS SOLICITADOS...\nResumen:\n{resumen}",
                     f"trazas/revisor{'' if ronda == 1 else f'_r{ronda}'}.jsonl")
    veredicto = revisor.ejecutar()
    agentes += [ejecutor, revisor]
    print(f"--- RONDA {ronda}\nEJECUTOR: {resumen}\nREVISOR: {veredicto}\n")
    if not veredicto.startswith("CAMBIOS SOLICITADOS"):            # el crítico acepta: se pasa al humano
        break
    retro = f"El revisor solicitó cambios:\n{veredicto}\n"         # el crítico rechaza: nueva ronda

print(f"Rondas actor-crítico: {ronda} de {MAX_RONDAS}. Decisión final: HUMANO (aprobar o rechazar el PR).")
for a in agentes:
    n = len(json.dumps(a.historial, ensure_ascii=False))
    print(f"[{a.nombre}] contexto final: {n} caracteres (~{n // 4} tokens)")
