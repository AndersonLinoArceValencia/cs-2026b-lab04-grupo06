# Bitácora de uso de IA — RutaSIT Arequipa

Esta bitácora registra las interacciones con asistentes de Inteligencia Artificial durante el diseño arquitectónico de **RutaSIT Arequipa**, aplicando el principio de la guía: *"La IA propone, el equipo decide y verifica"*.

---

## 1. Registro de Interacciones

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|:---:|:---:|:---:|---|---|---|:---:|
| **1** | 03/10/2026 | Antigravity AI | Análisis estructural de la Guía de Laboratorio 04 y mapeo de los requerimientos de entrega. | Resumen exhaustivo de los 8 entregables (E1-E8), rúbrica sobre 20 pts y desglose de los 10 casos propuestos. | Se revisó que las fechas y el formato correspondan a la UNSA (2026B). Se seleccionó formalmente el **Caso 6: RutaSIT Arequipa** identificando su atributo crítico de latencia. | **Aceptada** |
| **2** | 03/10/2026 | Antigravity AI | Propuesta de división de roles para 2 integrantes (Anderson Arce y Freddy Carlos) y recomendación de stack estándar. | Distribución de tareas (Anderson: E1, E3, E5, E6; Freddy: E2, E4, E7, E8) y stack base (FastAPI, Redis, PostgreSQL/PostGIS, Leaflet PWA en 1 VPS). | **Corrección crítica:** Se descartó la sugerencia preliminar de microservicios con brokers pesados (Kafka/Kubernetes). Un equipo de 2 personas con entrega en 1 mes (R-01) en 1 VPS (R-03) colapsaría operativamente. Se fijó Monolito Modular Asíncrono. | **Corregida** |
| **3** | 03/10/2026 | Antigravity AI | Redacción de Drivers arquitectónicos y escenarios de calidad de 6 partes según plantilla oficial (E1). | 6 RFs, 4 atributos de calidad ordenados por prioridad, 5 restricciones de proyecto y 3 escenarios con métricas numéricas. | Se verificó que ninguna métrica use términos ambiguos ("rápido", "óptimo"). Todas usan números medibles: p95 $\le 15$ s, pérdida $\le 0.1\%$, 0 tramas perdidas tras corte celular, esfuerzo $\le 1.5$ días-persona, 0 downtime. | **Aceptada** |
| **4** | 03/10/2026 | Antigravity AI | **(E2 - Prompt 1)** Generación de 3 alternativas de estilo arquitectónico para sistema de transportes con alta concurrencia en 1 VPS. | Propuso: A) Monolito en capas (Django), B) Microservicios distribuidos (FastAPI + RabbitMQ), C) Monolito modular asíncrono (FastAPI + Redis). Recomendó la opción C. | **Verificación del equipo:** Se calculó la carga (300 buses $\times$ 1 trama/10 s = 30 req/s continuas). Microservicios exige 4 servicios, RabbitMQ y varias bases en un VPS de 4-8 GB para 2 personas en 1 mes, lo que excede R-01 y R-03. En ese momento también aceptamos que un monolito WSGI saturaría sus workers; después se comprobó que era exagerado (ver interacción 9). Se aceptó la recomendación C. | **Aceptada** |
| **5** | 03/10/2026 | Antigravity AI | **(E2 - Prompt 2)** Crítica adversarial ("abogado del diablo") contra el Monolito Modular Asíncrono recomendado. | Señaló 5 riesgos críticos en producción: 1) Bloqueo del Event Loop por cómputo espacial, 2) Punto único de falla de Redis, 3) Erosión modular por prisas de entrega, 4) Agotamiento de sockets con pasajeros, 5) Agotamiento de conexiones a BD. | **Corrección crítica del equipo:** Se refutó la suposición ingenua de que un monolito asíncrono básico soporta la carga sin bloquearse. Se corrigió la propuesta inicial adoptando la *"Alternativa C Corregida"* (desacople de CPU mediante Redis Streams y workers en segundo plano) y se formalizaron las opciones en [`demostracion-abogado-del-diablo.md`](demostracion-abogado-del-diablo.md). | **Corregida** |
| **6** | 03/10/2026 | Antigravity AI | **(E3)** Generación del código Diagram as Code en Mermaid (`arquitectura.mmd`) a partir de la matriz de decisión y drivers. | Diagrama con 3 actores, 5 módulos de dominio explícitos, capa de infraestructura asíncrona, Redis y PostgreSQL/PostGIS, más servicios externos (OpenStreetMap y Web Push). | Se verificó la correspondencia biunívoca con los RF de `drivers.md` (RF-01 a RF-06), el aislamiento por subgraphs y la dirección no circular de dependencias. Se exportaron imágenes PNG y SVG a `diagramas/img/`. | **Aceptada** |
| **7** | 03/10/2026 | Antigravity AI | **(E5)** Modelado en PlantUML de la segunda mejor opción (`alternativa.puml`) con nota explicativa de descarte. | Diagrama de componentes de la Alternativa A (Monolito en capas Django) con nota técnica de descarte citando su puntaje (3.35/5.00). | Se verificó que la nota cumpla la extensión de 3 a 5 líneas de la guía y se generaron las imágenes PNG y SVG en `diagramas/img/`. El argumento de la nota (workers WSGI e I/O saturados) y el puntaje 3.35 se corrigieron después: la nota actual cita 3.60 y el problema real del polling (ver interacción 9). | **Aceptada** |
| **8** | 03/10/2026 | Antigravity AI | **(E6)** Script de vista de despliegue (`despliegue.py`) y diagrama PlantUML de topología física en VPS (`despliegue.puml`). | Topología en clusters: 300 buses, PWA de pasajeros, Nginx, FastAPI ASGI, Redis Streams, PostgreSQL/PostGIS, Prometheus/Grafana y servicios externos. | Al detectarse la ausencia de Graphviz/pip en el sistema, se implementó el fallback oficial E6.4 (elaborar la vista física con PlantUML y documentarlo en el README). Se generaron `despliegue.png` y `despliegue.svg` en `diagramas/img/`. | **Aceptada** |
| **9** | 04/10/2026 | Claude | Revisión del repositorio completo contra la guía del Lab 04 para detectar entregables faltantes y errores. | Señaló que faltaban los ADR, el README y el cuestionario, y que la crítica contra la Alternativa A exageraba: "WSGI agota los workers con 30 req/s" y "2,5 millones de inserciones saturan el disco". | **Corrección con cálculo (Ley de Little):** $L = 30 \text{ req/s} \times 0.05 \text{ s} = 1.5$ peticiones en curso, que 5 a 9 workers de Gunicorn atienden sin problema; 2,5 millones de inserciones al día son 30 por segundo. Se subió el rendimiento de A de 2 a 3 (total 3.35 → 3.60) y la conclusión no cambió. También se retiró la cifra sin evidencia de "<1.5 GB de RAM". Ver [`matriz-decision.md`](matriz-decision.md#afirmaciones-de-la-ia-verificadas). | **Corregida** |
| **10** | 04/10/2026 | Claude | **(E4)** Borradores de ADR-001 (estilo), ADR-002 (base de datos geovial) y ADR-003 (transmisión en tiempo real) con la plantilla de la sección 1.5. | Tres ADR en estado "Aceptado", cada uno con contexto que cita drivers, al menos 2 alternativas y consecuencias. Para ADR-003 sopesó SSE frente a WebSocket. | Se comprobó que todos los IDs citados (RF-01 a RF-06, QA-01 a QA-03, R-01 a R-05) existen en `drivers.md`, que cada ADR tiene consecuencias positivas y negativas y que los puntajes coinciden con la matriz. Se añadió como consecuencia negativa que un solo VPS limita la disponibilidad de 99,5 % de QA-02 (unas 3,6 h de caída al mes). | **Aceptada** |
| **11** | 04/10/2026 | Claude | **(E6)** Ejecutar `despliegue.py` con Graphviz en lugar del plan B en PlantUML. | Corregir el docstring (instrucciones para Windows con `winget install graphviz`), generar PNG y SVG y usar líneas curvas para que las etiquetas no se crucen. | Se ejecutó `python docs/architecture/diagramas/despliegue.py` con Graphviz y se revisó la imagen: las etiquetas de las conexiones quedaban junto a la flecha equivocada con líneas ortogonales, así que se cambió a `splines=spline`. `despliegue.puml` queda como vista complementaria (`img/despliegue-plantuml.png`). Esto reemplaza el plan B de la interacción 8. | **Corregida** |
| **12** | 04/10/2026 | Claude | Revisión de faltantes contra la rúbrica; implementar el reto opcional (GitHub Action con mermaid-cli) y el gráfico opcional de la matriz con matplotlib (E2.5). | Workflow `.github/workflows/diagramas.yml` que renderiza cada `.mmd` a PNG y SVG y hace commit de las imágenes; script `diagramas/matriz.py` con barras apiladas por criterio. | Al probar `mmdc` en local falló porque no encontraba el navegador de Puppeteer: en el runner de GitHub se descarga al instalar mermaid-cli, pero Chromium necesita `--no-sandbox`, así que se agregó un archivo de configuración. Los totales del gráfico (3.60, 2.35 y 4.45) se compararon con el cálculo manual de la matriz, y el script comprueba que los pesos sumen 100 %. | **Corregida** |

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
  > *"Número de grupo: 06. Integrantes: [integrante 1], [integrante 2]. ¿Cómo nos podemos separar los roles o actividades según la rúbrica? Y recomienda el stack tecnológico estándar y básico para este caso."*
  >
  > *(Nombres reemplazados en esta bitácora: la guía pide no incluir datos personales en los prompts.)*
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
  Se verificó que la nota técnica cite puntualmente el puntaje de 3.35 de `matriz-decision.md` y demuestre la inviabilidad ante el requerimiento crítico de latencia de 15 s (QA-01). *(Corregido el 04/10/2026: el puntaje pasó a 3.60 y la nota se reescribió; ver interacción 9.)* Se exportaron las imágenes renderizadas (`alternativa.png` y `alternativa.svg`) a `diagramas/img/`. Decisión: **Aceptada**.

---

### Interacción 8: Vista de Despliegue Físico en VPS (E6)
* **Rol:** Arquitecto de Software e Ingeniero de Infraestructura con IA.
* **Contexto:** Topología física de despliegue en un único servidor VPS económico (2-4 vCPU, 4-8 GB RAM) para RutaSIT Arequipa.
* **Prompt emitido:**
  > *"Genera el script `despliegue.py` con la librería Python Diagrams y el diagrama de despliegue PlantUML `despliegue.puml`. Debe modelar dispositivos (300 buses GPS y pasajeros), proxy Nginx, cluster de aplicación FastAPI con workers desacoplados, cluster de almacenamiento (Redis y PostGIS), cluster de observabilidad (Prometheus y Grafana) y servicios externos con conexiones etiquetadas."*
* **Respuesta de la IA:**
  Generó el código Python con la librería `diagrams` agrupando por `Cluster` y conexiones `Edge(label=...)`. Ante la ausencia de `graphviz` y `pip` en el entorno Linux, generó la especificación complementaria en PlantUML (`despliegue.puml`) conforme a la regla oficial E6.4 y renderizó las imágenes `despliegue.svg` y `despliegue.png` en `diagramas/img/`.
* **Validación humana:**
  Se verificó que todos los componentes esenciales para operar con 30 req/s y 1500 conexiones de pasajeros estuvieran claramente ubicados en el VPS. Se exportó `despliegue.png` y se realizó el commit `E6: vista de despliegue`. Decisión: **Aceptada**.

---

### Interacción 9: Revisión del repositorio y verificación de afirmaciones
* **Herramienta:** Claude.
* **Prompt emitido:**
  > *"Quiero que revises este proyecto y que me digas que es lo que falta implementar"*
* **Respuesta resumida de la IA:**
  Listó lo que faltaba (carpeta `adr/`, README, cuestionario, commits y PR de ambos integrantes) y señaló como exageradas las afirmaciones contra la Alternativa A, con el cálculo de la Ley de Little.
* **Validación humana / Corrección:**
  Se rehízo el cálculo y se corrigieron la matriz, la nota de `alternativa.puml` y el documento del abogado del diablo. Decisión: **Corregida**.

---

### Interacciones 10 y 11: Redacción de ADR y vista de despliegue con Graphviz
* **Herramienta:** Claude.
* **Prompt emitido:**
  > *"Quiero que desarrolles y hagas las correcciones"*
* **Respuesta resumida de la IA:**
  Redactó ADR-001 a ADR-003, el README y el cuestionario, agregó al diagrama Mermaid las tácticas de mitigación (persistencia AOF, rehidratación y endpoint `/telemetry/batch`) y ejecutó `despliegue.py` con Graphviz.
* **Validación humana:**
  Se revisaron los IDs citados en los ADR contra `drivers.md` y los diagramas se volvieron a renderizar con mermaid-cli, PlantUML y Graphviz sin errores. Decisiones: **Aceptada** (ADR) y **Corregida** (despliegue).

---

### Interacción 12: Reto opcional y gráfico de la matriz
* **Herramienta:** Claude.
* **Prompt emitido:**
  > *"Queremos desarrollar la propuesta 6, ya creamos el git, ahora quiero verifiques que es lo que falta implementar. Revisa bien la estructura antes y empieza"*
* **Respuesta resumida de la IA:**
  Comparó el repositorio de GitHub con la copia local: los ADR, el cuestionario y las correcciones estaban sin commit, todos los commits eran de un solo integrante y no había Pull Requests. Propuso el workflow de mermaid-cli que ya figuraba en `PROPUESTA_PROYECTO.md` pero no existía, y el gráfico de la matriz con matplotlib.
* **Validación humana / Corrección:**
  Se renderizó `arquitectura.mmd` con mermaid-cli antes de confiar en el workflow; hubo que añadir la opción `--no-sandbox` para Chromium. Se ejecutó `matriz.py` y se comprobó que los totales coinciden con la tabla. Decisión: **Corregida**.

---

## 3. Registro de Interacciones (Laboratorio 05 — Diseño UML)

| N.º | Fecha | Herramienta | Actividad / Prompt | Propuesta de la IA | Verificación del Equipo (Reglas C1–C5) | Decisión |
|:---:|:---:|:---:|---|---|---|:---:|
| **13** | 07/10/2026 | Gemini 3.1 Pro | **(E1 — Prompt IA 1)** Adaptación del prompt para generar diagrama de clases a partir de `historia.md` y ADR-001. | Generó `clases.puml` con 7 clases, enumeración `EstadoViaje`, e interfaces (`IProveedorGPS`, `IServicioMapas`). | Se verificó que cumpliera con ADR-001 (puertos/adaptadores). Se validaron multiplicidades en ambos extremos (C5) y nombres de dominio correctos. | **Aceptada con ajustes** |

---

## 4. Anexo Lab 05: Detalle del Prompt IA 1 Adaptado

### Interacción 13: Generación del Diagrama de Clases (E1)
* **Fecha:** 07/10/2026
* **Herramienta:** Gemini 3.1 Pro
* **Prompt Adaptado:**
  > "Actúa como diseñador de software orientado a objetos.  
  > Contexto: Módulo de Monitoreo de RutaSIT Arequipa dentro de un monolito modular (ADR-001: puertos y adaptadores para integraciones externas con GPS y servicios de mapas).  
  > Historia y criterios: [HU-01: Como pasajero del SIT quiero consultar el tiempo estimado de llegada (ETA) de un bus a mi paradero actual...]  
  > Tarea: Genera un diagrama de clases en PlantUML con atributos tipados, operaciones, multiplicidades en ambos extremos, una enumeración para el estado del viaje y dos interfaces (puertos) para el proveedor GPS y mapas."
* **Resultado:** Diagrama en PlantUML guardado en `docs/design/clases.puml` y renderizado en PNG.
