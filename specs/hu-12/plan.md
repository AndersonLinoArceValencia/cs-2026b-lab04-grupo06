# Plan técnico · HU-12

- Crear el módulo `src/monitoreo/llegada.py` dentro del módulo de monitoreo respetando ADR-001 y `.importlinter`.
- Reutilizar `FabricaEstrategiasETA` de `src/monitoreo/estrategias.py` para evitar duplicar fórmulas de cálculo ETA.
- Reutilizar `Coordenada` de `src/monitoreo/dominio.py` para representar la posición GPS del bus.
- Exponer el dataclass `ResultadoLlegada` y la función pura `estimar_hora_llegada(...)` usando solo la biblioteca estándar (`dataclasses`, `datetime`, `typing`).
- Validar coordenadas de Arequipa y rangos físicos de velocidad antes de invocar la estrategia.
- Mantener complejidad ciclomática máxima B (objetivo A) según `radon` y cobertura >= 85 %.
