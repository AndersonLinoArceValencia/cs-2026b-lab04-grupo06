"""Patrón Observer para el sistema de eventos y notificaciones de RutaSIT Arequipa.

Desacopla la publicación de eventos del flujo crítico de cálculo de ETA.
Permite agregar nuevos suscriptores (pasajeros, centro de control, auditoría, push)
sin modificar el servicio de monitoreo (Open/Closed Principle).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class ISuscriptor(ABC):
    """Interfaz observadora (Observer)."""

    @abstractmethod
    def actualizar(self, tipo_evento: str, datos: Dict[str, Any]) -> None:
        """Método de notificación invocado por el publicador."""
        raise NotImplementedError


class PublicadorEventos:
    """Sujeto observable (Subject) que gestiona suscripciones y despacha eventos."""

    def __init__(self):
        self._suscriptores: Dict[str, List[ISuscriptor]] = {}

    def suscribir(self, tipo_evento: str, suscriptor: ISuscriptor) -> None:
        """Registra un suscriptor para un tipo de evento o '*' para todos."""
        self._suscriptores.setdefault(tipo_evento, []).append(suscriptor)

    def desuscribir(self, tipo_evento: str, suscriptor: ISuscriptor) -> None:
        """Elimina la suscripción de un observador."""
        if tipo_evento in self._suscriptores:
            self._suscriptores[tipo_evento] = [
                s for s in self._suscriptores[tipo_evento] if s != suscriptor
            ]

    def publicar(self, tipo_evento: str, datos: Dict[str, Any]) -> None:
        """Notifica el evento a todos los suscriptores registrados."""
        for suscriptor in self._suscriptores.get(tipo_evento, []):
            suscriptor.actualizar(tipo_evento, datos)
        # Notifica a suscriptores globales
        for suscriptor in self._suscriptores.get("*", []):
            suscriptor.actualizar(tipo_evento, datos)


class NotificadorPasajeroObserver(ISuscriptor):
    """Suscriptor 1: Notifica al pasajero del tiempo estimado de llegada."""

    def __init__(self, bandeja_salida: List[str]):
        self.bandeja_salida = bandeja_salida

    def actualizar(self, tipo_evento: str, datos: Dict[str, Any]) -> None:
        if tipo_evento == "ETA_CALCULADO":
            self.bandeja_salida.append(
                f"pasajero:bus_{datos['id_bus']}:ETA_{datos['eta_minutos']}_min"
            )


class MonitorCentroControlObserver(ISuscriptor):
    """Suscriptor 2: Supervisión y telemetría para el panel del SIT."""

    def __init__(self, bandeja_salida: List[str]):
        self.bandeja_salida = bandeja_salida

    def actualizar(self, tipo_evento: str, datos: Dict[str, Any]) -> None:
        if tipo_evento == "ETA_CALCULADO":
            lat = datos["latitud"]
            lon = datos["longitud"]
            self.bandeja_salida.append(
                f"control:flota:bus_{datos['id_bus']}:lat_{lat:.5f}:lon_{lon:.5f}"
            )
        elif tipo_evento == "GPS_TIMEOUT":
            self.bandeja_salida.append(f"alerta:gps_timeout:{datos['id_bus']}")


class NotificadorWebPushObserver(ISuscriptor):
    """Suscriptor 3: Envía notificaciones push al canal de pasajeros."""

    def __init__(self, servicio_push):
        self.servicio_push = servicio_push

    def actualizar(self, tipo_evento: str, datos: Dict[str, Any]) -> None:
        if tipo_evento == "ETA_CALCULADO":
            self.servicio_push.enviar_alerta(
                canal="pasajeros",
                titulo=f"Bus {datos['placa']} aproximándose",
                cuerpo=f"Tiempo estimado: {datos['eta_minutos']} min al paradero {datos['paradero']}"
            )
