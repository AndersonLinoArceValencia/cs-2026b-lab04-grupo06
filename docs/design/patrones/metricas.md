# Métricas del refactor de RutaSIT (E6)

Medición reproducida el 25/10/2026 sobre `48af9a7`, con Radon 6.0.1 y pytest 9.1.1. Las cifras corresponden a archivos del repositorio; no se extrapolan a producción.

```powershell
python -m pytest -q
python -m radon cc -s -a src/monitoreo/antes/servicio.py
python -m radon cc -s -a src/monitoreo/servicio.py
python -m radon raw -s src/monitoreo/antes/servicio.py src/monitoreo/servicio.py
```

| Medida | Antes | Después |
|---|---:|---:|
| `ServicioMonitoreoSIT.consultar_tiempo_llegada` | D (25) | A (3) |
| Promedio de bloques en el archivo `servicio.py` | B (6,75), 8 bloques | A (1,68), 19 bloques |
| SLOC de `servicio.py` | 124 | 152 |
| LOC de `servicio.py` | 167 | 202 |
| Pruebas de comportamiento compartidas | 28 aprobadas sobre las dos versiones | 28 aprobadas sobre las dos versiones |
| Pruebas de patrones | No aplican | 12 aprobadas |

La implementación posterior ocupa 526 SLOC al sumar `servicio.py`, `adaptadores.py`, `estrategias.py`, `estados.py`, `eventos.py`, `decoradores.py` e `ia.py`. Esta suma no es una comparación directa con las 124 SLOC del servicio anterior: incluye responsabilidades nuevas y clases de soporte. La mejora comprobable es local al método crítico y a la extensibilidad probada. El costo es más archivos, clases e indirección. Para un único operador GPS y un único algoritmo ETA estables, la versión sencilla habría requerido menos mantenimiento inicial.

Se rechazó Singleton para el servicio o las fábricas: el estado global impediría inyectar dobles independientes en las pruebas. También se rechazó Command para `consultar_tiempo_llegada`, que es una lectura sin necesidad de deshacer o encolar. Ver `olores.md`.
