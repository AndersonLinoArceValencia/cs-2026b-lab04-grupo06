"""Patrón State para el ciclo de vida del Viaje en RutaSIT Arequipa.

Implementa formalmente la máquina de estados del Laboratorio 05 (estados-viaje.mmd):
PROGRAMADO -> EN_RUTA <-> (DETENIDO | DESVIADO) -> FINALIZADO.

Cada estado es una clase independiente. La clase base prohíbe todas las transiciones
lanzando TransicionInvalidaError; cada estado concreto redefine únicamente las permitidas.
"""

from abc import ABC
from typing import List, Optional


class TransicionInvalidaError(ValueError):
    """Excepción lanzada cuando se intenta una transición prohibida en la máquina de estados."""
    pass


class EstadoViajeState(ABC):
    """Clase base abstracta para los estados del viaje (prohíbe transiciones por defecto)."""
    nombre: str = "DESCONOCIDO"

    def iniciar_recorrido(self, viaje: "Viaje") -> None:
        raise TransicionInvalidaError(f"No se puede iniciar recorrido desde el estado {self.nombre}")

    def registrar_detencion(self, viaje: "Viaje", motivo: str) -> None:
        raise TransicionInvalidaError(f"No se puede registrar detención desde el estado {self.nombre}")

    def registrar_desvio(self, viaje: "Viaje", motivo: str) -> None:
        raise TransicionInvalidaError(f"No se puede registrar desvío desde el estado {self.nombre}")

    def reanudar_recorrido(self, viaje: "Viaje") -> None:
        raise TransicionInvalidaError(f"No se puede reanudar recorrido desde el estado {self.nombre}")

    def retornar_a_ruta(self, viaje: "Viaje") -> None:
        raise TransicionInvalidaError(f"No se puede retornar a ruta desde el estado {self.nombre}")

    def finalizar_recorrido(self, viaje: "Viaje") -> None:
        raise TransicionInvalidaError(f"No se puede finalizar recorrido desde el estado {self.nombre}")

    def validar_disponibilidad_eta(self, viaje: "Viaje", eventos: List[str]) -> None:
        """Valida si en este estado el viaje es elegible para cálculo de tiempo de llegada."""
        raise ValueError(f"Estado de viaje no reconocido: {self.nombre}")


class ProgramadoState(EstadoViajeState):
    """El viaje está registrado y programado, pero aún no inicia la marcha."""
    nombre = "PROGRAMADO"

    def iniciar_recorrido(self, viaje: "Viaje") -> None:
        viaje.cambiar_a(EnRutaState())

    def validar_disponibilidad_eta(self, viaje: "Viaje", eventos: List[str]) -> None:
        raise ValueError("El viaje está en estado PROGRAMADO y aún no inicia recorrido")


class EnRutaState(EstadoViajeState):
    """El bus se encuentra en recorrido activo sobre su ruta oficial."""
    nombre = "EN_RUTA"

    def registrar_detencion(self, viaje: "Viaje", motivo: str) -> None:
        viaje.motivo_contingencia = motivo
        viaje.cambiar_a(DetenidoState(motivo))

    def registrar_desvio(self, viaje: "Viaje", motivo: str) -> None:
        viaje.motivo_contingencia = motivo
        viaje.cambiar_a(DesviadoState(motivo))

    def finalizar_recorrido(self, viaje: "Viaje") -> None:
        viaje.cambiar_a(FinalizadoState())

    def validar_disponibilidad_eta(self, viaje: "Viaje", eventos: List[str]) -> None:
        # Estado óptimo: cálculo de ETA permitido sin excepciones
        pass


class DetenidoState(EstadoViajeState):
    """El bus está temporalmente detenido en ruta (ej. congestión o falla menor)."""
    nombre = "DETENIDO"

    def __init__(self, motivo: str = "Congestión vial"):
        self.motivo = motivo

    def reanudar_recorrido(self, viaje: "Viaje") -> None:
        viaje.motivo_contingencia = None
        viaje.cambiar_a(EnRutaState())

    def finalizar_recorrido(self, viaje: "Viaje") -> None:
        viaje.cambiar_a(FinalizadoState())

    def validar_disponibilidad_eta(self, viaje: "Viaje", eventos: List[str]) -> None:
        eventos.append(f"alerta:contingencia:viaje_{viaje.id_viaje}_detenido")
        raise ValueError("El viaje está DETENIDO por contingencia en la vía")


class DesviadoState(EstadoViajeState):
    """El bus ha salido de la geocerca de su trazado de ruta oficial."""
    nombre = "DESVIADO"

    def __init__(self, motivo: str = "Desvío por obras"):
        self.motivo = motivo

    def retornar_a_ruta(self, viaje: "Viaje") -> None:
        viaje.motivo_contingencia = None
        viaje.cambiar_a(EnRutaState())

    def reanudar_recorrido(self, viaje: "Viaje") -> None:
        viaje.motivo_contingencia = None
        viaje.cambiar_a(EnRutaState())

    def finalizar_recorrido(self, viaje: "Viaje") -> None:
        viaje.cambiar_a(FinalizadoState())

    def validar_disponibilidad_eta(self, viaje: "Viaje", eventos: List[str]) -> None:
        eventos.append(f"alerta:desvio:viaje_{viaje.id_viaje}_fuera_de_ruta")
        raise ValueError("El viaje está DESVIADO de su ruta oficial")


class FinalizadoState(EstadoViajeState):
    """El viaje ha concluido formalmente; no admite más transiciones."""
    nombre = "FINALIZADO"

    def validar_disponibilidad_eta(self, viaje: "Viaje", eventos: List[str]) -> None:
        raise ValueError("El viaje ya ha FINALIZADO")


class EstadoDesconocidoState(EstadoViajeState):
    """Representa estados no reconocidos en el dominio."""
    def __init__(self, nombre: str):
        self.nombre = nombre

    def validar_disponibilidad_eta(self, viaje: "Viaje", eventos: List[str]) -> None:
        raise ValueError(f"Estado de viaje no reconocido: {self.nombre}")


def crear_estado_desde_string(nombre_estado: str) -> EstadoViajeState:
    """Fábrica utilitaria para convertir cadenas de estado a instancias State."""
    mapeo = {
        "PROGRAMADO": ProgramadoState,
        "EN_RUTA": EnRutaState,
        "DETENIDO": DetenidoState,
        "DESVIADO": DesviadoState,
        "FINALIZADO": FinalizadoState,
    }
    cls = mapeo.get(nombre_estado)
    if cls:
        return cls()
    return EstadoDesconocidoState(nombre_estado)
