# Bitácora de Interacciones con el Asistente de IA (Lab 10)

**Caso:** Caso 6 — RutaSIT Arequipa  
**Estudiantes:** Arce Valencia Anderson Lino & Carlos Ccamaqque Wilson Freddy  
**Laboratorio:** Laboratorio 10 — Sistemas Agénticos en la Construcción de Software (2026-B)  

---

## Interacción 1 (E1): Diseño del Lienzo Agéntico y Delimitación de Alcance

* **Fecha/Hora:** 16/11/2026 — 15:00
* **Rol Asignado a la IA:** Arquitecto de Software Senior especializado en Sistemas Agénticos.
* **Prompt:**
  > "Actúa como arquitecto de software senior. Para el sistema RutaSIT Arequipa (300 buses, seguimiento en tiempo real, latencia p95 <= 15s), completa el lienzo de diseño de 7 decisiones del Paso 2 de la guía de Laboratorio 10. Justifica con rigor técnico por qué tareas como la ingesta de telemetría GPS deben ser un flujo de trabajo fijo determinista mientras que la resolución de incidencias en el repositorio requiere un sistema agéntico ReAct."
* **Propuesta de la IA:** Propuso un arquetipo Planificador-Ejecutor con ReAct, separando la ingesta de alta frecuencia (FastAPI/Redis en flujo fijo a <5ms) del bucle de diagnóstico y reparación (agente ReAct). Delimitó las 7 dimensiones: herramientas de mínimo privilegio, memoria de notas, coordinación actor-crítico y control estricto.
* **Verificación:** Se revisó contra las Secciones 1.1 y 1.2 de la guía y los objetivos de SWE-bench.
* **Decisión:** **Aceptada.** Se plasmó formalmente en [`agentes/diseno/lienzo.md`](file:///home/andersp666/cs-2026b-lab04-grupo06/agentes/diseno/lienzo.md).

---

## Interacción 2 (E2): Error de Contrato por Invención de Herramienta

* **Fecha/Hora:** 16/11/2026 — 15:15
* **Rol Asignado a la IA:** Agente Ejecutor ReAct en modo exploratorio.
* **Prompt (Simulación de Turno 2 en ISSUE-01):**
  > "El agente intenta explorar los archivos del repositorio para localizar las estrategias de ETA."
* **Propuesta de la IA:** La IA devolvió el siguiente JSON:
  ```json
  {"pensamiento": "Voy a buscar el archivo con una herramienta inventada", "accion": "buscar_archivos", "args": {"patron": "estrategias"}}
  ```
* **Error Detectado por el Contrato:** La función `validar_decision()` en `contrato.py` evaluó la clave `"accion"` contra el conjunto conocido de herramientas y detectó que `"buscar_archivos"` no forma parte del catálogo permitido.
  * **Observación generada por el entorno:**
    `ERROR DE CONTRATO: herramienta desconocida: 'buscar_archivos'. Responda solo con el JSON del protocolo.`
* **Verificación y Corrección:** El agente registró la observación de error y en el turno 3 se autocorigió invocando la herramienta oficial `"buscar"` con `{"patron": "def calcular_eta"}`.
* **Decisión:** **Corregida.** El error quedó registrado en la traza `trazas/ejecutor.jsonl` demostrando la eficacia del contrato estructurado.

---

## Interacción 3 (E3): Modelado de la Máquina de Estados y Contrato Estricto

* **Fecha/Hora:** 16/11/2026 — 15:30
* **Rol Asignado a la IA:** Ingeniero de Calidad y Verificación Formal.
* **Prompt:**
  > "Modela en PlantUML la máquina de estados completa del bucle ReAct del agente en `agente/nucleo.py`, integrando el estado `EsperandoAprobacion` para el humano en el circuito y los estados de terminación. Además, diseña pruebas parametrizadas en pytest para rechazar campos extra, argumentos no estructurados y acciones vacías."
* **Propuesta de la IA:** Entregó el código PlantUML con los estados `Decidiendo`, `ValidandoContrato`, `EvaluandoPolitica`, `EsperandoAprobacion`, `Ejecutando`, `Observando`, `Finalizado` y `LimiteAlcanzado`, junto con 6 casos de prueba negativos para `test_agente.py`.
* **Verificación:** Se compiló el diagrama con PlantUML generando [`estados.png`](file:///home/andersp666/cs-2026b-lab04-grupo06/agentes/diseno/estados.png) y se ejecutó `pytest agentes/pruebas_agente` con 15/15 pruebas aprobadas.
* **Decisión:** **Aceptada.**

---

## Interacción 4 (E4): Herramienta `mapa_repo()` con AST y Memoria de Notas

* **Fecha/Hora:** 16/11/2026 — 15:40
* **Rol Asignado a la IA:** Especialista en Ingeniería de Contexto e Introspección de Código.
* **Prompt:**
  > "Implementa en Herramientas la función `mapa_repo()` usando el módulo nativo `ast` de Python para extraer clases y firmas de funciones sin volcar el cuerpo del código. Añade herramientas `anotar()` y `leer_notas()` que persistan en `notas.md`. Resuelve ISSUE-03 y mide el impacto en el contexto respecto a E2."
* **Propuesta de la IA:** Implementó el visitor de AST para extraer definiciones de forma compacta y el manejador de memoria externa de notas. Resolvió `ISSUE-03` en 7 pasos y 14,801 caracteres de contexto.
* **Verificación:** Se comparó el contexto frente a E2 (24,180 caracteres). Redujo el consumo en un 38.8% y eliminó pasos de búsqueda ciega.
* **Decisión:** **Aceptada.**

---

## Interacción 5 (E5): Error de Diseño Detectado por el Revisor Crítico

* **Fecha/Hora:** 16/11/2026 — 15:55
* **Rol Asignado a la IA:** Revisor Crítico (Read-Only Code Reviewer).
* **Prompt:**
  > "Actúa como revisor crítico de código de solo lectura. Inspecciona el parche propuesto por el ejecutor en Ronda 1 para `src/monitoreo/desvios.py` que calcula distancia a segmentos de recta. Evalúa robustez matemática, posibles divisiones por cero y casos borde en rutas de transporte."
* **Propuesta Inicial del Ejecutor (Ronda 1):** El ejecutor calculaba la proyección `t = (px * dx + py * dy) / longitud_seg_sq` sin validar si `longitud_seg_sq == 0`, y asumía que toda ruta tiene al menos 2 waypoints.
* **Error Detectado por el Revisor:** El revisor emitió:
  > *"CAMBIOS SOLICITADOS: En distancia_punto_a_segmento_metros no se valida el caso longitud_seg_sq == 0 (dos waypoints idénticos o consecutivos muy cercanos), lo cual causará ZeroDivisionError. Además, evaluar_desvio_ruta arroja ValueError si la ruta contiene exactamente un solo waypoint. Agregue protecciones para ambos casos."*
* **Verificación y Corrección en Ronda 2:** El ejecutor recibió la retroalimentación, añadió `if longitud_seg_sq == 0.0: return distancia_metros(p, a)` y `if len(waypoints_ruta) == 1: return ...`, logrando la aprobación final del crítico.
* **Decisión:** **Corregida mediante bucle Actor-Crítico.** Se demostró experimentalmente cómo la coordinación multiagente evita que bugs silenciosos alcancen producción.
