# Cuestionario — Laboratorio 06: Modelo C4 (Grupo 06, RutaSIT Arequipa)

## 1. ¿Qué problema de los diagramas tradicionales de "cajas y flechas" resuelve el modelo C4? Dé un ejemplo de ambigüedad que haya evitado en su caso.
Resuelve la **ambigüedad semántica** y la **falta de jerarquía estandarizada** de los diagramas informales de cajas y flechas. En un diagrama tradicional no se sabe si una "caja" representa un servidor físico, un contenedor Docker, una base de datos, una librería de software o un sistema externo completo; ni si una "flecha" denota una llamada síncrona HTTP, un mensaje por cola, una relación de dependencia de compilación o un flujo de datos sin protocolo.

**Ejemplo en RutaSIT:** En un diagrama informal, elementos como *OpenStreetMap*, *PostgreSQL/PostGIS* y el *Servicio de Ingesta GPS* se dibujarían como cajas idénticas conectadas por líneas genéricas. En el modelo C4:
- *OpenStreetMap* queda claramente categorizado como un `Software System` externo con la etiqueta `Externo` (Nivel 1).
- *PostgreSQL/PostGIS* queda identificado como un `Container` de base de datos relacional interna (Nivel 2).
- *Módulo de Ingesta GPS* queda formalizado como un `Component` dentro del contenedor del API monolítico (Nivel 3).
- Las flechas declaran explícitamente su descripción de negocio y protocolo de red (`JSON/HTTPS`, `Redis Pub/Sub`, `SQL/asyncpg`, `WSS`), eliminando cualquier ambigüedad de comunicación.

---

## 2. ¿Qué es un "contenedor" en C4 y por qué no equivale a un contenedor Docker? Indique un contenedor de su caso que no se ejecute en Docker.
En el modelo C4, un **contenedor** es una unidad de software ejecutable de alto nivel o un almacén de datos que corre en su propio espacio de memoria/proceso y que puede desplegarse de manera independiente (por ejemplo: una Single-Page Application en el navegador, una aplicación de consola o worker, una API web o una base de datos).

**No equivale a un contenedor Docker** porque Docker es un mecanismo de empaquetamiento y aislamiento a nivel de sistema operativo Linux (namespaces, cgroups), mientras que el contenedor C4 es una frontera arquitectónica y lógica de ejecución. Un contenedor C4 puede ejecutarse directamente sobre el sistema operativo anfitrión, en una máquina virtual, en una función serverless o en el motor de JavaScript de un navegador cliente.

**Ejemplo en RutaSIT:** La **PWA del Pasajero SIT** (`pwa`) y el **Panel Web de Operaciones** (`panel`) son contenedores C4 (aplicaciones frontend web SPA construidas con HTML5/TypeScript y Leaflet) que se ejecutan en el navegador web del smartphone del pasajero o de la PC del operador, **fuera de cualquier contenedor Docker**.

---

## 3. ¿Qué público y qué nivel de detalle tiene cada uno de los cuatro niveles de C4? ¿Por qué rara vez se dibuja el nivel 4 a mano?
| Nivel C4 | Audiencia principal | Nivel de detalle | Contenido |
|---|---|---|---|
| **Nivel 1: Contexto del Sistema** | Usuarios, directivos, stakeholders de negocio, desarrolladores y personal externo | Visión panorámica (zoom exterior) | El sistema en su entorno, actores humanos (personas) y dependencias con sistemas externos. |
| **Nivel 2: Contenedores** | Arquitectos de software, desarrolladores, soporte y operaciones (DevOps/SRE) | Topología de alto nivel | Aplicaciones web, APIs, workers, bases de datos, buses de mensajes, responsabilidades y protocolos. |
| **Nivel 3: Componentes** | Desarrolladores de software y líderes técnicos | Estructura interna de un contenedor | Módulos, controladores, servicios, repositorios, interfaces internas y sus interconexiones. |
| **Nivel 4: Código** | Desarrolladores de software individuales | Máximo detalle de bajo nivel | Diagramas de clases UML, interfaces, métodos, atributos y patrones de diseño. |

**¿Por qué rara vez se dibuja el Nivel 4 a mano?**
1. **Volatilidad extrema:** El código cambia con cada commit o refactorización diaria; mantener diagramas de clases a mano genera deuda documental y rápida obsolescencia.
2. **Volumen inmanejable:** Modelar a mano decenas o cientos de clases por componente consume un tiempo desproporcionado respecto al valor que aporta.
3. **Automatización:** Existen herramientas de ingeniería inversa y generación bajo demanda (como `pyreverse`, herramientas IDE o generadores de AST) que pueden extraer el diagrama de clases exacto del código fuente solo cuando se necesita analizar un patrón complejo.

---

## 4. Compare la vista dinámica de C4 con el diagrama de secuencia UML de su flujo crítico. ¿Cuándo usaría cada una?
Ambas representan el comportamiento temporal de un escenario específico (en nuestro caso, **HU-01: Consultar el tiempo de llegada del bus**):
- **Vista Dinámica C4:** Proyecta la secuencia numerada de pasos (1, 2, 3...) directamente sobre el diagrama espacial de contenedores o componentes existentes en el modelo C4. Comunica con claridad cómo una petición atraviesa las fronteras arquitectónicas, redes y subsistemas sin añadir nuevas abstracciones gráficas.
- **Diagrama de Secuencia UML:** Utiliza líneas de vida verticales independientes para cada objeto o clase, modelando formalmente llamadas sincrónicas/asincrónicas, tiempos de activación, mensajes de retorno y argumentos de métodos.

**Criterio de uso:**
- Usaría la **vista dinámica C4** para comunicar la arquitectura a nivel de sistema a desarrolladores, DevOps o arquitectos que necesitan entender el recorrido end-to-end de un flujo crítico entre contenedores/componentes y sus protocolos de red.
- Usaría el **diagrama de secuencia UML** en la fase de diseño detallado o implementación, cuando el equipo de programación necesita definir los métodos exactos, signaturas de funciones y el orden de ejecución entre clases u objetos en memoria.

---

## 5. ¿Qué ventaja concreta tiene modelar con Structurizr DSL frente a dibujar cada vista con C4-PlantUML o Mermaid?
La ventaja fundamental es que Structurizr DSL implementa **Architecture as Code con Fuente Única de Verdad (Single Source of Truth)** frente a la **diagramación desconectada**:
- **Consistencia automática:** En Structurizr DSL los elementos (personas, sistemas, contenedores, componentes, relaciones) se declaran una sola vez en el bloque `model`. Cada vista (`systemContext`, `container`, `component`, `dynamic`, `deployment`) es una proyección declarativa de ese mismo grafo. Si se modifica la descripción de una relación o la tecnología de un contenedor, todas las vistas se actualizan automáticamente sin riesgo de contradicciones.
- **Evita la duplicación y errores humanos:** En C4-PlantUML o Mermaid puro, cada diagrama es un archivo independiente. Si se renombra un contenedor o cambia un protocolo, el ingeniero debe recordar modificar manualmente 5 archivos distintos, generando desincronización y errores sutiles.
- **Exportación agnóstica:** El DSL de Structurizr puede compilarse y exportarse automáticamente mediante CLI a múltiples formatos estándar (PlantUML, Mermaid, DOT, JSON, Web), permitiendo inspección, versionado y pipelines de CI/CD.

---

## 6. ¿Qué elementos del modelo C4 de su caso se justifican con el ADR-001 del Laboratorio 04? Cite al menos dos.
1. **Separación entre API Gateway/ASGI (`api`) y el Worker de Segundo Plano (`worker`) mediante Redis Streams:**
   El ADR-001 estipuló un monolito modular asíncrono para soportar 30 tramas/s de telemetría de 300 buses sin bloquear el hilo principal. En el modelo C4, el contenedor `api` recibe la telemetría por HTTP y escribe en Redis en $<1$ ms, mientras que el contenedor `worker` (instancia independiente en Python) consume el stream de Redis y ejecuta el cómputo geométrico de geocercas y ETA fuera del ciclo de petición-respuesta.
2. **Dualidad de almacenamiento: Redis (`redis`) para estado volátil en tiempo real y PostgreSQL/PostGIS (`db`) para persistencia espacial e histórica:**
   Justificado en el ADR-001 y ADR-002 para cumplir el atributo de calidad crítico QA-01 ($\le 15$ s de latencia p95) en un VPS de bajo costo ($\le \$12$/mes). Redis maneja el estado instantáneo de la flota y el broker Pub/Sub para 1,500 pasajeros simultáneos, mientras PostgreSQL persiste el catálogo geográfico y recibe escrituras en lote consolidado cada 5 s para no saturar las operaciones de I/O de disco.

---

## 7. Describa un error de la IA al generar o revisar su modelo C4 y cómo lo detectó con la lista de revisión.
Durante la revisión automatizada con IA (Interacción 22), el LLM generó un hallazgo que señalaba como "defecto grave" que el contenedor `worker` mantuviera una relación directa con el contenedor de base de datos `db` (PostgreSQL) para consultar el catálogo de rutas y paraderos georreferenciados. La IA argumentó que toda comunicación con la base de datos debía pasar obligatoriamente a través de la API REST para mantener "encapsulamiento de microservicios".

**Detección y resolución:**
Al contrastar la observación con la lista de revisión oficial de c4model.com (Pregunta 2: *"¿Las relaciones reflejan la realidad arquitectónica y el diseño aprobado?"*) y el ADR-001 del proyecto:
- Confirmamos que nuestra arquitectura es un **monolito modular asíncrono** en un único VPS, no una malla de microservicios distribuidos.
- Forzar al `worker` a consultar el catálogo de paraderos a través de llamadas HTTP a la API REST introduciría latencia de red innecesaria, serialización JSON redundante y sobrecarga al event loop de FastAPI.
- El `worker` y el `api` comparten el mismo modelo de dominio y la misma base de datos relacional de catálogo.
Por lo tanto, se catalogó y descartó formalmente el hallazgo de la IA como un **falso positivo** arquitectural, preservando la relación directa `worker -> db` con `SQL/asyncpg`.


---

## 8. ¿Cómo adaptaría la explicación de su arquitectura para un docente evaluador, un inversionista y un nuevo developer del equipo?
La arquitectura es la misma; cambia el nivel de zoom y lo que se destaca en cada caso.

- **Docente evaluador:** se presenta el modelo completo con trazabilidad. Se parte de `workspace.dsl` como fuente única, se recorren las cinco vistas y se muestra cómo cada contenedor se justifica con el ADR-001 y cada componente coincide con `paquetes.puml` del Lab 05. Se agrega `revision-c4.md` (lista oficial aplicada, con falsos positivos de la IA) y `bitacora-ia.md` como evidencia del proceso.
- **Inversionista:** solo el Nivel 1 y el despliegue. Se explica qué problema resuelve (pasajeros sin información de llegada de los buses), quién lo usa, de qué servicios externos depende (GPS, OpenStreetMap, notificaciones push) y que el MVP corre en un solo VPS de hasta 12 USD al mes, con salida en un mes. Sin protocolos ni nombres de tecnologías, tal como en `explicacion.md`.
- **Nuevo developer:** se entra por el Nivel 2 y el Nivel 3. Se indica qué hace cada contenedor (API, worker, Redis, PostgreSQL/PostGIS), cómo se comunican y con qué protocolo, y cómo se sigue el flujo "Consultar tiempo de llegada" en la vista dinámica. Luego se le remite al diagrama de clases del Lab 05 (nivel 4) y se le pide levantar Structurizr Lite para navegar el modelo.
