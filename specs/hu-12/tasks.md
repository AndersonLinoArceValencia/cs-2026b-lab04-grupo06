# Tareas · HU-12

- [x] **T1:** Escribir pruebas unitarias en `tests/test_hu12_llegada.py` para los 5 escenarios de `spec.md` y verificar que fallan en rojo.
- [x] **T2:** Implementar validaciones de seguridad (rango geográfico de Arequipa y velocidad válida) y casos borde (`SIN_GPS` y `YA_PASO`) en `src/monitoreo/llegada.py`.
- [x] **T3:** Integrar `FabricaEstrategiasETA` para calcular `minutos_eta` y `hora_estimada` con estrategias `LINEAL`, `HORA_PUNTA` y `PARADAS_INTERMEDIAS`.
- [x] **T4:** Ejecutar `pytest` y `calidad/verificar.py`, confirmar todas las compuertas en verde y documentar la sesión en `docs/lab12/sesion-ia.md`.
