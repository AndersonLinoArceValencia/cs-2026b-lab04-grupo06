"""Guardrails: qué puede hacer el agente, cuántas veces y con qué aprobación."""
import re
from dataclasses import dataclass, field


@dataclass
class Decision:
    permitido: bool
    motivo: str = ""


@dataclass
class Politica:
    herramientas_permitidas: set = field(default_factory=lambda: {
        "listar_archivos", "leer_archivo", "buscar", "mapa_repo", "anotar", "leer_notas",
        "ejecutar_pruebas", "editar_archivo", "ver_cambios", "ejecutar_comando"})
    comandos_permitidos: tuple = (r"^python -m pytest\b", r"^radon cc\b", r"^lint-imports\b", r"^git (status|diff)\b")
    rutas_protegidas: tuple = ("tests/",)          # el agente no puede "arreglar" las pruebas para que pasen
    max_pasos: int = 15
    aprobar_edicion: object = None                  # función opcional: humano en el circuito (human-in-the-loop)
    requieren_aprobacion: set = field(default_factory=set)   # Lab 11: herramientas MCP de escritura
    aprobar: object = None                          # Lab 11: función aprobar(accion, args) -> bool

    def evaluar(self, accion: str, args: dict, paso: int) -> Decision:
        if paso > self.max_pasos:
            return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida: {accion}")
        if accion == "ejecutar_comando":
            cmd = args.get("comando", "")
            if not any(re.search(p, cmd) for p in self.comandos_permitidos):
                return Decision(False, f"Comando fuera de la lista permitida: {cmd!r}")
        if accion == "editar_archivo":
            ruta = args.get("ruta", "")
            if ruta.startswith(self.rutas_protegidas):
                return Decision(False, f"Ruta protegida: {ruta}")
            if self.aprobar_edicion and not self.aprobar_edicion(args):
                return Decision(False, "El revisor humano rechazó la edición")
        return self._aprobacion_humana(accion, args)

    def _aprobacion_humana(self, accion: str, args: dict) -> Decision:
        """Lab 11: las herramientas de escritura (según sus anotaciones) exigen aprobación humana."""
        if accion in self.requieren_aprobacion and not (self.aprobar and self.aprobar(accion, args)):
            return Decision(False, f"{accion} requiere aprobación humana y no fue aprobada")
        return Decision(True)


def solicitar_aprobacion_consola(args: dict, entrada_fn=input) -> bool:
    """Valida la aprobación humana interactiva exigiendo estrictamente 's' o 'n' (E6)."""
    ruta = args.get("ruta", "(archivo desconocido)")
    print(f"\n[HUMANO EN EL CIRCUITO] Solicitud de edición sobre: {ruta}")
    print(f"--- FRAGMENTO ANTERIOR ---\n{args.get('antes', '')[:250]}")
    print(f"--- FRAGMENTO PROPUESTO ---\n{args.get('despues', '')[:250]}")
    while True:
        try:
            r = entrada_fn("¿Aprueba esta modificación en el código? (s/n): ").strip().lower()
        except EOFError:
            return False
        if r == "s":
            return True
        elif r == "n":
            return False
        print("Entrada no válida. Por favor responda únicamente con 's' o 'n'.")
