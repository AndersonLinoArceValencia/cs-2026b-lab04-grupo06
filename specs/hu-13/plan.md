# Plan técnico · HU-13

- Reutilizar `src/monitoreo/desvios.py` y `src/monitoreo/eventos.py` existentes en RutaSIT Arequipa.
- Mantener la lógica pura sin dependencias externas ni llamadas a infraestructura (`.importlinter`).
- Complejidad ciclomática máxima B (`radon`) y cobertura >= 85 %.
