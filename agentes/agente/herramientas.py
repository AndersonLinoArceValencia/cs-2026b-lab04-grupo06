"""Herramientas del agente. Cada una es una función pequeña, con descripción y parámetros explícitos.
Todas operan DENTRO del directorio de trabajo (sandbox)."""
import pathlib, subprocess, re


class Herramientas:
    def __init__(self, raiz: str):
        self.raiz = pathlib.Path(raiz).resolve()

    # --- utilidades ---
    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def catalogo(self) -> dict:
        """Descripción de las herramientas que se envía al modelo (como en un MCP server)."""
        return {
            "listar_archivos": "listar_archivos(carpeta='.'): lista los archivos .py y .md",
            "leer_archivo": "leer_archivo(ruta): devuelve el contenido con números de línea",
            "buscar": "buscar(patron): busca una expresión regular en los archivos .py",
            "mapa_repo": "mapa_repo(carpeta='.'): devuelve el mapa estructural con AST (clases, métodos y firmas) sin volcar todo el código",
            "anotar": "anotar(texto): guarda una hipótesis o nota de trabajo en notas.md",
            "leer_notas": "leer_notas(): devuelve las notas acumuladas en notas.md",
            "ejecutar_pruebas": "ejecutar_pruebas(): ejecuta pytest y devuelve el resumen",
            "editar_archivo": "editar_archivo(ruta, antes, despues): reemplaza un fragmento exacto (una sola vez)",
            "ver_cambios": "ver_cambios(): muestra el diff respecto de la versión original",
            "ejecutar_comando": "ejecutar_comando(comando): ejecuta un comando de shell (sujeto a la política)",
        }

    # --- herramientas ---
    def listar_archivos(self, carpeta="."):
        base = self._ruta(carpeta)
        return "\n".join(sorted(str(p.relative_to(self.raiz)) for p in base.rglob("*")
                                if p.suffix in (".py", ".md") and "__pycache__" not in p.parts))

    def leer_archivo(self, ruta):
        lineas = self._ruta(ruta).read_text(encoding="utf-8").splitlines()
        return "\n".join(f"{i:3d}| {l}" for i, l in enumerate(lineas, 1))

    def buscar(self, patron):
        rx, hallazgos = re.compile(patron), []
        for p in sorted(self.raiz.rglob("*.py")):
            for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(l):
                    hallazgos.append(f"{p.relative_to(self.raiz)}:{i}: {l.strip()}")
        return "\n".join(hallazgos) or "(sin resultados)"

    def mapa_repo(self, carpeta="."):
        """Devuelve las firmas y clases del proyecto extraídas con el módulo ast (Sección 1.5)."""
        import ast
        base = self._ruta(carpeta)
        lineas = []
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            rel = p.relative_to(self.raiz)
            try:
                arbol = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
            except Exception:
                continue
            items = []
            for nodo in arbol.body:
                if isinstance(nodo, ast.ClassDef):
                    metodos = [f"    def {m.name}()" for m in nodo.body if isinstance(m, ast.FunctionDef)]
                    items.append(f"  class {nodo.name}:\n" + "\n".join(metodos) if metodos else f"  class {nodo.name}")
                elif isinstance(nodo, ast.FunctionDef):
                    items.append(f"  def {nodo.name}()")
            if items:
                lineas.append(f"{rel}:\n" + "\n".join(items))
        return "\n\n".join(lineas) or "(repositorio vacío o sin definiciones Python)"

    def anotar(self, texto: str):
        """Guarda notas o hipótesis en notas.md (memoria de trabajo externa, Sección 1.6)."""
        p = self.raiz / "notas.md"
        anterior = p.read_text(encoding="utf-8") if p.exists() else ""
        nuevo = anterior + ("\n" if anterior and not anterior.endswith("\n") else "") + f"- {texto.strip()}\n"
        p.write_text(nuevo, encoding="utf-8")
        return "OK: nota guardada en notas.md"

    def leer_notas(self):
        """Devuelve el contenido actual de notas.md."""
        p = self.raiz / "notas.md"
        if not p.exists():
            return "(sin notas registradas en notas.md)"
        return p.read_text(encoding="utf-8").strip()

    def ejecutar_pruebas(self):
        import sys, os
        env = dict(os.environ)
        env["PYTHONPATH"] = str(self.raiz)
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
                           cwd=self.raiz, env=env, capture_output=True, text=True, timeout=120)
        salida = (r.stdout + r.stderr).strip().splitlines()
        fallos = [l for l in salida if l.startswith(("FAILED", "E "))][:6]
        return "\n".join(fallos + salida[-1:])

    def editar_archivo(self, ruta, antes, despues):
        p = self._ruta(ruta)
        texto = p.read_text(encoding="utf-8")
        if texto.count(antes) != 1:
            return f"ERROR: el fragmento aparece {texto.count(antes)} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ver_cambios(self, original="../trabajo_original"):
        import difflib
        base, salida = self._ruta_libre(original), []
        for p in sorted(self.raiz.rglob("*.py")):
            rel = p.relative_to(self.raiz); q = base / rel
            a = q.read_text(encoding="utf-8").splitlines() if q.exists() else []
            salida += difflib.unified_diff(a, p.read_text(encoding="utf-8").splitlines(),
                                           f"a/{rel}", f"b/{rel}", lineterm="", n=1)
        return "\n".join(salida) or "(sin cambios)"

    def _ruta_libre(self, ruta):
        return (self.raiz / ruta).resolve()

    def ejecutar_comando(self, comando):
        r = subprocess.run(comando, shell=True, cwd=self.raiz, capture_output=True, text=True, timeout=60)
        return (r.stdout + r.stderr).strip()[-2000:]
