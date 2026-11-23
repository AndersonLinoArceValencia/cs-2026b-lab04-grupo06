# Mini Experimento de Productividad · Lab 12 (E6)

En las dos tareas de tamaño similar (T-A: validaciones de rango físico y geográfico; T-B: cálculo de llegada con casos borde `SIN_GPS` y `YA_PASO`), trabajar con asistencia de IA redujo el tiempo bruto promedio de 22.5 minutos sin IA a 16.0 minutos con IA (28.9 % menos). Sin embargo, el código escrito sin IA aprobó las 8/8 compuertas al primer intento y no registró defectos en revisión, mientras que el código asistido por IA requirió 2 a 3 iteraciones de corrección por defectos como la duplicación de la fórmula ETA y una validación omitida.

Estos hallazgos coinciden con el informe DORA 2025, que señala que la IA acelera la entrega pero introduce mayor variabilidad si no existen compuertas automáticas y revisión rigurosa. También dialogan con el estudio de METR (2025): aunque en tareas pequeñas y bien especificadas la IA ahorró tiempo inicial, el tiempo adicional de depuración y revisión reduce la ganancia neta cuando el modelo desconoce las convenciones internas del repositorio.

Limitaciones del experimento: la muestra es muy reducida (dos integrantes y dos tareas cortas), las tareas T-A y T-B no tienen exactamente la misma complejidad lógica y existe un efecto de aprendizaje inevitable al diseñar previamente la especificación compartida.
