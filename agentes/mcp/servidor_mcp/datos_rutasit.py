"""Datos FICTICIOS de RutaSIT Arequipa para el servidor MCP (Lab 11).

Rutas, paraderos y buses inventados con coordenadas dentro del rango geográfico de Arequipa.
No contienen placas, personas ni posiciones reales.
"""

from dataclasses import dataclass

from src.monitoreo.desvios import CoordenadaGPS


@dataclass(frozen=True)
class ParaderoRuta:
    id_paradero: str
    nombre: str
    km: float  # distancia desde el inicio de la ruta
    lat: float
    lon: float


@dataclass(frozen=True)
class RutaSIT:
    id_ruta: str
    nombre: str
    paraderos: tuple[ParaderoRuta, ...]

    def waypoints(self) -> list[CoordenadaGPS]:
        return [CoordenadaGPS(lat=p.lat, lon=p.lon) for p in self.paraderos]


@dataclass(frozen=True)
class BusEnServicio:
    id_bus: str
    placa: str  # placa ficticia
    id_ruta: str
    estado: str  # EN_RUTA, DETENIDO, DESVIADO, PROGRAMADO
    km: float
    velocidad_kmh: float
    lat: float | None
    lon: float | None


RUTAS = {
    "R-01": RutaSIT(
        "R-01",
        "Cono Norte - Centro",
        (
            ParaderoRuta("P-101", "Terminal Cono Norte", 0.0, -16.3600, -71.5600),
            ParaderoRuta("P-102", "Av. Ejército", 3.0, -16.3800, -71.5450),
            ParaderoRuta("P-103", "Puente Grau", 6.0, -16.3950, -71.5380),
            ParaderoRuta("P-104", "Plaza de Armas", 8.0, -16.3990, -71.5370),
        ),
    ),
    "R-02": RutaSIT(
        "R-02",
        "Socabaya - Centro",
        (
            ParaderoRuta("P-201", "Terminal Socabaya", 0.0, -16.4600, -71.5300),
            ParaderoRuta("P-202", "Av. Dolores", 4.0, -16.4250, -71.5250),
            ParaderoRuta("P-203", "Av. Independencia", 7.5, -16.4050, -71.5300),
        ),
    ),
}

BUSES = {
    "B-011": BusEnServicio("B-011", "SIT-011", "R-01", "EN_RUTA", 2.0, 24.0, -16.3733, -71.5500),
    "B-012": BusEnServicio("B-012", "SIT-012", "R-01", "EN_RUTA", 5.0, 18.0, -16.3900, -71.5403),
    "B-013": BusEnServicio("B-013", "SIT-013", "R-01", "DESVIADO", 4.0, 15.0, -16.3780, -71.5250),
    "B-021": BusEnServicio("B-021", "SIT-021", "R-02", "EN_RUTA", 1.5, 30.0, -16.4470, -71.5280),
    "B-022": BusEnServicio("B-022", "SIT-022", "R-02", "DETENIDO", 5.0, 0.0, None, None),
}
