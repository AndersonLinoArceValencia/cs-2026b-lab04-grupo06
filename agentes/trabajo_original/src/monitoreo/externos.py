"""Servicios externos simulados para RutaSIT Arequipa.

Simula SDKs de proveedores de GPS con interfaces incompatibles entre sí,
tal como ocurre con los distintos consorcios operadores del SIT.
"""

class GPSOperadorASDK:
    """SDK del Concesionario A (Arequipa Bus / AQP Masivo).
    
    Interfaz: método obtener_posicion recibe string y retorna dict con
    coordenadas en grados decimales y velocidad en km/h.
    """
    def __init__(self, fallas: int = 0):
        self.fallas = fallas
        self.intentos = 0

    def obtener_posicion(self, id_unidad: str) -> dict:
        self.intentos += 1
        if self.intentos <= self.fallas:
            raise TimeoutError(f"Timeout al conectar con telemetría GPS de unidad {id_unidad}")
        return {
            "ok": True,
            "id_unidad": id_unidad,
            "lat": -16.40904,
            "lon": -71.53745,
            "velocidad_kmh": 30.0
        }


class GPSOperadorBSDK:
    """SDK del Concesionario B (Consorcio Cono Norte / Tranvía).
    
    Interfaz incompatible: método query_location recibe entero y retorna tupla
    (status_code, lat_microgrados, lon_microgrados, speed_cm_s).
    """
    def __init__(self, fallas: int = 0):
        self.fallas = fallas
        self.intentos = 0

    def query_location(self, bus_code: int) -> tuple:
        self.intentos += 1
        if self.intentos <= self.fallas:
            raise TimeoutError(f"Error de enlace con dispositivo GPS {bus_code}")
        # Retorna: status HTTP 200, lat*1e6, lon*1e6, velocidad en cm/s (30 km/h = 833 cm/s)
        return (200, -16409040, -71537450, 833)


class ServicioWebPushExterno:
    """Servicio externo simulado para despacho de notificaciones push."""
    def __init__(self):
        self.notificaciones_enviadas = []

    def enviar_alerta(self, canal: str, titulo: str, cuerpo: str) -> bool:
        self.notificaciones_enviadas.append({
            "canal": canal,
            "titulo": titulo,
            "cuerpo": cuerpo
        })
        return True
