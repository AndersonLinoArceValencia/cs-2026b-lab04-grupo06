"""Ejecutor del Ejercicio E2: Agente ReAct resolviendo el ISSUE-01."""
import pathlib
import shutil
import sys
import json

# Asegurar importación de módulos del mini-framework
RAIZ = pathlib.Path(__file__).parent
sys.path.insert(0, str(RAIZ))

from agente.nucleo import Agente
from agente.herramientas import Herramientas
from agente.modelos import ModeloGrabado, ModeloInteractivo
from agente.politica import Politica

# 1. Configuración del sandbox de trabajo
trabajo_dir = RAIZ / "trabajo"
origen_dir = RAIZ / "trabajo_original"
shutil.rmtree(trabajo_dir, ignore_errors=True)
shutil.copytree(origen_dir, trabajo_dir)

(RAIZ / "trazas").mkdir(exist_ok=True)
h = Herramientas(trabajo_dir)

# 2. Selección del modelo (si se pasa --interactivo se activa ModeloInteractivo)
trayectoria_path = RAIZ / "trayectorias" / "ejecutor_issue1.json"
traza_path = RAIZ / "trazas" / "ejecutor.jsonl"

if "--interactivo" in sys.argv:
    modelo = ModeloInteractivo(str(trayectoria_path))
else:
    modelo = ModeloGrabado(str(trayectoria_path))

objetivo = (
    "Resuelve ISSUE-01.md en el repositorio de RutaSIT Arequipa:\n"
    "Corregir las estrategias de cálculo de ETA en src/monitoreo/estrategias.py para que "
    "cuando distancia_km <= 0.0 (el bus ya pasó o llegó al paradero), el ETA retorne 0 minutos "
    "y nunca valores negativos.\n"
    "Verifica con ejecutar_pruebas() que pasen las pruebas de tests/test_issue_01.py.\n"
    f"Herramientas disponibles: {h.catalogo()}"
)

politica = Politica(max_pasos=15)
agente = Agente("ejecutor", modelo, h, politica, objetivo, str(traza_path))

print("=== INICIANDO AGENTE REACT (E2: ISSUE-01) ===")
resumen = agente.ejecutar()
print(f"\nRESULTADO FINAL DEL AGENTE:\n{resumen}\n")

# 3. Métricas y generación de diagrama Mermaid
from agente.traza import a_mermaid, metricas

eventos = [dict(json.loads(line), ronda=1) for line in open(traza_path, encoding="utf-8")]
mmd_path = RAIZ / "trazas" / "trayectoria.mmd"
mmd_path.write_text(a_mermaid(eventos), encoding="utf-8")

print("=== MÉTRICAS DE LA TRAZA ===")
print(json.dumps(metricas(eventos), ensure_ascii=False, indent=2))
print(f"\nTraza guardada en: {traza_path}")
print(f"Diagrama Mermaid guardado en: {mmd_path}")
