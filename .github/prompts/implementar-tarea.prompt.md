---
description: Implementa UNA tarea de specs/<hu>/tasks.md con TDD y compuertas de calidad
---
Lee AGENTS.md y los archivos `specs/${input:hu}/spec.md`, `plan.md` y `tasks.md`.
Implementa SOLO la tarea `${input:tarea}`:
1. Si la tarea es de pruebas, escríbelas y verifica que FALLAN. Si es de código, escribe lo mínimo para que pasen.
2. Ejecuta `python -m pytest -q` y `python calidad/verificar.py <modulo>`.
3. No agregues dependencias fuera de `calidad/dependencias_aprobadas.txt`; no modifiques pruebas existentes.
4. Termina indicando archivos cambiados, motivo, salida de compuertas y dudas para el equipo.
