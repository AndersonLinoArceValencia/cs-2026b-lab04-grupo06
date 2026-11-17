"""Graba las respuestas de un asistente (Claude Code en modo no interactivo) para cada caso.

Uso: python record.py <carpeta_tarea> <version> [id ...]
Cada respuesta se guarda tal cual en <carpeta_tarea>/grabaciones/<version>/<id>.txt (sin editar).
"""
import os
import pathlib
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

import yaml

tarea = pathlib.Path(sys.argv[1])
version = sys.argv[2]
ids = sys.argv[3:]
carpeta_prompts = tarea / "prompts"
if not (carpeta_prompts / f"{version}.txt").exists():  # seguridad reutiliza los prompts de criterios
    carpeta_prompts = tarea.parent / "criterios" / "prompts"
plantilla = (carpeta_prompts / f"{version}.txt").read_text(encoding="utf-8")
casos = yaml.safe_load((tarea / "casos" / "historias.yaml").read_text(encoding="utf-8"))
destino = tarea / "grabaciones" / version
if os.environ.get("GRABACION_EXTRA"):  # p. ej. "corrida2": guarda en grabaciones/no_determinismo/<corrida>/<version>
    destino = tarea / "grabaciones" / "no_determinismo" / os.environ["GRABACION_EXTRA"] / version
destino.mkdir(parents=True, exist_ok=True)


def grabar(caso):
    v = caso["vars"]
    prompt = plantilla
    for clave, valor in v.items():
        prompt = prompt.replace("{{" + clave + "}}", str(valor))
    # carpeta vacía y sin herramientas: el asistente solo ve el prompt
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(
            ["claude", "-p", "--tools", "", "--no-session-persistence", "--model", "sonnet",
             "--disable-slash-commands"],
            input=prompt, capture_output=True, text=True, encoding="utf-8", cwd=d, timeout=300,
        )
    (destino / f"{v['id']}.txt").write_text(r.stdout.strip() + "\n", encoding="utf-8")
    print(version, v["id"], len(r.stdout), flush=True)


seleccion = [c for c in casos if not ids or c["vars"]["id"] in ids]
with ThreadPoolExecutor(4) as ex:
    list(ex.map(grabar, seleccion))
