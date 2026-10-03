# Bitácora de uso de IA — RutaSIT Arequipa

Esta bitácora registra las interacciones con asistentes de Inteligencia Artificial durante el diseño arquitectónico de **RutaSIT Arequipa**, aplicando el principio de la guía: *"La IA propone, el equipo decide y verifica"*.

---

## 1. Registro de Interacciones

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| **1** | 03/10/2026 | Antigravity AI | Análisis estructural de la Guía de Laboratorio 04 y mapeo de los requerimientos de entrega. | Resumen exhaustivo de los 8 entregables (E1-E8), rúbrica sobre 20 pts y desglose de los 10 casos propuestos. | Se revisó que las fechas y el formato correspondan a la UNSA (2026B). Se seleccionó formalmente el **Caso 6: RutaSIT Arequipa** identificando su atributo crítico de latencia. | **Aceptada** |
| **2** | 03/10/2026 | Antigravity AI | Propuesta de división de roles para 2 integrantes (Anderson Arce y Freddy Carlos) y recomendación de stack estándar. | Distribución de tareas (Anderson: E1, E3, E5, E6; Freddy: E2, E4, E7, E8) y stack base (FastAPI, Redis, PostgreSQL/PostGIS, Leaflet PWA en 1 VPS). | **Corrección crítica:** Se descartó la sugerencia preliminar de microservicios con brokers pesados (Kafka). Un equipo de 2 personas con entrega en 1 mes (R-01) en 1 VPS (R-03) colapsaría operativamente. Se fijó Monolito Modular Asíncrono. | **Corregida** |
| **3** | 03/10/2026 | Antigravity AI | Redacción de Drivers arquitectónicos y escenarios de calidad de 6 partes según plantilla oficial (E1). | 6 RFs, 4 atributos de calidad ordenados por prioridad, 5 restricciones de proyecto y 3 escenarios con métricas numéricas. | Se verificó que ninguna métrica use términos ambiguos ("rápido", "óptimo"). Todas usan números medibles: p95 $\le 15$ s, pérdida $\le 0.1\%$, 0 tramas perdidas tras corte celular, esfuerzo $\le 1.5$ días-persona, 0 downtime. | **Aceptada** |

---

## 2. Anexo: Prompts Completos y Respuestas

### Interacción 1: Análisis de Guía y Selección del Caso 6
* **Rol:** Consultor Académico de Arquitectura de Software.
* **Contexto:** Guía de Práctica 04 — Construcción de Software EPIS-UNSA.
* **Prompt emitido:**
  > *"Analiza en detalle la guía de laboratorio 'Guia_Lab04_Fundamentos_Arquitectura_Software_2026B.pdf'. Extrae los entregables, criterios de evaluación y opciones de casos disponibles."*
* **Respuesta resumida de la IA:**
  La IA identificó la estructura de 8 entregables (E1 a E8), las reglas de commit individuales, la necesidad de matrices ponderadas, diagramas Diagram as Code (Mermaid, PlantUML, Python Diagrams) y 3 ADRs.
* **Validación humana:**
  Confirmación del Caso 6: *"RutaSIT Arequipa"* con atributo crítico de rendimiento en tiempo real (300 buses cada 10 s, propagación $\le 15$ s).

---

### Interacción 2: Roles de Equipo y Selección de Stack Tecnológico
* **Rol:** Arquitecto de Software Senior y Líder Técnico.
* **Contexto:** Equipo de 2 estudiantes (Anderson Arce Valencia y Freddy Carlos Ccamaqque). Caso: RutaSIT Arequipa.
* **Prompt emitido:**
  > *"Número de grupo: 06. Integrantes: Arce Valencia Anderson Lino, Carlos Ccamaqque Wilson Freddy. ¿Cómo nos podemos separar los roles o actividades según la rúbrica? Y recomienda el stack tecnológico estándar y básico para este caso."*
* **Respuesta de la IA:**
  Propuso roles diferenciados: Anderson Arce como Arquitecto Líder y Diagramador (E1, E3, E5, E6); Freddy Carlos como Evaluador de Trade-offs y Redactor de ADRs (E2, E4, E7, E8). Propuso stack FastAPI + Redis + PostgreSQL/PostGIS + Leaflet PWA en Docker Compose.
* **Validación humana / Corrección de alucinación o sesgo:**
  La IA inicialmente propuso evaluar Kubernetes o microservicios. El equipo intervino y estableció que para 300 buses y 1 VPS económico, un Monolito Modular con Redis en memoria es 10 veces más económico y factible de entregar en 4 semanas.

---

### Interacción 3: Generación del Entregable E1 (drivers.md)
* **Rol:** Ingeniero de Requisitos y Arquitecto de Software.
* **Contexto:** RutaSIT Arequipa, restricciones R-01 (1 mes), R-02 (2 devs), R-03 (1 VPS económico).
* **Prompt emitido:**
  > *"Genera el archivo docs/architecture/drivers.md siguiendo estrictamente la plantilla de la guía. Debe incluir mínimo 5 RF con actores, mínimo 4 atributos de calidad priorizados con justificación, mínimo 4 restricciones y 3 escenarios de 6 partes con medidas cuantitativas."*
* **Respuesta de la IA:**
  Generó el archivo completo con 6 RFs, 4 atributos liderados por Rendimiento en tiempo real, 5 restricciones realistas y 3 escenarios estructurados en tablas de seis partes.
* **Validación humana:**
  Se inspeccionó la tabla de escenarios asegurando que el QA-01 refleje exactamente el requerimiento crítico de la guía (300 buses cada 10 s, ETA $\le 15$ s). Se aprobó y versionó en Git con el mensaje `E1: drivers y escenarios de calidad`.
