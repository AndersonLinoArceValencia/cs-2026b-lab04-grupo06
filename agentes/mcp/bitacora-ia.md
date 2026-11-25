# E7. Bitácora de interacciones con IA (Lab 11)

Asistente: Claude Code (Claude Opus 5.5), usado como asistente de programación y como host MCP real.

| # | Pedido al asistente | Lo que propuso | Qué se revisó o corrigió |
|---|---|---|---|
| 1 | Diseñar el catálogo del caso 6 a partir del código real (`llegada.py`, `desvios.py`). | Tres lecturas (`buses_en_ruta`, `tiempo_llegada`, `verificar_desvio`) y la escritura `reportar_desvio`, más recursos y prompts. | Se aceptó; se exigió reutilizar `estimar_hora_llegada` y `evaluar_desvio_ruta` en lugar de recalcular. |
| 2 | Implementar `reportar_desvio`. | Validaba la descripción dentro de la función, sin límite en el esquema. | **Sugerencia corregida**: la regla nueva R6 del auditor la marcó; se publicó `maxLength` con `Field`. |
| 3 | Añadir una excepción de ruff al servidor de terceros. | Insertó `# ruff: noqa: E501` en la línea 2. | **Sugerencia corregida**: quedó dentro del docstring y no tenía efecto; se movió fuera. |
| 4 | Bajar la complejidad del auditor y del generador de trazas (radon dio C). | Separar las reglas en funciones pequeñas (`_reglas_descripcion`, `_reglas_escritura`, ...). | Se verificó con radon (máx. B) y las 20 pruebas siguieron en verde. |
| 5 | Abrir el servidor en MCP Inspector. | `npx @modelcontextprotocol/inspector ...` | Falló con Node 18 (`styleText`); se ejecutó con `npx -p node@22` sin cambiar el Node del sistema. |
| 6 | Responder 5 consultas como host conectado al servidor. | En la consulta de ETA buscó el ID del paradero con `grep` en el repositorio. | Se mejoró la descripción de `tiempo_llegada` para que remita al recurso del mapa; al repetir, el host usó el recurso. |
| 7 | Generar las decisiones del agente del Lab 10 para la consulta del centro de control. | Trayectoria de 7 decisiones, con un error de formato de hora a propósito. | Se grabó en `trayectorias/operador.json`; las herramientas se ejecutaron de verdad vía MCP. |
