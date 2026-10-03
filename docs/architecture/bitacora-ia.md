# Bitácora de uso de IA — RutaSIT Arequipa

Esta bitácora registra las interacciones con asistentes de Inteligencia Artificial durante el diseño arquitectónico de **RutaSIT Arequipa**, aplicando el principio de la guía: *"La IA propone, el equipo decide y verifica"*.

---

## 1. Registro de Interacciones

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|:---:|:---:|:---:|---|---|---|:---:|
| **1** | 03/10/2026 | Antigravity AI | Análisis estructural de la Guía de Laboratorio 04 y mapeo de los requerimientos de entrega. | Resumen exhaustivo de los 8 entregables (E1-E8), rúbrica sobre 20 pts y desglose de los 10 casos propuestos. | Se revisó que las fechas y el formato correspondan a la UNSA (2026B). Se seleccionó formalmente el **Caso 6: RutaSIT Arequipa** identificando su atributo crítico de latencia. | **Aceptada** |
| **2** | 03/10/2026 | Antigravity AI | Propuesta de división de roles para 2 integrantes (Anderson Arce y Freddy Carlos) y recomendación de stack estándar. | Distribución de tareas (Anderson: E1, E3, E5, E6; Freddy: E2, E4, E7, E8) y stack base (FastAPI, Redis, PostgreSQL/PostGIS, Leaflet PWA en 1 VPS). | **Corrección crítica:** Se descartó la sugerencia preliminar de microservicios con brokers pesados (Kafka/Kubernetes). Un equipo de 2 personas con entrega en 1 mes (R-01) en 1 VPS (R-03) colapsaría operativamente. Se fijó Monolito Modular Asíncrono. | **Corregida** |
| **3** | 03/10/2026 | Antigravity AI | Redacción de Drivers arquitectónicos y escenarios de calidad de 6 partes según plantilla oficial (E1). | 6 RFs, 4 atributos de calidad ordenados por prioridad, 5 restricciones de proyecto y 3 escenarios con métricas numéricas. | Se verificó que ninguna métrica use términos ambiguos ("rápido", "óptimo"). Todas usan números medibles: p95 $\le 15$ s, pérdida $\le 0.1\%$, 0 tramas perdidas tras corte celular, esfuerzo $\le 1.5$ días-persona, 0 downtime. | **Aceptada** |
| **4** | 03/10/2026 | Antigravity AI | **(E2 - Prompt 1)** Generación de 3 alternativas de estilo arquitectónico para sistema de transportes con alta concurrencia en 1 VPS. | Propuso: A) Monolito en capas (Django), B) Microservicios distribuidos (FastAPI + RabbitMQ), C) Monolito modular asíncrono (FastAPI + Redis). Recomendó la opción C. | **Verificación del equipo:** Se validó mediante cálculo de carga (300 buses $\times$ 1 trama/10 s = 30 req/s continuas). Un monolito síncrono WSGI saturaría hilos de ejecución rápidamente; y microservicios consumiría >4 GB de RAM solo en orquestación y colas, violando R-03. La recomendación C es la única viable. | **Aceptada** |
| **5** | 03/10/2026 | Antigravity AI | **(E2 - Prompt 2)** Crítica adversarial ("abogado del diablo") contra el Monolito Modular Asíncrono recomendado. | Señaló 5 riesgos críticos en producción: 1) Bloqueo del Event Loop por cómputo espacial, 2) Punto único de falla de Redis, 3) Erosión modular por prisas de entrega, 4) Agotamiento de sockets con pasajeros, 5) Agotamiento de conexiones a BD. | **Corrección crítica del equipo:** Se refutó la suposición ingenua de que un monolito asíncrono básico soporta la carga sin bloquearse. Se corrigió la propuesta inicial adoptando la *"Alternativa C Corregida"* (desacople de CPU mediante Redis Streams y workers en segundo plano) y se formalizaron las opciones en [`demostracion-abogado-del-diablo.md`](demostracion-abogado-del-diablo.md). | **Corregida** |
| **6** | 03/10/2026 | Antigravity AI | **(E3)** Generación del código Diagram as Code en Mermaid (`arquitectura.mmd`) a partir de la matriz de decisión y drivers. | Diagrama con 3 actores, 5 módulos de dominio explícitos, capa de infraestructura asíncrona, Redis y PostgreSQL/PostGIS, más servicios externos (OpenStreetMap y Web Push). | Se verificó la correspondencia biunívoca con los RF de `drivers.md` (RF-01 a RF-06), el aislamiento por subgraphs y la dirección no circular de dependencias. Se exportaron imágenes PNG y SVG a `diagramas/img/`. | **Aceptada** |
| **7** | 03/10/2026 | Antigravity AI | **(E5)** Modelado en PlantUML de la segunda mejor opción (`alternativa.puml`) con nota explicativa de descarte. | Diagrama de componentes de la Alternativa A (Monolito en capas Django) con nota técnica de descarte citando su puntaje (3.35/5.00). | Se verificó que la nota cumpla la extensión de 3 a 5 líneas de la guía, justificando el descarte por bloqueo de workers WSGI y saturación de I/O en BD. Se generaron las imágenes PNG y SVG en `diagramas/img/`. | **Aceptada** |

---

## 2. Anexo: Prompts Completos y Respuestas

### Interacción 1: Análisis de Guía y Selección del Caso 6
* **Rol:** Consultor Académico de Arquitectura de Software.
* **Contexto:** Guía de Práctica 04 — Construcción de Software EPIS-UNSA.
* **Prompt emitido:**
  > *"Analiza en detalle la guía de laboratorio 'Guia_Lab04_Fundamentos_Arquitectura_Software_2026B.pdf'. Extrae los entregables, criterios de evaluación y opciones de casos disponibles."*
* **Respuesta resumida de la IA:**
  Identificó los 8 entregables (E1 a E8), reglas de commit individuales, matriz ponderada, Diagram as Code (Mermaid, PlantUML, Python Diagrams) y 3 ADRs.
* **Validación humana:**
  Confirmación del Caso 6: *"RutaSIT Arequipa"* con atributo crítico de rendimiento en tiempo real (300 buses cada 10 s, propagación $\le 15$ s).

---

### Interacción 2: Roles de Equipo y Selección de Stack Tecnológico
* **Rol:** Arquitecto de Software Senior y Líder Técnico.
* **Contexto:** Equipo de 2 estudiantes (Anderson Arce Valencia y Freddy Carlos Ccamaqque). Caso: RutaSIT Arequipa.
* **Prompt emitido:**
  > *"Número de grupo: 06. Integrantes: Arce Valencia Anderson Lino, Carlos Ccamaqque Wilson Freddy. ¿Cómo nos podemos separar los roles o actividades según la rúbrica? Y recomienda el stack tecnológico estándar y básico para este caso."*
* **Respuesta de la IA:**
  Propuso roles diferenciados: Anderson Arce (Arquitecto Líder y Diagramador) y Freddy Carlos (Evaluador de Trade-offs y Redactor de ADRs). Propuso stack FastAPI + Redis + PostgreSQL/PostGIS + Leaflet PWA en Docker Compose.
* **Validación humana / Corrección:**
  La IA inicialmente mencionó microservicios con brokers distribuidos. El equipo descartó esa opción por exceder la capacidad operativa de 2 personas en 4 semanas en un solo VPS modesto.

---

### Interacción 3: Generación del Entregable E1 (drivers.md)
* **Rol:** Ingeniero de Requisitos y Arquitecto de Software.
* **Contexto:** RutaSIT Arequipa, restricciones R-01 (1 mes), R-02 (2 devs), R-03 (1 VPS económico).
* **Prompt emitido:**
  > *"Genera el archivo docs/architecture/drivers.md siguiendo estrictamente la plantilla de la guía. Debe incluir mínimo 5 RF con actores, mínimo 4 atributos de calidad priorizados con justificación, mínimo 4 restricciones y 3 escenarios de 6 partes con medidas cuantitativas."*
* **Respuesta de la IA:**
  Generó el archivo completo con 6 RFs, 4 atributos de calidad liderados por Rendimiento en tiempo real, 5 restricciones realistas y 3 escenarios de 6 partes.
* **Validación humana:**
  Se verificaron los números de las medidas (p95 $\le 15$ s, $\le 0.1\%$ pérdida, $\le 1.5$ días-persona) y se realizó el commit `E1: drivers y escenarios de calidad`.

---

### Interacción 4: Generación de Alternativas de Estilo Arquitectónico (E2 - Prompt 1)
* **Rol:** Arquitecto de Software Senior en Sistemas de Transporte.
* **Contexto:** Seguimiento en tiempo real de buses de RutaSIT Arequipa (300 buses cada 10 s, propagación ETA $\le 15$ s, 2 devs, 1 VPS, 1 mes).
* **Prompt emitido:**
  > *"Actúa como arquitecto de software senior con experiencia en sistemas para Transportes. Contexto: Seguimiento en tiempo real de los buses del Sistema integrado de transporte. Ubicacion de los buses en el mapa tiempo estimado de llegada la paradero, alertas de desvio o congestios; notificaciones para el Sistema RutaSIT Arequipa, rendimiento en tiempo real 300 buses envian su posicion cada 10 s; ek tiempo estimado de llegada se actualiza en menos de 15 segundos. Restricciones: 2 developers con experiencia en Python/Django, presupuesto de hosting bajo (un VPS), MVP en 1 mes. Tarea: propón 3 alternativas de estilo arquitectónico. Para cada una indica fortalezas, debilidades, riesgos y qué atributos de calidad favorece o penaliza. Formato: tabla comparativa en Markdown y, al final, tu recomendación justificada. No inventes APIs ni capacidades de servicios; si no estás seguro, indícalo."*
* **Respuesta de la IA:**
  Propuso 3 opciones:
  1. *Monolito en Capas Tradicional (Django + PostgreSQL)*: Fácil y rápido, pero colapsa ante 30 req/s concurrentes y WebSockets masivos en WSGI.
  2. *Microservicios Distribuidos (FastAPI + RabbitMQ + Multi-BD)*: Excelente aislamiento, pero inviable para 2 personas en 1 mes y sobrepasa los recursos de 1 VPS.
  3. *Monolito Modular Asíncrono (FastAPI + Redis + PostgreSQL/PostGIS)*: Alta concurrencia nativa (ASGI), latencias sub-segundo en memoria y bajo consumo de RAM. Recomendada.
* **Validación humana:**
  El equipo validó que la Alternativa C equilibra rendimiento y restricción de recursos sin caer en la falacia de sobredimensionar la infraestructura.

---

### Interacción 5: Crítica Adversarial "Abogado del Diablo" (E2 - Prompt 2)
* **Rol:** Arquitecto Adversario / Abogado del Diablo.
* **Contexto:** Crítica estricta al Monolito Modular Asíncrono en RutaSIT Arequipa.
* **Prompt emitido:**
  > *"Ahora actúa como 'abogado del diablo'. Critica duramente la alternativa que recomendaste: ¿qué supuestos no se cumplen con nuestras restricciones?, ¿qué podría fallar en producción?, ¿qué costo oculto tiene? Enumera los 5 riesgos más graves y, para cada uno, una táctica arquitectónica de mitigación."*
* **Respuesta de la IA (5 Riesgos y Tácticas):**
  1. **Riesgo 1 (Bloqueo de Event Loop):** El cálculo geométrico de desvíos y distancias lineales hacia paraderos consume CPU; si se ejecuta sincrónicamente en una corrutina de FastAPI, congela las lecturas de los demás 299 buses. *Táctica:* Desacoplar el cómputo pesado mediante workers en segundo plano (`asyncio.to_thread` o proceso worker dedicado que lee de Redis).
  2. **Riesgo 2 (Punto Único de Falla en Memoria):** Al almacenar el último estado de los 300 buses exclusivamente en Redis dentro del único VPS, un reinicio del servicio borra temporalmente las posiciones activas. *Táctica:* Configurar persistencia periódica RDB/AOF en Redis y rehidratar el estado desde PostgreSQL durante el inicio de la app.
  3. **Riesgo 3 (Erosión rápida de los límites modulares):** Bajo la presión de entregar en 4 semanas (R-01) con solo 2 personas (R-02), los desarrolladores tenderán a importar modelos o funciones cruzadas directamente, convirtiendo el sistema en un monolito espagueti ("Big Ball of Mud"). *Táctica:* Reglas estrictas en CI mediante `import-linter` y carpetas de dominio aisladas con una fachada pública `service.py`.
  4. **Riesgo 4 (Agotamiento de sockets y file descriptors):** Si 1500 pasajeros abren WebSockets simultáneos en hora pico, los límites por defecto del kernel de Linux (`nofile = 1024`) rechazarán nuevas conexiones. *Táctica:* Ajuste de `ulimit -n 65535` en el sistema operativo y terminación de conexiones en Nginx con compresión gzip desactivada en WebSockets.
  5. **Riesgo 5 (Contención en pool de conexiones a BD):** 30 escrituras por segundo hacia PostgreSQL/PostGIS pueden agotar rápidamente el pool de conexiones estándar de SQLAlchemy/Asyncpg. *Táctica:* Ingesta en búfer en memoria (Redis Stream o lista) y persistencia en base de datos consolidada por lotes (*batch writing*) cada 5 segundos.
* **Validación humana / Decisión Corregida:**
  El equipo refutó la premisa de que un monolito modular estándar funcionaría sin problemas. Se obligó a reformular la arquitectura adoptando la **"Alternativa C Corregida"** con desacoplamiento estricto de tareas CPU-intensivas y búfer de Redis Streams. Las alternativas del abogado del diablo quedaron registradas en [`demostracion-abogado-del-diablo.md`](demostracion-abogado-del-diablo.md) y se integraron en el diseño final. Decisión: **Corregida**.

---

### Interacción 6: Generación del Diagrama de Arquitectura Mermaid (E3)
* **Rol:** Arquitecto de Software y Diagramador con IA.
* **Contexto:** Diagramación de la arquitectura ganadora (Monolito Modular Asíncrono Corregido) para RutaSIT Arequipa.
* **Prompt emitido:**
  > *"Genera el código Mermaid (`arquitectura.mmd`) de la arquitectura elegida a partir de `matriz-decision.md` y `drivers.md`. Debe incluir mínimo 2 actores, todos los módulos de dominio con sus RF correspondientes, capa de infraestructura asíncrona, bases de datos (Redis y PostgreSQL/PostGIS), servicios externos y dirección estricta de dependencias usando subgraphs."*
* **Respuesta de la IA:**
  Generó el diagrama con 3 actores (`Bus SIT`, `Pasajero SIT`, `Operador SIT`), capa de entrada ASGI (FastAPI + Nginx), 5 módulos (`M1` Ingesta, `M2` ETA/Geocercas, `M3` Notificaciones/WebSockets, `M4` Catálogo SIT, `M5` Supervisión), capa de infraestructura con workers y adaptadores, almacenamiento en Redis y PostgreSQL/PostGIS, y servicios externos (OpenStreetMap y Web Push).
* **Validación humana:**
  Se verificó que no existieran dependencias circulares, que cada módulo mapee a un RF de `drivers.md` y que la sintaxis compile limpiamente sin errores. Se exportaron las vistas gráficas (`arquitectura.svg` y `arquitectura.png`) y se realizó el commit `E3: diagrama Mermaid`. Decisión: **Aceptada**.

---

### Interacción 7: Diagrama PlantUML de la Alternativa Descartada (E5)
* **Rol:** Arquitecto Líder y Diagramador con IA.
* **Contexto:** Representación de la 2da mejor alternativa (Alternativa A: Monolito en capas Django) y justificación de descarte.
* **Prompt emitido:**
  > *"Genera el código PlantUML (`alternativa.puml`) para la segunda mejor alternativa de la matriz de decisión (Monolito en capas Django). Debe incluir actores (buses y usuarios), las capas del monolito, la base de datos PostgreSQL, el servicio de mapas y una nota explicativa de 3 a 5 líneas que cite su puntaje (3.35) y explique técnicamente por qué se descartó."*
* **Respuesta de la IA:**
  Generó el diagrama de componentes en PlantUML estructurado en 3 capas secuenciales (Presentación, Lógica y ORM) hacia PostgreSQL único, con la nota técnica de descarte detallando la saturación de workers síncronos WSGI y el colapso de I/O en la base de datos.
* **Validación humana:**
  Se verificó que la nota técnica cite puntualmente el puntaje de 3.35 de `matriz-decision.md` y demuestre la inviabilidad ante el requerimiento crítico de latencia de 15 s (QA-01). Se exportaron las imágenes renderizadas (`alternativa.png` y `alternativa.svg`) a `diagramas/img/`. Decisión: **Aceptada**.


