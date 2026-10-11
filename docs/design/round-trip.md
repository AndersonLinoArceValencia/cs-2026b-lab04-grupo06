# E6: Round-trip con IA (Ingeniería Inversa)

## 1. Generación de código (ingeniería directa)
Se utilizó IA para generar el esqueleto en Python (`src/monitoreo/dominio.py`) a partir del diagrama de clases (`clases.puml`). Se respetaron:
- Dataclasses de Python 3.10+ y type hints.
- Puertos como interfaces con `ABC` y `@abstractmethod`; los adaptadores (`ProveedorGPSAdapter`, `ServicioMapasAdapter`, `WebPushAdapter`) lanzan `NotImplementedError`.
- Nomenclatura convertida de `camelCase` (diagrama) a `snake_case` (Python, PEP 8).
- Lógica mínima en `Viaje`, `ServicioMonitoreoSIT` y `AppPasajero`.

## 2. Ingeniería inversa
```bash
pip install pylint
pyreverse -o puml -p monitoreo src/monitoreo/dominio.py   # genera classes_monitoreo.puml
```
Se obtuvo `classes_monitoreo.puml` (imagen en `img/classes_monitoreo.png`). `packages_monitoreo.puml` es el que pyreverse genera para el paquete `monitoreo` y no representa los módulos del ADR-001; el diagrama de paquetes del diseño es `paquetes.puml`.

## 3. Comparativa y diferencias (diseño vs código)

| N.º | Diferencia observada en `classes_monitoreo.puml` respecto a `clases.puml` | Causa | Acción tomada |
| :---: | :--- | :--- | :--- |
| 1 | Los puertos aparecen como clases con métodos `{abstract}`, sin el estereotipo `<<puerto>>`/`<<interface>>`; los adaptadores figuran con `--\|>` y métodos abstractos. | Python implementa interfaces con `ABC` y pyreverse no inyecta estereotipos. Los adaptadores aún lanzan `NotImplementedError`. | **Documentar limitación:** `ABC` cumple el rol de interfaz. |
| 2 | No aparecen la agregación `Ruta o-- Paradero` ni las multiplicidades; `Ruta.paraderos` figura como atributo `List[Paradero]`. | pyreverse no infiere asociaciones desde colecciones tipadas y el código no expresa multiplicidades. | **Documentar limitación:** el diagrama de diseño se mantiene como fuente de las multiplicidades. Se agregará en el MVP una validación de 2 o más paraderos por ruta (C3). |
| 3 | `EstadoViaje` muestra solo `name`, sin los cinco valores. | pyreverse trata las enumeraciones como clases con el atributo estándar de `Enum`. | **Documentar limitación.** |
| 4 | El código agrega `Viaje.bus` y `Viaje.servicio_mapas`, que son campos del dataclass y no atributos del diagrama de diseño (en el diseño son las asociaciones `Bus–Viaje` y `Viaje ..> IServicioMapas`). | Un dataclass materializa las asociaciones como referencias. | **Aceptar:** equivalencia entre asociación del diseño y campo del código. |
| 5 | `Paradero._viajes_proximos` existe en el código (almacén en memoria) y no en el diseño. | El esqueleto necesita una fuente de datos para `obtenerViajesProximos()`; en el MVP vendrá de PostGIS. | **Corregir el código en el MVP** (reemplazar por repositorio) y mantener el diseño. |
| 6 | `ServicioMonitoreoSIT` no tiene dependencia hacia `IServicioMapas` (en el diseño sí la tenía) y se agregó `notificador`/`proveedor_gps` como atributos. | Se corrigió por la regla C1: es `Viaje` quien usa el puerto de mapas. El constructor inyecta los puertos que usa el servicio. | **Se actualizó el diagrama** (`Viaje ..> IServicioMapas`). |
| 7 | Cambio de nombres `calcularTiempoLlegada` → `calcular_tiempo_llegada`. | Convención PEP 8. | **Aceptar** y documentar la equivalencia (C5). |
