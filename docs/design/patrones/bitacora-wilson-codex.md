# Bitácora de revisión con Codex — Wilson (Lab 07)

Los cinco textos siguientes son **prompts reproducibles redactados para esta revisión**, no transcripciones de una sesión histórica. Git conserva los cambios, pero no el texto literal de las conversaciones. Anderson realizó E1–E5 con Antigravity según `bitacora-ia.md`; esta revisión de E1, E6–E8 se hizo con Codex sobre `48af9a7`.

## Interacción 1 — olores

```text
Revisa src/monitoreo/antes/servicio.py de RutaSIT.
Señala olores por línea y un patrón que los resuelva.
Indica costo y rechaza patrones sin necesidad concreta.
```

**Resultado verificado:** `olores.md` registra condicionales ETA → Strategy, formatos GPS → Adapter, estados → State, avisos → Observer y reintentos → Decorator. Rechaza Singleton y Command. El método inicial mide D (25).

## Interacción 2 — pruebas

```text
Compara el flujo antes y después sin cambiar el código.
Ejecuta test_comportamiento.py y test_patrones.py.
Resume casos aprobados y cualquier fallo observable.
```

**Resultado verificado:** 28 ejecuciones de comportamiento y 12 pruebas de patrones aprobadas, total 40. La bitácora de Anderson documenta un fallo anterior `assert 1 == 3` en reintentos GPS; el commit E4 elimina los reintentos internos del adaptador y el estado actual aprueba.

## Interacción 3 — métricas

```text
Mide con radon el método de consulta antes y después.
Compara promedio de complejidad y SLOC del servicio.
Explica el costo de los módulos añadidos sin ocultarlo.
```

**Resultado verificado:** método D (25) → A (3); promedio B (6,75) → A (1,68); servicio 124 → 152 SLOC. Siete módulos posteriores suman 526 SLOC. Detalle en `metricas.md`.

## Interacción 4 — decisión

```text
Redacta el ADR-005 para los patrones de RutaSIT.
Usa solo código, pruebas y métricas del repositorio.
Incluye patrones rechazados y consecuencias negativas.
```

**Resultado:** borrador de ADR-005 creado en `docs/architecture/adr/005-patrones-de-diseno.md`, con estado **Propuesto para revisión**. No se atribuye aprobación del equipo ni Pull Request inexistente.

## Interacción 5 — consistencia y entrega

```text
Contrasta clases y pruebas con el Lab 07 de RutaSIT.
Responde las ocho preguntas del cuestionario.
Marca entregables pendientes sin inventar PR ni etiqueta.
```

**Resultado:** cuestionario local en `docs/design/patrones/cuestionario-lab07.md`. Al revisar `48af9a7`, no había ADR-005, `metricas.md`, etiqueta `v0.7-patrones` ni evidencia de PR del Lab 07; los dos primeros se redactaron en esta revisión. La etiqueta y la revisión cruzada siguen pendientes de una decisión del equipo.
