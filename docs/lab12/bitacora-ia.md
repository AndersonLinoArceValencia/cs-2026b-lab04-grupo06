# Bitácora de Interacciones con IA · Lab 12 (E7)

| # | Fecha | Tarea | Prompt / solicitud resumida | Error o desviación detectada | Cómo se detectó | Corrección aplicada |
|---|---|---|---|---|---|---|
| 1 | 2026-11-23 | E1 | Adaptar `AGENTS.md` y lista de dependencias al proyecto RutaSIT. | Sugirió incluir `requests` y `pandas` sin necesidad. | Revisión humana contra ADR-001 y `calidad/dependencias_aprobadas.txt`. | Se restringió la lista exclusivamente a la biblioteca estándar y `src`. |
| 2 | 2026-11-23 | E2 | Redactar `specs/hu-12/spec.md` para estimación de hora de llegada. | Incluyó envío de alertas push dentro de la misma historia. | Revisión del equipo durante E2. | Se movió a la sección *Fuera de alcance* para mantener cohesión. |
| 3 | 2026-11-23 | E3-T1 | Escribir pruebas unitarias para `HU-12`. | Omitió inicialmente el caso borde `km_bus == km_paradero`. | Revisión humana contra criterios de aceptación. | Se añadió `test_bus_en_el_mismo_paradero`. |
| 4 | 2026-11-23 | E3-T3 | Implementar `estimar_hora_llegada` en `src/monitoreo/llegada.py`. | Duplicó la fórmula lineal en lugar de reutilizar `FabricaEstrategiasETA`. | Revisión contra `AGENTS.md` y fallo de `test_hora_punta_reutiliza_estrategia`. | Se inyectó `FabricaEstrategiasETA().crear(estrategia)`. |
| 5 | 2026-11-23 | E4 | Revisión automática del Pull Request de HU-12. | Falso positivo: reportó falta de prueba para distancia 0 cuando ya existía. | Verificación manual en `tests/test_hu12_llegada.py`. | Se descartó la sugerencia y se registró en `revision-pr.md`. |
| 6 | 2026-11-23 | E5 | Generar borrador rápido con prompt vago sin contexto (`borrador_v0`). | Alucinó el paquete inexistente `geopy_fast_eta` (riesgo de slopsquatting) y usó `subprocess.call(..., shell=True)`. | Compuertas `Dependencias aprobadas` y `Bandit (B602 HIGH)` en `calidad/verificar.py`. | Se descartó el borrador y se validó la eficacia de las 8 compuertas automáticas. |
