"""Proveedor de promptfoo que devuelve respuestas GRABADAS (fixtures).

Las respuestas se obtuvieron con un asistente de IA (prompts/record.py) y se guardaron en
<tarea>/grabaciones/<version>/<id>.txt. Así la evaluación es reproducible y no requiere clave de API.
Se ejecuta desde la carpeta de la tarea (prompts/criterios, prompts/pruebas o prompts/seguridad).
Para evaluar un modelo real, reemplace este proveedor en promptfooconfig.yaml.
"""
import pathlib
import re

BASE = pathlib.Path.cwd() / "grabaciones"


def call_api(prompt, options, context):
    etiqueta = context["prompt"]["label"]
    version = re.search(r"prompts[\\/](v[\w.]+)\.txt", etiqueta).group(1)
    caso = context["vars"]["id"]
    archivo = BASE / version / f"{caso}.txt"
    if not archivo.exists():
        return {"error": f"Sin grabación para {version}/{caso}"}
    return {"output": archivo.read_text(encoding="utf-8").strip()}
