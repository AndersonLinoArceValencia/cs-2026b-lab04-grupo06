# AGENTS.md — RutaSIT Arequipa (Grupo 06)

## Contexto
Monolito modular asíncrono en Python (ADR-001) con patrones Strategy, Adapter, State, Observer, Decorator y Chain of Responsibility (ADR-005).
Código fuente en `src/monitoreo/` y pruebas en `tests/`.
Cada historia tiene `specs/<hu>/spec.md`, `plan.md` y `tasks.md`: léelos antes de escribir código.

## Forma de trabajo
1. Una tarea de `tasks.md` a la vez. Primero la prueba en rojo, luego el código mínimo para que pase en verde.
2. Reutiliza funciones y clases existentes del proyecto antes de crear nuevas (por ejemplo, `FabricaEstrategiasETA` en `src/monitoreo/estrategias.py` y `Coordenada` en `src/monitoreo/dominio.py`).
3. Respeta las capas arquitectónicas de `.importlinter` (FF-01, FF-02 y FF-03).
4. Explica en cada resumen qué cambiaste, por qué y cómo lo verificaste.

## Compuertas de calidad (todas deben pasar)
Ejecutar `python calidad/verificar.py <modulo>`:
- Dependencias aprobadas (`calidad/dependencias_aprobadas.txt`).
- Pruebas unitarias (`pytest`).
- Cobertura mínima >= 85 %.
- Estilo y errores (`ruff`).
- Seguridad estática (`bandit`).
- Complejidad ciclomática máxima B (`radon`).
- Detección de secretos en el código.
- Contratos de arquitectura (`lint-imports`).

## Prohibido
- Agregar dependencias fuera de `calidad/dependencias_aprobadas.txt`.
- Modificar pruebas existentes para forzar que pasen.
- Usar `shell=True`, `eval`, `exec` o `pickle` con datos externos.
- Incluir claves, tokens o datos personales reales en código, pruebas o prompts.
