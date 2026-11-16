"""Ejecutor del Ejercicio E4: Agente con herramienta mapa_repo (AST) y memoria de notas resolviendo ISSUE-03."""
import pathlib
import shutil
import sys
import json

RAIZ = pathlib.Path(__file__).parent
sys.path.insert(0, str(RAIZ))

from agente.nucleo import Agente
from agente.herramientas import Herramientas
from agente.modelos import ModeloGrabado, ModeloInteractivo
from agente.politica import Politica

# Configuración del sandbox de trabajo
trabajo_dir = RAIZ / "trabajo"
origen_dir = RAIZ / "trabajo_original"
shutil.rmtree(trabajo_dir, ignore_errors=True)
shutil.copytree(origen_dir, trabajo_dir)

(RAIZ / "trazas").mkdir(exist_ok=True)
h = Herramientas(trabajo_dir)

trayectoria_path = RAIZ / "trayectorias" / "ejecutor_issue3.json"
traza_path = RAIZ / "trazas" / "ejecutor_issue3.jsonl"

if "--interactivo" in sys.argv:
    modelo = ModeloInteractivo(str(trayectoria_path))
else:
    modelo = ModeloGrabado(str(trayectoria_path))

objetivo = (
    "Resuelve ISSUE-03.md en el repositorio de RutaSIT Arequipa:\n"
    "Corregir GPSOperadorAAdapter en src/monitoreo/adaptadores.py para que cuando una trama "
    "tenga coordenadas nulas (lat=None o lon=None), eleve ValueError con mensaje descriptivo "
    "en vez de propagar datos corruptos.\n"
    "Utiliza la herramienta mapa_repo() para explorar la arquitectura y la memoria anotar() "
    "para registrar tus hipótesis sin saturar el contexto.\n"
    f"Herramientas disponibles: {h.catalogo()}"
)

politica = Politica(max_pasos=15)
agente = Agente("ejecutor", modelo, h, politica, objetivo, str(traza_path))

print("=== INICIANDO AGENTE REACT CON AST Y MEMORIA DE NOTAS (E4: ISSUE-03) ===")
resumen = agente.ejecutar()
print(f"\nRESULTADO FINAL:\n{resumen}\n")

eventos = [dict(json.loads(line), ronda=1) for line in open(traza_path, encoding="utf-8")]
from agente.traza import metricas
print("=== MÉTRICAS DE LA TRAZA (E4) ===")
print(json.dumps(metricas(eventos), ensure_ascii=False, indent=2))

caracteres_contexto = len(json.dumps(agente.historial, ensure_ascii=False))
print(f"\nContexto final acumulado: {caracteres_contexto} caracteres (~{caracteres_contexto // 4} tokens)")
print(f"Traza guardada en: {traza_path}")
