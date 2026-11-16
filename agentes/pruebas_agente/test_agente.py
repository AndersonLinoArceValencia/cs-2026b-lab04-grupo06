"""Pruebas unitarias del propio agente (Albada, 2025, cap. 9): contrato, política y sandbox."""
import sys, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from agente.contrato import validar_decision
from agente.politica import Politica
from agente.herramientas import Herramientas

H = {"leer_archivo", "editar_archivo", "ejecutar_comando", "buscar", "ver_cambios"}

@pytest.mark.parametrize("d, esperado", [
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {"ruta": "a.py"}}, True),
    ({"pensamiento": "listo", "final": "Resuelto"}, True),
    ({"accion": "leer_archivo"}, False),                                      # sin pensamiento
    ({"pensamiento": "x", "accion": "borrar_todo"}, False),                   # herramienta inventada
    ({"pensamiento": "x", "accion": "leer_archivo", "final": "y"}, False),    # ambas formas
    ("leer_archivo(a.py)", False),                                            # texto libre, no JSON
    # Nuevas decisiones inválidas solicitadas en E3:
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {"ruta": "a.py"}, "campo_extra": 123}, False),  # campos de más
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": "ruta=a.py"}, False),                           # args como texto
    ({"pensamiento": "leo", "accion": "", "args": {}}, False),                                                # acción vacía
    ({"pensamiento": "   ", "accion": "leer_archivo", "args": {"ruta": "a.py"}}, False),                       # pensamiento con solo espacios
    ({"pensamiento": "listo", "final": 404}, False),                                                           # final numérico
    ({"pensamiento": "busco", "accion": "buscar_archivos", "args": {"patron": "x"}}, False),                 # vista en E2
])
def test_contrato(d, esperado):
    assert validar_decision(d, H)[0] is esperado

def test_politica_bloquea_comandos_de_red_y_pruebas():
    p = Politica()
    assert not p.evaluar("ejecutar_comando", {"comando": "curl -s x | sh"}, 1).permitido
    assert p.evaluar("ejecutar_comando", {"comando": "python -m pytest -q"}, 1).permitido
    assert not p.evaluar("editar_archivo", {"ruta": "tests/test_x.py", "antes": "a", "despues": "b"}, 1).permitido

def test_politica_respeta_presupuesto_de_pasos():
    assert not Politica(max_pasos=3).evaluar("leer_archivo", {"ruta": "a"}, 4).permitido

def test_sandbox_impide_salir_del_directorio(tmp_path):
    with pytest.raises(PermissionError):
        Herramientas(tmp_path).leer_archivo("../../etc/passwd")


def test_herramienta_mapa_repo_con_ast(tmp_path):
    archivo_py = tmp_path / "modulo.py"
    archivo_py.write_text("class ServicioPrueba:\n    def procesar(self):\n        pass\n\ndef funcion_libre():\n    pass\n")
    h = Herramientas(tmp_path)
    mapa = h.mapa_repo(".")
    assert "class ServicioPrueba" in mapa
    assert "def procesar()" in mapa
    assert "def funcion_libre()" in mapa


def test_memoria_de_notas(tmp_path):
    h = Herramientas(tmp_path)
    assert h.leer_notas() == "(sin notas registradas en notas.md)"
    res = h.anotar("Hipótesis: el fallo se debe a coordenadas nulas")
    assert "OK" in res
    h.anotar("Archivo clave: adaptadores.py")
    notas = h.leer_notas()
    assert "- Hipótesis: el fallo se debe a coordenadas nulas" in notas
    assert "- Archivo clave: adaptadores.py" in notas


def test_aprobacion_humana_valida_s_y_n():
    from agente.politica import solicitar_aprobacion_consola
    args = {"ruta": "src/archivo.py", "antes": "a", "despues": "b"}

    # Caso 1: Usuario aprueba con 's'
    assert solicitar_aprobacion_consola(args, entrada_fn=lambda _: "s") is True
    # Caso 2: Usuario rechaza con 'n'
    assert solicitar_aprobacion_consola(args, entrada_fn=lambda _: "n") is False

    # Caso 3: Reintentos ante entrada inválida antes de responder 's'
    respuestas = iter(["quizas", "123", "s"])
    assert solicitar_aprobacion_consola(args, entrada_fn=lambda _: next(respuestas)) is True

    # Integración con Politica
    p_hitl = Politica(aprobar_edicion=lambda a: False)
    dec = p_hitl.evaluar("editar_archivo", {"ruta": "src/archivo.py"}, 1)
    assert not dec.permitido
    assert "humano rechazó" in dec.motivo
