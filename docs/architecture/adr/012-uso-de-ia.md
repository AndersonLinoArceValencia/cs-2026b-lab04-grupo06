# ADR-012: Política de uso responsable de IA en el desarrollo de RutaSIT Arequipa

- **Estado:** Aceptado
- **Fecha:** 2026-11-23
- **Autores:** Arce Valencia Anderson Lino, Carlos Ccamaqque Wilson Freddy (Grupo 06)

## Contexto
El equipo incorpora asistentes de programación con modo agente (GitHub Copilot, Gemini CLI, Claude Code / Antigravity) en la evolución del monolito modular RutaSIT Arequipa. La evidencia empírica (DORA 2025, METR 2025, Pearce et al. 2022, Spracklen et al. 2025) demuestra que la IA acelera tareas acotadas pero puede introducir dependencias inventadas (*slopsquatting*), vulnerabilidades, duplicación de reglas y código no comprendido si no se aplica ingeniería disciplinada.

## Decisión
1. **Herramientas permitidas:** Asistentes con soporte para archivos de contexto `AGENTS.md` (GitHub Copilot plan educativo, Gemini CLI, Claude Code y Antigravity).
2. **Tareas delegables:** Generación de borradores de `spec.md`, casos de prueba iniciales bajo revisión humana, implementación incremental de tareas pequeñas de `tasks.md` y refactorizaciones cubiertas por pruebas.
3. **Tareas NO delegables:** Definición final de criterios de aceptación, decisiones arquitectónicas (ADRs), aprobación de Pull Requests, gestión de secretos/credenciales y fusión a `main`.
4. **Compuertas obligatorias:** Todo cambio debe aprobar las 8 compuertas automatizadas de `calidad/verificar.py` (dependencias aprobadas, pruebas `pytest`, cobertura >= 85 %, `ruff`, `bandit`, `radon` <= B, escaneo de secretos y contratos `import-linter`) tanto en local como en GitHub Actions.
5. **Trazabilidad en commits y PR:** Todo commit con apoyo de IA incluirá un pie `Asistencia-IA: <herramienta> (<modo>)` y cada Pull Request se revisará con `calidad/revision_pr.md` antes de fusionarse.
6. **Datos, secretos y licencias:** Queda prohibido ingresar datos personales reales, contraseñas, tokens de API o código propietario de terceros en los prompts; toda prueba usará datos sintéticos y solo se aceptará código compatible con la licencia del repositorio.
7. **Responsabilidad:** El autor humano y el revisor que aprueban el Pull Request son los únicos responsables de la calidad y seguridad del código fusionado; nada se fusiona si el equipo no puede explicarlo línea por línea.

## Consecuencias
- Mayor trazabilidad, menor riesgo de vulnerabilidades y preservación de la arquitectura definida en ADR-001 y ADR-005.
- Requiere disciplina adicional en especificaciones y revisión cruzada, lo cual puede incrementar ligeramente el tiempo de revisión frente a la generación sin control, a cambio de estabilidad sostenida.
