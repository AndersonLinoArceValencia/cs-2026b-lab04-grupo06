"""Reglas nuevas del auditor (E7) y adaptador del agente del Lab 10 con aprobación humana (E4)."""

import pathlib
import sys
from types import SimpleNamespace

from mcp import StdioServerParameters
from mcp.types import ToolAnnotations

MCP_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MCP_DIR / "cliente"))
sys.path.insert(0, str(MCP_DIR.parent))  # carpeta agentes/ (framework del Lab 10)
from auditar import revisar_herramienta  # noqa: E402
from agente.herramientas_mcp import HerramientasMCP  # noqa: E402
from agente.politica import Politica  # noqa: E402

ESCRITURA = ToolAnnotations(read_only_hint=False)


def herramienta(
    nombre="crear",
    desc="Crea un registro nuevo en la carpeta de reportes.",
    props=None,
    ann=ESCRITURA,
):
    return SimpleNamespace(
        name=nombre,
        description=desc,
        annotations=ann,
        input_schema={"type": "object", "properties": props or {}},
    )


def test_regla_nueva_escritura_sin_destructive_hint():
    motivos = [h[2] for h in revisar_herramienta(herramienta())]
    assert "escritura sin destructiveHint explícito" in motivos


def test_regla_nueva_texto_libre_sin_max_length_en_escritura():
    t = herramienta(
        props={
            "nota": {"type": "string"},
            "zona": {"type": "string", "enum": ["A", "B"]},
            "motivo": {"type": "string", "maxLength": 200},
        }
    )
    motivos = [h[2] for h in revisar_herramienta(t)]
    assert motivos.count("texto libre 'nota' sin maxLength en una escritura") == 1
    assert not any("'zona'" in m or "'motivo'" in m for m in motivos)


def test_lectura_no_dispara_reglas_de_escritura():
    t = herramienta(props={"q": {"type": "string"}}, ann=ToolAnnotations(read_only_hint=True))
    assert revisar_herramienta(t) == []


def test_adaptador_descubre_ejecuta_y_la_politica_exige_aprobacion():
    h = HerramientasMCP(
        StdioServerParameters(
            command=sys.executable, args=[str(MCP_DIR / "servidor_mcp/rutasit_mcp.py")]
        )
    )
    try:
        assert {"buses_en_ruta", "tiempo_llegada", "leer_recurso"} <= set(h.catalogo())
        assert '"minutos_eta": 15' in h.tiempo_llegada(
            id_bus="B-011", id_paradero="P-104", hora_actual="2026-11-25T07:30"
        )
        assert h.buses_en_ruta(id_ruta="R-09").startswith("ERROR")
        assert h.herramientas_de_escritura() == {"reportar_desvio"}
        p = Politica(
            herramientas_permitidas=set(h.catalogo()),
            requieren_aprobacion=h.herramientas_de_escritura(),
        )
        assert not p.evaluar("reportar_desvio", {"id_bus": "B-013"}, 1).permitido  # sin aprobador
        p.aprobar = lambda accion, args: True
        assert p.evaluar("reportar_desvio", {"id_bus": "B-013"}, 1).permitido
    finally:
        h.cerrar()
