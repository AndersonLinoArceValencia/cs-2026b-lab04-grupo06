# Auditoría y Lista de Revisión Oficial del Modelo C4 (Laboratorio 06)

Este documento aplica la lista de revisión oficial de **c4model.com** a las cinco vistas arquitectónicas generadas en el sistema **RutaSIT Arequipa**, documentando la evidencia en el modelo y evaluando las observaciones de la IA para identificar falsos positivos.

---

## 1. Evaluación de Vistas con la Lista Oficial (c4model.com/diagrams/checklist)

| Vista C4 | Grupo | Pregunta de la Lista de Revisión | Cumple (Sí / No) | Evidencia en el Modelo / Diagrama | Observación / Corrección |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Contexto (N1)** | General | ¿Tiene título, tipo de diagrama y alcance claro? | **Sí** | Título explícito: `"System Context View: RutaSIT Arequipa"`. Muestra la frontera entre el sistema y su entorno. | Cumple con la vista de negocio. |
| **Contexto (N1)** | Elementos | ¿Cada elemento tiene nombre, tipo y descripción de rol? | **Sí** | Personas (`Pasajero`, `Operador`) y sistemas (`RutaSIT`, `GPS`, `OSM`, `Web Push`) con descripciones claras. | No contiene jerga tecnológica interna. |
| **Contexto (N1)** | Relaciones | ¿Cada flecha tiene etiqueta de intención activa y coincide en dirección? | **Sí** | Flechas con verbos de negocio: `"Consulta rutas..."`, `"Supervisa ubicación..."`, `"Envía telemetría..."`. | No usa verbos ambiguos como "usa". |
| **Contenedores (N2)** | General | ¿El alcance delimita claramente el sistema y sus aplicaciones? | **Sí** | Subgrafo `"RutaSIT Arequipa"` agrupando los 6 contenedores (`pwa`, `panel`, `api`, `worker`, `redis`, `db`). | Separa aplicaciones de almacenes. |
| **Contenedores (N2)** | Elementos | ¿Cada contenedor indica su tecnología concreta y responsabilidad? | **Sí** | PWA (`React + Leaflet`), API (`FastAPI ASGI`), Worker (`Python Worker`), Redis (`Redis 7.x`), DB (`PostGIS 3.4`). | Cumple con ADR-001 y ADR-002. |
| **Contenedores (N2)** | Relaciones | ¿Se indican protocolos explícitos de comunicación? | **Sí** | Etiquetas con protocolos: `HTTPS`, `HTTPS / WSS`, `HTTPS/JSON`, `Redis protocol`, `SQL/TCP`. | Protocolos técnicos correctos. |
| **Componentes (N3)** | General | ¿Se enfoca en el contenedor principal y muestra su estructura interna? | **Sí** | Subgrafo centrado exclusivamente en el contenedor `API Monolito Asíncrono`. | Delimita componentes internos. |
| **Componentes (N3)** | Elementos | ¿Los componentes coinciden 1:1 con el diseño de paquetes y sin ciclos? | **Sí** | 5 componentes (`ingesta`, `eta`, `notificaciones`, `catalogo`, `supervision`) idénticos a `paquetes.puml`. | Cumple con regla C4 sin dependencias circulares. |
| **Componentes (N3)** | Relaciones | ¿Las dependencias internas y externas indican responsabilidades claras? | **Sí** | `eta` usa `ingesta` (IProveedorGPS) y `catalogo`; `notificaciones` escucha eventos y canaliza a Redis y Push. | Acoplamiento desacoplado. |
| **Dinámica (Flujo)** | General | ¿Modela un escenario crítico numerado paso a paso? | **Sí** | Flujo `"ConsultarTiempoLlegada"` (HU-01) con 8 pasos ordenados secuencialmente. | Mismo flujo que secuencia UML. |
| **Dinámica (Flujo)** | Relaciones | ¿Cada paso corresponde estrictamente a una relación existente? | **Sí** | Los 8 pasos corresponden a relaciones previamente declaradas en el modelo `workspace.dsl`. | Sin relaciones inventadas. |
| **Despliegue (N5)** | General | ¿Muestra el entorno de producción con nodos anidados de infraestructura? | **Sí** | Nodos anidados: Smartphones/PCs cliente $\rightarrow$ Navegador; Servidor VPS $\rightarrow$ Docker Compose $\rightarrow$ Contenedores. | Coherente con `despliegue.py`. |
| **Despliegue (N5)** | Elementos | ¿Cada nodo indica sistema operativo, tamaño y restricción de presupuesto? | **Sí** | Nodo VPS declara: `"Ubuntu 24.04 LTS, 4 vCPU, 8 GB RAM (≤ $12 USD/mes)"`. Todos los contenedores tienen instancia. | Cumple restricción R-03. |

---

## 2. Auditoría con IA y Detección de Falsos Positivos (Prompt IA 2)

Durante la evaluación de las vistas con el **Prompt IA 2 (Auditor C4)**, la IA generó el siguiente reporte crítico donde se detectaron falsos positivos provocados por la rigidez sintáctica del asistente:

### Falso Positivo N.º 1: "Ausencia de protocolos tecnológicos en las flechas del Diagrama de Contexto"
* **Observación emitida por la IA:**  
  > *"En el diagrama de contexto (`structurizr-Contexto`), las flechas entre el Pasajero y RutaSIT, y entre el Operador y RutaSIT carecen de tecnología o protocolo de red (por ejemplo, falta indicar HTTPS o WebSockets). Debe agregarse el protocolo para cumplir con la lista de revisión de relaciones."*
* **Evaluación humana y justificación técnica:**  
  * **Clasificación:** **FALSO POSITIVO**.
  * **Justificación según la regla oficial C4:** Simon Brown y la guía oficial de C4 establecen taxativamente que el **Nivel 1 (Contexto)** está destinado a personas de negocio, gerentes y usuarios no técnicos. En este nivel está **terminantemente prohibido incluir protocolos técnicos o nombres de librerías** (como HTTPS, REST o JSON), ya que estos detalles pertenecen exclusivamente a los Niveles 2 y 3. Introducir protocolos en el contexto oscurece la comprensión del propósito del sistema.
  * **Acción tomada:** Se rechazó la sugerencia de la IA y se mantuvieron las flechas con verbos de intención pura (*"Consulta rutas, paraderos y tiempos estimados de llegada"*).

### Falso Positivo N.º 2: "Falta del contenedor Docker Compose en el Diagrama de Contenedores"
* **Observación emitida por la IA:**  
  > *"En el diagrama de contenedores (`structurizr-Contenedores`), no figura la caja de Docker Compose que gestiona la API y la Base de Datos, por lo que el diagrama está incompleto."*
* **Evaluación humana y justificación técnica:**  
  * **Clasificación:** **FALSO POSITIVO**.
  * **Justificación según la regla oficial C4:** Un *contenedor C4* representa una unidad de software desplegable o almacén de datos (un ejecutable, una app web, una base de datos). **Docker Compose es infraestructura de soporte y orquestación**, no un contenedor C4. Confundir contenedor C4 con contenedor Docker es uno de los errores conceptuales más frecuentes advertidos en la sección 1.7 de la guía. Docker Compose debe figurar únicamente en la **Vista de Despliegue** como un nodo de ejecución.
  * **Acción tomada:** Se rechazó la observación y se mantuvo Docker Compose exclusivamente en el Nivel 5 de despliegue.
