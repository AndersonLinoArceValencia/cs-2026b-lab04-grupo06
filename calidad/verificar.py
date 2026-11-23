import ast
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
APROBADAS_PATH = RAIZ / "calidad" / "dependencias_aprobadas.txt"
PATRON_SECRETO = re.compile(
    r"(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]{8,}['\"]",
    re.IGNORECASE,
)


def cargar_aprobadas() -> set[str]:
    lineas = APROBADAS_PATH.read_text(encoding="utf-8").splitlines()
    return {x.strip() for x in lineas if x.strip() and not x.strip().startswith("#")}


def ruta_de_modulo(nombre_modulo: str) -> Path:
    spec = importlib.util.find_spec(nombre_modulo)
    if spec and spec.origin:
        return Path(spec.origin)
    return RAIZ / (nombre_modulo.replace(".", "/") + ".py")


def verificar_dependencias(ruta: Path) -> tuple[bool, str]:
    aprobadas = cargar_aprobadas()
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    imports = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            imports.add(nodo.module.split(".")[0])
    no_aprobadas = sorted(imports - aprobadas)
    if no_aprobadas:
        return False, "no aprobadas: " + ", ".join(no_aprobadas)
    return True, f"{len(imports)} importaciones aprobadas"


def verificar_pruebas_y_cobertura(nombre_modulo: str, archivo_pruebas: str) -> tuple[tuple[bool, str], tuple[bool, str]]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(RAIZ)
    env["MODULO"] = nombre_modulo
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        archivo_pruebas,
        f"--cov={nombre_modulo}",
        "--cov-report=term-missing",
        "-q",
    ]
    res = subprocess.run(cmd, cwd=RAIZ, env=env, capture_output=True, text=True)
    salida = res.stdout + "\n" + res.stderr
    m_pass = re.search(r"(\d+) passed", salida)
    m_fail = re.search(r"(\d+) failed", salida)
    m_err = re.search(r"(\d+) error", salida)
    n_pass = int(m_pass.group(1)) if m_pass else 0
    n_fail = (int(m_fail.group(1)) if m_fail else 0) + (int(m_err.group(1)) if m_err else 0)
    ok_tests = res.returncode == 0 and n_pass > 0
    msg_tests = f"{n_pass} pasan, {n_fail} fallan"

    m_cov = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", salida)
    cov = int(m_cov.group(1)) if m_cov else 0
    ok_cov = cov >= 85
    msg_cov = f"{cov} % (minimo 85 %)"
    return (ok_tests, msg_tests), (ok_cov, msg_cov)


def verificar_ruff(ruta: Path) -> tuple[bool, str]:
    cmd = [sys.executable, "-m", "ruff", "check", str(ruta)]
    res = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True)
    if res.returncode == 0:
        return True, "0 hallazgos"
    m = re.search(r"Found (\d+) error", res.stdout)
    cnt = m.group(1) if m else "1+"
    return False, f"{cnt} hallazgo(s)"


def verificar_bandit(ruta: Path) -> tuple[bool, str]:
    cmd = [sys.executable, "-m", "bandit", "-q", "-f", "txt", str(ruta)]
    res = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True)
    if res.returncode == 0:
        return True, "sin hallazgos"
    codigos = re.findall(r"Issue: \[(B\d+):[^\]]+\].*?Severity: (\w+)", res.stdout, re.S)
    resumen = ", ".join(f"{c} ({s.upper()})" for c, s in codigos) or "hallazgos detectados"
    return False, resumen


def verificar_radon(ruta: Path) -> tuple[bool, str]:
    cmd = [sys.executable, "-m", "radon", "cc", "-s", str(ruta)]
    res = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True)
    bloques = re.findall(r" - ([A-F]) \((\d+)\)", res.stdout)
    if not bloques:
        return True, "maximo A (CC=1)"
    peor_letra, peor_cc = max(bloques, key=lambda x: int(x[1]))
    ok = peor_letra in ("A", "B")
    return ok, f"maximo {peor_letra} (CC={peor_cc})"


def verificar_secretos(ruta: Path) -> tuple[bool, str]:
    texto = ruta.read_text(encoding="utf-8")
    hallazgos = PATRON_SECRETO.findall(texto)
    if hallazgos:
        return False, f"{len(hallazgos)} posible(s) secreto(s)"
    return True, "0 posibles secretos"


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python calidad/verificar.py <modulo> [archivo_pruebas]")
        return 1
    modulo = sys.argv[1]
    pruebas = sys.argv[2] if len(sys.argv) > 2 else "tests/test_hu12_llegada.py"
    ruta = ruta_de_modulo(modulo)
    if not ruta.exists():
        print(f"Modulo no encontrado: {ruta}")
        return 1

    print(f"Compuertas de calidad · {modulo}")
    resultados = []
    resultados.append(("Dependencias aprobadas", *verificar_dependencias(ruta)))
    r_tests, r_cov = verificar_pruebas_y_cobertura(modulo, pruebas)
    resultados.append(("Pruebas (HU-12)", *r_tests))
    resultados.append(("Cobertura", *r_cov))
    resultados.append(("Ruff (estilo y errores)", *verificar_ruff(ruta)))
    resultados.append(("Bandit (seguridad)", *verificar_bandit(ruta)))
    resultados.append(("Radon (complejidad)", *verificar_radon(ruta)))
    resultados.append(("Secretos en el codigo", *verificar_secretos(ruta)))

    aprobadas = 0
    for nombre, ok, detalle in resultados:
        etiqueta = "[PASA]" if ok else "[FALLA]"
        if ok:
            aprobadas += 1
        print(f"{etiqueta:7} {nombre:26} {detalle}")

    print(f"Resultado: {aprobadas}/{len(resultados)} compuertas aprobadas")
    return 0 if aprobadas == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
