# ADR-010: Arquitectura del Sistema Agéntico para Diagnóstico y Mantenimiento de Software

- **Estado:** Aceptado
- **Fecha:** 2026-11-16
- **Decisores:** Arce Valencia Anderson Lino & Carlos Ccamaqque Wilson Freddy

---

## Contexto

El mantenimiento y evolución del sistema de monitoreo en tiempo real RutaSIT Arequipa enfrenta incidencias de software de diversa complejidad (como cálculo de tiempos de llegada con paraderos ya rebasados, detección de desvíos en geometrías curvas y resiliencia ante pérdidas de señal GPS). Resolver estos problemas exige exploración del código, localización de causas raíz, edición quirúrgica de componentes y verificación objetiva con suites de pruebas unitarias (`pytest`).

Se requiere definir la arquitectura de un sistema agéntico capaz de abordar estas tareas de manera autónoma pero controlada, satisfaciendo los atributos de calidad de modificabilidad, confiabilidad y seguridad frente a riesgos de **exceso de agencia (OWASP LLM06)** e inyección indirecta de instrucciones.

---

## Alternativas Consideradas

1. **Flujo de trabajo fijo (Hardcoded CI/CD o scripts rígidos):**
   * *Ventajas:* Determinista, costo cero de inferencia y latencia mínima.
   * *Desventajas:* Incapaz de diagnosticar ni corregir defectos nuevos; las secuencias de pasos para resolver un bug no se conocen de antemano.
2. **Agente único sin guardrails (Monolithic Free-Form Agent):**
   * *Ventajas:* Implementación sencilla, menor consumo de tokens y ejecución rápida en una sola pasada.
   * *Desventajas:* Propenso a alucinaciones de herramientas, omisión de casos de borde críticos (como división por cero en algoritmos matemáticos) y alto riesgo de modificar arbitrariamente las pruebas de regresión para forzar el aprobado.
3. **Sistema Multiagente Gestor + Actor-Crítico con Mínimo Privilegio y HITL (Seleccionada):**
   * *Ventajas:* Separación estricta de responsabilidades (un agente genera el parche y otro independiente lo audita con permisos de solo lectura), contrato JSON estricto, introspección estructural con AST y aprobación humana interactiva obligatoria para escrituras en código.
   * *Desventajas:* Mayor consumo de tokens (~2.8x respecto al agente único) y necesidad de orquestación.

---

## Decisión

Usaremos un **Sistema Multiagente basado en el Arquetipo Planificador-Ejecutor + ReAct**, coordinado por un **Gestor (Planificador)** y un bucle **Actor-Crítico (Ejecutor y Revisor)**:

1. **Arquetipo y Ciclo de Vida:** El bucle ReAct (*Reasoning + Acting*) opera como una máquina de estados finita formal (`INICIO` $\rightarrow$ `DECIDIENDO` $\rightarrow$ `VALIDANDO_CONTRATO` $\rightarrow$ `EVALUANDO_POLITICA` $\rightarrow$ `EJECUTANDO` $\rightarrow$ `OBSERVANDO` $\rightarrow$ `FINALIZADO`).
2. **Coordinación y Mínimo Privilegio:** 
   * **Planificador:** Descompone el issue en un plan acotado de 3 a 4 pasos (sin herramientas de ejecución).
   * **Ejecutor (Actor):** Aplica herramientas de lectura, búsqueda, ejecución de pruebas y edición (límite: 12 pasos).
   * **Revisor (Crítico):** Posee permisos exclusivos de solo lectura (`ver_cambios`, `leer_archivo`, `ejecutar_pruebas`, `buscar`) y evalúa el diff para emitir veredicto `APROBADO` o `CAMBIOS SOLICITADOS` (máximo 2 rondas).
3. **Herramientas e Ingeniería de Contexto:** Caja de herramientas acotada en sandbox con introspección estructural mediante `mapa_repo()` (módulo `ast`) y persistencia de memoria de trabajo en `notas.md` (`anotar()`, `leer_notas()`).
4. **Humano en el Circuito (HITL) y Delegación Progresiva:** El hook interactivo `aprobar_edicion` exige confirmación humana (`s`/`n`) para cualquier modificación de archivos fuente, y el Pull Request final requiere aprobación humana antes del merge.

---

## Consecuencias

### Positivas
- **Detección temprana de fallos ocultos:** El revisor crítico detecta omisiones de diseño y fallos silenciosos (como `ZeroDivisionError` en tramos de ruta con buses detenidos) antes de que el código llegue a producción.
- **Eficiencia de contexto:** La herramienta `mapa_repo()` con AST reduce en ~38.8% el consumo de caracteres y tokens frente a la lectura de archivos completos.
- **Seguridad e integridad de pruebas:** La política de guardrails protege la carpeta `tests/`, impidiendo que el agente altere las pruebas para fingir su resolución.

### Negativas / Trade-offs
- **Consumo de tokens:** En tareas multiagente, el contexto total acumulado ronda los 27,000 caracteres frente a los 9,500 de un agente simple; sin embargo, el principio de parsimonia indica que este sobrecosto es plenamente justificable en componentes centrales de negocio.
- **Latencia de revisión:** El bucle de 2 rondas duplica el tiempo de ejecución del proceso frente a un flujo lineal.
