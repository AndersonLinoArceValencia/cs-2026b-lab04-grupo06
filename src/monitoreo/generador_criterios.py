"""Generador de criterios de aceptación detrás del puerto IProveedorLLM (Laboratorio 09, E6).

La plantilla del prompt se carga por versión desde prompts/criterios/prompts/ y la salida del modelo se
valida contra el JSON Schema (capa 3 de la defensa): si no cumple el contrato, se rechaza y nunca se
muestra "tal cual".
"""
import json
import pathlib

from jsonschema import ValidationError, validate

from src.monitoreo.ia import IProveedorLLM

RAIZ = pathlib.Path(__file__).resolve().parents[2] / "prompts" / "criterios"
ESQUEMA = json.loads((RAIZ / "asserts" / "esquema.json").read_text(encoding="utf-8"))


class SalidaInvalida(Exception):
    """La respuesta del LLM no cumple el contrato: se descarta y se registra."""


class GeneradorCriterios:
    def __init__(self, proveedor: IProveedorLLM, version: str = "v3.1"):
        self._proveedor = proveedor
        self._plantilla = (RAIZ / "prompts" / f"{version}.txt").read_text(encoding="utf-8")
        self.version = version

    def generar(self, id_historia: str, historia: str) -> dict:
        prompt = self._plantilla.replace("{{id}}", id_historia).replace("{{historia}}", historia)
        texto = self._proveedor.generar_explicacion(prompt).texto
        try:
            criterios = json.loads(texto)
            validate(criterios, ESQUEMA)
        except (json.JSONDecodeError, ValidationError) as e:
            raise SalidaInvalida(f"{self.version}/{id_historia}: {e}") from e
        return criterios
